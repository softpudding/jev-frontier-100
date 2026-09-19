import collections,json,unittest
from jf100.core import ROOT,digest,load_items,presented
from jf100.runner import jev_payload
from jf100.budget_runner import payload_for
class ReleaseTests(unittest.TestCase):
 def test_all_published_conditions_are_complete_and_hash_verified(self):
  folder=ROOT/'results/v0.2-budget';config=json.loads((folder/'run_config.json').read_text())
  rows=[json.loads(x) for x in (folder/'outcomes.jsonl').read_text().splitlines()]
  byid={x['id']:x for x in load_items()[0]};counts=collections.Counter();seen=set()
  self.assertEqual(len(config['systems']),10);self.assertEqual(len(rows),3000)
  for r in rows:
   key=(r['system'],r['item_id'],r['trial']);self.assertNotIn(key,seen);seen.add(key);counts[r['system']]+=1
   item=byid[r['item_id']]
   p,g=jev_payload(item,r['trial']) if r['model']=='jev' else payload_for(item,r['trial'],r['budget'])
   self.assertEqual(r['request_sha256'],digest(p));self.assertEqual(r['gold'],g)
   self.assertEqual(r['correct'],r['status']=='ok' and r['answer']==g)
  self.assertEqual(set(counts),{x['key'] for x in config['systems']})
  self.assertEqual(set(counts.values()),{300})
 def test_published_summary_matches_outcomes(self):
  folder=ROOT/'results/v0.2-budget';s=json.loads((folder/'summary.json').read_text())
  rows=[json.loads(x) for x in (folder/'outcomes.jsonl').read_text().splitlines()]
  self.assertTrue(s['complete'])
  for key,v in s['systems'].items():
   subset=[r for r in rows if r['system']==key]
   self.assertEqual(sum(r['correct'] for r in subset),v['correct'])
   self.assertEqual(len(subset),v['records'])
   self.assertEqual(v['accuracy'],sum(r['correct'] for r in subset)/len(subset))
