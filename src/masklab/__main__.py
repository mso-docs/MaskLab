"""TASK-012 / REQ-023 local operations; defaults never enable spending."""
import argparse
import asyncio
import os
from pathlib import Path
import uvicorn
from .api import create_app
from .store import Store
from .worker import Worker


def main():
    parser = argparse.ArgumentParser(prog='masklab')
    parser.add_argument('command',choices=['serve','worker','backup','budget'])
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--data-dir',default=os.getenv('MASKLAB_DATA_DIR','./artifacts/workspace'))
    parser.add_argument('--destination')
    parser.add_argument('--env-file',help='Explicit private dotenv file; never executed as shell code')
    parser.add_argument('--external-worker',action='store_true')
    args = parser.parse_args()
    if args.env_file:
        from .runtime import load_env_file
        load_env_file(args.env_file)
        if args.data_dir == './artifacts/workspace':
            args.data_dir=os.getenv('MASKLAB_DATA_DIR',args.data_dir)
    if args.command == 'budget':
        from .budget import configured_ledger
        import json
        print(json.dumps(configured_ledger().snapshot(),indent=2))
        return
    if args.command == 'serve':
        if args.host not in ('127.0.0.1','localhost','::1') and os.getenv('MASKLAB_MODE','owner') == 'owner' and not os.getenv('MASKLAB_OWNER_TOKEN'):
            parser.error('Non-loopback owner binding requires MASKLAB_OWNER_TOKEN')
        uvicorn.run(create_app(args.data_dir,embedded_worker=not args.external_worker),host=args.host,port=args.port,access_log=False)
    elif args.command == 'worker':
        asyncio.run(Worker(Store(Path(args.data_dir)/'masklab.sqlite3')).serve())
    else:
        if not args.destination:
            parser.error('--destination is required for backup')
        if Path(args.destination).exists():
            parser.error('Backup destination must be new')
        Store(Path(args.data_dir)/'masklab.sqlite3').backup(args.destination)


if __name__ == '__main__':
    main()
