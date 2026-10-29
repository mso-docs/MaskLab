"""TASK-013 / REQ-009/012/021/024: opt-in, ledgered live verification.
Each named phase has a stable idempotency key. Never prints secrets/provider error bodies.
"""
import argparse
import asyncio
from decimal import Decimal
import json
import os
from pathlib import Path
from masklab.api import sample_dataset
from masklab.contracts import ProtocolConfig, Role, canonical, digest
from masklab.store import Store
from masklab.worker import Worker
from masklab.runtime import load_env_file
from masklab.provider import NebiusProvider
from masklab.budget import configured_ledger
from masklab.analysis import analyze
from masklab.portable import export_run,import_archive
from masklab.contracts import render_protocol

async def verify(phase):
    load_env_file('.env')
    store=Store(Path(os.getenv('MASKLAB_DATA_DIR','artifacts/workspace'))/'masklab.sqlite3')
    provider=NebiusProvider();model=os.environ['NEBIUS_MODEL']
    key='verified-live:'+os.environ['MASKLAB_AUTHORIZATION_ID']+':'+phase
    prior=store.all('SELECT * FROM runs WHERE idempotency=?',(key,))
    if prior:
        run=store.run(prior[0]['id']);protocol=store.protocol(run['protocol_id'])['protocol']
    else:
        data=sample_dataset()
        settings=dict(provider='nebius',models=[model],input_price_per_million='0.06',output_price_per_million='0.24',budget_usd='0.01',concurrency=1,repetitions=1,roles=[Role(id='neutral',instruction='')],frames=['absent'],max_output_tokens=64)
        if phase=='smoke':
            data.questions=data.questions[:1];settings.update(purpose='access_smoke')
        elif phase=='reasoning-cap':
            data.questions=data.questions[:1];settings.update(enable_thinking=True)
        elif phase=='matrix':
            # A complete default 648-call matrix tests configured scope, not a benchmark claim.
            settings.update(roles=ProtocolConfig().roles,frames=['absent','correct','incorrect'],repetitions=3,concurrency=2,max_output_tokens=512,budget_usd='0.50')
        elif phase=='paired':
            data.questions=[q for q in data.questions if q.split=='development'][:6]
            settings.update(roles=ProtocolConfig().roles,frames=['absent','correct','incorrect'],repetitions=2,concurrency=2,max_output_tokens=128,budget_usd='0.05')
        else:raise ValueError('Unknown live phase')
        cfg=provider.bind_config(ProtocolConfig(**settings))
        protocol=render_protocol(data,cfg,digest(data.model_dump()))
        if Decimal(protocol['conservative_cost_usd'])>Decimal(cfg.budget_usd):
            raise ValueError('Conservative phase reservation exceeds its fixed verification sub-budget')
        ledger=configured_ledger().snapshot()
        if ledger['halted'] or Decimal(protocol['conservative_cost_usd'])>Decimal(ledger['remaining_usd']):
            raise ValueError('Insufficient reliably bounded cumulative budget')
        study=store.create_study('Live integration verification • '+phase)
        store.add_dataset(study['id'],data.model_dump(),canonical(data.model_dump()).encode())
        frozen=store.freeze(study['id'],protocol)
        run=store.create_run(frozen['id'],key)
    worker=Worker(store)
    try:
        for i in range(2000):
            status=store.run(run['id'])
            if status['state'] not in ('QUEUED','RUNNING','PAUSE_REQUESTED','CANCEL_REQUESTED'):break
            await worker.tick()
            if i%25==0:print(json.dumps({'phase':phase,'run_id':run['id'],'state':store.run(run['id'])['state'],'counts':store.run(run['id'])['counts']}),flush=True)
        else:raise ValueError('Verification did not settle within its bounded iterations')
    finally:worker.close()
    records=store.records(run['id']);analysis=analyze(protocol,records)
    archive=export_run(store,run['id']);import_archive(archive)
    folder=Path('artifacts/live-verification');(folder/(phase+'.zip')).write_bytes(archive)
    receipts=[]
    for r in records:
        for a in r['attempts']:
            body=a['body'];receipts.append({'attempt_id':a['id'],'request_id':r['id'],'ordinal':a['ordinal'],'state':a['state'],'started':a['started'],'ended':a['ended'],'provider_request_id':body.get('provider_request_id'),'model':body.get('raw_metadata',{}).get('model'),'usage':body.get('usage'),'cost_state':body.get('cost_state'),'estimated_cost_usd':body.get('cost_usd'),'reserve_usd':body.get('reserve_usd'),'finish_reason':body.get('raw_metadata',{}).get('finish_reason'),'serving_revision':body.get('serving_revision'),'service_tier':body.get('raw_metadata',{}).get('service_tier'),'error_code':body.get('error_code')})
    result={'phase':phase,'run_id':run['id'],'study_id':run['study_id'],'state':store.run(run['id'])['state'],'selected_model':model,'simulation':False,'request_count':protocol['request_count'],'protocol_hash':protocol['hash'],'archive_sha256':digest(archive),'conservative_reservation_usd':protocol['conservative_cost_usd'],'summary':analysis['summary'],'receipts':receipts,'cumulative_budget':configured_ledger().snapshot(),'evidence_scope':'Live software integration verification on synthetic tooling questions; not a validated model benchmark.'}
    rendered=canonical(result)
    if os.environ['NEBIUS_API_KEY'] in rendered or os.environ['NEBIUS_API_KEY'].encode() in archive:
        raise ValueError('Secret canary check blocked output')
    (folder/(phase+'.json')).write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ('summary','receipts')},indent=2))
    if result['state'] not in ('COMPLETED','COMPLETED_WITH_ERRORS') or result['cumulative_budget']['halted']:
        raise SystemExit('Live phase halted; preserve ledger and reconcile before further inference')
    if phase=='smoke':
        assert len(receipts)==1 and receipts[0]['state']=='SUCCEEDED' and receipts[0]['usage'] is not None
        assert receipts[0]['model']==model and receipts[0]['usage']['output_tokens']<=64
        assert analysis['summary']['counts']['correct']==1
        cap_path=Path(os.environ['MASKLAB_CAPABILITIES_FILE']);cap=json.loads(cap_path.read_text())
        cap['models'][model]['inference_verified']=True
        cap['models'][model]['smoke_protocol_hash']=protocol['hash']
        cap_path.write_text(json.dumps(cap,indent=2))
        print(json.dumps({'smoke':'PASS','usage':receipts[0]['usage'],'estimated_cost_usd':receipts[0]['estimated_cost_usd'],'model_verified':True}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['smoke','reasoning-cap','paired','matrix'])
    asyncio.run(verify(parser.parse_args().phase))
