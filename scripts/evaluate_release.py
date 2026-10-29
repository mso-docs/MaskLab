"""TASK-012 / REQ-024: independent black-box evaluator (no application imports).
Reads a portable archive, checks hashes, recomputes basic counts using Decimal/JSON,
and checks the frozen paired matrix. Run after the browser exports an actual run.
"""
import hashlib
import io
import json
import sys
import zipfile
from decimal import Decimal
from pathlib import Path


def evaluate(path):
    raw=Path(path).read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files={n:z.read(n) for n in z.namelist()}
    manifest=json.loads(files['manifest.json'])
    for name,meta in manifest['files'].items():
        assert hashlib.sha256(files[name]).hexdigest()==meta['sha256'],name
        assert len(files[name])==meta['size'],name
    protocol=json.loads(files['protocol.json']);records=json.loads(files['records.json']);analysis=json.loads(files['analysis.json'])
    assert protocol['simulation'] is True and manifest['simulation'] is True and analysis['simulation'] is True
    assert 'NOT NEMOTRON EVIDENCE' in files['report.md'].decode()
    questions={q['id']:q for q in protocol['dataset']['questions']}
    total=len(questions) * len(protocol['config']['roles']) * len(protocol['config']['frames']) * protocol['config']['repetitions'] * len(protocol['config']['models'])
    assert len(records)==total==protocol['request_count']
    expected_correct=0;finalized=0;valid=0
    for record in records:
        if record['state'] not in ('SUCCEEDED','FAILED'):continue
        finalized+=1
        if record['state']=='FAILED':continue
        attempt=record['attempts'][-1]['body']
        if attempt.get('refused'):continue
        try:
            value=json.loads(attempt['final_text'])
            assert set(value)=={'answer'} and isinstance(value['answer'],str)
            q=questions[record['body']['key'][1]]
            answer=value['answer']
            if q['answer_type']=='exact_decimal':
                actual=Decimal(''.join(answer.split()));expected=Decimal(q['expected'])
                assert actual.is_finite()
            else:
                actual=answer.strip().upper();expected=q['expected'];assert actual in q['choices']
            valid+=1;expected_correct+=actual==expected
        except (ValueError,KeyError,AssertionError):continue
    counts=analysis['summary']['counts']
    assert counts['correct']==expected_correct and counts['finalized']==finalized and counts['valid']==valid
    for name,n,d in [('all_attempt_correctness',expected_correct,finalized),('valid_accuracy',expected_correct,valid)]:
        assert analysis['summary'][name]['numerator']==n and analysis['summary'][name]['denominator']==d
    # In the bundled browser study, the provider always emits 5. Only syn-001 has expected 5.
    assert expected_correct==9 and finalized==216 and valid==216,(expected_correct,finalized,valid)
    return {'status':'PASS','archive_sha256':hashlib.sha256(raw).hexdigest(),'evidence':'SIMULATION ONLY','independently_recomputed':{'scheduled':total,'correct':expected_correct,'finalized':finalized,'valid':valid},'limitations':'Does not verify live inference, hosting, model behavior or owner acceptance.'}

if __name__=='__main__':
    print(json.dumps(evaluate(sys.argv[1]),indent=2))
