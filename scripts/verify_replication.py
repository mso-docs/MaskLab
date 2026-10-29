"""TASK-012 / REQ-005/024: independent text-based replication key checks.
Uses Fraction arithmetic and exhaustive permutations; never imports the generator.
"""
import collections,hashlib,itertools,json,re
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

def check_question(q,info):
 text=q['text'];arithmetic=logic=0
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

 return arithmetic,logic

def verify():
 folder=Path('data/replication-060-v2');data=json.loads((folder/'questions.json').read_text());m=json.loads((folder/'manifest.json').read_text());plan=json.loads((folder/'run-plan.json').read_text())
 prior=json.loads(Path('data/study-draft-150/questions.json').read_text())
 normal=lambda s:' '.join(s.split()).casefold()
 canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
 assert hashlib.sha256(canonical(data)).hexdigest()==m['dataset_hash']==plan['dataset_hash']
 assert hashlib.sha256((folder/'questions.json').read_bytes()).hexdigest()==m['source_bytes_sha256']
 assert len(data['questions'])==60 and len({q['id'] for q in data['questions']})==60
 texts={normal(q['text']) for q in data['questions']};assert len(texts)==60
 assert not texts&{normal(q['text']) for q in prior['questions']}
 assert not {q['id'] for q in data['questions']}&{q['id'] for q in prior['questions']}
 counts=collections.Counter();families=collections.Counter();targets=collections.Counter()
 for q in data['questions']:
  assert q['split']=='evaluation' and q['expected']!=q['incorrect_belief']
  info=m['questions'][q['id']];assert info['operator_review']=='PENDING'
  if q['answer_type']=='single_choice':
   assert q['expected'] in q['choices'] and q['incorrect_belief'] in q['choices']
   assert len(set(q['choices'].values()))==len(q['choices'])
   targets[info['target_position']]+=1
  else:families[info['family']]+=1
  a,l=check_question(q,info);counts['independent_arithmetic_checks']+=a;counts['independent_logic_checks']+=l
 assert counts=={'independent_arithmetic_checks':30,'independent_logic_checks':30}
 assert len(families)==5 and set(families.values())=={6}
 assert len(targets)==5 and set(targets.values())=={6}
 frozen=json.loads(Path('artifacts/mixed-study/frozen-choices.json').read_text())['config']
 assert {k:v for k,v in plan['config'].items() if k!='split'}=={k:v for k,v in frozen.items() if k!='split'}
 assert plan['request_count']==60*3*3*3==1620
 assert Decimal(plan['conservative_reservation_usd'])<Decimal(plan['config']['budget_usd'])<=2
 return {'status':'MECHANICAL_CHECKS_PASS_OPERATOR_REVIEW_PENDING',**counts,'exact_text_overlap':0,'id_overlap':0,'same_template_families':True,'settings_unchanged':True,'evaluation_only':True,'provider_calls':0}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
