"""TASK-013 / TEST-003/022/024: explicit LOCAL live-demo verification, never deployment.
Uses the same additional-spend ledger as owner workspaces. Startup seeds at most one idempotent
8-request measured example; subsequent browser execution remains quota-limited.
"""
import asyncio
import json
import os
from pathlib import Path
import uvicorn
from masklab.api import create_app,sample_dataset
from masklab.runtime import load_env_file
from masklab.provider import NebiusProvider
from masklab.contracts import ProtocolConfig,Role,render_protocol,digest,canonical
from masklab.worker import Worker
from masklab.budget import configured_ledger

load_env_file('.env')
app=create_app('artifacts/live-demo-workspace',mode='demo');store=app.state.store
key='curated-live-demo:'+os.environ['MASKLAB_AUTHORIZATION_ID']
previous=store.all('SELECT * FROM runs WHERE idempotency=?',(key,))
if previous:
    run=store.run(previous[0]['id'])
else:
    provider=NebiusProvider();cap=provider.capabilities();model=os.environ['NEBIUS_MODEL'];prices=cap['models'][model]
    cfg=provider.bind_config(ProtocolConfig(provider='nebius',models=[model],roles=[Role(id='neutral',instruction=''),Role(id='expert',instruction='You are a careful expert. Answer accurately.')],frames=['absent','incorrect'],repetitions=1,concurrency=1,max_output_tokens=64,budget_usd='0.01',input_price_per_million=prices['input_price_per_million'],output_price_per_million=prices['output_price_per_million']))
    data=sample_dataset();data.questions=data.questions[:2]
    protocol=render_protocol(data,cfg,digest(data.model_dump()));assert protocol['request_count']==8
    study=store.create_study('Curated live tooling verification',public=True)
    store.add_dataset(study['id'],data.model_dump(),canonical(data.model_dump()).encode())
    frozen=store.freeze(study['id'],protocol);run=store.create_run(frozen['id'],key)

async def seed():
    worker=Worker(store)
    try:
        for _ in range(20):
            r=store.run(run['id'])
            if r['state'] not in ('QUEUED','RUNNING'):break
            await worker.tick()
        assert store.run(run['id'])['state']=='COMPLETED','Curated live seed did not complete; no fallback'
    finally:worker.close()
asyncio.run(seed())
Path('artifacts/live-verification/demo-seed.zip').write_bytes(__import__('masklab.portable',fromlist=['export_run']).export_run(store,run['id']))
print(json.dumps({'local_demo':'ready','saved_live_run':run['id'],'request_ceiling':8,'budget':configured_ledger().snapshot()}),flush=True)
uvicorn.run(app,host='127.0.0.1',port=8767,access_log=False)
