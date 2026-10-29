"""TASK-002/007/012; REQ-004/005/007/024: broad draft, no inference or approval."""
import collections,csv,io,json,random,re,tarfile
from pathlib import Path
from decimal import Decimal
import prepare_study_questions as g
from replication_curations import READING,CONTEXT_PHRASES
from masklab.contracts import Dataset,ProtocolConfig,digest,render_protocol
from masklab.portable import safe_cell
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/replication-mixed-150-v2';SEED=2810202602

def normal(s):return ' '.join(s.split()).casefold()
def decode(raw):
 try:return raw.decode('utf-8')
 except UnicodeDecodeError:return raw.decode('latin-1')
def prepare():
 prior=json.loads((ROOT/'data/study-draft-150/questions.json').read_text());old_meta=json.loads((ROOT/'data/study-draft-150/manifest.json').read_text())
 old_text={normal(q['text']) for q in prior['questions']};old_ids={q['id'] for q in prior['questions']};old_articles={v.get('article_title') for v in old_meta['questions'].values() if v.get('article_title')}
 questions=[];metadata={}
 def add(q,info):
  q={**q,'id':'rep2-'+q['id'],'split':'evaluation'};questions.append(q);metadata[q['id']]={**info,'operator_review':'PENDING'}
 g.SEED=SEED
 pool,meta,_=g.gsm(100)
 for q in [q for q in pool if q['id'] not in old_ids][:38]:add(q,meta[q['id']])
 pool,meta=g.arithmetic(250)
 for family,n in enumerate([8,8,8,7,7]):
  candidates=[q for q in pool if meta[q['id']]['family']==f'arithmetic-{family}' and normal(q['text']) not in old_text and Decimal(q['expected'])>=0]
  random.Random(SEED+family).shuffle(candidates)
  for q in candidates[:n]:add(q,meta[q['id']])
 pool,meta=g.logic(250)
 for position,n in enumerate([8,8,7,7,7],1):
  candidates=[q for q in pool if meta[q['id']]['target_position']==position and normal(q['text']) not in old_text]
  random.Random(SEED+100+position).shuffle(candidates)
  for q in candidates[:n]:add(q,meta[q['id']])
 archive_path=ROOT/'data/question-sources/cmu-qa/Question_Answer_Dataset_v1.2.tar.gz';upstream=json.loads((archive_path.parent/'upstream.json').read_text());assert digest(archive_path.read_bytes())==upstream['sha256']
 with tarfile.open(archive_path) as z:
  prefix='Question_Answer_Dataset_v1.2/S10/';rows=list(csv.DictReader(io.StringIO(decode(z.extractfile(prefix+'question_answer_pairs.txt').read())),delimiter='\t'));articles=set()
  for i,(answer,others) in READING.items():
   row=rows[i];title=row['ArticleTitle'];assert title not in articles;articles.add(title)
   assert normal(answer) in normal(row['Answer']),('answer adaptation not in source answer',i)
   assert not any(normal(row['Question'])==normal(v.get('source_question','')) for v in old_meta['questions'].values())
   assert re.fullmatch(r'data/set\d+/a\d+',row['ArticleFile'])
   member=prefix+row['ArticleFile']+'.txt.clean'
   try:article=decode(z.extractfile(member).read())
   except KeyError:member=prefix+row['ArticleFile']+'.txt';article=decode(z.extractfile(member).read())
   text=' '.join(article.split());matches=list(re.finditer(re.escape(answer),text,re.I));assert matches,('literal answer missing',i,answer)
   words={w for w in re.findall(r'\w+',row['Question'].casefold()) if len(w)>3 and w not in {'what','where','when','which','many','does','have','were','there','their','with'}}
   spans=[]
   for match in matches:
    start=max(0,text.rfind('. ',0,max(0,match.start()-150))+2);end=text.find('. ',match.end()+100);end=len(text) if end<0 else end+1
    excerpt=text[start:end]
    if 20<=len(excerpt)<=1800:spans.append((len(words&set(re.findall(r'\w+',excerpt.casefold()))),excerpt))
   assert spans,('excerpt bounds',i);excerpt=max(spans,key=lambda v:v[0])[1]
   if i in CONTEXT_PHRASES:
    anchor=text.casefold().index(CONTEXT_PHRASES[i].casefold());start=max(0,text.rfind('. ',0,anchor)+2);end=text.find('. ',anchor+len(CONTEXT_PHRASES[i])+80);end=len(text) if end<0 else end+1;excerpt=text[start:end]
    assert 20<=len(excerpt)<=1800 and answer.casefold() in excerpt.casefold()
   q=g.choice_question({'id':f'cmu-s10-{i:04d}','text':f'Use only this archived excerpt from the article "{title.replace("_"," ")}". Answer according to the excerpt, not current-world updates.\n\n{excerpt}\n\nQuestion: {row["Question"]}','category':'reading_comprehension','split':'evaluation'},answer,others,len(articles)-1)
   add(q,{'origin':'CMU/Pittsburgh QA 1.2 S10','license':'CC BY-SA 3.0; NOT MIT','source_row':i,'source_question':row['Question'],'source_original_answer':row['Answer'],'source_all_answers':sorted({r['Answer'] for r in rows if r['ArticleTitle']==title and normal(r['Question'])==normal(row['Question'])}),'source_answer_selected':answer,'article_title':title,'article_member':member,'excerpt':excerpt,'article_shared_with_first_study':title in old_articles,'source_archive_sha256':upstream['sha256'],'source_url':upstream['source_url'],'adaptation':'Answer span extracted from original answer and archived article; new labeled distractors; context chosen by question-word overlap. Semantic review required.','mechanical_check':'Literal span/source checks only; not semantic validation'})
 assert len(questions)==150 and len({normal(q['text']) for q in questions})==150
 assert not {normal(q['text']) for q in questions}&old_text
 assert not {q['id'] for q in questions}&old_ids
 assert not {q['id'].removeprefix('rep2-') for q in questions if q['category'] in ('numerical_reasoning','reading_comprehension')}&old_ids
 limits='DRAFT: operator review of all 150 new keys, wording, distractors and source semantics PENDING. Broad fresh-question replication with frozen prior settings; all evaluation-only. Exact question text and source-row IDs do not overlap the first study. Generated template families recur; some CMU articles recur and public benchmark training exposure is unknown. Not a source-independent or representative benchmark. No model results exist for this set.'+'\n\n'+prior['limitations'].split('\n\n',1)[1]
 data=Dataset.model_validate({'name':'DRAFT • Broad replication — 150 fresh mixed questions','limitations':limits,'questions':questions});raw=(json.dumps(data.model_dump(),indent=2,ensure_ascii=False)+'\n').encode()
 if OUT.exists():assert (OUT/'questions.json').read_bytes()==raw,'Refusing to overwrite differing replication';return {'status':'EXISTING_DRAFT_PRESERVED'}
 OUT.mkdir();(OUT/'questions.json').write_bytes(raw)
 shared=sum(v.get('article_shared_with_first_study',False) for v in metadata.values())
 manifest={'status':'DRAFT_OPERATOR_REVIEW_REQUIRED','dataset_hash':digest(data.model_dump()),'source_bytes_sha256':digest(raw),'prior_dataset_hash':digest(prior),'generator_seed':SEED,'question_count':150,'category_counts':dict(collections.Counter(q['category'] for q in questions)),'source_overlap':{'exact_question_text':0,'source_question_ids':0,'cmu_articles_shared':shared,'cmu_articles_new':37-shared,'generated_template_families':'shared'},'questions':metadata,'provider_calls':0};(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 with (OUT/'review.csv').open('w',newline='') as f:
  columns=['id','category','split','question','choices','expected','expected_text','false_alternative','false_text','source','license','operator_review','review_notes'];w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
  for q in questions:
   info=metadata[q['id']];values={'id':q['id'],'category':q['category'],'split':q['split'],'question':q['text'],'choices':json.dumps(q['choices'],ensure_ascii=False),'expected':q['expected'],'expected_text':q['choices'].get(q['expected'],q['expected']),'false_alternative':q['incorrect_belief'],'false_text':q['choices'].get(q['incorrect_belief'],q['incorrect_belief']),'source':info.get('source_url',info.get('origin')),'license':info['license'],'operator_review':'PENDING','review_notes':''};w.writerow({k:safe_cell(v) for k,v in values.items()})
 cfg=ProtocolConfig.model_validate({**json.loads((ROOT/'artifacts/mixed-study/frozen-choices.json').read_text())['config'],'split':'evaluation'});preview=render_protocol(data,cfg,digest(raw));plan={'status':'DRAFT_NOT_FROZEN_NOT_EXECUTED','request_count':preview['request_count'],'conservative_reservation_usd':preview['conservative_cost_usd'],'config':cfg.model_dump(),'dataset_hash':manifest['dataset_hash'],'provider_calls':0,'operator_question_review_required':True};(OUT/'run-plan.json').write_text(json.dumps(plan,indent=2))
 import shutil
 for name in ['LICENSE-gsm8k.txt','ATTRIBUTION-CMU-S10.txt']:shutil.copyfile(ROOT/'data/study-draft-150'/name,OUT/name)
 return {'folder':str(OUT.relative_to(ROOT)),'categories':manifest['category_counts'],'overlap':manifest['source_overlap'],**plan}
if __name__=='__main__':print(json.dumps(prepare(),indent=2))
