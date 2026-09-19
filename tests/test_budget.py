import unittest
from jf100.budget_runner import payload_for,classify
from jf100.confidence import answer_token_score
from jf100.core import load_items
class BudgetTests(unittest.TestCase):
 def test_budget_and_output_headroom(self):
  item=load_items()[0][0]
  for b in [0,512,2048]:
   p,g=payload_for(item,1,b)
   self.assertEqual(p['max_tokens'],b+128)
   self.assertEqual(p['reasoning_budget_tokens'],b)
   self.assertEqual(p['chat_template_kwargs']['enable_thinking'],b>0)
   self.assertTrue(p['logprobs']);self.assertEqual(p['top_logprobs'],5)
   self.assertNotIn(item['rationale'],str(p))
 def test_normal_answer_after_cap_is_valid(self):
  r={'http_status':200,'body':{'choices':[{'finish_reason':'stop','message':{'content':'{"answer":"A"}','reasoning_content':'some thinking'}}]}}
  self.assertEqual(classify(r,'A')[:3],('A','ok',True))
  r['body']['choices'][0]['finish_reason']='length'
  self.assertEqual(classify(r,'A')[:3],('A','generation_limit',False))
 def test_lp_alignment_uses_final_answer_not_reasoning(self):
  chunks=['Earlier answer A. </think>','{"answer":"','C','"}']
  body={'choices':[{'message':{'content':'{"answer":"C"}'},'logprobs':{'content':[{'token':s,'bytes':list(s.encode()),'logprob':-.2} for s in chunks]}}]}
  score=answer_token_score(body)
  self.assertEqual(score['answer_token_index'],2)
  self.assertEqual(score['answer_token_logprob'],-.2)
  self.assertEqual(score['alignment'],'exact_single_label_token')
 def test_lp_missing_or_merged_is_not_invented(self):
  self.assertIsNone(answer_token_score({})['answer_token_probability'])
  s='{"answer":"C"}'
  body={'choices':[{'message':{'content':s},'logprobs':{'content':[{'token':s,'bytes':list(s.encode()),'logprob':-.2}]}}]}
  self.assertIsNone(answer_token_score(body)['answer_token_probability'])
