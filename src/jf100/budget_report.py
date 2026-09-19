"""Audit, compact export and paired-template statistics for budget conditions."""
import argparse,collections,json,math,statistics
from .core import ROOT,load_items,digest
from .runner import jev_payload
from .aggregate import summarize,bootstrap_pair_means
from .budget_runner import payload_for

def report(run_id,require_complete=False,public_only=False):
 run=ROOT/'runs'/run_id;out=ROOT/'results'/run_id
 config=json.loads((out/'run_config.json' if public_only else run/'config.json').read_text());items,manifest=load_items();byid={i['id']:i for i in items}
 saved=[json.loads(x) for x in (out/'outcomes.jsonl').read_text().splitlines()] if public_only else []
 if config['dataset']['sha256']!=manifest['sha256'] or config['protocol_sha256']!=digest((ROOT/'docs/PROTOCOL.md').read_text()):raise ValueError('Frozen data/protocol mismatch')
 systems={};public=[];calibration={}

 for spec in config['systems']:
  rows=[];path=run/spec['file']
  def source_rows():
   if public_only:
    yield from (x for x in saved if x['system']==spec['key'])
   elif path.exists():
    with path.open() as f:
     for line in f:
      if not line.endswith('\n'):break
      yield json.loads(line)
  for r in source_rows():
   p,g=jev_payload(byid[r['item_id']],r['trial']) if spec['model']=='jev' else payload_for(byid[r['item_id']],r['trial'],spec['budget'])
   if digest(p)!=r['request_sha256'] or r['gold']!=g:raise ValueError('Request hash or gold audit failed')
   if not public_only and r['request']!=p:raise ValueError('Stored request differs')
   if spec['model']!='jev' and not r['logprobs_present']:raise ValueError('Missing required LP flag')
   compact={k:r.get(k) for k in ['item_id','trial','gold','answer','correct','status','elapsed_ms','domain','difficulty','pair_id','request_sha256','reasoning_tokens_retokenized','thinking_present','logprobs_present','lp_token_count','answer_token_probability','answer_token_logprob','answer_token_index','alignment','confidence','usage','finish_reason']}
   compact.update(system=spec['key'],model=spec['model'],budget=spec['budget']);rows.append(compact);public.append(compact)
  s=summarize(rows,items,3)
  s['reasoning_tokens_mean']=statistics.mean(r['reasoning_tokens_retokenized'] for r in rows if r['reasoning_tokens_retokenized'] is not None) if any(r['reasoning_tokens_retokenized'] is not None for r in rows) else None
  s['generated_tokens_mean']=statistics.mean(r['usage'].get('completion_tokens',0) for r in rows if r['usage']) if any(r['usage'] for r in rows) else None
  systems[spec['key']]=s
  eligible=[]
  for r in rows:
   score=r['confidence'] if spec['model']=='jev' else r['answer_token_probability']
   if r['status']=='ok' and isinstance(score,(int,float)) and math.isfinite(score) and 0<=score<=1:eligible.append((score,int(r['correct'])))
  bins=[]
  for i in range(10):
   xs=[(p,y) for p,y in eligible if min(int(p*10),9)==i]
   if xs:bins.append({'bin':i,'n':len(xs),'mean_confidence':statistics.mean(p for p,y in xs),'accuracy':statistics.mean(y for p,y in xs)})
  calibration[spec['key']]={'score_type':'Jev returned confidence' if spec['model']=='jev' else 'uncalibrated probability of exact emitted answer-letter token, not four-choice normalized','eligible_valid_answers':len(eligible),'brier_as_correctness_proxy':statistics.mean((p-y)**2 for p,y in eligible) if eligible else None,'reliability_bins':bins}
 complete=all(s['complete'] for s in systems.values())
 if require_complete and not complete:raise ValueError('Incomplete experiment')
 differences={}
 pairs=[(k,'jev') for k in systems if k!='jev']
 for model in sorted({x['model'] for x in config['systems'] if x['model']!='jev'}):
  pairs.extend((model+' / '+b,model+' / off') for b in ['512','2048'])
 for a,b in pairs:
  sa,sb=systems[a],systems[b]
  if not(sa['complete'] and sb['complete']):continue
  ds={p:sa['pair_values'][p]-sb['pair_values'][p] for p in sa['pair_values']}
  differences[a+' minus '+b]={'difference':statistics.mean(ds.values()),'95ci':bootstrap_pair_means(ds,sa['pair_domains'])}
 summary={'complete':complete,'config':config,'audit_source':'public compact outcomes' if public_only else 'local full records','systems':{k:{f:v for f,v in s.items() if f not in ['pair_values','pair_domains']} for k,s in systems.items()},'paired_differences':differences,'confidence_analysis':calibration,'raw_record_location':'runs/'+run_id,'raw_retention':'Exact request objects; full response including thinking, final answer, token IDs/bytes/logprobs and top-5 alternatives. Jev inputs reconstructed and hash-verified.'}
 out=ROOT/'results'/run_id;out.mkdir(exist_ok=True,parents=True)
 (out/'run_config.json').write_text(json.dumps(config,indent=2)+'\n')
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'outcomes.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in public))
 lines=['# JF100 v0.2 budget experiment','',('Complete.' if complete else 'INCOMPLETE: do not compare partial scores as final rankings.'),'','| Condition | Completed | Accuracy | Valid completion | Median seconds | Mean generated tokens |','|---|---:|---:|---:|---:|---:|']
 for k,s in systems.items():
  fmt=lambda x:f'{x:.1f}' if x is not None else '—'
  lines.append(f'| {k} | {s["records"]}/300 | {fmt(s["accuracy"]*100 if s["accuracy"] is not None else None)}% | {fmt(s["valid_completion_rate"]*100 if s["valid_completion_rate"] is not None else None)}% | {fmt(s["latency_median_ms"]/1000 if s["latency_median_ms"] is not None else None)} | {fmt(s["generated_tokens_mean"])} |')
 lines+=['','Full inputs/outputs and logprobs remain in the local raw run directory. Compact public data excludes raw thinking. Jev is a reused, dated reference. Timing is descriptive under shared-GPU batching. Confidence scores have different semantics; see docs/PROTOCOL.md and summary.json.','']
 (out/'REPORT.md').write_text('\n'.join(lines));print('Report refreshed:',sum(s['records'] for s in systems.values()),'/3000',flush=True)
 return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('run_id',nargs='?',default='v0.2-budget');p.add_argument('--from-public',action='store_true');a=p.parse_args();report(a.run_id,public_only=a.from_public)
