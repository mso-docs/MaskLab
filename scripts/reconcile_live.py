"""TASK-013 / REQ-021/024: independent receipt-to-shared-ledger reconciliation.
No application imports, credentials, provider calls or invoice claims.
"""
from decimal import Decimal
import json
from pathlib import Path
import sqlite3
import sys
import zipfile

ledger=sys.argv[1];receipts={}
for filename in sys.argv[2:]:
    with zipfile.ZipFile(filename) as z:records=json.loads(z.read('records.json'))
    for request in records:
        for attempt in request['attempts']:
            if attempt['id'] in receipts:raise ValueError('Duplicate receipt coverage')
            receipts[attempt['id']]={'request_id':request['id'],'cost':Decimal(attempt['body']['cost_usd']),'state':attempt['body']['cost_state']}
with sqlite3.connect('file:'+str(Path(ledger).resolve())+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    grant=db.execute('SELECT * FROM authorization').fetchone();charges=db.execute('SELECT * FROM charges').fetchall()
assert grant['limit_usd']=='10' and grant['halted'] is None
assert len(charges)==len(receipts)==669
for row in charges:
    receipt=receipts[row['attempt_id']]
    assert row['request_id']==receipt['request_id']
    assert row['state']==receipt['state']=='KNOWN'
    assert Decimal(row['cost_usd'])==receipt['cost']<=Decimal(row['reserved_usd'])
spent=sum((r['cost'] for r in receipts.values()),Decimal(0))
assert spent==Decimal('0.00455352')
print(json.dumps({'status':'PASS','unique_receipts':len(receipts),'ledger_charges_matched':len(charges),'estimated_spent_usd':str(spent),'held_usd':'0','remaining_usd':str(Decimal(grant['limit_usd'])-spent),'invoice_reconciled':False,'provider_calls':0},indent=2))
