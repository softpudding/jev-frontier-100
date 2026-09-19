"""Native llama-server factorial reasoning-budget experiment."""
import argparse,concurrent.futures,datetime,hashlib,json,os,random,shutil,signal,subprocess,threading,time
from pathlib import Path
from .core import ROOT,SEEDS,load_items,presented,parse_choice,digest
from .runner import SYSTEM,request,jev_payload,model_slug
from .confidence import answer_token_score
MODELS=['qwen3.5:0.8b','qwen3.5:2b-q8_0','qwen3.5:4b-q8_0']
BUDGETS=[0,512,2048]
BINARY=os.environ.get('JF100_LLAMA_SERVER') or shutil.which('llama-server') or '/Applications/Ollama.app/Contents/Resources/llama-server'
HOST=os.environ.get('JF100_LLAMA_HOST','127.0.0.1')
PORT=int(os.environ.get('JF100_LLAMA_PORT','11438'))
URL=f'http://{HOST}:{PORT}'
OLLAMA=os.environ.get('JF100_OLLAMA_URL','http://127.0.0.1:11434')
SCHEMA={'type':'object','properties':{'answer':{'type':'string','enum':list('ABCD')}},'required':['answer'],'additionalProperties':False}
def system_key(model,budget):return model+' / '+('off' if budget==0 else str(budget))
def file_name(model,budget):return model_slug(model)+'-'+str(budget)+'.jsonl'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic_json(path,value):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)
def payload_for(item,trial,budget):
 visible,gold=presented(item,trial)
 return {'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps(visible,ensure_ascii=False)}],
 'stream':False,'logprobs':True,'top_logprobs':5,'temperature':1,'top_k':20,'top_p':.95,'min_p':0,'presence_penalty':1.5,'frequency_penalty':0,'repeat_penalty':1,'repeat_last_n':64,'typical_p':1,'seed':SEEDS[trial],
 'chat_template_kwargs':{'enable_thinking':budget>0},'reasoning_budget_tokens':budget,'max_tokens':budget+128,
 'response_format':{'type':'json_schema','json_schema':{'name':'answer','strict':True,'schema':SCHEMA}}},gold

def classify(result,gold):
 body=result['body'];choice=body.get('choices',[{}])[0] if isinstance(body,dict) else {};message=choice.get('message',{})
 answer=parse_choice(message.get('content'));reason=choice.get('finish_reason')
 status='ok'
 if result['http_status']!=200:status='service_error'
 elif reason=='length':status='generation_limit'
 elif answer is None:status='invalid_output'
 return answer,status,bool(status=='ok' and answer==gold),message,reason

def run(run_id):
 items,manifest=load_items();folder=ROOT/'runs'/run_id;folder.mkdir(parents=True,exist_ok=True)
 systems=[{'key':'jev','model':'jev','budget':None,'file':'jev.jsonl'}]+[{'key':system_key(m,b),'model':m,'budget':b,'file':file_name(m,b)} for m in MODELS for b in BUDGETS]
 config={'version':'0.2','dataset':manifest,'trials':3,'seeds':SEEDS,'systems':systems,'workers':16,'context':32768,'protocol_sha256':digest((ROOT/'docs/PROTOCOL.md').read_text()),'binary_sha256':hashlib.sha256(Path(BINARY).read_bytes()).hexdigest(),'jev_model':'jev-1.13.0'}
 cp=folder/'config.json'
 if cp.exists() and json.loads(cp.read_text())!=config:raise RuntimeError('Frozen configuration differs')
 if not cp.exists():atomic_json(cp,config)
 atomic_json(folder/'pipeline-process.json',{'pid':os.getpid(),'launcher':'detached budget runner'})
 def state(s,**kwargs):atomic_json(folder/'pipeline-status.json',{'state':s,'timestamp_utc':now(),**kwargs})
 stop=threading.Event();active=[None]
 def terminate(*_):
  stop.set()
  if active[0] is not None:active[0].terminate()
  raise KeyboardInterrupt()
 signal.signal(signal.SIGTERM,terminate)
 state('running')
 try:
  target=folder/'jev.jsonl';byid={x['id']:x for x in items}
  reference=[json.loads(x) for x in target.read_text().splitlines()] if target.exists() else []
  completed=set()
  for row in reference:
   p,g=jev_payload(byid[row['item_id']],row['trial'])
   if row['request_sha256']!=digest(p) or row['gold']!=g:raise RuntimeError('Jev reference mismatch')
   completed.add((row['item_id'],row['trial']))
  if len(completed)!=len(reference):raise RuntimeError('Duplicate Jev checkpoint')
  for t in range(3):
   order=list(items);random.Random(SEEDS[t]).shuffle(order)
   for item in order:
    if (item['id'],t) in completed:continue
    key=os.environ.get('JEV_KEY')
    if not key:raise RuntimeError('Set JEV_KEY for a fresh Jev reference, or provide verified existing jev.jsonl')
    p,g=jev_payload(item,t);attempts=[]
    for attempt in range(2):
     result=request('https://api.typesafe.ai/v1/systemone',p,key=key,timeout=45);attempts.append(result)
     if result['http_status'] not in [0,429,500,502,503,504,529]:break
     if attempt==0:time.sleep(2)
    if result['http_status'] in [401,402,403]:raise RuntimeError('Jev authentication or billing failed')
    answer_data=result['body'].get('answers',{}).get('answer',{});answer=answer_data.get('choice')
    status='service_error' if result['http_status']!=200 else ('ok' if answer in list('ABCD') else 'invalid_output')
    row={'model':'jev','item_id':item['id'],'pair_id':item['pair_id'],'domain':item['domain'],'difficulty':item['difficulty'],'trial':t,'seed':None,'request':p,'request_sha256':digest(p),'gold':g,'answer':answer,'confidence':answer_data.get('confidence'),'correct':status=='ok' and answer==g,'status':status,'elapsed_ms':result['elapsed_ms'],'timestamp_utc':now(),'attempts':attempts}
    with target.open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    print('jev',t+1,item['id'],status,flush=True)
  for model in MODELS:
   done=set()
   for b in BUDGETS:
    path=folder/file_name(model,b)
    if path.exists():
     for line in path.read_text().splitlines():
      r=json.loads(line);key=(r['item_id'],r['trial'],b)
      if key in done:raise RuntimeError('Duplicate checkpoint')
      done.add(key)
   tasks=[(item,t,b) for b in BUDGETS for t in range(3) for item in items if (item['id'],t,b) not in done]
   if not tasks:continue
   random.Random(92026).shuffle(tasks)
   meta=request(OLLAMA+'/api/show',{'model':model})
   if meta['http_status']!=200:raise RuntimeError('Model metadata unavailable')
   show=meta['body']
   if show['details']['quantization_level']!='Q8_0':raise RuntimeError('Requires Q8_0')
   blob=Path(next(l[5:] for l in show['modelfile'].splitlines() if l.startswith('FROM ')).strip('"'))
   hasher=hashlib.sha256()
   with blob.open('rb') as bf:
    for chunk in iter(lambda:bf.read(8*1024*1024),b''):hasher.update(chunk)
   fingerprint=hasher.hexdigest()
   mp=folder/(model_slug(model)+'-metadata.json')
   metadata={'model':model,'blob_sha256':fingerprint,'details':show['details'],'parameters':show.get('parameters'),'template':show.get('template'),'binary_sha256':config['binary_sha256']}
   if mp.exists() and json.loads(mp.read_text())!=metadata:raise RuntimeError('Runtime/model changed')
   atomic_json(mp,metadata)
   # Refuse to attach to an unrelated service.
   if request(URL+'/health',timeout=1)['http_status']!=0:raise RuntimeError('Probe port already occupied')
   cmd=[BINARY,'--model',str(blob),'--host',HOST,'--port',str(PORT),'--offline','--no-webui','--jinja','--reasoning-format','deepseek','--reasoning-budget','512','-c','524288','-np','16','-ngl','all','--flash-attn','on']
   with (folder/(model_slug(model)+'-server.log')).open('ab') as log:proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
   active[0]=proc
   atomic_json(folder/'server-process.json',{'pid':proc.pid,'model':model,'command':cmd})
   lock=threading.Lock();count=[len(done)];abort=stop
   try:
    for _ in range(240):
     if proc.poll() is not None:raise RuntimeError('Backend exited during startup')
     if request(URL+'/health',timeout=1)['http_status']==200:break
     time.sleep(.5)
    else:raise RuntimeError('Backend startup timeout')
    props=request(URL+'/props')['body'];atomic_json(folder/(model_slug(model)+'-server-properties.json'),props)
    def score(task):
     if abort.is_set():return
     item,t,b=task;p,g=payload_for(item,t,b);attempts=[]
     for attempt in range(2):
      result=request(URL+'/v1/chat/completions',p,timeout=600);attempts.append(result)
      if result['http_status'] not in [0,429,500,502,503,504]:break
      if attempt==0:time.sleep(2)
     answer,status,correct,message,finish=classify(result,g)
     reasoning=message.get('reasoning_content') or '';reasoning_n=0;tokenization_ok=True
     if reasoning:
      tok=request(URL+'/tokenize',{'content':reasoning,'add_special':False})
      tokenization_ok=tok['http_status']==200;reasoning_n=len(tok['body'].get('tokens',[])) if tokenization_ok else None
     row={'model':model,'system':system_key(model,b),'budget':b,'item_id':item['id'],'pair_id':item['pair_id'],'domain':item['domain'],'difficulty':item['difficulty'],'trial':t,'seed':SEEDS[t],
          'request':p,'request_sha256':digest(p),'gold':g,'answer':answer,'correct':correct,'status':status,'elapsed_ms':result['elapsed_ms'],'timestamp_utc':now(),'attempts':attempts,
          'logprobs_present':bool(result['body'].get('choices',[{}])[0].get('logprobs')),'reasoning_tokens_retokenized':reasoning_n,'tokenization_ok':tokenization_ok,'thinking_present':bool(reasoning),'finish_reason':finish,'usage':result['body'].get('usage',{}),'workers':16}
     row.update(answer_token_score(result['body']))
     if result['http_status']==200 and not row['logprobs_present']:
      abort.set();(folder/f'lp-failure-{item["id"]}-{t}-{b}.json').write_text(json.dumps(row,ensure_ascii=False));raise RuntimeError('Successful response missing required logprobs; raw response saved')
     with lock:
      with (folder/file_name(model,b)).open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush()
      count[0]+=1;state('running',model=model,model_completed=count[0],model_expected=900)
      print(f'{model} budget={b} {count[0]}/900 trial={t+1} {item["id"]} {status} correct={int(correct)} thinking_tokens={reasoning_n} {result["elapsed_ms"]}ms',flush=True)
     if result['http_status']==0 and proc.poll() is not None:raise RuntimeError('Backend crashed')
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
     futures=[pool.submit(score,task) for task in tasks]
     for f in concurrent.futures.as_completed(futures):f.result()
   finally:
    proc.terminate()
    try:proc.wait(timeout=15)
    except subprocess.TimeoutExpired:proc.kill();proc.wait()
    active[0]=None
   from .budget_report import report
   report(run_id)
  state('auditing')
  from .budget_report import report
  report(run_id,require_complete=True)
  state('rendering')
  subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/plot_budget_results.py'),run_id],check=True)
  state('complete');print('COMPLETE',run_id,flush=True)
 except KeyboardInterrupt:state('stopped');raise
 except BaseException as e:state('failed',error_type=type(e).__name__);raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('run_id',nargs='?',default='v0.2-budget');run(p.parse_args().run_id)
