#!/usr/bin/env python3
"""F9 streaming dictation with a bounded release wait and no live key injection."""
import argparse
import fcntl
import json
import logging
import math
import multiprocessing as mp
import os
from pathlib import Path
import selectors
import signal
import socket
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parent
RUNTIME = Path(os.environ.get('XDG_RUNTIME_DIR', '/tmp')) / 'f9-streaming'
MODEL = ROOT / 'moonshine-models/download.moonshine.ai/model/small-streaming-en/quantized_26_08_21'
FINALIZE_BUDGET = 1.35


def recognize(engine, model, inbox, outbox):
    """Inference stays outside the process receiving F9 release commands."""
    try:
        if engine == 'moonshine':
            import numpy as np
            from moonshine_voice import Transcriber, ModelArch
            recognizer = Transcriber(model, ModelArch.SMALL_STREAMING, update_interval=0.4,
                                     options={'keyterms': 'Omarchy,Hyprland,Codex,Claude,Gemini,F9',
                                              'keyterm_boost': '1.5',
                                              'vad_threshold': '0.4',
                                              'max_tokens_per_second': '8.0'})
        else:
            from vosk import Model, KaldiRecognizer, SetLogLevel
            SetLogLevel(-1)
            recognizer = Model(str(ROOT / 'vosk-model-small-en-us-0.15'))
        outbox.send({'engine': engine, 'kind': 'ready'})
        stream = None
        session = None
        lines = {}
        parts = []
        def publish(kind, text):
            outbox.send({'engine': engine, 'kind': kind, 'session': session, 'text': text})
        def changed(event):
            if hasattr(event, 'line'):
                lines[event.line.line_id] = event.line.text
                publish('partial', ' '.join(lines.values()).strip())
        while True:
            command, sid, audio = inbox.get()
            if command == 'quit':
                break
            if command == 'start':
                if stream is not None and engine == 'moonshine':
                    stream.close()
                session, lines, parts = sid, {}, []
                if engine == 'moonshine':
                    stream = recognizer.create_stream(update_interval=0.4)
                    stream.add_listener(changed)
                    stream.start()
                else:
                    stream = KaldiRecognizer(recognizer, 16000)
                continue
            if sid != session or stream is None:
                continue
            if command == 'audio':
                if engine == 'moonshine':
                    samples = np.frombuffer(audio, dtype='<i2').astype(np.float32) / 32768
                    stream.add_audio(samples.tolist(), 16000)
                else:
                    if stream.AcceptWaveform(audio):
                        text = json.loads(stream.Result()).get('text', '')
                        if text:
                            parts.append(text)
                    tail = json.loads(stream.PartialResult()).get('partial', '')
                    publish('partial', ' '.join([*parts, tail]).strip())
            elif command == 'stop':
                if engine == 'moonshine':
                    final = stream.stop()
                    if final:
                        for line in final.lines:
                            lines[line.line_id] = line.text
                    publish('final', ' '.join(lines.values()).strip())
                    stream.close()
                else:
                    final = json.loads(stream.FinalResult()).get('text', '')
                    publish('final', ' '.join([*parts, final]).strip())
                stream = None
            elif command == 'cancel':
                if engine == 'moonshine':
                    stream.close()
                stream = None
        if engine == 'moonshine':
            recognizer.close()
    except Exception as exc:
        logging.exception('%s inference worker failed', engine)
        outbox.send({'engine': engine, 'kind': 'error', 'error': str(exc)})


class Daemon:
    def __init__(self, args):
        self.args = args
        self.selector = selectors.DefaultSelector()
        self.workers = {}
        ctx = mp.get_context('spawn')
        for engine in ('moonshine', 'vosk'):
            inbox = ctx.Queue()
            inbox.cancel_join_thread()
            reader, writer = ctx.Pipe(duplex=False)
            proc = ctx.Process(target=recognize, args=(engine, str(args.model), inbox, writer), daemon=True)
            proc.start()
            writer.close()
            self.workers[engine] = {'proc': proc, 'inbox': inbox, 'reader': reader, 'ready': False}
            self.selector.register(reader, selectors.EVENT_READ, engine)
        self.capture = None
        self.session = 0
        self.results = {}
        self.samples = 0
        self.pending = b''
        self.osd_clients = []
        self.osd = None
        self.frame_seq = 0
        self.recording_started = 0

    def send(self, command, audio=None):
        for worker in self.workers.values():
            if worker['proc'].is_alive() and worker['ready']:
                worker['inbox'].put((command, self.session, audio))

    def drain(self, engine):
        worker = self.workers[engine]
        try:
            while worker['reader'].poll():
                msg = worker['reader'].recv()
                if msg['kind'] == 'ready':
                    worker['ready'] = True
                    logging.info('%s worker ready', engine)
                elif msg['kind'] == 'error':
                    worker['ready'] = False
                    logging.error('%s: %s', engine, msg['error'])
                elif msg.get('session') == self.session:
                    previous = self.results.get(engine, {})
                    if previous.get('kind') != 'final':
                        self.results[engine] = msg
        except (EOFError, OSError):
            worker['ready'] = False
            try:
                self.selector.unregister(worker['reader'])
            except KeyError:
                pass

    def start(self):
        if self.capture:
            return {'state': 'recording'}
        if not any(w['ready'] and w['proc'].is_alive() for w in self.workers.values()):
            raise RuntimeError('Recognition models are still loading')
        self.session += 1
        self.results = {}
        self.samples = 0
        self.pending = b''
        self.send('start')
        command = ['parec', '--raw', '--rate=16000', '--format=s16le', '--channels=1',
                   '--latency-msec=20', '--process-time-msec=20']
        if self.args.source:
            command += ['--device', self.args.source]
        self.capture = subprocess.Popen(command, stdout=subprocess.PIPE)
        os.set_blocking(self.capture.stdout.fileno(), False)
        self.selector.register(self.capture.stdout, selectors.EVENT_READ, 'audio')
        self.recording_started = time.monotonic()
        logging.info('Recording started session=%s', self.session)
        return {'state': 'recording'}

    def feed(self, raw):
        raw = self.pending + raw
        size = len(raw) & ~1
        self.pending, raw = raw[size:], raw[:size]
        if not raw:
            return
        self.samples += len(raw) // 2
        self.send('audio', raw)
        if self.osd_clients:
            values = struct.unpack('<' + 'h' * (len(raw) // 2), raw)
            frames = bytearray()
            for offset in range(0, len(values), 160):
                frame = values[offset:offset + 160]
                lo, hi = min(frame) / 32768, max(frame) / 32768
                peak = max(abs(lo), abs(hi), 0.000001)
                frames.extend(struct.pack('=Ifff', self.frame_seq, lo, hi, max(-120, 20 * math.log10(peak))))
                self.frame_seq = (self.frame_seq + 1) & 0xffffffff
            for client in self.osd_clients[:]:
                try:
                    if client.send(frames) != len(frames):
                        raise OSError('Slow OSD')
                except OSError:
                    client.close()
                    self.osd_clients.remove(client)

    def audio(self):
        try:
            raw = os.read(self.capture.stdout.fileno(), 1600)
        except BlockingIOError:
            return
        if raw:
            self.feed(raw)
        else:
            self.stop(cancel=True)
            logging.error('Microphone capture exited')

    def stop(self, cancel=False):
        if not self.capture:
            return {'state': 'idle', 'characters': 0}
        released = time.monotonic()
        capture = self.capture
        self.selector.unregister(capture.stdout)
        capture.terminate()
        drain_until = released + 0.08
        while True:
            try:
                raw = os.read(capture.stdout.fileno(), 1600)
            except BlockingIOError:
                if capture.poll() is not None or time.monotonic() >= drain_until:
                    break
                time.sleep(0.001)
                continue
            if not raw:
                break
            if not cancel:
                self.feed(raw)
            if time.monotonic() >= drain_until:
                break
        try:
            capture.wait(timeout=0.08)
        except subprocess.TimeoutExpired:
            capture.kill()
            capture.wait(timeout=0.08)
        capture.stdout.close()
        self.capture = None
        if cancel:
            self.send('cancel')
            self.results = {}
            logging.info('Recording cancelled')
            return {'state': 'idle', 'characters': 0}
        self.send('stop')
        deadline = released + FINALIZE_BUDGET
        primary = self.workers['moonshine']
        while time.monotonic() < deadline:
            for engine in self.workers:
                self.drain(engine)
            if self.results.get('moonshine', {}).get('kind') == 'final':
                break
            if not primary['ready'] and self.results.get('vosk', {}).get('kind') == 'final':
                break
            time.sleep(0.002)
        for engine in self.workers:
            self.drain(engine)
        moon = self.results.get('moonshine', {})
        fallback = self.results.get('vosk', {})
        if moon.get('kind') == 'final':
            selected = moon
        elif fallback.get('kind') == 'final':
            selected = fallback
        else:
            selected = moon if moon.get('text') else fallback
        text = selected.get('text', '').strip()
        if selected.get('engine') == 'vosk' and text:
            text = text[0].upper() + text[1:]
        ready_ms = round((time.monotonic() - released) * 1000, 1)
        output_status = 'empty'
        if text:
            output_status = self.output(text, released + 1.9)
        result = {'state': 'idle', 'characters': len(text), 'engine': selected.get('engine', 'none'),
                  'finalized': selected.get('kind') == 'final', 'ready_ms': ready_ms,
                  'output_ms': round((time.monotonic() - released) * 1000, 1),
                  'output_status': output_status, 'audio_secs': round(self.samples / 16000, 2)}
        logging.info('Recording completed: %s', json.dumps(result))
        state = Path.home() / '.local/state/f9-streaming'
        state.mkdir(parents=True, exist_ok=True)
        (state / 'last-result.json').write_text(json.dumps(result) + '\n')
        return result

    def output(self, text, deadline):
        if self.args.output_file:
            Path(self.args.output_file).write_text(text)
            return 'file'
        try:
            subprocess.run([str(ROOT / 'f9-wtype'), '--', text], check=True,
                           timeout=max(0.05, deadline - time.monotonic()))
            return 'typed'
        except (subprocess.SubprocessError, OSError):
            subprocess.run(['wl-copy'], input=text.encode(), check=True, timeout=0.1)
            subprocess.Popen(['notify-send', '-t', '2500', 'Dictation copied',
                              'Typing failed; the text is on the clipboard.'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return 'clipboard'

    def serve(self):
        path = self.args.socket
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        lock = open(path.with_suffix('.lock'), 'w')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        path.unlink(missing_ok=True)
        server = socket.socket(socket.AF_UNIX)
        server.bind(str(path))
        os.chmod(path, 0o600)
        server.listen(8)
        self.selector.register(server, selectors.EVENT_READ, 'control')
        osd_path = path.parent / 'audio.sock'
        osd_path.unlink(missing_ok=True)
        osd_server = socket.socket(socket.AF_UNIX)
        osd_server.bind(str(osd_path))
        os.chmod(osd_path, 0o600)
        osd_server.listen(4)
        self.selector.register(osd_server, selectors.EVENT_READ, 'osd')
        if not self.args.no_osd:
            self.osd = subprocess.Popen(['/usr/lib/voxtype/voxtype-osd-gtk4', '--socket', str(osd_path)])
        def shutdown(*_):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, shutdown)
        try:
            while True:
                for key, _ in self.selector.select(timeout=0.1):
                    kind = key.data
                    if kind in self.workers:
                        self.drain(kind)
                    elif kind == 'audio' and self.capture:
                        self.audio()
                    elif kind == 'osd':
                        client, _ = osd_server.accept()
                        client.setblocking(False)
                        self.osd_clients.append(client)
                    elif kind == 'control':
                        conn, _ = server.accept()
                        with conn:
                            conn.settimeout(0.1)
                            try:
                                action = conn.recv(64).decode().strip()
                                if action == 'status':
                                    result = {'state': 'recording' if self.capture else 'idle',
                                              'ready': self.workers['moonshine']['ready'],
                                              'workers': {e: {'pid': w['proc'].pid, 'ready': w['ready']}
                                                          for e, w in self.workers.items()}}
                                elif action == 'start':
                                    result = self.start()
                                elif action == 'stop':
                                    result = self.stop()
                                elif action == 'cancel':
                                    result = self.stop(cancel=True)
                                elif action == 'toggle':
                                    result = self.stop() if self.capture else self.start()
                                else:
                                    raise ValueError('Unknown action')
                                reply = {'ok': True, **result}
                            except Exception as exc:
                                logging.exception('Control command failed')
                                self.stop(cancel=True)
                                reply = {'ok': False, 'error': str(exc)}
                            try:
                                conn.sendall((json.dumps(reply) + '\n').encode())
                            except OSError:
                                pass
                if self.capture and time.monotonic() - self.recording_started > 120:
                    self.stop(cancel=True)
                    logging.warning('Cancelled at recording safety limit')
        except KeyboardInterrupt:
            pass
        finally:
            self.stop(cancel=True)
            if self.osd:
                self.osd.terminate()
            for worker in self.workers.values():
                worker['inbox'].put(('quit', self.session, None))
                worker['proc'].join(timeout=0.2)
                if worker['proc'].is_alive():
                    worker['proc'].terminate()
            for client in self.osd_clients:
                client.close()
            server.close()
            osd_server.close()
            path.unlink(missing_ok=True)
            osd_path.unlink(missing_ok=True)
            lock.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['daemon', 'status', 'start', 'stop', 'cancel', 'toggle'])
    parser.add_argument('--socket', type=Path, default=RUNTIME / 'control.sock')
    parser.add_argument('--model', type=Path, default=MODEL)
    parser.add_argument('--source')
    parser.add_argument('--output-file')
    parser.add_argument('--no-osd', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    if args.action == 'daemon':
        Daemon(args).serve()
    else:
        # Keep the hotkey client lightweight: no model imports or loading.
        from control_client import request
        print(json.dumps(request(args.action, args.socket)))


if __name__ == '__main__':
    main()
