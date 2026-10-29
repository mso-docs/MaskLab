"""TASK-002/007/012 / REQ-004/005/024: pinned public source, no provider calls.
Dataset bytes stay under ignored data/. Preserve upstream MIT notice and raw hashes.
"""
import hashlib
import json
from pathlib import Path
import urllib.request

out=Path('data/question-sources/gsm8k');out.mkdir(parents=True,exist_ok=True)
headers={'User-Agent':'MaskLab-dataset-preparation'}
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as response:return response.read()
manifest=out/'upstream.json'
if manifest.exists():
    value=json.loads(manifest.read_text())
    for item in value['files']:
        assert hashlib.sha256((out/item['name']).read_bytes()).hexdigest()==item['sha256']
    print(json.dumps({'status':'REUSED_PINNED_SOURCE','commit':value['commit']}))
else:
    commit=json.loads(fetch('https://api.github.com/repos/openai/grade-school-math/commits/master'))['sha']
    files=[]
    for path,name in [('grade_school_math/data/test.jsonl','gsm8k-test.jsonl'),('LICENSE','LICENSE-gsm8k.txt'),('README.md','README-gsm8k.md')]:
        url=f'https://raw.githubusercontent.com/openai/grade-school-math/{commit}/{path}'
        raw=fetch(url)
        (out/name).write_bytes(raw)
        files.append({'name':name,'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    value={'repository':'https://github.com/openai/grade-school-math','commit':commit,'license':'MIT; upstream notice retained','files':files}
    manifest.write_text(json.dumps(value,indent=2))
    print(json.dumps({'status':'DOWNLOADED','commit':commit,'files':[f['name'] for f in files]}))

# Reconstruct selection inputs on a fresh checkout; no hidden manual source files required.
import random
rows=[json.loads(line) for line in (out/'gsm8k-test.jsonl').read_text().splitlines()]
initial=random.Random(28102026).sample(range(len(rows)),25)
remaining=[i for i in range(len(rows)) if i not in initial]
random.Random(28102027).shuffle(remaining)
for filename,value in [('selected-indices.json',initial),('fallback-indices.json',remaining)]:
    target=out/filename
    if target.exists():assert json.loads(target.read_text())==value,'Preserve differing selection metadata for review'
    else:target.write_text(json.dumps(value))
