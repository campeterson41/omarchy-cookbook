import json
import socket
from pathlib import Path
import os
SOCKET = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "f9-streaming/control.sock"

def request(action, path=SOCKET):
    with socket.socket(socket.AF_UNIX) as client:
        client.settimeout(4)
        client.connect(str(path))
        client.sendall((action + '\n').encode())
        chunks = bytearray()
        while b'\n' not in chunks:
            part = client.recv(4096)
            if not part:
                raise RuntimeError('dictation daemon disconnected')
            chunks.extend(part)
        reply = json.loads(chunks.split(b'\n', 1)[0])
        if not reply.get('ok'):
            raise RuntimeError(reply.get('error', 'dictation command failed'))
        return reply
