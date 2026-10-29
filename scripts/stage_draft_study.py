"""TASK-007 / REQ-001/004/005: stage the approved preparation for local owner inspection.
Creates a DRAFT-labeled study/dataset only. Never freezes a protocol, queues a run or loads keys.
"""
import argparse,json
from pathlib import Path
from masklab.contracts import load_dataset,digest
from masklab.store import Store

parser=argparse.ArgumentParser();parser.add_argument('--folder',default='data/study-draft-150');parser.add_argument('--workspace',default='artifacts/workspace')
args=parser.parse_args();folder=Path(args.folder);manifest=json.loads((folder/'manifest.json').read_text());assert manifest['status']=='DRAFT_OPERATOR_REVIEW_REQUIRED'
raw=(folder/'questions.json').read_bytes();dataset=load_dataset(raw,'json');assert digest(dataset.model_dump())==manifest['dataset_hash']
path=Path(args.workspace)/'masklab.sqlite3'
if not path.exists():raise ValueError('Existing owner workspace required; select --workspace explicitly')
store=Store(path);name=f'DRAFT • {len(dataset.questions)}-question mixed study — review keys before running'
existing=store.all('SELECT * FROM studies WHERE name=? AND archived=0',(name,))
study=existing[0] if existing else store.create_study(name)
versions=store.all('SELECT * FROM datasets WHERE study_id=? AND hash=?',(study['id'],manifest['dataset_hash']))
version=versions[0] if versions else store.add_dataset(study['id'],dataset.model_dump(),raw)
assert not store.all('SELECT * FROM runs WHERE study_id=?',(study['id'],))
result={'status':'DRAFT_STAGED_FOR_REVIEW','study_id':study['id'],'dataset_id':version['id'],'dataset_hash':manifest['dataset_hash'],'name':name,'questions':len(dataset.questions),'protocols_created':0,'runs_queued':0,'provider_calls':0,'url':f'http://127.0.0.1:8001/#view=design&study={study["id"]}&run='}
Path('artifacts/charts/staged-study.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
