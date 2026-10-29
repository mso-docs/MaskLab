"""TASK-004 — REQ-010/011/012/021. Commit intent before dispatch; never replay uncertainty."""
from __future__ import annotations
import asyncio
from decimal import Decimal
import fcntl
import json
import os
import time
from .contracts import canonical, digest
from .budget import configured_ledger
from .provider import provider_for, ProviderError
from .store import Store, now, uid


class Worker:
    def __init__(self, store: Store):
        self.store = store
        self.lock = None
        self.stopping = False

    def acquire(self):
        if self.lock:
            return
        self.lock = open(self.store.path + '.worker.lock', 'a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            self.lock = None
            raise RuntimeError('Another single-writer worker holds the workspace') from None
        self.recover()

    def close(self):
        if self.lock:
            fcntl.flock(self.lock, fcntl.LOCK_UN)
            self.lock.close()
            self.lock = None

    def recover(self):
        if not self.lock:
            raise RuntimeError('Recovery requires the exclusive workspace worker lock')
        with self.store.tx() as db:
            for a in db.execute("SELECT * FROM attempts WHERE state='IN_FLIGHT'").fetchall():
                body = json.loads(a['body'])
                body.update(error_code='WORKER_INTERRUPTED', cost_state='UNCERTAIN_COST', usage=None, recovered=True)
                db.execute("UPDATE attempts SET state='UNCERTAIN',ended=?,body=? WHERE id=?", (now(), canonical(body), a['id']))
                db.execute("UPDATE requests SET state='UNCERTAIN' WHERE id=?", (a['request_id'],))
            db.execute("UPDATE runs SET state='QUEUED',updated=? WHERE state='RUNNING'", (now(),))
        if os.getenv('MASKLAB_SPEND_LEDGER'):
            bodies={a['id']:json.loads(a['body']) for a in self.store.all('SELECT id,body FROM attempts')}
            configured_ledger().recover_workspace(digest(os.path.realpath(self.store.path)),bodies)

    def claim(self, run, protocol):
        cfg = protocol['config']
        with self.store.tx() as db:
            current = db.execute('SELECT * FROM runs WHERE id=?', (run['id'],)).fetchone()
            study = db.execute('SELECT archived FROM studies WHERE id=?', (run['study_id'],)).fetchone()
            if current['state'] not in ('QUEUED', 'RUNNING'):
                return None
            if study['archived']:
                db.execute("UPDATE runs SET state='BLOCKED',blocked_reason='STUDY_ARCHIVED' WHERE id=?", (run['id'],))
                return None
            request = db.execute("SELECT * FROM requests WHERE run_id=? AND state='PENDING' ORDER BY position LIMIT 1", (run['id'],)).fetchone()
            if not request:
                return None
            body = json.loads(request['body'])
            reserve = Decimal(body['reserve_usd'])
            if cfg['provider'] == 'nebius':
                approved = Decimal(os.getenv('MASKLAB_APPROVED_SPEND_USD', '0'))
                totals = db.execute('SELECT reserved,spent FROM runs WHERE simulation=0').fetchall()
                total = sum((Decimal(r['reserved']) + Decimal(r['spent']) for r in totals), Decimal(0))
                if total + reserve > approved or Decimal(current['reserved']) + Decimal(current['spent']) + reserve > Decimal(cfg['budget_usd']):
                    db.execute("UPDATE runs SET state='BLOCKED',blocked_reason='BUDGET_EXHAUSTED',updated=? WHERE id=?", (now(), run['id']))
                    return None
            count = db.execute('SELECT count(*) FROM attempts WHERE request_id=?', (request['id'],)).fetchone()[0]
            if count >= 2:
                db.execute("UPDATE requests SET state='FAILED' WHERE id=?", (request['id'],))
                return None
            attempt_id = uid()
            started = now()
            if cfg['provider'] == 'nebius':
                try:
                    configured_ledger().reserve(attempt_id,digest(os.path.realpath(self.store.path)),request['id'],reserve,ceiling=approved,ordinal=count+1)
                except ValueError as exc:
                    db.execute("UPDATE runs SET state='BLOCKED',blocked_reason=?,updated=? WHERE id=?",(str(exc),now(),run['id']))
                    return None
            db.execute("INSERT INTO attempts VALUES (?,?,?,'IN_FLIGHT',?,NULL,?)", (attempt_id, request['id'], count+1, started, canonical({'reserve_usd': str(reserve), 'cost_state': 'RESERVED', 'simulation': protocol['simulation']})))
            db.execute("UPDATE requests SET state='IN_FLIGHT' WHERE id=?", (request['id'],))
            db.execute("UPDATE runs SET state='RUNNING',reserved=?,updated=? WHERE id=?", (str(Decimal(current['reserved'])+reserve), started, run['id']))
        return dict(request), body, attempt_id, count+1

    async def execute(self, run, protocol, provider, claim):
        request, body, attempt_id, ordinal = claim
        started = time.monotonic()
        retry = False
        reserve = Decimal(body['reserve_usd'])
        known_cost = Decimal(0)
        try:
            result = await asyncio.wait_for(provider.complete(body, protocol['config'], ordinal), timeout=65)
            state = 'SUCCEEDED'
            usage = result.get('usage')
            if usage is not None:
                cfg = protocol['config']
                known_cost = (Decimal(usage['input_tokens']) * Decimal(cfg['input_price_per_million']) + Decimal(usage['output_tokens']) * Decimal(cfg['output_price_per_million'])) / 1000000
                result.update(cost_state='KNOWN', cost_usd=str(known_cost))
            else:
                result.update(cost_state='UNCERTAIN_COST', cost_usd=None)
        except (ProviderError, TimeoutError) as exc:
            uncertain = isinstance(exc, TimeoutError) or exc.uncertain
            state = 'UNCERTAIN' if uncertain else 'FAILED'
            retry = isinstance(exc, ProviderError) and exc.transient and not uncertain and ordinal < 2
            result = {'error_code': 'DEADLINE_AMBIGUOUS' if isinstance(exc, TimeoutError) else exc.code, 'usage': None, 'cost_state': 'UNCERTAIN_COST' if uncertain else 'KNOWN', 'cost_usd': None if uncertain else '0', 'simulation': protocol['simulation']}
        except Exception:
            # Unexpected errors after dispatch have unknown acceptance; preserve intent and stop replay.
            state = 'UNCERTAIN'
            result = {'error_code': 'UNEXPECTED_AFTER_DISPATCH', 'usage': None, 'cost_state': 'UNCERTAIN_COST', 'cost_usd': None, 'simulation': protocol['simulation']}
        result.update(duration_ms=round((time.monotonic()-started)*1000, 3), reserve_usd=str(reserve))
        with self.store.tx() as db:
            current = db.execute('SELECT * FROM runs WHERE id=?', (run['id'],)).fetchone()
            release = reserve if result['cost_state'] == 'KNOWN' else Decimal(0)
            db.execute('UPDATE attempts SET state=?,ended=?,body=? WHERE id=?', (state, now(), canonical(result), attempt_id))
            db.execute('UPDATE requests SET state=? WHERE id=?', ('PENDING' if retry else state, request['id']))
            spent = Decimal(current['spent']) + known_cost
            db.execute('UPDATE runs SET reserved=?,spent=?,updated=? WHERE id=?', (str(Decimal(current['reserved'])-release), str(spent), now(), run['id']))
            if known_cost > reserve:
                db.execute("UPDATE runs SET state='BLOCKED',blocked_reason='PRICE_OR_USAGE_EXCEEDS_RESERVATION' WHERE id=?", (run['id'],))
        if not protocol['simulation']:
            violation = None
            usage = result.get('usage')
            if usage and (usage['input_tokens'] > body['input_token_bound'] or usage['output_tokens'] > protocol['config']['max_output_tokens']):
                violation = 'TOKEN_BOUND_EXCEEDED'
            configured_ledger().settle(attempt_id,known_cost,uncertain=result['cost_state']!='KNOWN',violation=violation)
            if violation or result['cost_state'] != 'KNOWN':
                with self.store.tx() as db:
                    db.execute("UPDATE runs SET state='BLOCKED',blocked_reason=? WHERE id=?",(violation or 'UNCERTAIN_COST',run['id']))
        if retry:
            await asyncio.sleep(0.05 if protocol['simulation'] else 2)

    def settle(self, id):
        with self.store.tx() as db:
            row = db.execute('SELECT * FROM runs WHERE id=?', (id,)).fetchone()
            pending = db.execute("SELECT count(*) FROM requests WHERE run_id=? AND state IN ('PENDING','IN_FLIGHT')", (id,)).fetchone()[0]
            inflight = db.execute("SELECT count(*) FROM requests WHERE run_id=? AND state='IN_FLIGHT'", (id,)).fetchone()[0]
            state = row['state']
            if not inflight and state == 'PAUSE_REQUESTED':
                state = 'PAUSED'
            elif not inflight and state == 'CANCEL_REQUESTED':
                state = 'CANCELLED'
            elif not pending and state in ('RUNNING', 'QUEUED'):
                errors = db.execute("SELECT count(*) FROM requests WHERE run_id=? AND state!='SUCCEEDED'", (id,)).fetchone()[0]
                state = 'COMPLETED_WITH_ERRORS' if errors else 'COMPLETED'
            db.execute('UPDATE runs SET state=?,updated=? WHERE id=?', (state, now(), id))

    async def tick(self):
        self.acquire()
        runs = self.store.all("SELECT * FROM runs WHERE state IN ('QUEUED','RUNNING','PAUSE_REQUESTED','CANCEL_REQUESTED') ORDER BY created")
        if not runs:
            return False
        run = runs[0]
        protocol = self.store.protocol(run['protocol_id'])['protocol']
        cfg = protocol['config']
        provider = provider_for(cfg)
        try:
            if not protocol['simulation']:
                provider.preflight(cfg)
        except ValueError:
            with self.store.tx() as db:
                db.execute("UPDATE runs SET state='BLOCKED',blocked_reason='LIVE_PREFLIGHT_REQUIRED' WHERE id=?", (run['id'],))
            return True
        claims = []
        for _ in range(cfg['concurrency']):
            claimed = self.claim(run, protocol)
            if claimed:
                claims.append(claimed)
        if claims:
            await asyncio.gather(*(self.execute(run, protocol, provider, claim) for claim in claims))
        self.settle(run['id'])
        return True

    async def serve(self):
        self.acquire()
        try:
            while not self.stopping:
                active = await self.tick()
                await asyncio.sleep(0.05 if active else 0.5)
        finally:
            self.close()
