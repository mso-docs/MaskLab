"""TASK-004 • TEST-010–012/021: real persistence and controlled provider failures."""
import asyncio
from decimal import Decimal
import json
import os
import subprocess
import sys
import pytest
from masklab.worker import Worker
from masklab.provider import ProviderError, SimulatedProvider
from masklab.contracts import ProtocolConfig, render_protocol, digest
from masklab.store import Store

async def drain(worker,store,id):
    for _ in range(200):
        await worker.tick()
        if store.run(id)['state'] in ('COMPLETED','COMPLETED_WITH_ERRORS','CANCELLED','PAUSED','BLOCKED'):
            return store.run(id)
    raise AssertionError('Job did not settle')

@pytest.mark.parametrize('scenario,final,attempts',[('success','SUCCEEDED',1),('invalid','SUCCEEDED',1),('refusal','SUCCEEDED',1),('transient','SUCCEEDED',2),('timeout','UNCERTAIN',1),('unknown_usage','SUCCEEDED',1)])
async def test_controlled_provider_outcomes(make_run,store,scenario,final,attempts):
    r,p=make_run(scenario)
    worker=Worker(store)
    try:
        result=await drain(worker,store,r['id'])
        records=store.records(r['id'])
        assert {x['state'] for x in records}=={final}
        assert {len(x['attempts']) for x in records}=={attempts}
        if scenario=='timeout':assert result['state']=='COMPLETED_WITH_ERRORS'
        else:assert result['state']=='COMPLETED'
        assert all(a['body']['simulation'] for x in records for a in x['attempts'])
    finally:worker.close()

async def test_pause_cancel_and_resume(make_run,store):
    r,p=make_run(questions=5)
    w=Worker(store)
    try:
        await w.tick()
        attempted=sum(bool(x['attempts']) for x in store.records(r['id']))
        store.control(r['id'],'pause');await w.tick()
        assert store.run(r['id'])['state']=='PAUSED'
        assert sum(bool(x['attempts']) for x in store.records(r['id']))==attempted
        store.control(r['id'],'resume');await w.tick()
        assert sum(bool(x['attempts']) for x in store.records(r['id']))>attempted
        store.control(r['id'],'cancel');await w.tick()
        assert store.run(r['id'])['state']=='CANCELLED'
        assert store.run(r['id'])['counts']['PENDING']>0
    finally:w.close()

async def test_single_writer_and_actual_process_crash(make_run,store):
    r,p=make_run(questions=1)
    # A real child obtains the OS lock, commits an IN_FLIGHT intent, then dies before response persistence.
    code="""import os,sys
from masklab.store import Store
from masklab.worker import Worker
s=Store(sys.argv[1]);w=Worker(s);w.acquire();r=s.run(sys.argv[2]);w.claim(r,s.protocol(r['protocol_id'])['protocol']);os._exit(73)
"""
    result=subprocess.run([sys.executable,'-c',code,store.path,r['id']],env={**os.environ,'PYTHONPATH':'src'},capture_output=True)
    assert result.returncode==73,result.stderr.decode()
    w=Worker(Store(store.path));w.acquire()
    other=Worker(Store(store.path))
    with pytest.raises(RuntimeError,match='Another'):other.acquire()
    try:
        records=store.records(r['id'])
        uncertain=[x for x in records if x['state']=='UNCERTAIN']
        assert len(uncertain)==1 and uncertain[0]['attempts'][0]['body']['error_code']=='WORKER_INTERRUPTED'
        await drain(w,store,r['id'])
        record=next(x for x in store.records(r['id']) if x['id']==uncertain[0]['id'])
        assert len(record['attempts'])==1 and record['state']=='UNCERTAIN'
    finally:w.close()

async def test_unknown_cost_preserves_reservation(make_run,store):
    r,p=make_run('unknown_usage',input_price_per_million='1',output_price_per_million='1',budget_usd='1')
    w=Worker(store)
    try:
        result=await drain(w,store,r['id'])
        assert Decimal(result['reserved'])==Decimal(p['conservative_cost_usd'])>0
        assert result['spent']=='0'
        assert all(x['attempts'][0]['body']['cost_state']=='UNCERTAIN_COST' for x in store.records(r['id']))
    finally:w.close()

async def test_live_reservations_global_cap_and_no_authorization(store,dataset,monkeypatch):
    data=dataset.model_copy(deep=True);data.questions=data.questions[:1]
    cfg=ProtocolConfig(provider='nebius',models=['nvidia/nemotron-test'],repetitions=1,concurrency=1,input_price_per_million='1',output_price_per_million='1',budget_usd='1')
    p=render_protocol(data,cfg,digest(b'x'));s=store.create_study('Live adapter fixture')
    frozen=store.freeze(s['id'],p);r=store.create_run(frozen['id'],'live-test-1')
    class Controlled:
        def preflight(self,cfg):return {}
        async def complete(self,*args):raise ProviderError('TIMEOUT',uncertain=True)
    monkeypatch.setattr('masklab.worker.provider_for',lambda cfg:Controlled())
    w=Worker(store)
    try:
        monkeypatch.setenv('MASKLAB_APPROVED_SPEND_USD','0')
        await w.tick()
        assert store.run(r['id'])['state']=='BLOCKED' and not any(x['attempts'] for x in store.records(r['id']))
        monkeypatch.setenv('MASKLAB_APPROVED_SPEND_USD',p['requests'][0]['reserve_usd'])
        store.control(r['id'],'resume')
        await w.tick();await w.tick()
        row=store.run(r['id'])
        assert row['state']=='BLOCKED' and row['blocked_reason']=='UNCERTAIN_COST'
        assert sum(bool(x['attempts']) for x in store.records(r['id']))==1
        assert Decimal(row['reserved'])==Decimal(p['requests'][0]['reserve_usd'])
    finally:w.close()

async def test_idempotent_start_and_final_attempt_immutable(make_run,store):
    r,p=make_run()
    assert store.create_run(r['protocol_id'],'test-key-'+r['protocol_id'])['id']==r['id']
    w=Worker(store)
    try:
        await w.tick();record=next(x for x in store.records(r['id']) if x['attempts'])
        import sqlite3
        with pytest.raises(sqlite3.IntegrityError),store.tx() as db:
            db.execute("UPDATE attempts SET state='FAILED' WHERE id=?",(record['attempts'][0]['id'],))
    finally:w.close()

async def test_committed_responses_survive_subsequent_process_death(make_run,store):
    r,p=make_run(questions=1)
    code="""import asyncio,os,sys
from masklab.store import Store
from masklab.worker import Worker
s=Store(sys.argv[1]);w=Worker(s);asyncio.run(w.tick());os._exit(74)
"""
    result=subprocess.run([sys.executable,'-c',code,store.path],env={**os.environ,'PYTHONPATH':'src'},capture_output=True)
    assert result.returncode==74,result.stderr.decode()
    committed=[x for x in store.records(r['id']) if x['state']=='SUCCEEDED']
    assert len(committed)==2
    before={x['id']:json.dumps(x['attempts'],sort_keys=True) for x in committed}
    w=Worker(Store(store.path))
    try:
        await drain(w,store,r['id'])
        for row in store.records(r['id']):
            if row['id'] in before:assert json.dumps(row['attempts'],sort_keys=True)==before[row['id']]
    finally:w.close()

async def test_draft_never_dispatches_until_explicit_queue(make_run,store):
    original,p=make_run(questions=1)
    # Cancel the helper's queued run, then create a separate durable draft.
    store.control(original['id'],'cancel')
    draft=store.create_run(original['protocol_id'],'draft-fixture-key',draft=True)
    w=Worker(store)
    try:
        await w.tick()
        assert store.run(draft['id'])['state']=='DRAFT'
        assert all(not r['attempts'] for r in store.records(draft['id']))
        store.control(draft['id'],'queue')
        result=await drain(w,store,draft['id'])
        assert result['state']=='COMPLETED'
    finally:w.close()
