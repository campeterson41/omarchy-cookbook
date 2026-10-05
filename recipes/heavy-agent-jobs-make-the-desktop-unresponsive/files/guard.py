#!/usr/bin/python3
"""Shared local resource telemetry, Codex hook, and serialized low-priority jobs."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import shlex
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path.home() / '.local/share/resource-guard'
RUNTIME = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')) / 'resource-guard'
STATE = RUNTIME / 'state.json'
CONFIG = Path.home() / '.config/resource-guard/config.json'
DEFAULTS = dict(cpu_busy=80, cpu_critical=95, sustained_seconds=15,
                memory_busy=80, memory_critical=95, minimum_memory_gib=1.5,
                disk_busy=85, disk_critical=95, minimum_disk_gib=2,
                sample_seconds=3)

def config():
    try: return DEFAULTS | json.loads(CONFIG.read_text())
    except (OSError, ValueError): return DEFAULTS

def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_name(path.name + '.' + str(os.getpid()) + '.tmp')
    temp.write_text(json.dumps(data))
    temp.replace(path)

def cpu_ticks():
    v = list(map(int, Path('/proc/stat').read_text().splitlines()[0].split()[1:]))
    return sum(v[:8]), v[3] + v[4]

def pressure(kind):
    try:
        line = Path('/proc/pressure/' + kind).read_text().splitlines()[0]
        return float(dict(x.split('=') for x in line.split()[1:])['avg10'])
    except (OSError, ValueError, KeyError): return 0

def gib(k): return f'{k / 1048576:.1f} GiB'

def measure(previous):
    now = cpu_ticks()
    delta = now[0] - previous[0]
    cpu = max(0, min(100, round(100 * (1 - (now[1]-previous[1])/delta)))) if delta else 0
    mem = {s.split(':')[0]: int(s.split()[1]) for s in Path('/proc/meminfo').read_text().splitlines()}
    used = mem['MemTotal'] - mem['MemAvailable']
    rows = [dict(label='CPU', value=cpu, detail=f'{os.cpu_count()} logical cores · load {os.getloadavg()[0]:.1f}'),
            dict(label='Memory', value=round(100*used/mem['MemTotal']), detail=f"{gib(used)} / {gib(mem['MemTotal'])} · {gib(mem['MemAvailable'])} available")]
    st=mem['SwapTotal']; su=st-mem['SwapFree']
    rows.append(dict(label='Swap', value=round(100*su/st) if st else 0, detail=f'{gib(su)} / {gib(st)}' if st else 'No swap configured'))
    paths=['/']
    if os.stat('/').st_dev != os.stat(Path.home()).st_dev: paths.append(str(Path.home()))
    disks=[]
    for p in paths:
        d=shutil.disk_usage(p); value=round(100*d.used/(d.used+d.free))
        disks.append(dict(path=p, value=value, free_gib=d.free/2**30))
        rows.append(dict(label='Disk · '+('system' if p=='/' else 'home'), value=value, detail=f'{gib(d.used/1024)} used · {gib(d.free/1024)} free'))
    output=subprocess.check_output(['ps','-eo','comm=,rss=','--sort=-rss'], text=True, timeout=2)
    apps=[dict(name=s.rsplit(None,1)[0], memory=gib(int(s.rsplit(None,1)[1]))) for s in output.splitlines()[:5]]
    return dict(rows=rows, apps=apps, cpu=cpu, memory=rows[1]['value'],
                available_memory_gib=mem['MemAvailable']/1048576,
                memory_pressure=pressure('memory'), cpu_pressure=pressure('cpu'), disks=disks), now

def raw_level(data, c):
    reasons=[]; level=0
    checks=[(data['cpu'],c['cpu_busy'],c['cpu_critical'],'CPU'),
            (data['memory'],c['memory_busy'],c['memory_critical'],'memory')]
    checks += [(d['value'],c['disk_busy'],c['disk_critical'],'disk '+d['path']) for d in data['disks']]
    for value,busy,critical,name in checks:
        severity=2 if value>=critical else 1 if value>=busy else 0
        if severity: reasons.append(f'{name} {value}%'); level=max(level,severity)
    if data['available_memory_gib'] < c['minimum_memory_gib']:
        level=2; reasons.append('less than 1.5 GiB memory available')
    if data['memory_pressure'] >= 10:
        level=2; reasons.append('memory stalls')
    for d in data['disks']:
        if d['free_gib'] < c['minimum_disk_gib']:
            level=2; reasons.append('disk space critically low')
    return level, reasons

class Debounce:
    def __init__(self): self.level=0; self.candidate=0; self.since=0
    def update(self, wanted, immediate, now, duration):
        if wanted != self.candidate: self.candidate=wanted; self.since=now
        if immediate and wanted==2: self.level=2
        elif now-self.since >= duration: self.level=wanted
        return self.level

def daemon():
    RUNTIME.mkdir(parents=True,exist_ok=True,mode=0o700)
    with open(RUNTIME/'collector.lock','a') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: return 0
        prev=cpu_ticks(); debouncer=Debounce()
        while True:
            c=config()
            try:
                data,prev=measure(prev)
                raw,reasons=raw_level(data,c)
                immediate=data['available_memory_gib']<c['minimum_memory_gib'] or data['memory_pressure']>=10 or any(d['free_gib']<c['minimum_disk_gib'] for d in data['disks'])
                gate=debouncer.update(raw,immediate,time.monotonic(),c['sustained_seconds'])
                data.update(timestamp=time.time(),level=raw,gate_level=gate,reasons=reasons,
                            policy=['normal','cautious','defer heavy jobs'][gate],pid=os.getpid(),active_job=active_job())
                atomic(STATE,data)
            except (OSError,ValueError,subprocess.SubprocessError) as e:
                print(f'collector: {e}',file=sys.stderr,flush=True)
            time.sleep(c['sample_seconds'])

def state():
    try:
        data=json.loads(STATE.read_text())
        if time.time()-data['timestamp']>12: raise ValueError('stale')
        return data
    except (OSError,ValueError,KeyError):
        return dict(level=1,gate_level=1,policy='cautious',reasons=['resource readings unavailable'],timestamp=0)

def summary(data):
    return f"Resource guard: {data['policy']}; " + ', '.join(data.get('reasons',[]) or ['room to spare'])

# Route common workloads by executable, not words inside echoed text or files.
# This is a cooperative workload classifier, not a security boundary.
def heavy_command(command, depth=0):
    if depth > 4: return False
    lines=command.splitlines(); clean=[]; delimiter=None
    for line in lines:
        if delimiter is not None:
            if line.strip()==delimiter: delimiter=None
            continue
        found=re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z_0-9]*)\1",line)
        if found: delimiter=found.group(2)
        clean.append(line)
    try:
        lexer=shlex.shlex('\n'.join(clean),posix=True,punctuation_chars=';&|()\n')
        lexer.whitespace=' \t\r'; lexer.whitespace_split=True
        tokens=list(lexer)
    except ValueError: return False
    segments=[]; current=[]
    for token in tokens:
        if token and all(c in ';&|()\n' for c in token):
            if current: segments.append(current); current=[]
        else: current.append(token)
    if current: segments.append(current)
    for args in segments:
        while args and re.match(r'^[A-Za-z_][A-Za-z_0-9]*=',args[0]): args=args[1:]
        if not args: continue
        name=Path(args[0]).name
        if name in ('ssh','remote-worker','resource-guard'): continue
        if name in ('bash','sh','zsh'):
            for i,arg in enumerate(args[1:],1):
                if arg.startswith('-') and 'c' in arg and i+1<len(args):
                    if heavy_command(args[i+1],depth+1): return True
            continue
        if name in ('env','nice','ionice','timeout','time','sudo'):
            # Wrappers' options precede the executable. Recursively find common
            # executables while leaving their remaining argv quoted intact.
            known={'npm','pnpm','yarn','bun','npx','pytest','playwright','vitest','jest','make','ninja','cargo','go','cmake','docker','podman','ffmpeg','tsc','python','python3','bash','sh','zsh'}
            for i,arg in enumerate(args[1:],1):
                if Path(arg).name in known and heavy_command(shlex.join(args[i:]),depth+1): return True
            continue
        if name in ('npm','pnpm','yarn','bun') and any(x in {'build','test','install','ci','playwright','vitest'} for x in args[1:]): return True
        if name=='npx' and any(x in {'playwright','vitest','jest','tsc'} for x in args[1:]): return True
        if name in ('pytest','playwright','vitest','jest','make','ninja','stress-ng','ffmpeg','tsc'): return True
        if name in ('python','python3') and '-m' in args and any(x in {'pytest','compileall'} for x in args[1:]): return True
        if name in ('cargo','go') and any(x in {'build','test','run'} for x in args[1:]): return True
        if name in ('docker','podman') and any(x in {'build','compose'} for x in args[1:]): return True
        if name=='cmake' and '--build' in args: return True
        if name in ('next','vite') and 'build' in args[1:]: return True
    return False

def hook(payload, data):
    event=payload.get('hook_event_name','PreToolUse')
    output={'hookEventName':event}
    text=summary(data)+'. Use ~/.local/bin/resource-guard run -- COMMAND for heavy local builds/tests/browser jobs; it serializes them and lowers scheduling priority. Under pressure prefer remote-worker after verifying its files, credentials and load. Read/edit work may continue; never retry a refused heavy command unguarded.'
    if event=='PreToolUse':
        command=payload.get('tool_input',{}).get('command','')
        if isinstance(command,list): command=' '.join(command)
        if not isinstance(command,str): command=''
        if not heavy_command(command): return {}
        output.update(permissionDecision='deny',permissionDecisionReason=text +
                      (' Heavy local work deferred until pressure falls.' if data['gate_level']==2
                       else ' Route this heavy command through resource-guard run so local sessions share one job slot.'))
    else: output['additionalContext']=text
    return {'hookSpecificOutput':output}

def scope_alive(info):
    unit=info.get('unit','')
    if not re.fullmatch(r'resource-job-[0-9a-f]{10}',unit): return False
    try:
        result=subprocess.run(['systemctl','--user','show','--property=ActiveState','--value',unit+'.scope'],capture_output=True,text=True,timeout=2)
        if result.returncode==0: return result.stdout.strip() in ('active','activating','deactivating')
        if result.returncode in (3,4): return False
        return True  # Cannot verify completion: keep the job slot reserved.
    except (OSError,subprocess.TimeoutExpired): return True

def active_job():
    path=RUNTIME/'active-job.json'
    try: info=json.loads(path.read_text())
    except (OSError,ValueError): return False
    try:
        os.kill(int(info.get('pid',0)),0)
        if int(info.get('pid',0))>0: return True
    except (ProcessLookupError,ValueError): pass
    except PermissionError: return True
    if scope_alive(info): return True
    try: path.unlink()
    except FileNotFoundError: pass
    return False

def run_job(command, wait):
    if not command: raise ValueError('Provide a command after --')
    RUNTIME.mkdir(parents=True,exist_ok=True,mode=0o700)
    deadline=time.monotonic()+wait
    with open(RUNTIME/'heavy-job.lock','a') as lock:
        warned=False
        while True:
            acquired=False
            try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB); acquired=True
            except BlockingIOError: pass
            data=state()
            if acquired and data['gate_level']<2 and not active_job(): break
            if acquired: fcntl.flock(lock,fcntl.LOCK_UN)
            if time.monotonic()>=deadline:
                print('Resource guard: heavy job deferred; '+summary(data)+'. Offload or retry later.',file=sys.stderr)
                return 75
            if not warned:
                print('Resource guard: waiting for headroom / another guarded job.',file=sys.stderr); warned=True
            time.sleep(1)
        unit='resource-job-'+uuid.uuid4().hex[:10]
        info=dict(unit=unit,pid=os.getpid(),started_at=time.time(),policy=data['policy'])
        atomic(RUNTIME/'active-job.json',info)
        env=os.environ.copy()
        env.update(CMAKE_BUILD_PARALLEL_LEVEL='2',CARGO_BUILD_JOBS='2',MAKEFLAGS='-j2',OMP_NUM_THREADS='2')
        # MemoryHigh reclaims/throttles rather than killing work; no MemoryMax.
        launch=['systemd-run','--user','--scope','--quiet', '--unit='+unit,
                '-p','CPUWeight=20','-p','IOWeight=20','-p','MemoryHigh=40%',
                '/usr/bin/nice','-n','10','/usr/bin/ionice','-c','2','-n','7',*command]
        try:
            p=subprocess.Popen(launch,env=env)
            def forward(sig,frame):
                result=subprocess.run(['systemctl','--user','kill','--kill-whom=all','--signal='+str(sig),unit+'.scope'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                if result.returncode:
                    print('Resource guard: scope signal failed; forwarding to job launcher.',file=sys.stderr)
                    p.send_signal(sig)
            old={sig:signal.signal(sig,forward) for sig in (signal.SIGINT,signal.SIGTERM)}
            try: return p.wait()
            finally:
                for sig,handler in old.items(): signal.signal(sig,handler)
        finally:
            if not scope_alive(info):
                try: (RUNTIME/'active-job.json').unlink()
                except FileNotFoundError: pass

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='action',required=True)
    sub.add_parser('daemon')
    s=sub.add_parser('status'); s.add_argument('--json',action='store_true')
    sub.add_parser('hook')
    r=sub.add_parser('run'); r.add_argument('--wait',type=float,default=120); r.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args()
    if a.action=='daemon': return daemon()
    if a.action=='status':
        data=state(); print(json.dumps(data) if a.json else summary(data)); return 0
    if a.action=='hook':
        try: payload=json.load(sys.stdin)
        except (ValueError,OSError): return 0
        print(json.dumps(hook(payload,state()))); return 0
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    return run_job(command,max(0,a.wait))
if __name__=='__main__': sys.exit(main())
