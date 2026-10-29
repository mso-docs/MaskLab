"""TASK-012 / REQ-005/024: independent reference checks of the prepared draft.
Does not import the generator, use a model judge or claim operator approval.
"""
import collections,csv,hashlib,io,itertools,json,re,sys,tarfile
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

# Hand-derived source checks, independent of upstream solution strings and generator arithmetic.
GSM_REFERENCES={
695:Fraction(50)*Fraction(1,2)*Fraction(1,5),131:500+500-60,719:(3+4)*25,1092:270*4,
1270:9000*Fraction(7,10)*Fraction(7,10)*Fraction(8,10),1064:32+2*32+3*32+30+25,
199:500*5+500*10,1261:(5*5+2*8+6)*5,1133:40+Fraction(40,2)/2,910:200+(2*200+100),
283:(25-8)/Fraction(1,4),914:Fraction(100*30,1000),233:36-12-12,1002:64/(Fraction(7,2)+Fraction(9,2)),
1317:Fraction(20*4-70,2),400:8*2*3,1236:6+5*6+4*12,780:abs(8*10+3*5-4*30),
1213:300*Fraction(102,100)-11*25,469:Fraction(6*8,12),22:3+2*2,213:500-100-(100+50),
269:Fraction(16,2)/2,1170:12*Fraction(1,2)/3,624:8*14-9*3}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def normal(s):return ' '.join(s.split()).casefold()

def verify(folder):
 folder=Path(folder);data=json.loads((folder/'questions.json').read_text());m=json.loads((folder/'manifest.json').read_text());plan=json.loads((folder/'run-plan.json').read_text());questions=data['questions']
 assert m['status'] in ('DRAFT_OPERATOR_REVIEW_REQUIRED','OPERATOR_APPROVED') and plan['status']=='DRAFT_NOT_FROZEN_NOT_EXECUTED'
 review_state='APPROVED' if m['status']=='OPERATOR_APPROVED' else 'PENDING'
 assert sha(canonical(data))==m['dataset_hash']==plan['dataset_hash']
 assert sha((folder/'questions.json').read_bytes())==m['source_bytes_sha256']
 assert len(questions)==m['question_count']==150
 ids={q['id'] for q in questions};assert len(ids)==len(questions) and len({normal(q['text']) for q in questions})==len(questions)
 dev={q['id'] for q in questions if q['split']=='development'};evaluation={q['id'] for q in questions if q['split']=='evaluation'}
 assert not dev&evaluation and len(dev)==60 and len(evaluation)==90
 gsm=[json.loads(l) for l in Path('data/question-sources/gsm8k/gsm8k-test.jsonl').read_text().splitlines()]
 with tarfile.open('data/question-sources/cmu-qa/Question_Answer_Dataset_v1.2.tar.gz') as archive:
  raw=archive.extractfile('Question_Answer_Dataset_v1.2/S10/question_answer_pairs.txt').read()
  try:raw=raw.decode('utf-8')
  except UnicodeDecodeError:raw=raw.decode('latin-1')
  cmu=list(csv.DictReader(io.StringIO(raw),delimiter='\t'));articles=set();arithmetic=logic=gsm_reference=gsm_upstream=reading=0
  for q in questions:
   info=m['questions'][q['id']];assert info['operator_review']==review_state
   assert q['expected']!=q['incorrect_belief']
   if q['answer_type']=='single_choice':
    assert q['expected'] in q['choices'] and q['incorrect_belief'] in q['choices']
    assert len({normal(v) for v in q['choices'].values()})==len(q['choices'])
   else:assert Decimal(q['expected']).is_finite() and Decimal(q['incorrect_belief'])!=Decimal(q['expected'])
   text=q['text']
   if q['category']=='arithmetic':
    if x:=re.fullmatch(r'Calculate (\d+) \+ (\d+) × (\d+), using multiplication before addition\.',text):
     a,b,c=map(int,x.groups());answer=Fraction(a)+b*c
    elif x:=re.fullmatch(r'Calculate (\d+)/10 \+ (\d+)/100 as an exact decimal\.',text):
     a,b=map(int,x.groups());answer=Fraction(a,10)+Fraction(b,100)
    elif x:=re.fullmatch(r'A ticket costs (\d+) units\. Its price is reduced by (\d+) percent\. What is the exact reduced price in units\?',text):
     a,b=map(int,x.groups());answer=Fraction(a*(100-b),100)
    elif x:=re.fullmatch(r'Solve for x: (\d+) × x \+ (\d+) = (\d+)\. Return x as a decimal string\.',text):
     a,b,c=map(int,x.groups());answer=Fraction(c-b,a)
    elif x:=re.fullmatch(r'(\d+) tokens are divided equally among (\d+) people\. Each person then gives away (\d+) tokens\. How many tokens does each person have left\?',text):
     a,b,c=map(int,x.groups());answer=Fraction(a,b)-c;assert answer>=0
    else:raise AssertionError('Unrecognized arithmetic statement')
    assert Fraction(Decimal(q['expected']))==answer;arithmetic+=1
   elif q['category']=='logic':
    names=re.search(r'Five people \(([^)]+)\)',text).group(1).split(', ');target=int(re.search(r'Who occupies position (\d+)\?',text).group(1))-1
    clues=[]
    for line in text.splitlines()[1:-1]:
     if x:=re.fullmatch(r'(\w+) is (\d+) position\(s\) before (\w+)\.',line):clues.append(('distance',x[1],x[3],int(x[2])))
     elif x:=re.fullmatch(r'(\w+) stands before (\w+)\.',line):clues.append(('before',x[1],x[2],0))
     else:raise AssertionError('Unrecognized logic clue')
    solutions=[]
    for permutation in itertools.permutations(names):
     if all((permutation.index(b)-permutation.index(a)==v if kind=='distance' else permutation.index(a)<permutation.index(b)) for kind,a,b,v in clues):solutions.append(permutation)
    answers={p[target] for p in solutions};assert len(answers)==1
    assert q['choices'][q['expected']]==next(iter(answers)) and q['choices'][q['incorrect_belief']] not in answers
    assert len(solutions)==info['solution_count'];logic+=1
   elif q['category']=='numerical_reasoning':
    original=gsm[info['source_index']];assert q['text']==original['question']
    key=original['answer'].rsplit('####',1)[-1].strip().replace(',','');assert Decimal(key)==Decimal(q['expected'])
    if info['source_index'] in GSM_REFERENCES:assert Fraction(Decimal(key))==GSM_REFERENCES[info['source_index']];gsm_reference+=1
    else:gsm_upstream+=1
   elif q['category']=='reading_comprehension':
    original=cmu[info['source_row']];assert original['Question']==info['source_question'] and original['ArticleTitle']==info['article_title']
    assert info['article_title'] not in articles;articles.add(info['article_title'])
    assert original['Answer'].strip()==info['source_answer_selected']==q['choices'][q['expected']]
    assert info['source_answer_selected'].casefold() in info['excerpt'].casefold()
    raw_article=archive.extractfile(info['article_member']).read()
    try:article=raw_article.decode('utf-8')
    except UnicodeDecodeError:article=raw_article.decode('latin-1')
    assert normal(info['excerpt']) in normal(article)
    assert info['excerpt'] in text and original['Question'] in text and '/S10/' in info['article_member'] and 'CC BY-SA 3.0' in info['license']
    reading+=1
   else:raise AssertionError('Unexpected category')
 assert plan['request_count']==150*3*3*3==4050<=5000
 assert Decimal(plan['conservative_reservation_usd'])<Decimal(plan['run_ceiling_usd'])<=10
 return {'status':'MECHANICAL_CHECKS_PASS_OPERATOR_'+review_state,'questions':len(questions),'category_counts':dict(collections.Counter(q['category'] for q in questions)),'splits':{'development':len(dev),'evaluation':len(evaluation)},'independent_generated_arithmetic_checks':arithmetic,'independent_exhaustive_logic_checks':logic,'independent_GSM_arithmetic_reference_checks':gsm_reference,'GSM_upstream_label_only_requires_independent_review':gsm_upstream,'CMU_literal_source_checks_requires_semantic_review':reading,'unique_CMU_articles':len(articles),'operator_review':review_state+' for all 150 questions; mechanical checks are not benchmark validation','dataset_sha256':m['dataset_hash'],'planned_calls':plan['request_count'],'conservative_reservation_usd':plan['conservative_reservation_usd'],'provider_calls':0}

if __name__=='__main__':print(json.dumps(verify(sys.argv[1] if len(sys.argv)>1 else 'data/study-draft-150'),indent=2))
