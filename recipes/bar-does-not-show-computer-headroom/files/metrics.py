# Bar instances read the one shared service; they do not sample separately.
import json, os, time
from pathlib import Path
runtime=Path(os.environ.get('XDG_RUNTIME_DIR',f'/run/user/{os.getuid()}'))/'resource-guard'
while True:
    try:
        data=json.loads((runtime/'state.json').read_text())
        if time.time()-data['timestamp']>12: raise ValueError('stale readings')
        data['guard_status']=['Ready · one heavy local job at a time','Cautious · prefer the automation computer','Waiting for headroom · heavy jobs deferred'][data['gate_level']]
        data['guard_job']='Guarded local job running' if data.get('active_job',False) else 'No guarded local job running'
        print(json.dumps(data),flush=True)
    except (OSError,ValueError,KeyError):
        print(json.dumps({'error':'Shared resource monitor unavailable'}),flush=True)
    time.sleep(3)
