"""TASK-013 / REQ-020: exact secret canary scan; never outputs secret/fingerprint/content."""
import json
import os
from pathlib import Path
import subprocess
import zipfile
from masklab.runtime import load_env_file
load_env_file('.env')
secret=os.environ['NEBIUS_API_KEY'].encode()
assert secret,'Credential missing; cannot check boundaries'
root=Path('.').resolve();files=set()
source=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard']).split(b'\0')
for name in source:
    if name:
        p=root/os.fsdecode(name)
        if p.is_file() and not p.is_symlink():files.add(p)
for base in ('src/masklab/static','artifacts/live-verification','artifacts/charts','artifacts/mixed-study','artifacts/replication-v2','data/replication-mixed-150-v2','data/replication-060-v2','data/study-draft-150'):
    files.update(p for p in (root/base).rglob('*') if p.is_file())
files.update((root/'artifacts').rglob('*.sqlite3'))
files.update((root/'dist').glob('*.whl'))
for p in files:
    if secret in p.read_bytes():raise SystemExit('FAIL: exact credential detected; content and location withheld')
    if p.suffix in ('.zip','.whl'):
        with zipfile.ZipFile(p) as z:
            for info in z.infolist():
                if secret in z.read(info):raise SystemExit('FAIL: exact credential detected in archive; content withheld')
tracked_env=subprocess.check_output(['git','ls-files','-z','--','.env*']).split(b'\0')
if any(n and n!=b'.env.example' for n in tracked_env):raise SystemExit('FAIL: local dotenv variant is tracked')
result={'status':'PASS','files_checked':len(files),'archive_members_checked':True,'frontend_api_artifact_database_and_nonignored_source_boundaries':'clean','credential_or_fingerprint_printed':False}
Path('artifacts/live-verification/secret-boundaries.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
