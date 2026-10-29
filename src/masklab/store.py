"""TASK-001/004: REQ-001/005/008/010–012. SQLite is the evidence authority."""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import uuid
from .contracts import canonical, digest


def now():
    return datetime.now(timezone.utc).isoformat()


def uid():
    return uuid.uuid4().hex


SCHEMA = '''
CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS studies (id TEXT PRIMARY KEY, name TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0, public INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL, updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS blobs (hash TEXT PRIMARY KEY, body BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS datasets (id TEXT PRIMARY KEY, study_id TEXT NOT NULL REFERENCES studies(id), hash TEXT NOT NULL REFERENCES blobs(hash), source_hash TEXT NOT NULL REFERENCES blobs(hash), created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS protocols (id TEXT PRIMARY KEY, study_id TEXT NOT NULL REFERENCES studies(id), hash TEXT NOT NULL REFERENCES blobs(hash), created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, study_id TEXT NOT NULL REFERENCES studies(id), protocol_id TEXT NOT NULL REFERENCES protocols(id), state TEXT NOT NULL, simulation INTEGER NOT NULL, idempotency TEXT NOT NULL UNIQUE, created TEXT NOT NULL, updated TEXT NOT NULL, reserved TEXT NOT NULL DEFAULT '0', spent TEXT NOT NULL DEFAULT '0', blocked_reason TEXT);
CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), position INTEGER NOT NULL, body TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'PENDING', UNIQUE(run_id,position));
CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES requests(id), ordinal INTEGER NOT NULL CHECK(ordinal BETWEEN 1 AND 2), state TEXT NOT NULL, started TEXT NOT NULL, ended TEXT, body TEXT NOT NULL, UNIQUE(request_id,ordinal));
CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), hash TEXT NOT NULL REFERENCES blobs(hash), created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS imported (id TEXT PRIMARY KEY, hash TEXT NOT NULL REFERENCES blobs(hash), created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS quotas (day TEXT NOT NULL, visitor TEXT NOT NULL, batches INTEGER NOT NULL, reserved TEXT NOT NULL, PRIMARY KEY(day,visitor));
CREATE TABLE IF NOT EXISTS worker_lease (id INTEGER PRIMARY KEY CHECK(id=1), owner TEXT NOT NULL, heartbeat REAL NOT NULL);
CREATE TRIGGER IF NOT EXISTS immutable_blob BEFORE UPDATE ON blobs BEGIN SELECT RAISE(ABORT,'immutable evidence'); END;
CREATE TRIGGER IF NOT EXISTS immutable_dataset BEFORE UPDATE ON datasets BEGIN SELECT RAISE(ABORT,'immutable dataset'); END;
CREATE TRIGGER IF NOT EXISTS immutable_protocol BEFORE UPDATE ON protocols BEGIN SELECT RAISE(ABORT,'immutable protocol'); END;
CREATE TRIGGER IF NOT EXISTS immutable_request BEFORE UPDATE OF body,position,run_id ON requests BEGIN SELECT RAISE(ABORT,'immutable rendered request'); END;
CREATE TRIGGER IF NOT EXISTS immutable_final_attempt BEFORE UPDATE ON attempts WHEN OLD.state != 'IN_FLIGHT' BEGIN SELECT RAISE(ABORT,'immutable final attempt'); END;
CREATE TRIGGER IF NOT EXISTS immutable_run_protocol BEFORE UPDATE OF protocol_id,simulation,study_id ON runs BEGIN SELECT RAISE(ABORT,'immutable run identity'); END;
CREATE INDEX IF NOT EXISTS request_queue ON requests(run_id,state,position);
'''


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.connect() as db:
            version = db.execute('PRAGMA user_version').fetchone()[0]
            if version > 1:
                raise ValueError('Database newer than this application; restore supported version')
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript(SCHEMA)
            db.execute('PRAGMA user_version=1')

    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA busy_timeout=15000')
        return db

    @contextmanager
    def tx(self):
        db = self.connect()
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def all(self, sql, params=()):
        with self.connect() as db:
            return [dict(r) for r in db.execute(sql, params)]

    def one(self, sql, params=()):
        rows = self.all(sql, params)
        if not rows:
            raise KeyError('Record not found')
        return rows[0]

    def blob(self, h):
        return strict_decode(self.one('SELECT body FROM blobs WHERE hash=?', (h,))['body'])

    @staticmethod
    def put_blob(db, value):
        body = value if isinstance(value, bytes) else canonical(value).encode()
        h = digest(body)
        db.execute('INSERT OR IGNORE INTO blobs VALUES (?,?)', (h, body))
        return h

    def create_study(self, name, public=False):
        id = uid()
        with self.tx() as db:
            db.execute('INSERT INTO studies VALUES (?,?,0,?,?,?)', (id, name, int(public), now(), now()))
        return self.one('SELECT * FROM studies WHERE id=?', (id,))

    def mutable(self, db, study_id):
        row = db.execute('SELECT * FROM studies WHERE id=?', (study_id,)).fetchone()
        if not row:
            raise KeyError('Study not found')
        if row['archived']:
            raise ValueError('Archived studies cannot accept new versions/runs')
        db.execute('UPDATE studies SET updated=? WHERE id=?', (now(), study_id))

    def add_dataset(self, study_id, data, raw):
        id = uid()
        with self.tx() as db:
            self.mutable(db, study_id)
            h, source = self.put_blob(db, data), self.put_blob(db, raw)
            db.execute('INSERT INTO datasets VALUES (?,?,?,?,?)', (id, study_id, h, source, now()))
        return {'id': id, 'hash': h, 'source_hash': source, 'dataset': data}

    def freeze(self, study_id, protocol):
        id = uid()
        with self.tx() as db:
            self.mutable(db, study_id)
            h = self.put_blob(db, protocol)
            db.execute('INSERT INTO protocols VALUES (?,?,?,?)', (id, study_id, h, now()))
        return {'id': id, 'protocol': protocol}

    def protocol(self, id):
        row = self.one('SELECT * FROM protocols WHERE id=?', (id,))
        return {**row, 'protocol': self.blob(row['hash'])}

    def create_run(self, protocol_id, idempotency, demo_visitor=None, draft=False):
        p = self.protocol(protocol_id)
        protocol = p['protocol']
        id = uid()
        with self.tx() as db:
            previous = db.execute('SELECT * FROM runs WHERE idempotency=?', (idempotency,)).fetchone()
            if previous:
                if previous['protocol_id'] != protocol_id:
                    raise ValueError('Idempotency key belongs to a different protocol')
                return dict(previous)
            self.mutable(db, p['study_id'])
            if demo_visitor:
                from decimal import Decimal
                day = now()[:10]
                active = db.execute("SELECT count(*) FROM runs WHERE idempotency LIKE ? AND state IN ('QUEUED','RUNNING','PAUSE_REQUESTED','PAUSED','BLOCKED')", (f'demo:{demo_visitor}:%',)).fetchone()[0]
                visitor_batches = db.execute('SELECT batches FROM quotas WHERE day=? AND visitor=?', (day, demo_visitor)).fetchone()
                total = db.execute('SELECT coalesce(sum(batches),0) FROM quotas WHERE day=?', (day,)).fetchone()[0]
                costs = sum((Decimal(x[0]) for x in db.execute('SELECT reserved FROM quotas WHERE day=?', (day,))), Decimal(0))
                if active or (visitor_batches and visitor_batches[0] >= 3) or total >= 50 or costs + Decimal(protocol['conservative_cost_usd']) > 1 or protocol['request_count'] > 8:
                    raise ValueError('Public quota unavailable; inspect saved evidence instead')
                db.execute('INSERT INTO quotas VALUES (?,?,1,?) ON CONFLICT(day,visitor) DO UPDATE SET batches=batches+1,reserved=CAST(reserved AS REAL)+CAST(excluded.reserved AS REAL)', (day, demo_visitor, protocol['conservative_cost_usd']))
            db.execute('INSERT INTO runs(id,study_id,protocol_id,state,simulation,idempotency,created,updated) VALUES (?,?,?,?,?,?,?,?)', (id, p['study_id'], protocol_id, 'DRAFT' if draft else 'QUEUED', int(protocol['simulation']), idempotency, now(), now()))
            for i, request in enumerate(protocol['requests']):
                db.execute('INSERT INTO requests(id,run_id,position,body) VALUES (?,?,?,?)', (uid(), id, i, canonical(request)))
        return self.run(id)

    def run(self, id):
        row = self.one('SELECT * FROM runs WHERE id=?', (id,))
        counts = self.all('SELECT state,count(*) AS count FROM requests WHERE run_id=? GROUP BY state', (id,))
        row['counts'] = {r['state']: r['count'] for r in counts}
        return row

    def records(self, run_id):
        rows = self.all('SELECT * FROM requests WHERE run_id=? ORDER BY position', (run_id,))
        attempts = self.all('SELECT a.* FROM attempts a JOIN requests r ON a.request_id=r.id WHERE r.run_id=? ORDER BY a.ordinal', (run_id,))
        grouped = {}
        for a in attempts:
            a['body'] = json.loads(a['body'])
            grouped.setdefault(a['request_id'], []).append(a)
        for row in rows:
            row['body'] = json.loads(row['body'])
            row['attempts'] = grouped.get(row['id'], [])
        return rows

    def control(self, id, action):
        with self.tx() as db:
            run = db.execute('SELECT * FROM runs WHERE id=?', (id,)).fetchone()
            if not run:
                raise KeyError('Run not found')
            state = run['state']
            if action == 'queue' and state == 'DRAFT':
                self.mutable(db, run['study_id'])
                state = 'QUEUED'
            elif action == 'pause' and state in ('QUEUED', 'RUNNING'):
                state = 'PAUSE_REQUESTED'
            elif action == 'cancel' and state in ('DRAFT','QUEUED','RUNNING','PAUSE_REQUESTED','PAUSED','BLOCKED'):
                state = 'CANCELLED' if state == 'DRAFT' else 'CANCEL_REQUESTED'
            elif action == 'resume' and state in ('PAUSED', 'BLOCKED'):
                self.mutable(db, run['study_id'])
                state = 'QUEUED'
            else:
                raise ValueError('Action not available for current run state')
            db.execute('UPDATE runs SET state=?,updated=?,blocked_reason=NULL WHERE id=?', (state, now(), id))
        return self.run(id)

    def save_analysis(self, run_id, analysis):
        id = uid()
        with self.tx() as db:
            h = self.put_blob(db, analysis)
            db.execute('INSERT INTO analyses VALUES (?,?,?,?)', (id, run_id, h, now()))
        return {'id': id, 'hash': h, 'analysis': analysis}

    def backup(self, destination):
        with self.connect() as source, sqlite3.connect(destination) as target:
            source.backup(target)
        return str(destination)


def strict_decode(body):
    from .contracts import strict_json
    return strict_json(body)
