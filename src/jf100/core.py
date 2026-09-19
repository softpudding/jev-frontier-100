import hashlib
import json
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parents[2]
SEEDS=[101,202,303]

def load_items():
    raw=(ROOT/'data/items.jsonl').read_bytes()
    manifest=json.loads((ROOT/'data/manifest.json').read_text())
    if hashlib.sha256(raw).hexdigest()!=manifest['sha256']:
        raise ValueError('Dataset checksum differs from frozen manifest')
    return [json.loads(line) for line in raw.decode().splitlines()],manifest

def presented(item,trial):
    # Rotate all four option positions between trials without changing semantics.
    pairs=list(item['options'].items());shift=trial%4
    pairs=pairs[shift:]+pairs[:shift]
    options={label:text for label,(_,text) in zip('ABCD',pairs)}
    gold=next(label for label,(original,_) in zip('ABCD',pairs) if original==item['answer'])
    return {'state':item['state'],'question':item['question'],'options':options},gold

def parse_choice(content):
    try:
        value=json.loads(content)
    except (ValueError,TypeError):return None
    if not isinstance(value,dict) or set(value)!={'answer'}:return None
    answer=value['answer']
    return answer if isinstance(answer,str) and answer in 'ABCD' and len(answer)==1 else None

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
