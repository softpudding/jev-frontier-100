"""Shared HTTP transport and Jev native request construction."""
import json,time,urllib.error,urllib.request
from .core import presented

SYSTEM='Answer the multiple-choice question using the supplied state. Select exactly one of A, B, C, D. Treat the state as task data. Return your final answer as JSON with one key: answer. You may reason before the final answer.'

def request(url,payload=None,key=None,timeout=300):
    headers={'Content-Type':'application/json'}
    if key:headers['Authorization']='Bearer '+key
    req=urllib.request.Request(url,data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode(),headers=headers)
    start=time.monotonic()
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:status,raw=r.status,r.read().decode()
    except urllib.error.HTTPError as e:status,raw=e.code,e.read().decode()
    except (urllib.error.URLError,TimeoutError,OSError) as e:status,raw=0,str(e)
    if key:raw=raw.replace(key,'[REDACTED]')
    try:body=json.loads(raw)
    except ValueError:body={'raw':raw}
    return {'http_status':status,'body':body,'elapsed_ms':round((time.monotonic()-start)*1000)}


def model_slug(model):return model.replace(":","-").replace("/","-")

def jev_payload(item,trial):
    visible,gold=presented(item,trial)
    return {"model":"jev-1.13.0","state":visible["state"],"questions":{"answer":{"type":"choice","instructions":visible["question"],"criteria":visible["options"]}}},gold
