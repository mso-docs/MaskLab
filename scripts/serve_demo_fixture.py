"""TASK-012 / REQ-003/022/024: browser-only simulated demo fixture, not a release dataset."""
import asyncio
from pathlib import Path
import tempfile
import uvicorn
from masklab.api import create_app,sample_dataset
from masklab.contracts import ProtocolConfig,render_protocol,digest
from masklab.worker import Worker

folder=Path(tempfile.mkdtemp(prefix='demo-e2e-',dir='artifacts'))
app=create_app(folder,mode='demo');store=app.state.store
store.create_study('PRIVATE CANARY')
s=store.create_study('Curated simulated example',public=True)
data=sample_dataset();data.questions=data.questions[:1]
p=store.freeze(s['id'],render_protocol(data,ProtocolConfig(roles=[{'id':'neutral','instruction':''}],repetitions=1),digest(b'demo-fixture')))
r=store.create_run(p['id'],'saved-simulated-fixture')
async def seed():
    w=Worker(store)
    try:
        while store.run(r['id'])['state'] not in ('COMPLETED','COMPLETED_WITH_ERRORS'):await w.tick()
    finally:w.close()
asyncio.run(seed())
uvicorn.run(app,host='127.0.0.1',port=8766,access_log=False)
