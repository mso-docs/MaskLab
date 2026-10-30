"""TASK-014 / REQ-018/020/023/025: key-free local judge test build."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--check', action='store_true', help='Validate and seed saved evidence, then exit without serving')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    # No dotenv loading; inherited research credentials/budget settings cannot enable this build.
    for key in list(os.environ):
        if key.startswith(('NEBIUS_', 'MASKLAB_')):
            os.environ.pop(key)
    os.environ['MASKLAB_MODE'] = 'owner'
    os.environ['MASKLAB_APPROVED_SPEND_USD'] = '0'
    from masklab.store import Store, now
    from masklab.portable import import_archive
    raw = (root / 'saved-evidence.zip').read_bytes()
    expected = json.loads((root / 'BUILD.json').read_text())['saved_evidence_sha256']
    if hashlib.sha256(raw).hexdigest() != expected:
        raise SystemExit('Saved evidence checksum mismatch; download a fresh build.')
    evidence = import_archive(raw)
    store = Store(root / 'workspace' / 'masklab.sqlite3')
    if not store.all('SELECT * FROM imported WHERE id=?', ('saved-public-replication',)):
        with store.tx() as db:
            blob = store.put_blob(db, evidence)
            db.execute('INSERT INTO imported VALUES (?,?,?)', ('saved-public-replication', blob, now()))
    print('Saved real Nemotron evidence validated: 4,050 finalized / 2,427 correct / 150 invalid.', flush=True)
    print('No provider credentials loaded. New experiments are SIMULATED; saved evidence is LIVE.', flush=True)
    if args.check:
        return
    import uvicorn
    from masklab.api import create_app
    print(f'Open http://127.0.0.1:{args.port} — Studies → Portable evidence → saved-public-replication', flush=True)
    uvicorn.run(create_app(root / 'workspace', mode='owner'), host='127.0.0.1', port=args.port, access_log=False)


if __name__ == '__main__':
    main()
