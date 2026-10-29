"""TASK-004/013 / REQ-021: one durable additional-spend grant across workspaces.
Never resets on restart/day/run. Reservations do not expire. Unknown usage stops admission.
"""
from contextlib import contextmanager
from decimal import Decimal
import os
from pathlib import Path
import sqlite3
from .store import now


def money(value):
    amount=Decimal(str(value))
    if not amount.is_finite() or amount < 0:
        raise ValueError('Invalid spend amount')
    return amount


class SpendLedger:
    def __init__(self,path,authorization_id):
        self.path=str(Path(path).resolve())
        self.authorization_id=authorization_id
        if not Path(self.path).is_file():
            raise ValueError('Shared spend ledger missing; explicit authorization initialization required')
        with self.tx() as db:
            grant=db.execute('SELECT * FROM authorization WHERE id=1').fetchone()
            if not grant or grant['authorization_id']!=authorization_id:
                raise ValueError('Spend authorization identity does not match ledger')

    @classmethod
    def initialize(cls,path,authorization_id,limit='10'):
        amount=money(limit)
        if not authorization_id or not 0 < amount <= 10:
            raise ValueError('Additional authorization must be positive and at most USD10')
        path=Path(path).resolve();path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        # Never overwrite/reset an existing authorization, even if a new ID is supplied.
        if path.exists():
            ledger=cls(path,authorization_id)
            if money(ledger.snapshot()['limit_usd']) != amount:
                raise ValueError('Existing grant cannot be changed or topped up')
            return ledger
        fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
        with sqlite3.connect(path) as db:
            db.executescript('''
CREATE TABLE authorization(id INTEGER PRIMARY KEY CHECK(id=1),authorization_id TEXT NOT NULL,limit_usd TEXT NOT NULL,created TEXT NOT NULL,halted TEXT);
CREATE TABLE charges(attempt_id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,request_id TEXT NOT NULL,reserved_usd TEXT NOT NULL,state TEXT NOT NULL CHECK(state IN ('RESERVED','KNOWN','UNCERTAIN_COST')),cost_usd TEXT,created TEXT NOT NULL,settled TEXT);
CREATE TRIGGER fixed_grant BEFORE UPDATE OF authorization_id,limit_usd ON authorization BEGIN SELECT RAISE(ABORT,'grant cannot be raised or reset'); END;
CREATE TRIGGER no_grant_delete BEFORE DELETE ON authorization BEGIN SELECT RAISE(ABORT,'grant cannot be deleted'); END;
CREATE TRIGGER no_charge_delete BEFORE DELETE ON charges BEGIN SELECT RAISE(ABORT,'charges cannot be deleted'); END;
CREATE TRIGGER final_charge BEFORE UPDATE ON charges WHEN OLD.state='KNOWN' BEGIN SELECT RAISE(ABORT,'settled charge immutable'); END;
''')
            db.execute('INSERT INTO authorization VALUES (1,?,?,?,NULL)',(authorization_id,str(amount),now()))
        return cls(path,authorization_id)

    @contextmanager
    def tx(self):
        # mode=rw prevents a missing ledger from silently becoming an empty new budget.
        db=sqlite3.connect('file:'+self.path+'?mode=rw',uri=True,timeout=15)
        db.row_factory=sqlite3.Row
        try:
            db.execute('BEGIN IMMEDIATE');yield db;db.commit()
        except BaseException:
            db.rollback();raise
        finally:db.close()

    @staticmethod
    def totals(db):
        rows=db.execute('SELECT * FROM charges').fetchall()
        spent=sum((money(r['cost_usd']) for r in rows if r['state']=='KNOWN'),Decimal(0))
        held=sum((money(r['reserved_usd']) for r in rows if r['state']!='KNOWN'),Decimal(0))
        return rows,spent,held

    def snapshot(self):
        with self.tx() as db:
            grant=db.execute('SELECT * FROM authorization WHERE id=1').fetchone();rows,spent,held=self.totals(db)
            uncertain=sum(r['state']=='UNCERTAIN_COST' for r in rows)
            return {'authorization_id':grant['authorization_id'],'limit_usd':grant['limit_usd'],'estimated_spent_usd':str(spent),'held_usd':str(held),'remaining_usd':str(money(grant['limit_usd'])-spent-held),'attempts':len(rows),'uncertain_attempts':uncertain,'halted':grant['halted'],'automatic_topups':False}

    def reserve(self,attempt_id,workspace_id,request_id,amount,ceiling=None,ordinal=None):
        amount=money(amount)
        if amount<=0:raise ValueError('Live reservation must be positive')
        with self.tx() as db:
            grant=db.execute('SELECT * FROM authorization WHERE id=1').fetchone();rows,spent,held=self.totals(db)
            if grant['halted'] or any(r['state']=='UNCERTAIN_COST' for r in rows):
                raise ValueError('SHARED_BUDGET_HALTED_UNCERTAIN_COST')
            limit=money(grant['limit_usd']) if ceiling is None else min(money(grant['limit_usd']),money(ceiling))
            if spent+held+amount>limit:
                raise ValueError('SHARED_BUDGET_EXHAUSTED')
            if ordinal is not None:
                history=db.execute('SELECT count(*) FROM charges WHERE request_id=?',(request_id,)).fetchone()[0]
                if history != ordinal-1:
                    raise ValueError('LEDGER_ATTEMPT_HISTORY_MISMATCH_RECONCILE_RESTORED_WORKSPACE')
            db.execute("INSERT INTO charges VALUES (?,?,?,?,'RESERVED',NULL,?,NULL)",(attempt_id,workspace_id,request_id,str(amount),now()))

    def settle(self,attempt_id,cost=None,uncertain=False,violation=None):
        with self.tx() as db:
            row=db.execute('SELECT * FROM charges WHERE attempt_id=?',(attempt_id,)).fetchone()
            if not row:raise ValueError('Attempt has no durable spend reservation')
            if row['state']=='KNOWN':
                if not uncertain and money(row['cost_usd'])==money(cost):return
                raise ValueError('Settled usage cannot be changed')
            if uncertain:
                db.execute("UPDATE charges SET state='UNCERTAIN_COST',settled=? WHERE attempt_id=?",(now(),attempt_id))
                db.execute("UPDATE authorization SET halted='UNCERTAIN_COST' WHERE id=1")
            else:
                actual=money(cost)
                db.execute("UPDATE charges SET state='KNOWN',cost_usd=?,settled=? WHERE attempt_id=?",(str(actual),now(),attempt_id))
                if violation or actual>money(row['reserved_usd']):
                    db.execute('UPDATE authorization SET halted=? WHERE id=1',(violation or 'RESERVATION_EXCEEDED',))

    def recover_workspace(self,workspace_id,attempts):
        # Lock is held by that workspace's replacement worker. Cross-DB crash windows are conservative.
        with self.tx() as db:
            rows=db.execute("SELECT * FROM charges WHERE workspace_id=? AND state='RESERVED'",(workspace_id,)).fetchall()
        for row in rows:
            attempt=attempts.get(row['attempt_id'])
            if attempt and attempt['cost_state']=='KNOWN':
                self.settle(row['attempt_id'],attempt.get('cost_usd','0'))
            else:
                self.settle(row['attempt_id'],uncertain=True)


def configured_ledger():
    path=os.getenv('MASKLAB_SPEND_LEDGER','');identity=os.getenv('MASKLAB_AUTHORIZATION_ID','')
    if not path or not identity:raise ValueError('A shared cumulative spend ledger and authorization ID are required')
    return SpendLedger(path,identity)
