"""TASK-007/013 / REQ-009/012/021/024: explicitly authorized live replication.
Idempotent, fixed original settings, shared ledger; never logs credentials/provider error bodies.
"""
import argparse,json,time,urllib.request
from pathlib import Path
from decimal import Decimal
from masklab.runtime import load_env_file
from masklab.budget import configured_ledger
from masklab.contracts import digest
from evaluate_live import evaluate

FOLDER=Path('artifacts/replication-v2/live');BASE='http://127.0.0.1:8001/api'
def api(path,data=None,method=None,headers=None):
 req=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),method=method,headers={'X-MaskLab-Request':'1','Content-Type':'application/json',**(headers or {})})
 with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)
def save(name,obj):(FOLDER/name).write_text(json.dumps(obj,indent=2))
def main():
 global FOLDER
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--repeat-approved-20261029',action='store_true',help='Explicit operator-authorized additional pass; same approved questions/settings, separate evidence and idempotency identity')
 args=parser.parse_args()
 if args.repeat_approved_20261029:FOLDER=Path('artifacts/replication-v2/repeat-20261029')
 FOLDER.mkdir(parents=True,exist_ok=True);load_env_file('.env')
 root=Path('data/replication-mixed-150-v2');manifest=json.loads((root/'manifest.json').read_text());plan=json.loads((root/'run-plan.json').read_text());stage=json.loads(Path('artifacts/replication-v2/mixed-staged-study.json').read_text());study=stage['study_id']
 assert manifest['status']=='OPERATOR_APPROVED' and all(q['operator_review']=='APPROVED' for q in manifest['questions'].values())
 assert digest(json.loads((root/'questions.json').read_text()))==manifest['dataset_hash']==stage['dataset_hash']
 cfg=plan['config'];prior=json.loads(Path('artifacts/mixed-study/frozen-choices.json').read_text())['config']
 assert {k:v for k,v in cfg.items() if k!='split'}=={k:v for k,v in prior.items() if k!='split'}
 assert cfg['provider']=='nebius' and cfg['split']=='evaluation'
 import os
 assert cfg['models']==[os.environ['NEBIUS_MODEL']]
 baseline_path=FOLDER/'budget-before.json'
 if not baseline_path.exists():save('budget-before.json',configured_ledger().snapshot())
 ledger=configured_ledger().snapshot();assert not ledger['halted']
 detail=api('/studies/'+study)
 for r in detail['runs']:
  if r['simulation'] and r['state'] in ['QUEUED','RUNNING']:api('/runs/'+r['id']+'/pause',{})
 for _ in range(60):
  detail=api('/studies/'+study)
  if not any(r['simulation'] and r['state'] in ['QUEUED','RUNNING','PAUSE_REQUESTED'] for r in detail['runs']):break
  time.sleep(1)
 else:raise RuntimeError('Simulation did not pause safely')
 api('/studies/'+study,{'name':'APPROVED • Broad replication — 150 fresh mixed questions'},method='PATCH')
 preview=api('/studies/'+study+'/preview',{'dataset_id':stage['dataset_id'],'config':cfg})
 assert preview['request_count']==4050 and preview['simulation'] is False
 assert Decimal(preview['conservative_cost_usd'])<=Decimal(cfg['budget_usd'])<=2
 assert Decimal(preview['conservative_cost_usd'])<=Decimal(ledger['remaining_usd'])
 save('preview.json',preview);save('frozen-choice-confirmation.json',{'status':'UNCHANGED_BEFORE_REPLICATION','dataset_hash':manifest['dataset_hash'],'config':cfg,'first_study_choices':'artifacts/mixed-study/frozen-choices.json','operator_approval':'Explicit new-row approval and request for Nebius run in chat; no new key/prompt/scorer changes'})
 existing_path=FOLDER/'run.json';known=json.loads(existing_path.read_text()) if existing_path.exists() else None
 frozen=next((p for p in detail['protocols'] if known and p['id']==known['protocol_id']),None)
 if frozen is None:frozen=next((p for p in detail['protocols'] if p['protocol']['hash']==preview['hash']),None)
 if frozen is None:frozen=api('/studies/'+study+'/freeze',{'dataset_id':stage['dataset_id'],'config':cfg,'expected_hash':preview['hash']})
 else:assert frozen['protocol']['hash']==preview['hash']
 identity='approved-broad-replication-150-nebius-v2'
 if args.repeat_approved_20261029:identity+='-repeat-20261029'
 run=api('/protocols/'+frozen['id']+'/runs',{},headers={'Idempotency-Key':identity});save('run.json',run)
 assert not run['simulation'];print(json.dumps({'run_id':run['id'],'study_id':study,'requests':4050,'conservative_reservation_usd':preview['conservative_cost_usd'],'simulation':False}),flush=True)
 for tick in range(7200):
  run=api('/runs/'+run['id'])
  if tick%10==0:print(json.dumps({'state':run['state'],'counts':run['counts']}),flush=True)
  if run['state'] not in ['QUEUED','RUNNING']:break
  time.sleep(3)
 else:raise RuntimeError('Monitoring timeout; inspect existing run before any resume')
 save('run.json',run);analysis=api('/runs/'+run['id']+'/analysis');save('analysis.json',analysis)
 with urllib.request.urlopen(BASE+'/runs/'+run['id']+'/export',timeout=90) as r:raw=r.read()
 # Exact-key canary blocks output/export publication; key is never printed.
 if os.environ['NEBIUS_API_KEY'].encode() in raw:raise RuntimeError('Private credential boundary failure; content withheld')
 (FOLDER/'original.zip').write_bytes(raw);independent=evaluate(FOLDER/'original.zip');independent['scope']=('Additional pass over the same approved replication questions; repeated measurements, not fresh-question or source-independent evidence.' if args.repeat_approved_20261029 else 'Fresh-question mixed convenience replication; shared templates and 22 source articles, not source-independent benchmark evidence.');save('independent.json',independent)
 final=configured_ledger().snapshot();save('budget-final.json',final)
 assert run['state']=='COMPLETED' and not final['halted'] and final['uncertain_attempts']==0
 print(json.dumps({'state':run['state'],'counts':analysis['summary']['counts'],'usage':{k:independent[k] for k in ['attempts','input_tokens','output_tokens','reasoning_tokens_subset','estimated_cost_usd']},'budget':final}),flush=True)
if __name__=='__main__':main()
