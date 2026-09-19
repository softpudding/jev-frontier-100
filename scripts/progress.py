"""Cheap local progress snapshot without exposing model thinking or secrets."""
import collections,json,sys,os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
run=root/'runs'/(sys.argv[1] if len(sys.argv)>1 else 'v0.2-budget')
config=json.loads((run/'config.json').read_text())
process_file=run/'pipeline-process.json'
if process_file.exists():
 pid=json.loads(process_file.read_text())['pid']
 try:os.kill(pid,0);print('Evaluator process present:',pid)
 except ProcessLookupError:print('Evaluator process absent:',pid,'(saved status may be stale)')
if 'systems' in config:
 total=0
 for spec in config['systems']:
  path=run/spec['file'];counts=collections.Counter();last='—'
  if path.exists():
   with path.open() as f:
    for line in f:
     try:r=json.loads(line)
     except ValueError:continue
     counts[r['status']]+=1;last=r.get('timestamp_utc','—')
  n=sum(counts.values());total+=n;print(spec['key'],f'{n}/300',dict(counts),'last',last)
 print(f'TOTAL {total}/3000 (Jev reference reused)');raise SystemExit
