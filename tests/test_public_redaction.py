"""TASK-010/012, REQ-018–020: public redaction boundary and original integrity."""
import hashlib
import io
import json
import zipfile
from masklab.portable import public_redacted_archive


def test_public_copy_preserves_evening_other_days_and_original_bytes():
    out=io.BytesIO()
    payload={'times':['2026-10-28T20:59:59Z','2026-10-28T16:59:59-04:00','2026-10-28T21:00:00Z','2026-10-29T01:00:00Z','2026-10-27T12:00:00Z'],'answer':'B','correct':False,'raw_metadata':{'provider_created':1793188800},'evening_metadata':{'provider_created':1793221200}}
    with zipfile.ZipFile(out,'w') as z:z.writestr('records.json',json.dumps(payload))
    original=out.getvalue();original_hash=hashlib.sha256(original).hexdigest()
    with zipfile.ZipFile(io.BytesIO(public_redacted_archive(original))) as z:
        record=json.loads(z.read('records.json'));m=json.loads(z.read('manifest.json'))
        assert record['times'][:2]==['[timestamp omitted for public display]']*2
        assert record['times'][2:]==payload['times'][2:]
        assert record['raw_metadata']['provider_created']=='[timestamp omitted for public display]'
        assert record['evening_metadata']['provider_created']==1793221200
        assert record['answer']=='B' and record['correct'] is False
        assert m['original_archive_sha256']==original_hash
        assert m['format']=='masklab-public-redacted-evidence'
        assert m['redaction']['timestamp_occurrences']==3
        assert m['files']['records.json']['sha256']==hashlib.sha256(z.read('records.json')).hexdigest()
        assert all(x.date_time==(1980,1,1,0,0,0) for x in z.infolist())
    assert hashlib.sha256(original).hexdigest()==original_hash
