"""Export only the ten published conditions as a compressed release asset."""
import gzip,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];run=root/'runs/v0.2-budget'
config=json.loads((run/'config.json').read_text());out=root/'artifacts';out.mkdir(exist_ok=True)
target=out/'full-records.jsonl.gz';counts={};redacted_paths=0
with gzip.open(target,'wt',encoding='utf-8',compresslevel=6) as dst:
 for spec in config['systems']:
  count=0
  with (run/spec['file']).open() as src:
   for line in src:
    r=json.loads(line);encoded=json.dumps(r['request'],sort_keys=True,ensure_ascii=False).encode()
    if hashlib.sha256(encoded).hexdigest()!=r['request_sha256']:raise ValueError('Input hash mismatch')
    
    for attempt in r.get('attempts',[]):
     body=attempt.get('body',{});model=body.get('model')
     if isinstance(model,str) and model.startswith('/'):
      body['model']=Path(model).name;redacted_paths+=1
    r['published_condition']=spec['key'];dst.write(json.dumps(r,ensure_ascii=False)+'\n');count+=1
  if count!=300:raise ValueError('Incomplete condition')
  counts[spec['key']]=count
if len(counts)!=10 or sum(counts.values())!=3000:raise ValueError('Release scope mismatch')
h=hashlib.sha256()
with target.open('rb') as f:
 for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
(out/'manifest.json').write_text(json.dumps({'file':target.name,'bytes':target.stat().st_size,'sha256':h.hexdigest(),'records':3000,'conditions':counts,'export_transformations':{'response_model_local_path_replaced_with_blob_filename':redacted_paths},'unchanged':'All request bodies, thinking, final answers, token IDs/logprobs and scores. Original full responses remain local.'},indent=2)+'\n')
print(target)
