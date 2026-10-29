"""TASK-013 / REQ-024: independent final split and ledger report; no paid calls or secret output."""
import json,hashlib,zipfile
from pathlib import Path
from decimal import Decimal
folder=Path('artifacts/mixed-study')
sets={};protocols={};totals={'input_tokens':0,'output_tokens':0,'reasoning_tokens_subset':0,'attempts':0};cost=Decimal(0)
for split,n in [('development',60),('evaluation',90)]:
 with zipfile.ZipFile(folder/(split+'.zip')) as z:
  p=json.loads(z.read('protocol.json'));rows=json.loads(z.read('records.json'))
  protocols[split]=p
  questions={q['id']:q for q in p['dataset']['questions']}
  sets[split]={r['body']['key'][1] for r in rows}
  assert len(sets[split])==n and len(rows)==n*27
  assert all(questions[q]['split']==split for q in sets[split])
  assert p['config']['split']==split and not p['simulation']
  assert all(len(r['attempts'])==1 for r in rows)
 result=json.loads((folder/(split+'-independent.json')).read_text())
 assert result['status']=='PASS'
 for key in totals:totals[key]+=result[key]
 cost+=Decimal(result['estimated_cost_usd'])
assert not sets['development'] & sets['evaluation']
assert protocols['development']['dataset_hash']==protocols['evaluation']['dataset_hash']
assert protocols['development']['system_template']==protocols['evaluation']['system_template']
assert {k:v for k,v in protocols['development']['config'].items() if k!='split'}=={k:v for k,v in protocols['evaluation']['config'].items() if k!='split'}
assert json.loads((folder/'frozen-choices.json').read_text())['status']=='FROZEN_BEFORE_EVALUATION'
assert totals['attempts']==4050
ledger=json.loads((folder/'budget-final.json').read_text())
assert ledger['attempts']==669+4050
assert Decimal(ledger['estimated_spent_usd'])==Decimal('0.00455352')+cost
assert ledger['held_usd']=='0' and ledger['halted'] is None and ledger['uncertain_attempts']==0
result={'status':'PASS','development_questions':60,'held_out_questions':90,'disjoint_actual_request_ids':True,'single_attempt_per_request':True,**totals,'additional_estimated_cost_usd':str(cost),'cumulative_estimated_cost_usd':ledger['estimated_spent_usd'],'remaining_usd':ledger['remaining_usd'],'simulation':False,'limitations':'Convenience sample with shared generated templates and unknown public benchmark exposure; not population-wide evidence or invoice reconciliation.'}
(folder/'split-ledger-independent.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
