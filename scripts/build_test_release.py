"""TASK-014 / REQ-018/020/023/025. Build an allowlisted, key-free release and Pages artifact.
No commit, upload, publication or provider calls. Run after frontend + wheel builds.
"""
import hashlib
import io
import json
from pathlib import Path
import shutil
import zipfile
from masklab.portable import import_archive

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/release'
SITE = OUT / 'pages'
BUNDLE = OUT / 'masklab-test-build'
SOURCE = ROOT / 'public-evidence/replication-v2-redacted.zip'


def sha(raw): return hashlib.sha256(raw).hexdigest()


def main():
    for directory in (BUNDLE, SITE):
        if directory.exists(): shutil.rmtree(directory)
        directory.mkdir(parents=True)
    with zipfile.ZipFile(SOURCE) as z:
        manifest = json.loads(z.read('manifest.json'))
        assert manifest['format'] == 'masklab-public-redacted-evidence'
        assert manifest['redaction']['timestamp_occurrences'] == 0, 'Redacted data cannot become a standard import'
        files = {name: z.read(name) for name in manifest['files']}
        for name, raw in files.items():
            assert sha(raw) == manifest['files'][name]['sha256']
            assert len(raw) == manifest['files'][name]['size']
    protocol = json.loads(files['protocol.json'])
    analysis = json.loads(files['analysis.json'])
    records = json.loads(files['records.json'])
    data = json.loads(files['dataset.json'])
    standard = {'schema_version': 1, 'format': 'masklab-evidence', 'simulation': False,
                'protocol_hash': protocol['hash'],
                'provenance': {'repackaged_from': SOURCE.name, 'source_sha256': sha(SOURCE.read_bytes()),
                               'scientific_payloads_unchanged': True, 'timestamp_substitutions': 0},
                'files': {name: {'sha256': sha(raw), 'size': len(raw)} for name, raw in files.items()}}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for name, raw in {**files, 'manifest.json': json.dumps(standard).encode()}.items():
            info = zipfile.ZipInfo(name, (1980,1,1,0,0,0)); info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, raw)
    saved = buf.getvalue()
    validated = import_archive(saved)
    assert validated['analysis']['summary']['counts'] == analysis['summary']['counts']
    (BUNDLE / 'saved-evidence.zip').write_bytes(saved)
    wheels = list((ROOT / 'dist').glob('masklab-0.1.0.dev0-py3-none-any.whl'))
    assert len(wheels) == 1
    for src in [wheels[0], ROOT/'requirements.lock', ROOT/'LICENSE', ROOT/'release/run.py', ROOT/'release/README.txt']:
        shutil.copyfile(src, BUNDLE/src.name)
    (BUNDLE/'DATA-NOTICES.txt').write_text(data['limitations'], encoding='utf-8')
    build = {'release': '0.1.0-rc1', 'package_version': '0.1.0.dev0', 'python': '3.14',
             'saved_evidence_sha256': sha(saved), 'public_source_sha256': sha(SOURCE.read_bytes()),
             'protocol_hash': protocol['hash'], 'counts': analysis['summary']['counts'],
             'live_calls_enabled': False, 'source': 'approved public derivative; unchanged scientific payloads'}
    (BUNDLE/'BUILD.json').write_text(json.dumps(build, indent=2))
    bundle_zip = OUT/'masklab-test-build.zip'
    with zipfile.ZipFile(bundle_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(BUNDLE.iterdir()): z.write(p, 'masklab-test-build/'+p.name)
    for p in (ROOT/'web-demo').iterdir():
        if p.is_file(): shutil.copyfile(p, SITE/p.name)
    (SITE/'brand').mkdir()
    shutil.copyfile(ROOT/'frontend/public/brand/masklab-mark.svg', SITE/'brand/mark.svg')
    (SITE/'downloads').mkdir()
    shutil.copyfile(bundle_zip, SITE/'downloads'/bundle_zip.name)
    shutil.copyfile(BUNDLE/'saved-evidence.zip', SITE/'downloads/saved-evidence.zip')
    shutil.copyfile(SOURCE, SITE/'downloads/public-evidence.zip')
    shutil.copyfile(BUNDLE/'DATA-NOTICES.txt', SITE/'downloads/DATA-NOTICES.txt')
    # Compact public viewer projection; no timestamps, host paths, request IDs or credentials.
    scores = {r['id']: r['score'] for r in analysis['records']}
    rows = [{'question': r['body']['key'][1], 'role': r['body']['key'][2], 'frame': r['body']['key'][3],
             'repeat': r['body']['key'][4]+1, 'score': scores[r['id']],
             'prompt': r['body']['messages'],
             'response': r['attempts'][-1]['body'].get('final_text', '') if r['attempts'] else ''}
            for r in records]
    view = {'model': protocol['config']['models'][0], 'protocol_hash': protocol['hash'],
            'counts': analysis['summary']['counts'], 'questions': data['questions'], 'records': rows,
            'source_sha256': sha(SOURCE.read_bytes()), 'limitations': data['limitations']}
    (SITE/'evidence.json').write_text(json.dumps(view, ensure_ascii=False), encoding='utf-8')
    (SITE/'release.json').write_text(json.dumps({**build, 'download_sha256': sha(bundle_zip.read_bytes())}, indent=2))
    (SITE/'.nojekyll').write_text('')
    (OUT/'SHA256SUMS').write_text(f'{sha(bundle_zip.read_bytes())}  masklab-test-build.zip\n')
    print(json.dumps({'bundle': str(bundle_zip.relative_to(ROOT)), 'pages': str(SITE.relative_to(ROOT)),
                      'sha256': sha(bundle_zip.read_bytes()), 'counts': build['counts']}))


if __name__ == '__main__': main()
