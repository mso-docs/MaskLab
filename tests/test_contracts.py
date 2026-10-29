"""TASK-001/002 • independent boundary and immutability checks TEST-001/004–008."""
import json
import sqlite3
import pytest
from masklab.contracts import Dataset, Question, ProtocolConfig, Role, load_dataset, render_protocol, digest


def q(**kw):
    return Question(id='q1',text='What is 1+1?',answer_type='exact_decimal',expected='2',incorrect_belief='3',category='arithmetic',split='development',**kw)

@pytest.mark.parametrize('value',['NaN','Infinity','1,000','2+2','=2','1e99999'])
def test_decimal_rejects_nonfinite_and_executable(value):
    d=q().model_dump();d['expected']=value
    with pytest.raises(ValueError):Question.model_validate(d)

@pytest.mark.parametrize('field,value',[('id','=cmd'),('expected','3'),('category','=SUM(A1)'),('split','both')])
def test_invalid_fields(field,value):
    d=q().model_dump();d[field]=value
    with pytest.raises(ValueError):Question.model_validate(d)


def test_json_csv_roundtrip_and_diagnostics():
    data=Dataset(name='One',questions=[q()])
    assert load_dataset(json.dumps(data.model_dump()).encode(),'json')==data
    csv=b'id,text,answer_type,expected,incorrect_belief,category,split,choices\nq1,What is 1+1?,exact_decimal,2,3,arithmetic,development,\n'
    assert load_dataset(csv,'csv').questions==[q()]
    with pytest.raises(ValueError,match='CSV row 2'):
        load_dataset(csv.replace(b',2,3,',b',NaN,3,'),'csv')
    with pytest.raises(ValueError):load_dataset(b'\xff','json')
    with pytest.raises(ValueError):load_dataset(b'x'*(5*1024*1024+1),'json')
    with pytest.raises(ValueError):load_dataset(b'{"name":"a","name":"b"}','json')
    with pytest.raises(ValueError):load_dataset(b'id,id\nx,x','csv')


def test_unique_disjoint_ids():
    with pytest.raises(ValueError,match='Duplicate/overlapping'):
        Dataset(name='Overlap',questions=[q(),q().model_copy(update={'split':'evaluation'})])


def test_choice_validation():
    v=q().model_dump();v.update(answer_type='single_choice',choices={'A':'Two','B':'Three'},expected='a',incorrect_belief='B')
    assert Question.model_validate(v).expected=='A'
    v['incorrect_belief']='C'
    with pytest.raises(ValueError):Question.model_validate(v)

@pytest.mark.parametrize('kw',[{'roles':[Role(id='expert',instruction='hello')]},{'roles':[Role(id='neutral',instruction='hello')]},{'repetitions':21},{'concurrency':5},{'models':['unverified/live']},{'max_output_tokens':513},{'frames':['absent','absent']},{'budget_usd':'11'}])
def test_protocol_limits(kw):
    with pytest.raises(ValueError):ProtocolConfig(**kw)


def test_matrix_pairing_order_and_hash(dataset):
    p=render_protocol(dataset,ProtocolConfig(),digest(b'source'))
    assert p['request_count']==648 # 24 x 3 x 3 x 3 x 1, independently specified
    assert len({tuple(r['key']) for r in p['requests']})==648
    assert p==render_protocol(dataset,ProtocolConfig(),digest(b'source'))
    neutral=next(r for r in p['requests'] if r['key'][1:]==['syn-001','neutral','absent',0])
    skeptic=next(r for r in p['requests'] if r['key'][1:]==['syn-001','skeptic','absent',0])
    assert neutral['messages'][0]==skeptic['messages'][0]
    assert neutral['messages'][-1]==skeptic['messages'][-1]
    assert len(neutral['messages'])==2 and len(skeptic['messages'])==3
    assert all('expected' not in r for r in p['requests'])
    with pytest.raises(ValueError):render_protocol(dataset,ProtocolConfig(repetitions=20,roles=[Role(id='neutral',instruction=''),*[Role(id=f'r{i}',instruction='x') for i in range(7)]]),digest(b'x'))
    with pytest.raises(ValueError):render_protocol(dataset,ProtocolConfig(),digest(b'x'),limits=10)


def test_store_reopen_archive_immutability_and_backup(store,dataset,tmp_path):
    s=store.create_study('Original')
    d=store.add_dataset(s['id'],dataset.model_dump(),b'raw')
    protocol=render_protocol(dataset,ProtocolConfig(),d['source_hash'])
    p=store.freeze(s['id'],protocol)
    dataset.questions[0].text='changed after freeze'
    assert store.protocol(p['id'])['protocol']['dataset']['questions'][0]['text']!=dataset.questions[0].text
    with pytest.raises(sqlite3.IntegrityError),store.tx() as db:
        db.execute('UPDATE protocols SET hash=? WHERE id=?',(d['hash'],p['id']))
    with store.tx() as db:db.execute('UPDATE studies SET archived=1 WHERE id=?',(s['id'],))
    with pytest.raises(ValueError,match='Archived'):store.create_run(p['id'],'archived-key')
    assert store.protocol(p['id'])['protocol']==protocol
    path=store.backup(tmp_path/'backup.sqlite3')
    from masklab.store import Store
    assert Store(path).protocol(p['id'])['protocol']==protocol
    with store.tx() as db:db.execute('PRAGMA user_version=99')
    with pytest.raises(ValueError,match='newer'):Store(store.path)
