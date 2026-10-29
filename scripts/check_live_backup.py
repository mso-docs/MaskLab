"""TASK-013 / REQ-023/024: offline actual-evidence backup verification; no inference."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from masklab.runtime import load_env_file
from masklab.store import Store
from masklab.budget import configured_ledger
load_env_file('.env')
source=Store(Path(os.environ['MASKLAB_DATA_DIR'])/'masklab.sqlite3')
workspace=Path('artifacts/private/acceptance-workspace.sqlite3')
ledger_backup=Path('artifacts/private/acceptance-nebius-spend.sqlite3')
if workspace.exists() or ledger_backup.exists():raise ValueError('Backup destinations must be new; preserve existing evidence')
source.backup(workspace)
restored=Store(workspace)
counts={}
for table in ('studies','datasets','protocols','runs','requests','attempts','analyses','blobs'):
    a=source.all(f'SELECT * FROM {table} ORDER BY rowid');b=restored.all(f'SELECT * FROM {table} ORDER BY rowid')
    assert a==b,'Backup evidence mismatch';counts[table]=len(a)
for row in restored.all('SELECT * FROM blobs'):
    assert hashlib.sha256(row['body']).hexdigest()==row['hash']
with sqlite3.connect(os.environ['MASKLAB_SPEND_LEDGER']) as original,sqlite3.connect(ledger_backup) as target:
    original.backup(target)
    assert original.execute('SELECT * FROM authorization').fetchall()==target.execute('SELECT * FROM authorization').fetchall()
    assert original.execute('SELECT * FROM charges ORDER BY attempt_id').fetchall()==target.execute('SELECT * FROM charges ORDER BY attempt_id').fetchall()
    assert target.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
with restored.connect() as db:assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
result={'status':'PASS','evidence_table_counts':counts,'all_blobs_rehashed':True,'shared_ledger_snapshot_verified':True,'budget_unchanged':configured_ledger().snapshot(),'workspace_backup_sha256':hashlib.sha256(workspace.read_bytes()).hexdigest(),'ledger_backup_sha256':hashlib.sha256(ledger_backup.read_bytes()).hexdigest(),'provider_calls':0}
Path('artifacts/live-verification/backup-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
