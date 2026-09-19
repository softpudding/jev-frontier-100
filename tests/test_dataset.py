import collections
import datetime as dt
import json
from pathlib import Path
import unittest
from jf100.core import ROOT,load_items,presented,parse_choice
from jf100.runner import jev_payload
from jf100.budget_runner import payload_for

class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.items,cls.manifest=load_items()
    def test_design(self):
        xs=self.items
        self.assertEqual(len(xs),100)
        self.assertEqual(len({i['id'] for i in xs}),100)
        self.assertEqual(set(collections.Counter(i['domain'] for i in xs).values()),{10})
        self.assertEqual(set(collections.Counter(i['pair_id'] for i in xs).values()),{2})
        self.assertEqual(collections.Counter(i['difficulty'] for i in xs),{'easy':30,'medium':40,'hard':30})
        self.assertEqual(collections.Counter(i['answer'] for i in xs),dict.fromkeys('ABCD',25))
    def test_options_and_pairs(self):
        pairs=collections.defaultdict(list)
        for i in self.items:
            self.assertEqual(set(i['options']),set('ABCD'))
            self.assertEqual(len(set(i['options'].values())),4)
            self.assertIn(i['answer'],i['options'])
            self.assertTrue(i['rationale'])
            pairs[i['pair_id']].append(i)
        for name,(a,b) in pairs.items():
            self.assertNotEqual(a['options'][a['answer']],b['options'][b['answer']],name)
    def test_independent_gold_anchors(self):
        # Hand-derived anchors, independent of generator's numeric computations.
        expected={
            'mathematics-01a':'139','mathematics-01b':'167',
            'mathematics-02a':'66','mathematics-02b':'99',
            'mathematics-03a':'3/10','mathematics-03b':'2/5',
            'mathematics-05a':'8/17','mathematics-05b':'2/3',
            'temporal-01a':'A','temporal-01b':'B',
            'temporal-02a':'2028-03-02','temporal-02b':'2028-03-01',
            'temporal-04a':'2028-05-04','temporal-04b':'2028-05-05',
            'temporal-05a':'11','temporal-05b':'12',
            'algorithms-02a':'5','algorithms-02b':'7',
            'algorithms-03a':'12','algorithms-03b':'14',
            'algorithms-05a':'7','algorithms-05b':'8',
            'formal_logic-05a':'inconsistent_premises','formal_logic-05b':'undetermined',
        }
        byid={i['id']:i for i in self.items}
        for id,answer in expected.items():self.assertEqual(byid[id]['options'][byid[id]['answer']],answer,id)
    def test_graph_oracle_independently(self):
        for i in self.items:
            if i['domain']!='relations':continue
            state=i['state'];edges=dict(line.split(' -> ') for line in state['links']);node=state['start']
            for _ in range(state['steps']):node=edges[node]
            self.assertEqual(i['options'][i['answer']],node,i['id'])
    def test_code_oracle(self):
        # Execute only bundled, original code; no model-generated code is executed.
        for i in self.items:
            if i['domain']!='code_semantics':continue
            env={};exec(i['state']['code'],env)
            self.assertEqual(i['options'][i['answer']],repr(env['result']),i['id'])
    def test_label_rotation_and_no_leak(self):
        for i in self.items:
            for trial in range(3):
                visible,gold=presented(i,trial)
                self.assertEqual(visible['options'][gold],i['options'][i['answer']])
                self.assertEqual(set(visible),{'state','question','options'})
                for model in ['jev','qwen3.5:0.8b']:
                    p,g=jev_payload(i,trial) if model=='jev' else payload_for(i,trial,2048)
                    self.assertEqual(g,gold)
                    self.assertNotIn(i['rationale'],json.dumps(p,ensure_ascii=False))
    def test_strict_parser(self):
        self.assertEqual(parse_choice('{"answer":"C"}'),'C')
        for s in ['C','{"answer":"AB"}','{"answer":""}','{"answer":1}','{"answer":"B","explanation":"x"}','{}']:
            self.assertIsNone(parse_choice(s))

if __name__=='__main__':unittest.main()
