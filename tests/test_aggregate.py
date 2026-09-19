import unittest
from jf100.aggregate import bootstrap_pair_means,summarize
from jf100.core import load_items,presented

class AggregateTests(unittest.TestCase):
    def test_unstarted_model(self):
        items,_=load_items()
        s=summarize([],items,3,10)
        self.assertFalse(s['complete'])
        self.assertIsNone(s['accuracy'])
        self.assertEqual(s['expected_records'],300)
    def test_degenerate_bootstrap(self):
        self.assertEqual(bootstrap_pair_means({'x':1.,'y':1.},{'x':'d','y':'d'},100),[1.,1.])
        self.assertEqual(bootstrap_pair_means({'x':0.,'y':0.},{'x':'d','y':'d'},100),[0.,0.])
    def test_complete_and_incomplete(self):
        items,_=load_items();rows=[]
        for i in items:
            for t in range(3):
                _,g=presented(i,t)
                rows.append({'item_id':i['id'],'trial':t,'gold':g,'answer':g,'status':'ok','correct':True,'elapsed_ms':1})
        s=summarize(rows,items,3,100)
        self.assertEqual(s['accuracy'],1)
        self.assertEqual(s['pair_joint_accuracy'],1)
        self.assertEqual(s['semantic_consistency'],1)
        self.assertEqual(s['accuracy_95ci'],[1,1])
        self.assertIsNone(summarize(rows[:-1],items,3,100)['accuracy_95ci'])
    def test_duplicate_or_bad_grade_rejected(self):
        items,_=load_items();i=items[0];_,g=presented(i,0)
        r={'item_id':i['id'],'trial':0,'gold':g,'answer':g,'status':'ok','correct':True,'elapsed_ms':1}
        with self.assertRaises(ValueError):summarize([r,r],items,3,10)
        with self.assertRaises(ValueError):summarize([dict(r,correct=False)],items,3,10)
    def test_noncompletion_is_separate(self):
        items,_=load_items();i=items[0];_,g=presented(i,0)
        r={'item_id':i['id'],'trial':0,'gold':g,'answer':None,'status':'budget_exhausted','correct':False,'elapsed_ms':1}
        s=summarize([r],items,3,10)
        self.assertEqual(s['accuracy'],0)
        self.assertEqual(s['valid_completion_rate'],0)
        self.assertIsNone(s['accuracy_among_valid'])
