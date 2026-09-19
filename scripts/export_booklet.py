"""Readable complete item set and answer key for independent review."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
items=[json.loads(s) for s in (ROOT/'data/items.jsonl').read_text().splitlines()]
questions=['# JF100 question booklet','','Original v0.1 items. No answer key is included in this file.','']
answers=['# JF100 answer key and rationale','','Reviewer-facing only. Never send this document to a tested model.','']
for i in items:
 questions += [f'## {i["id"]} · {i["difficulty"]}','', '```text',i['state'] if isinstance(i['state'],str) else json.dumps(i['state'],ensure_ascii=False,indent=2),'```','',i['question'],'']
 questions += [f'- **{k}.** {v}' for k,v in i['options'].items()]
 questions.append('')
 answers += [f'## {i["id"]}','',f'**{i["answer"]}: {i["options"][i["answer"]]}**','',i['rationale'],'',f'Oracle: `{i["oracle"]}` · Pair: `{i["pair_id"]}`','']
(ROOT/'docs/QUESTIONS.md').write_text('\n'.join(questions))
(ROOT/'docs/ANSWERS.md').write_text('\n'.join(answers))
print('Exported 100 questions and 100 rationales.')
