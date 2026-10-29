"""TASK-010 — REQ-018–020: inert, bounded, hash-verified research archives."""
import csv
import io
import json
from pathlib import PurePosixPath
import stat
import zipfile
from .analysis import analyze
from .contracts import Dataset, ProtocolConfig, canonical, digest, render_protocol, strict_json

MAX_COMPRESSED = 25*1024*1024
MAX_EXPANDED = 100*1024*1024


def safe_cell(value):
    text = '' if value is None else str(value)
    if text.lstrip().startswith(('=','+','-','@','\t','\r')):
        return "'" + text
    return text


def csv_bytes(rows, columns):
    out = io.StringIO(newline='')
    writer = csv.writer(out)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([safe_cell(row.get(k)) for k in columns])
    return out.getvalue().encode()


def report(analysis):
    s = analysis['summary']; c = s['counts']
    return '\n'.join(['# MaskLab research record', '', '**'+analysis['evidence_label']+'**', '', f"Protocol SHA256: {analysis['protocol_hash']}", f"Metric version: {analysis['metric_version']}", '', '## Observations', '', f"Scheduled: {c['scheduled']}; finalized: {c['finalized']}; valid: {c['valid']}; correct: {c['correct']}; failed: {c['failed']}; uncertain: {c['uncertain']}; pending: {c['pending']}.", f"All-attempt correctness: {c['correct']}/{c['finalized']}; valid accuracy: {c['correct']}/{c['valid']}.", '', '## Methods and limitations', '', 'Roles and stated belief are crossed independently, with fresh conversations and frozen prompts. Decimal scoring is exact; invalid/refused/failed responses are non-correct finalized outcomes. Pending and uncertain outcomes are separate. Bootstrap uses 2,000 question-cluster resamples and 95% percentile intervals, with no interval below five eligible questions. See analysis.json for sample sizes, excluded pairs, seeds and sensitivity results.', '', *['- '+x for x in analysis['limitations']], '', 'No model-written interpretation is included. Negative and uncertain findings are retained.', ''])


def export_run(store, run_id):
    run = store.run(run_id)
    protocol = store.protocol(run['protocol_id'])['protocol']
    records = store.records(run_id)
    analysis = analyze(protocol, records)
    public_run = {k:run[k] for k in ['id','state','simulation','created','updated','reserved','spent','blocked_reason']}
    files = {'protocol.json':canonical(protocol).encode(), 'dataset.json':canonical(protocol['dataset']).encode(), 'run.json':canonical(public_run).encode(), 'records.json':canonical(records).encode(), 'analysis.json':canonical(analysis).encode(), 'report.md':report(analysis).encode()}
    flat = [{'request_id':r['id'], 'model':r['key'][0], 'question_id':r['key'][1], 'role':r['key'][2], 'frame':r['key'][3], 'repeat':r['key'][4], 'status':r['score']['status'], 'answer':r['score']['normalized'], 'correct':r['score']['correct'], 'simulation':protocol['simulation']} for r in analysis['records']]
    files['scores.csv'] = csv_bytes(flat, ['request_id','model','question_id','role','frame','repeat','status','answer','correct','simulation'])
    files['summaries.csv'] = csv_bytes([{'dimension':r['dimension'],'value':r['value'],**r['counts']} for r in analysis['breakdowns']], ['dimension','value',*analysis['summary']['counts']])
    files['manifest.json'] = canonical({'schema_version':1, 'format':'masklab-evidence', 'simulation':protocol['simulation'], 'protocol_hash':protocol['hash'], 'files':{k:{'sha256':digest(v),'size':len(v)} for k,v in files.items()}}).encode()
    out = io.BytesIO()
    # Low compression avoids extreme expansion ratios in valid repeated-prompt archives.
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for name, data in files.items():
            z.writestr(name, data)
    result = out.getvalue()
    if len(result) > MAX_COMPRESSED or sum(map(len, files.values())) > MAX_EXPANDED:
        raise ValueError('Export exceeds portable archive limits; inspect locally')
    return result


def _import_archive(raw):
    if len(raw) > MAX_COMPRESSED:
        raise ValueError('Archive exceeds 25 MiB')
    files = {}; expanded = 0
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            entries = z.infolist()
            if len(entries) > 5000:
                raise ValueError('Too many archive entries')
            for entry in entries:
                p = PurePosixPath(entry.filename)
                mode = entry.external_attr >> 16
                if entry.filename in files or p.is_absolute() or '..' in p.parts or '\\' in entry.filename or str(p) != entry.filename or len(p.parts) != 1 or entry.is_dir() or entry.flag_bits & 1 or stat.S_ISLNK(mode) or mode & 0o111:
                    raise ValueError('Unsafe/duplicate/executable archive entry')
                expanded += entry.file_size
                if expanded > MAX_EXPANDED or entry.file_size > MAX_EXPANDED or entry.file_size > max(1024*1024, entry.compress_size*200):
                    raise ValueError('Archive expansion limit exceeded')
                files[entry.filename] = z.read(entry)
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError) as e:
        raise ValueError('Invalid archive') from e
    expected = {'manifest.json','protocol.json','dataset.json','run.json','records.json','analysis.json','report.md','scores.csv','summaries.csv'}
    if set(files) != expected:
        raise ValueError('Archive must contain the exact v1 evidence file set')
    manifest = strict_json(files['manifest.json'])
    if manifest.get('schema_version') != 1 or manifest.get('format') != 'masklab-evidence' or set(manifest.get('files',{})) != expected-{'manifest.json'}:
        raise ValueError('Invalid manifest/schema')
    for name, info in manifest['files'].items():
        if info != {'sha256':digest(files[name]),'size':len(files[name])}:
            raise ValueError('Archive hash/size mismatch: '+name)
    protocol = strict_json(files['protocol.json'])
    cfg = ProtocolConfig.model_validate(protocol['config'])
    dataset = Dataset.model_validate(strict_json(files['dataset.json']))
    rebuilt = render_protocol(dataset,cfg,protocol['source_hash'])
    if protocol != rebuilt or manifest['protocol_hash'] != protocol['hash'] or manifest['simulation'] is not protocol['simulation']:
        raise ValueError('Protocol/dataset/hash consistency failed')
    records = strict_json(files['records.json'])
    if not isinstance(records,list) or len(records) != protocol['request_count'] or len({r.get('id') for r in records}) != len(records):
        raise ValueError('Invalid record count/IDs')
    attempt_ids = set()
    run_ids = set()
    for i, r in enumerate(records):
        if set(r) != {'id','run_id','position','body','state','attempts'} or r['position'] != i or r['body'] != protocol['requests'][i] or r['state'] not in ('PENDING','IN_FLIGHT','SUCCEEDED','FAILED','UNCERTAIN'):
            raise ValueError('Invalid rendered request record')
        run_ids.add(r['run_id'])
        if len(r['attempts']) > 2:
            raise ValueError('Too many attempts')
        for ordinal, a in enumerate(r['attempts'],1):
            if set(a) != {'id','request_id','ordinal','state','started','ended','body'} or a['id'] in attempt_ids or a['request_id'] != r['id'] or a['ordinal'] != ordinal or a['state'] not in ('IN_FLIGHT','SUCCEEDED','FAILED','UNCERTAIN'):
                raise ValueError('Invalid attempt provenance')
            if a['body'].get('simulation') is not protocol['simulation']:
                raise ValueError('Evidence kind mismatch')
            allowed = {'reserve_usd','cost_state','simulation','final_text','refused','usage','provider_request_id','serving_revision','endpoint','raw_metadata','cost_usd','error_code','duration_ms','recovered'}
            if set(a['body']) - allowed or len(canonical(a['body']).encode()) > 2*1024*1024:
                raise ValueError('Unsafe response metadata')
            attempt_ids.add(a['id'])
    if len(run_ids) != 1:
        raise ValueError('Cross-run records are not permitted')
    analysis = strict_json(files['analysis.json'])
    if analysis != analyze(protocol,records):
        raise ValueError('Scored evidence differs from deterministic reanalysis')
    return {'schema_version':1,'manifest':manifest,'protocol':protocol,'records':records,'analysis':analysis,'run':strict_json(files['run.json']),'source_archive_hash':digest(raw),'inspection_only':True}


def import_archive(raw):
    try:
        return _import_archive(raw)
    except (KeyError, TypeError, AttributeError, IndexError, RecursionError, OverflowError) as exc:
        raise ValueError("Malformed archive schema") from exc


# Public display derivative; original portable archives remain immutable.
import hashlib
import re
from datetime import datetime
# Operator requested this specific day's timestamps, not a rolling redaction rule.
STAMP = re.compile(r'2026-10-28T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})')

PUBLIC_REDACTION_START = datetime.fromisoformat('2026-10-28T04:00:00+00:00')
PUBLIC_REDACTION_END = datetime.fromisoformat('2026-10-28T21:00:00+00:00')

def public_redacted_archive(original):
    files = {}
    count = 0
    with zipfile.ZipFile(io.BytesIO(original)) as z:
        for name in z.namelist():
            if name == 'manifest.json':
                continue
            textual_redactions = [0]
            def replace_stamp(match):
                stamp = datetime.fromisoformat(match.group().replace('Z', '+00:00'))
                if PUBLIC_REDACTION_START <= stamp < PUBLIC_REDACTION_END:
                    textual_redactions[0] += 1
                    return '[timestamp omitted for public display]'
                return match.group()
            text = STAMP.sub(replace_stamp, z.read(name).decode('utf-8'))
            n = textual_redactions[0]
            if name.endswith('.json'):
                value = json.loads(text)
                numeric_redactions = [0]
                def redact_numeric(node):
                    if isinstance(node, dict):
                        for field, item in node.items():
                            if field == 'provider_created' and type(item) in (int, float) and PUBLIC_REDACTION_START.timestamp() <= item < PUBLIC_REDACTION_END.timestamp():
                                node[field] = '[timestamp omitted for public display]'
                                numeric_redactions[0] += 1
                            else:
                                redact_numeric(item)
                    elif isinstance(node, list):
                        for item in node:
                            redact_numeric(item)
                redact_numeric(value)
                if numeric_redactions[0]:
                    text = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
                    n += numeric_redactions[0]
            files[name] = text.encode()
            count += n
    manifest = {'format': 'masklab-public-redacted-evidence', 'schema_version': 1,
                'inspection_only': True, 'original_archive_sha256': hashlib.sha256(original).hexdigest(),
                'redaction': {'scope': 'operator-selected day', 'timestamp_occurrences': count,
                              'replacement': '[timestamp omitted for public display]',
                              'private_original_preserved': True},
                'files': {name: {'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw)} for name, raw in files.items()}}
    files['manifest.json'] = json.dumps(manifest, indent=2).encode()
    files['PUBLIC-COPY.txt'] = b'Public redacted derivative, not the original MaskLab portable archive. Timestamp fields were redacted. Original protocol, answers, scores and negative outcomes retained. Original private archive preserved. Not supported by the standard archive importer.\n'
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for name, raw in files.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, raw)
    return out.getvalue()

