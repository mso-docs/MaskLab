"""TASK-012 / REQ-005/024: independent broad-draft checks, no generator/model imports."""
import collections,csv,hashlib,io,json,tarfile
from pathlib import Path
from decimal import Decimal
from fractions import Fraction
from verify_replication import check_question

# Separate arithmetic derivations from the displayed source problems, not upstream solutions.
REFERENCES={556:40+3*40,82:125+4*125-2,1289:11*3+8*4+6*6,1203:60*7-60*3,29:33+2*33+5,1013:Fraction(10000,5)/((10+15)*40),961:70*3+15,897:7-3*(7-5),839:25//5-3,774:Fraction(150*2,75)+6,171:80*8+90*6+3*10,691:125-Fraction(2*20,Fraction(2,5))}
def normal(s):return ' '.join(s.split()).casefold()
def decode(b):
 try:return b.decode('utf8')
 except UnicodeDecodeError:return b.decode('latin1')
def verify():
 root=Path('data/replication-mixed-150-v2');data=json.loads((root/'questions.json').read_text());m=json.loads((root/'manifest.json').read_text());plan=json.loads((root/'run-plan.json').read_text())
 canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
 assert hashlib.sha256(canonical(data)).hexdigest()==m['dataset_hash']==plan['dataset_hash']
 assert hashlib.sha256((root/'questions.json').read_bytes()).hexdigest()==m['source_bytes_sha256']
 prior=json.loads(Path('data/study-draft-150/questions.json').read_text());pm=json.loads(Path('data/study-draft-150/manifest.json').read_text());old_ids={q['id'] for q in prior['questions']};old_text={normal(q['text']) for q in prior['questions']};old_source_q={normal(v.get('source_question','')) for v in pm['questions'].values()};old_articles={v.get('article_title') for v in pm['questions'].values() if v.get('article_title')}
 assert len(data['questions'])==150 and len({q['id'] for q in data['questions']})==150
 assert len({normal(q['text']) for q in data['questions']})==150
 assert not {normal(q['text']) for q in data['questions']}&old_text
 gsm=[json.loads(s) for s in Path('data/question-sources/gsm8k/gsm8k-test.jsonl').read_text().splitlines()]
 checks=collections.Counter();articles=set();overlap=0
 with tarfile.open('data/question-sources/cmu-qa/Question_Answer_Dataset_v1.2.tar.gz') as z:
  rows=list(csv.DictReader(io.StringIO(decode(z.extractfile('Question_Answer_Dataset_v1.2/S10/question_answer_pairs.txt').read())),delimiter='\t'))
  for q in data['questions']:
   info=m['questions'][q['id']];assert info['operator_review']==('APPROVED' if m['status']=='OPERATOR_APPROVED' else 'PENDING') and q['split']=='evaluation'
   assert q['id'] not in old_ids and q['expected']!=q['incorrect_belief']
   if q['answer_type']=='single_choice':
    assert q['expected'] in q['choices'] and q['incorrect_belief'] in q['choices'];assert len(set(q['choices'].values()))==len(q['choices'])
   if q['category'] in ['arithmetic','logic']:
    a,l=check_question(q,info);checks['independent_arithmetic']+=a;checks['independent_exhaustive_logic']+=l
   elif q['category']=='numerical_reasoning':
    assert q['id'].removeprefix('rep2-') not in old_ids
    original=gsm[info['source_index']];assert q['text']==original['question'];assert Decimal(q['expected'])==Decimal(original['answer'].rsplit('####',1)[-1].strip().replace(',',''))
    if info['source_index'] in REFERENCES:assert Fraction(Decimal(q['expected']))==REFERENCES[info['source_index']];checks['independent_GSM_calculations']+=1
    else:checks['GSM_upstream_label_only']+=1
   elif q['category']=='reading_comprehension':
    assert q['id'].removeprefix('rep2-') not in old_ids
    r=rows[info['source_row']];assert r['Question']==info['source_question'] and r['Answer']==info['source_original_answer']
    assert normal(r['Question']) not in old_source_q
    answer=q['choices'][q['expected']];assert normal(answer) in normal(r['Answer'])
    article=decode(z.extractfile(info['article_member']).read());assert normal(info['excerpt']) in normal(article) and normal(answer) in normal(info['excerpt'])
    assert info['excerpt'] in q['text'] and r['Question'] in q['text']
    assert info['article_title'] not in articles;articles.add(info['article_title']);overlap+=info['article_title'] in old_articles
    assert 'CC BY-SA 3.0' in info['license'] and '/S10/' in info['article_member'];checks['CMU_source_span_only']+=1
   else:raise AssertionError('Unexpected category')
 assert checks=={'independent_arithmetic':38,'independent_exhaustive_logic':37,'independent_GSM_calculations':12,'GSM_upstream_label_only':26,'CMU_source_span_only':37}
 assert len(articles)==37 and overlap==22 and len(articles-old_articles)==15
 frozen=json.loads(Path('artifacts/mixed-study/frozen-choices.json').read_text())['config']
 assert {k:v for k,v in plan['config'].items() if k!='split'}=={k:v for k,v in frozen.items() if k!='split'}
 assert plan['request_count']==4050<=5000 and Decimal(plan['conservative_reservation_usd'])<Decimal(plan['config']['budget_usd'])<=2
 assert 'MIT' in data['limitations'] and 'CC BY-SA 3.0' in data['limitations']
 return {'status':'MECHANICAL_CHECKS_PASS_ALL_150_OPERATOR_REVIEWS_'+('APPROVED' if m['status']=='OPERATOR_APPROVED' else 'PENDING'),'dataset_hash':m['dataset_hash'],'checks':dict(checks),'exact_text_overlap':0,'source_question_overlap':0,'CMU_articles_new':15,'CMU_articles_shared':22,'generated_families':'shared','all_evaluation':True,'frozen_settings_retained':True,'request_count':4050,'conservative_reservation_usd':plan['conservative_reservation_usd'],'provider_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
