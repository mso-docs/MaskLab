"""TASK-012 / REQ-023–025: local reference/traceability check, not product acceptance."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
paths=[root/'README.md',*(root/'docs').glob('*.md'),*(root/'specs/001-initial-feature').glob('*.md')]
errors=[]
for p in paths:
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if '://' in target or target.startswith(('#','mailto:')):continue
        local=target.split('#')[0]
        if local and not (p.parent/local).exists():errors.append(f'{p.relative_to(root)}: {target}')
for name in ['tasks.md','acceptance.md','traceability.md']:
    text=(root/'specs/001-initial-feature'/name).read_text()
    for n in range(1,26):
        if f'REQ-{n:03d}' not in text:errors.append(name+f': missing REQ-{n:03d}')
assert not errors,'\n'.join(errors)
print(f'PASS: local links in {len(paths)} documents; 25 requirements mapped in tasks/acceptance/traceability')
