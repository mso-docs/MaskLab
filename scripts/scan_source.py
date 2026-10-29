"""Scan all tracked and nonignored source without changing the real Git index.
TASK-012 / REQ-020/024. This does not authorize any commit or push.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
report=root/'artifacts/verification/gitleaks.json'
report.parent.mkdir(parents=True,exist_ok=True)
listed=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=root).split(b'\0')
with tempfile.TemporaryDirectory(prefix='masklab-source-scan-') as folder:
    count=0
    for raw in dict.fromkeys(listed):
        if not raw:continue
        rel=Path(raw.decode());source=root/rel
        if source.is_file() and not source.is_symlink():
            target=Path(folder)/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);count+=1
    print(f'Scanning {count} source files; real Git index untouched.',flush=True)
    result=subprocess.run(['gitleaks','detect','--no-git','--source',folder,'--redact','--report-path',str(report),'--no-banner'])
    raise SystemExit(result.returncode)
