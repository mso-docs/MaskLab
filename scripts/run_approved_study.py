"""TASK-007/013: operator-approved development then frozen held-out evaluation.
Uses the existing owner worker and shared spending guard; never prints credentials.
"""
import hashlib,json,time,urllib.request
from pathlib import Path
from decimal import Decimal

BASE='http://127.0.0.1:8001/api'
FOLDER=Path('artifacts/mixed-study');FOLDER.mkdir(parents=True,exist_ok=True)
def api(path,data=None,method=None,headers=None):
 req=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),method=method,headers={'X-MaskLab-Request':'1','Content-Type':'application/json',**(headers or {})})
 with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)
def save(name,obj): (FOLDER/name).write_text(json.dumps(obj,indent=2))

stage=json.loads(Path('artifacts/charts/staged-study.json').read_text());study=stage['study_id']
plan=json.loads(Path('data/study-draft-150/run-plan.json').read_text())
approval=json.loads(Path('data/study-draft-150/manifest.json').read_text())
assert approval['status']=='OPERATOR_APPROVED' and approval['dataset_hash']==stage['dataset_hash']
assert all(q['operator_review']=='APPROVED' for q in approval['questions'].values())
# Choices explicitly remain unchanged following development; negative findings are retained.
for split,expected in [('development',1620),('evaluation',2430)]:
 if split=='evaluation':
  decision={'status':'FROZEN_BEFORE_EVALUATION','development_run':dev['id'],'dataset_hash':stage['dataset_hash'],'choices':'No changes to question keys, prompts, roles, frames, scoring, temperature, output cap, repetitions or analysis. Preserve all negative findings.','config':plan['config'],'development_review':json.loads((FOLDER/'development-review.json').read_text())}
  save('frozen-choices.json',decision)
 cfg={**plan['config'],'split':split}
 preview=api('/studies/'+study+'/preview',{'dataset_id':stage['dataset_id'],'config':cfg})
 assert preview['request_count']==expected
 assert Decimal(preview['conservative_cost_usd'])<=Decimal('2')
 save(split+'-preview.json',preview)
 existing=api('/studies/'+study)['protocols']
 prior_path=FOLDER/(split+'-run.json')
 prior=json.loads(prior_path.read_text()) if prior_path.exists() else None
 frozen=next((p for p in existing if prior and p['id']==prior['protocol_id']),None)
 if frozen is None:
  frozen=next((p for p in existing if p['protocol']['hash']==preview['hash']),None)
 if frozen is not None:assert frozen['protocol']['hash']==preview['hash']
 if frozen is None:frozen=api('/studies/'+study+'/freeze',{'dataset_id':stage['dataset_id'],'config':cfg,'expected_hash':preview['hash']})
 identity='approved-mixed-150-'+split+'-v1'
 run=api('/protocols/'+frozen['id']+'/runs',{},headers={'Idempotency-Key':identity})
 save(split+'-run.json',run)
 print(json.dumps({'split':split,'run':run['id'],'requests':expected,'reservation':preview['conservative_cost_usd']}),flush=True)
 for tick in range(7200):
  run=api('/runs/'+run['id'])
  if tick%10==0:print(json.dumps({'split':split,'state':run['state'],'counts':run['counts']}),flush=True)
  if run['state'] not in ['QUEUED','RUNNING']:break
  time.sleep(3)
 else:raise RuntimeError('Bounded monitoring timeout; inspect existing run before resuming')
 save(split+'-run.json',run)
 analysis=api('/runs/'+run['id']+'/analysis');save(split+'-analysis.json',analysis)
 with urllib.request.urlopen(BASE+'/runs/'+run['id']+'/export',timeout=60) as response:archive=response.read()
 (FOLDER/(split+'.zip')).write_bytes(archive)
 assert run['state']=='COMPLETED', 'Run not cleanly completed; evaluation remains gated'
 counts=analysis['summary']['counts']
 assert counts['finalized']==expected and counts['failed']==0 and counts['uncertain']==0, 'Technical failures or missing outcomes require review before proceeding'
 if split=='development' and counts['invalid']:
  reviewed=json.loads((FOLDER/'development-review.json').read_text())
  assert reviewed['status']=='DEVELOPMENT_REVIEW_COMPLETE_CHOICES_FROZEN' and reviewed['development_run']==run['id'] and reviewed['invalid']==counts['invalid'], 'Invalid outcomes need explicit development review'
 from evaluate_live import evaluate
 independent=evaluate(FOLDER/(split+'.zip'))
 independent['scope']='Mixed public-source and generated convenience sample; integrity/scoring/billing checks, not benchmark validation or invoice reconciliation.'
 save(split+'-independent.json',independent)
 if split=='development':dev=run
 print(json.dumps({'split':split,'completed':True,'counts':counts}),flush=True)
