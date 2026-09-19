"""Extract an explicitly labelled, uncalibrated answer-token probability."""
import math,re

def answer_token_score(body):
 choice=body.get('choices',[{}])[0];content=choice.get('message',{}).get('content')
 entries=(choice.get('logprobs') or {}).get('content') or []
 result={'lp_token_count':len(entries),'answer_token_probability':None,'answer_token_logprob':None,'answer_token_index':None,'alignment':'unavailable'}
 if not isinstance(content,str) or not entries:return result
 chunks=[]
 for e in entries:
  raw=e.get('bytes');chunks.append(bytes(raw) if raw is not None else e.get('token','').encode())
 full=b''.join(chunks);final=content.strip().encode();offset=full.rfind(final)
 match=re.search(rb'"answer"\s*:\s*"([ABCD])"',final)
 if offset<0 or not match:return result
 start=offset+match.start(1);end=offset+match.end(1);position=0
 for index,(entry,chunk) in enumerate(zip(entries,chunks)):
  if position==start and position+len(chunk)==end:
   lp=entry.get('logprob')
   if isinstance(lp,(int,float)) and math.isfinite(lp):
    result.update(answer_token_probability=math.exp(min(0,lp)),answer_token_logprob=lp,answer_token_index=index,alignment='exact_single_label_token')
   return result
  position+=len(chunk)
 result['alignment']='label_not_an_exact_single_token'
 return result
