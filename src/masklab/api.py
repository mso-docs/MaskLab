"""TASK-006–012 — authoritative owner/demo API and local React delivery."""
from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
import hashlib
import hmac
import ipaddress
import json
import os
from pathlib import Path
import secrets
from urllib.parse import urlsplit
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from .contracts import Dataset, ProtocolConfig, load_dataset, render_protocol, canonical, digest
from .store import Store, now, uid
from .worker import Worker
from .analysis import analyze
from .portable import export_run, import_archive, public_redacted_archive
from .provider import NebiusProvider
from .budget import configured_ledger

ROOT = Path(__file__).resolve().parents[2]


def sample_dataset():
    # Bundled synthetic fixture, not a scientific benchmark or model result.
    path = Path(__file__).parent / 'fixtures' / 'synthetic-v1.json'
    value = json.loads(path.read_text())
    for q in value['questions']:
        q.pop('verification', None)
    return Dataset.model_validate(value)


async def bounded_body(request, limit):
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > limit:
            raise ValueError('Request body exceeds size limit')
    return bytes(body)


def create_app(data_dir=None, mode=None, embedded_worker=True):
    mode = mode or os.getenv('MASKLAB_MODE', 'owner')
    if mode not in ('owner','demo'):
        raise ValueError('Mode must be owner or demo')
    folder = Path(data_dir or os.getenv('MASKLAB_DATA_DIR', './artifacts/workspace'))
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    store = Store(folder / 'masklab.sqlite3')
    worker = Worker(store)
    secret_path = folder / 'visitor-secret'
    if not secret_path.exists():
        fd = os.open(secret_path, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
        with os.fdopen(fd,'w') as f:
            f.write(secrets.token_hex(32))
    visitor_secret = secret_path.read_bytes()

    @asynccontextmanager
    async def lifespan(app):
        if embedded_worker:
            worker.acquire()  # Fail startup if another worker owns the volume; never claim false health.
        task = asyncio.create_task(worker.serve()) if embedded_worker else None
        app.state.worker_task=task
        yield
        if task:
            worker.stopping = True
            await task

    app = FastAPI(title='MaskLab', version='0.1.0', lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.store = store
    app.state.worker = worker
    app.state.mode = mode

    def error_response(status, code, message):
        return JSONResponse(status_code=status, content={'error':{'code':code,'message':message}})

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        if isinstance(exc, ValidationError):
            message = '; '.join('.'.join(map(str,x['loc']))+': '+x['msg'] for x in exc.errors(include_input=False))
        else:
            message = str(exc)[:3000]
        return error_response(422,'VALIDATION_ERROR', message)

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return error_response(404,'NOT_FOUND','Record not found')

    @app.middleware('http')
    async def boundary(request, call_next):
        host = request.headers.get('host','').split(':')[0].strip('[]')
        if host not in ('127.0.0.1','localhost','testserver') and mode == 'owner' and not os.getenv('MASKLAB_OWNER_TOKEN'):
            return error_response(403,'AUTH_REQUIRED','Hosted owner access requires server authentication')
        if request.url.path.startswith('/api/') and request.url.path not in ('/api/health','/api/config'):
            if mode == 'owner':
                token = os.getenv('MASKLAB_OWNER_TOKEN')
                if token:
                    supplied = request.headers.get('authorization','').removeprefix('Bearer ')
                    if not hmac.compare_digest(supplied,token):
                        return error_response(401,'OWNER_AUTH_REQUIRED','Owner session token required')
                elif not request.client or request.client.host not in ('127.0.0.1','::1','testclient'):
                    return error_response(403,'LOOPBACK_ONLY','Owner mode defaults to loopback-only access')
            elif request.method not in ('GET','HEAD') and request.url.path != '/api/demo/run':
                return error_response(403,'DEMO_RESTRICTED','This action is available only in the private owner workspace')
            if request.method not in ('GET','HEAD','OPTIONS'):
                origin = request.headers.get('origin')
                if origin and urlsplit(origin).netloc != request.headers.get('host'):
                    return error_response(403,'ORIGIN_REJECTED','Cross-origin writes are forbidden')
                if request.headers.get('x-masklab-request') != '1':
                    return error_response(403,'CSRF_REJECTED','Same-origin application request header required')
        response = await call_next(request)
        response.headers.update({'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",'Cache-Control':'no-store'})
        return response

    def visible_study(id):
        row = store.one('SELECT * FROM studies WHERE id=?',(id,))
        if mode == 'demo' and not row['public']:
            raise KeyError('Private study')
        return row

    def visible_run(id):
        row = store.run(id)
        visible_study(row['study_id'])
        return row

    async def body(request):
        from .contracts import strict_json
        return strict_json(await bounded_body(request, 6*1024*1024))

    @app.get('/api/health')
    def health():
        task=getattr(app.state,'worker_task',None)
        if task is not None and task.done():
            return JSONResponse(status_code=503,content={'status':'worker_unavailable','schema_version':1})
        return {'status':'ok','schema_version':store.one('PRAGMA user_version')['user_version']}

    @app.get('/api/config')
    def config():
        authorized=False;verified=False
        try:
            from decimal import Decimal
            ledger=configured_ledger().snapshot()
            approved=Decimal(os.getenv('MASKLAB_APPROVED_SPEND_USD','0'))
            authorized=approved.is_finite() and 0 < approved <= 10 and not ledger['halted']
            cap=NebiusProvider().capabilities()
            verified=any(m.get('inference_verified') for m in cap.get('models',{}).values())
        except (ValueError,KeyError):
            pass
        return {'mode':mode,'simulation_available':True,'live_spending_authorized':bool(authorized),'owner_auth_required':bool(os.getenv('MASKLAB_OWNER_TOKEN')),'limits':{'requests':5000,'questions':500,'roles':8,'models':3,'repetitions':20,'concurrency':4},'live_status':'READY: verified live profile with cumulative spend guard' if authorized and verified else 'PENDING verified capabilities, explicit authorization and shared ledger'}

    @app.get('/api/studies')
    def studies():
        return store.all('SELECT * FROM studies '+('WHERE public=1 ' if mode=='demo' else '')+'ORDER BY updated DESC')

    @app.post('/api/studies')
    async def create_study(request: Request):
        data = await body(request)
        name = data.get('name','').strip()
        if not 1 <= len(name) <= 200:
            raise ValueError('Study name must contain 1–200 characters')
        return store.create_study(name)

    @app.patch('/api/studies/{id}')
    async def edit_study(id: str, request: Request):
        visible_study(id)
        data = await body(request)
        if set(data) - {'name','archived','public'}:
            raise ValueError('Unknown study field')
        with store.tx() as db:
            for key, value in data.items():
                if key == 'name' and (not isinstance(value,str) or not 1 <= len(value.strip()) <= 200):
                    raise ValueError('Invalid study name')
                if key != 'name' and type(value) is not bool:
                    raise ValueError('Study flags must be booleans')
                db.execute(f'UPDATE studies SET {key}=?,updated=? WHERE id=?', (value,now(),id))
        return visible_study(id)

    @app.get('/api/studies/{id}')
    def study(id: str):
        row = visible_study(id)
        datasets = store.all('SELECT * FROM datasets WHERE study_id=? ORDER BY created DESC',(id,))
        return {**row,'datasets':[{**d,'dataset':store.blob(d['hash'])} for d in datasets], 'protocols':[{**p,'protocol':store.blob(p['hash'])} for p in store.all('SELECT * FROM protocols WHERE study_id=? ORDER BY created DESC',(id,))], 'runs':[store.run(r['id']) for r in store.all('SELECT id FROM runs WHERE study_id=? ORDER BY created DESC',(id,))]}

    @app.post('/api/studies/{id}/sample')
    def add_sample(id: str):
        dataset = sample_dataset().model_dump()
        return store.add_dataset(id,dataset,canonical(dataset).encode())

    @app.post('/api/studies/{id}/datasets')
    async def add_dataset(id: str, request: Request, kind: str = 'json'):
        visible_study(id)
        raw = await bounded_body(request,5*1024*1024)
        dataset = load_dataset(raw,kind)
        return store.add_dataset(id,dataset.model_dump(),raw)

    def prepare(id, data):
        visible_study(id)
        d = store.one('SELECT * FROM datasets WHERE id=? AND study_id=?',(data['dataset_id'],id))
        cfg = ProtocolConfig.model_validate(data['config'])
        if cfg.concurrency > int(os.getenv('MASKLAB_MAX_CONCURRENCY','4')):
            raise ValueError('Owner concurrency ceiling exceeded')
        if cfg.provider == 'nebius':
            cfg=NebiusProvider().bind_config(cfg)
        protocol = render_protocol(Dataset.model_validate(store.blob(d['hash'])),cfg,d['source_hash'],int(os.getenv('MASKLAB_MAX_REQUESTS','5000')))
        if cfg.provider == 'nebius':
            NebiusProvider().preflight(cfg.model_dump())
        return protocol

    @app.post('/api/studies/{id}/preview')
    async def preview(id: str, request: Request):
        return prepare(id,await body(request))

    @app.post('/api/studies/{id}/freeze')
    async def freeze(id: str, request: Request):
        data=await body(request)
        protocol=prepare(id,data)
        if data.get('expected_hash') and data['expected_hash'] != protocol['hash']:
            raise ValueError('Protocol changed since preview; review the new matrix before freezing')
        return store.freeze(id,protocol)

    @app.post('/api/protocols/{id}/runs')
    async def run_start(id: str, request: Request, draft: bool = False):
        p = store.protocol(id)
        visible_study(p['study_id'])
        if not p['protocol']['simulation']:
            NebiusProvider().preflight(p['protocol']['config'])
        key = request.headers.get('idempotency-key','')
        if not 8 <= len(key) <= 200 or key.startswith('demo:'):
            raise ValueError('Provide an 8–200 character idempotency key')
        return store.create_run(id,key,draft=draft)

    @app.get('/api/runs/{id}')
    def run(id: str):
        return visible_run(id)

    @app.post('/api/runs/{id}/{action}')
    async def run_action(id: str, action: str, request: Request):
        visible_run(id)
        if action == 'reanalyze':
            r = store.run(id)
            p = store.protocol(r['protocol_id'])['protocol']
            return store.save_analysis(id,analyze(p,store.records(id)))
        if action == 'queue':
            row = store.run(id)
            protocol = store.protocol(row['protocol_id'])['protocol']
            if not protocol['simulation']:
                NebiusProvider().preflight(protocol['config'])
        if action not in ('queue','pause','resume','cancel'):
            raise ValueError('Unknown run action')
        return store.control(id,action)

    @app.get('/api/runs/{id}/analysis')
    def results(id: str):
        r = visible_run(id)
        return analyze(store.protocol(r['protocol_id'])['protocol'],store.records(id))

    @app.get('/api/runs/{id}/export')
    def export(id: str):
        visible_run(id)
        return Response(public_redacted_archive(export_run(store,id)) if mode == 'demo' else export_run(store,id),media_type='application/zip',headers={'Content-Disposition':f'attachment; filename="masklab-{id}.zip"'})

    @app.post('/api/imports')
    async def import_study(request: Request):
        evidence = import_archive(await bounded_body(request,25*1024*1024))
        id = uid()
        with store.tx() as db:
            h = store.put_blob(db,evidence)
            db.execute('INSERT INTO imported VALUES (?,?,?)',(id,h,now()))
        return {'id':id,'inspection_only':True,'simulation':evidence['protocol']['simulation']}

    @app.get('/api/imports')
    def imported_list():
        if mode == 'demo':
            raise KeyError('Private imports')
        return store.all('SELECT * FROM imported ORDER BY created DESC')

    @app.get('/api/imports/{id}')
    def imported_inspect(id: str):
        if mode == 'demo':
            raise KeyError('Private import')
        r = store.one('SELECT * FROM imported WHERE id=?',(id,))
        return store.blob(r['hash'])

    @app.post('/api/imports/{id}/reanalyze')
    def imported_reanalyze(id: str):
        r = store.one('SELECT * FROM imported WHERE id=?',(id,))
        original = store.blob(r['hash'])
        derived = {**original,'analysis':analyze(original['protocol'],original['records']),'parent_import_id':id}
        new_id = uid()
        with store.tx() as db:
            h = store.put_blob(db,derived)
            db.execute('INSERT INTO imported VALUES (?,?,?)',(new_id,h,now()))
        return {'id':new_id,'parent_import_id':id,'inspection_only':True}

    @app.get('/api/provider/status')
    def provider_status():
        if mode == 'demo':
            raise KeyError('Private provider configuration')
        try:
            ledger=configured_ledger().snapshot()
        except ValueError:
            ledger=None
        models=[]
        provider=NebiusProvider()
        if provider.capability_file:
            cap=provider.capabilities()
            for model,details in cap.get('models',{}).items():
                models.append({'id':model,'inference_verified':bool(details.get('inference_verified')),'input_price_per_million':details.get('input_price_per_million'),'output_price_per_million':details.get('output_price_per_million'),'parameters':details.get('parameters',[]),'output_parameter':cap['output_parameter'],'enable_thinking':cap.get('enable_thinking'),'response_format':cap.get('response_format')})
        return {'credential_configured':bool(provider.key),'selected_model':os.getenv('NEBIUS_MODEL'),'models':models,'budget':ledger}

    @app.post('/api/provider/smoke')
    async def provider_smoke(request: Request):
        data = await body(request)
        model = data.get('model', '')
        provider = NebiusProvider()
        cap = provider.capabilities()
        prices = cap.get('models', {}).get(model, {})
        cfg = ProtocolConfig(provider='nebius', purpose='access_smoke', models=[model], roles=[{'id':'neutral','instruction':''}], frames=['absent'], repetitions=1, concurrency=1, max_output_tokens=64, budget_usd=data.get('budget_usd','0'), input_price_per_million=str(prices.get('input_price_per_million','0')), output_price_per_million=str(prices.get('output_price_per_million','0')))
        cfg=provider.bind_config(cfg)
        dataset = sample_dataset()
        dataset.questions = dataset.questions[:1]
        protocol = render_protocol(dataset,cfg,digest(dataset.model_dump()))
        study = store.create_study('Explicit funded provider access smoke')
        store.add_dataset(study['id'],dataset.model_dump(),canonical(dataset.model_dump()).encode())
        frozen = store.freeze(study['id'],protocol)
        return store.create_run(frozen['id'],'smoke:'+uid())

    @app.post('/api/provider/models')
    async def provider_models():
        return await NebiusProvider().list_models()

    @app.post('/api/demo/run')
    def demo_run(request: Request):
        if mode != 'demo':
            raise ValueError('Demo execution is available only in separate demo mode')
        # IP is taken from the socket, never client-controlled headers/cookies. Global quota remains binding.
        peer = request.client.host if request.client else 'unknown'
        visitor = hmac.new(visitor_secret,peer.encode(),hashlib.sha256).hexdigest()
        public = store.all('SELECT p.* FROM protocols p JOIN studies s ON p.study_id=s.id WHERE s.public=1 AND s.archived=0 ORDER BY p.created DESC')
        allowed = [p for p in public if store.blob(p['hash'])['request_count'] <= 8]
        if not allowed:
            raise ValueError('No curated bounded protocol is available; live demo pending authorized release')
        p = allowed[0]
        protocol = store.blob(p['hash'])
        if not protocol['simulation']:
            NebiusProvider().preflight(protocol['config'])
        return store.create_run(p['id'],f'demo:{visitor}:{uid()}',demo_visitor=visitor)

    static = Path(__file__).parent / 'static'
    if static.exists():
        if (static/'brand').exists():
            app.mount('/brand',StaticFiles(directory=static/'brand'),name='brand')
        app.mount('/assets',StaticFiles(directory=static/'assets'),name='assets')
        @app.get('/{route:path}')
        def frontend(route: str):
            if route.startswith('api/'):
                return error_response(404,'NOT_FOUND','Unknown API route')
            return FileResponse(static/'index.html')
    return app
