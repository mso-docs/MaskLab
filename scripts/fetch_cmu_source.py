"""TASK-002/007/012 / REQ-004/005/024: public CMU source inspection, no execution/inference.
Archive stays outside Git; no tar entries are extracted to the filesystem.
"""
import hashlib,json,urllib.request,tarfile
from pathlib import Path
out=Path('data/question-sources/cmu-qa');out.mkdir(parents=True,exist_ok=True)
url='https://www.cs.cmu.edu/~ark/QA-data/data/Question_Answer_Dataset_v1.2.tar.gz'
path=out/'Question_Answer_Dataset_v1.2.tar.gz'
if not path.exists():
    with urllib.request.urlopen(url,timeout=60) as r:raw=r.read(30*1024*1024+1)
    if len(raw)>30*1024*1024:raise ValueError('Source exceeds bounded download')
    path.write_bytes(raw)
raw=path.read_bytes()
if (out/'upstream.json').exists():
    assert hashlib.sha256(raw).hexdigest()==json.loads((out/'upstream.json').read_text())['sha256'],'Pinned source hash changed; preserve it for review'
manifest={'source_url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'release':'1.2 (2013-08-23)','selected_cohort':'S10','license':'CC BY-SA 3.0 for S10; GFDL S08/S09 excluded','authority':'https://www.cs.cmu.edu/~ark/QA-data/data/README.v1.2','archive_extracted':False}
(out/'upstream.json').write_text(json.dumps(manifest,indent=2))
with tarfile.open(path,'r:gz') as archive:
    members=archive.getmembers()
    if len(members)>5000 or sum(m.size for m in members)>100*1024*1024:raise ValueError('Source expansion bound exceeded')
    names=[m.name for m in members if Path(m.name).name=='question_answer_pairs.txt' or Path(m.name).name.startswith(('LICENSE','README'))]
print(json.dumps({**manifest,'metadata_members':names},indent=2))
