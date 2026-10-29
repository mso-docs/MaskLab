"""TASK-007 / REQ-004/005: stage a local draft only; never freeze or infer."""
import json,urllib.request
from pathlib import Path
ROOT=Path('data/replication-mixed-150-v2');BASE='http://127.0.0.1:8001/api'
def call(path,data=None,raw=None,method=None):
 req=urllib.request.Request(BASE+path,data=raw if raw is not None else None if data is None else json.dumps(data).encode(),method=method,headers={'X-MaskLab-Request':'1','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
if __name__=='__main__':
 m=json.loads((ROOT/'manifest.json').read_text());assert m['status']=='DRAFT_OPERATOR_REVIEW_REQUIRED'
 name='DRAFT • Broad replication — 150 fresh mixed questions';studies=call('/studies');study=next((s for s in studies if s['name']==name),None)
 if study is None:study=call('/studies',{'name':name})
 detail=call('/studies/'+study['id']);assert not detail['runs'] and not detail['protocols']
 version=next((d for d in detail['datasets'] if d['hash']==m['dataset_hash']),None)
 if version is None:version=call('/studies/'+study['id']+'/datasets?kind=json',raw=(ROOT/'questions.json').read_bytes())
 prior=Path('artifacts/replication-v2/staged-study.json')
 if prior.exists():
  focused=json.loads(prior.read_text());call('/studies/'+focused['study_id'],{'archived':True},method='PATCH')
 result={'status':'DRAFT_STAGED_FOR_OPERATOR_REVIEW','study_id':study['id'],'dataset_id':version['id'],'dataset_hash':m['dataset_hash'],'url':BASE.removesuffix('/api')+'/#view=design&study='+study['id']+'&run=','protocols_created':0,'runs_created':0,'provider_calls':0}
 Path('artifacts/replication-v2/mixed-staged-study.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
