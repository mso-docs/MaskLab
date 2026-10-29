"""TASK-010/011/012 • TEST-003/018–023 API, portability and permission boundaries."""
import asyncio
import io
import json
import stat
import zipfile
import pytest
from fastapi.testclient import TestClient
from masklab.api import create_app
from masklab.contracts import canonical, digest, ProtocolConfig, render_protocol
from masklab.portable import export_run, import_archive, safe_cell
from masklab.worker import Worker
from masklab.provider import NebiusProvider

H={'X-MaskLab-Request':'1'}

async def completed(make_run,store):
    r,p=make_run(questions=1)
    w=Worker(store)
    try:
        for _ in range(10):await w.tick()
    finally:w.close()
    return r,p

async def test_archive_roundtrip_reanalysis_no_execution(make_run,store):
    r,p=await completed(make_run,store)
    archive=export_run(store,r['id']);e=import_archive(archive)
    assert e['inspection_only'] is True and e['protocol']==p
    assert e['manifest']['simulation'] is True
    assert e['analysis']['evidence_label'].startswith('SIMULATED')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for name,meta in e['manifest']['files'].items():
            assert digest(z.read(name))==meta['sha256']
        report=z.read('report.md').decode();assert 'NOT NEMOTRON EVIDENCE' in report
        assert 'Authorization' not in b''.join(z.read(x) for x in z.namelist()).decode()
        assert store.path not in b''.join(z.read(x) for x in z.namelist()).decode()

@pytest.mark.parametrize('name,mode',[('../escape',0o100644),('/absolute',0o100644),('a\\b',0o100644),('symlink',stat.S_IFLNK|0o777),('script.py',0o100755)])
def test_unsafe_archive_entries(name,mode):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        info=zipfile.ZipInfo(name);info.external_attr=mode<<16;z.writestr(info,b'x')
    with pytest.raises(ValueError,match='Unsafe'):import_archive(out.getvalue())

async def test_hash_schema_and_score_tampering(make_run,store):
    r,p=await completed(make_run,store);archive=export_run(store,r['id'])
    with zipfile.ZipFile(io.BytesIO(archive)) as z:files={x:z.read(x) for x in z.namelist()}
    files['analysis.json']=b'{}'
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        for name,data in files.items():z.writestr(name,data)
    with pytest.raises(ValueError,match='hash'):import_archive(out.getvalue())
    manifest=json.loads(files['manifest.json']);manifest['files']['analysis.json']={'sha256':digest(b'{}'),'size':2};files['manifest.json']=canonical(manifest).encode()
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        for name,data in files.items():z.writestr(name,data)
    with pytest.raises(ValueError,match='Scored'):import_archive(out.getvalue())


def test_duplicate_and_zip_bomb():
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        z.writestr('x',b'a');z.writestr('x',b'b')
    with pytest.raises(ValueError):import_archive(out.getvalue())
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('bomb',b'0'*(2*1024*1024))
    with pytest.raises(ValueError,match='expansion'):import_archive(out.getvalue())
    for v in ['=cmd','+SUM(A1)','-2','@script',' \t=cmd']:assert safe_cell(v).startswith("'")


def test_api_owner_import_validation_archiving_and_restore(tmp_path):
    app=create_app(tmp_path,embedded_worker=False)
    with TestClient(app) as client:
        assert client.get('/api/health').json()['schema_version']==1
        assert client.post('/api/studies',json={'name':'x'}).status_code==403
        assert client.post('/api/studies',json={'name':'x'},headers={**H,'Origin':'https://evil.test'}).status_code==403
        s=client.post('/api/studies',json={'name':'<script>alert(1)</script>'},headers=H).json()
        assert s['name']=='<script>alert(1)</script>' # inert React text, never interpreted
        id=s['id'];base='/api/studies/'+id
        assert client.post(base+'/datasets?kind=json',content=b'{bad',headers=H).status_code==422
        assert not client.get(base).json()['datasets']
        d=client.post(base+'/sample',headers=H).json()
        payload={'dataset_id':d['id'],'config':ProtocolConfig(repetitions=1).model_dump()}
        p=client.post(base+'/freeze',json=payload,headers=H).json()
        r=client.post('/api/protocols/'+p['id']+'/runs',headers={**H,'Idempotency-Key':'test-key-1'}).json()
        again=client.post('/api/protocols/'+p['id']+'/runs',headers={**H,'Idempotency-Key':'test-key-1'}).json()
        assert r['id']==again['id']
        client.patch(base,json={'name':'Renamed','archived':True},headers=H)
        assert client.get(base).json()['name']=='Renamed'
        assert client.post(base+'/freeze',json=payload,headers=H).status_code==422
        raw=client.get('/api/runs/'+r['id']+'/export').content
        imported=client.post('/api/imports',content=raw,headers=H).json()
        evidence=client.get('/api/imports/'+imported['id']).json()
        assert evidence['inspection_only'] and len(app.state.store.all('SELECT * FROM runs'))==1
        derived=client.post('/api/imports/'+imported['id']+'/reanalyze',headers=H).json()
        assert derived['id']!=imported['id'] and derived['parent_import_id']==imported['id']
        assert client.get('/api/imports/'+imported['id']).json()==evidence
    restored=create_app(tmp_path,embedded_worker=False)
    assert restored.state.store.run(r['id'])['state']=='QUEUED'


def test_hosted_owner_requires_auth_and_credentials_never_returned(tmp_path,monkeypatch):
    monkeypatch.setenv('NEBIUS_API_KEY','secret-canary-do-not-export')
    app=create_app(tmp_path,embedded_worker=False)
    with TestClient(app) as c:
        assert c.get('/api/studies',headers={'Host':'attacker.test'}).status_code==403
        assert 'secret-canary' not in c.get('/api/config').text
    monkeypatch.setenv('MASKLAB_OWNER_TOKEN','owner-canary')
    with TestClient(create_app(tmp_path,embedded_worker=False)) as c:
        assert c.get('/api/studies').status_code==401
        assert c.get('/api/studies',headers={'Authorization':'Bearer owner-canary'}).status_code==200


def test_demo_private_boundaries_quota_and_spoofed_headers(tmp_path):
    app=create_app(tmp_path,mode='demo',embedded_worker=False);store=app.state.store
    private=store.create_study('Private')
    public=store.create_study('Curated',public=True)
    from masklab.api import sample_dataset
    data=sample_dataset();data.questions=data.questions[:1]
    protocol=render_protocol(data,ProtocolConfig(roles=[{'id':'neutral','instruction':''}],repetitions=1),digest(b'x'))
    p=store.freeze(public['id'],protocol)
    with TestClient(app) as c:
        assert len(c.get('/api/studies').json())==1
        assert c.get('/api/studies/'+private['id']).status_code==404
        assert c.post('/api/studies',json={'name':'hack'},headers=H).status_code==403
        assert c.get('/api/imports').status_code==404
        first=c.post('/api/demo/run',headers=H);assert first.status_code==200,first.text
        assert c.post('/api/demo/run',headers={**H,'X-Forwarded-For':'different','Cookie':'visitor=spoof'}).status_code==422
        with store.tx() as db:db.execute("UPDATE runs SET state='COMPLETED'")
        from masklab.store import now
        with store.tx() as db:db.execute('UPDATE quotas SET batches=50 WHERE day=?',(now()[:10],))
        assert c.post('/api/demo/run',headers=H).status_code==422


def test_ssrf_and_live_authorization(monkeypatch):
    monkeypatch.setenv('NEBIUS_BASE_URL','http://169.254.169.254/latest/meta-data')
    with pytest.raises(ValueError,match='allowlisted'):NebiusProvider()
    monkeypatch.delenv('NEBIUS_BASE_URL');monkeypatch.delenv('NEBIUS_API_KEY',raising=False)
    with pytest.raises(ValueError,match='credential'):NebiusProvider().preflight(ProtocolConfig().model_dump())


def test_parallel_public_batches_are_atomic(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from masklab.api import sample_dataset
    from masklab.store import Store
    store=Store(tmp_path/'parallel.sqlite3');s=store.create_study('public',public=True)
    data=sample_dataset();data.questions=data.questions[:1]
    p=store.freeze(s['id'],render_protocol(data,ProtocolConfig(roles=[{'id':'neutral','instruction':''}],frames=['absent'],repetitions=1),digest(b'x')))
    def attempt(i):
        try:
            store.create_run(p['id'],f'demo:same-ip:{i}',demo_visitor='same-ip');return 'accepted'
        except ValueError:return 'blocked'
    with ThreadPoolExecutor(max_workers=8) as pool:outcomes=list(pool.map(attempt,range(8)))
    assert outcomes.count('accepted')==1 and outcomes.count('blocked')==7


def test_live_smoke_is_gated_and_single_request(tmp_path,monkeypatch):
    monkeypatch.delenv('NEBIUS_API_KEY',raising=False)
    with TestClient(create_app(tmp_path,embedded_worker=False)) as c:
        assert c.post('/api/provider/smoke',json={'model':'nvidia/nemotron-test','budget_usd':'0.01'},headers=H).status_code==422
    from masklab.api import sample_dataset
    cfg=ProtocolConfig(purpose='access_smoke')
    with pytest.raises(ValueError,match='exactly one'):render_protocol(sample_dataset(),cfg,digest(b'x'))


def test_embedded_worker_lock_failure_is_startup_failure(tmp_path):
    app=create_app(tmp_path,embedded_worker=True)
    held=Worker(app.state.store);held.acquire()
    try:
        with pytest.raises(RuntimeError,match='Another'):
            with TestClient(app):pass
    finally:held.close()
