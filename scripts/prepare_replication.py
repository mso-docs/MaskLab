"""TASK-002/007/012; REQ-004/005/007/024: fresh draft only, no provider calls."""
import collections,csv,json,random
from pathlib import Path
from decimal import Decimal
import prepare_study_questions as generator
from masklab.contracts import Dataset,ProtocolConfig,canonical,digest,render_protocol
from masklab.portable import safe_cell

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/replication-060-v2'
SEED=2810202602

def norm(text):return ' '.join(text.split()).casefold()

def prepare():
 original=json.loads((ROOT/'data/study-draft-150/questions.json').read_text())
 original_text={norm(q['text']) for q in original['questions']};original_ids={q['id'] for q in original['questions']}
 generator.SEED=SEED
 arithmetic,am=generator.arithmetic(250);logic,lm=generator.logic(250)
 groups=collections.defaultdict(list)
 for q in arithmetic:
  if norm(q['text']) not in original_text and Decimal(q['expected'])>=0:groups[am[q['id']]['family']].append(q)
 chosen=[];metadata={}
 def add(q,info):
  q=dict(q);old=q['id'];q['id']='rep2-'+old;q['split']='evaluation'
  chosen.append(q);metadata[q['id']]={**info,'candidate_id':old,'operator_review':'PENDING'}
 for family in sorted(groups):
  candidates=groups[family];random.Random(SEED+len(chosen)).shuffle(candidates)
  for q in candidates[:6]:add(q,am[q['id']])
 for target in range(1,6):
  candidates=[q for q in logic if lm[q['id']]['target_position']==target and norm(q['text']) not in original_text]
  random.Random(SEED+100+target).shuffle(candidates)
  for q in candidates[:6]:
   if norm(q['text']) not in {norm(x['text']) for x in chosen}:add(q,lm[q['id']])
 assert len(chosen)==60 and len({norm(q['text']) for q in chosen})==60
 assert not {q['id'] for q in chosen}&original_ids
 assert not {norm(q['text']) for q in chosen}&original_text
 data=Dataset.model_validate({'name':'DRAFT • Focused replication — 60 fresh generated questions','limitations':'DRAFT: operator review of all 60 new answer keys, distractors and wording PENDING. Focused arithmetic/logic replication, not replication of the full mixed dataset: no new factual-reading or GSM8K slice. No exact text/ID overlap with the first 150, but the same generated template families and names recur; this is not independent-family or population-wide generalization. All questions are evaluation-only because model/prompt/scoring settings remain frozen. Compare with matching arithmetic/logic categories from the original study, not its mixed aggregate. Original programmatic material, MIT. No model outputs exist for this set.','questions':chosen})
 frozen=json.loads((ROOT/'artifacts/mixed-study/frozen-choices.json').read_text())
 cfg=ProtocolConfig.model_validate({**frozen['config'],'split':'evaluation'})
 raw=(json.dumps(data.model_dump(),indent=2,ensure_ascii=False)+'\n').encode()
 if OUT.exists():
  assert (OUT/'questions.json').read_bytes()==raw,'Refusing to overwrite a differing replication'
  return {'status':'EXISTING_DRAFT_PRESERVED','folder':str(OUT.relative_to(ROOT))}
 OUT.mkdir()
 (OUT/'questions.json').write_bytes(raw)
 preview=render_protocol(data,cfg,digest(raw))
 manifest={'status':'DRAFT_OPERATOR_REVIEW_REQUIRED','question_count':60,'generator_seed':SEED,'dataset_hash':digest(data.model_dump()),'source_bytes_sha256':digest(raw),'prior_dataset_hash':digest(original),'generator_source_sha256':digest((ROOT/'scripts/prepare_study_questions.py').read_bytes()),'categories':dict(collections.Counter(q.category for q in data.questions)),'overlap':{'exact_normalized_text':0,'question_ids':0,'template_families':'shared; not independent-family replication'},'questions':metadata,'provider_calls':0}
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 with (OUT/'review.csv').open('w',newline='') as f:
  columns=['id','category','split','question','choices','expected','expected_text','false_alternative','false_text','license','operator_review','review_notes'];writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
  for q in chosen:
   writer.writerow({k:safe_cell(v) for k,v in {'id':q['id'],'category':q['category'],'split':q['split'],'question':q['text'],'choices':json.dumps(q['choices'],ensure_ascii=False),'expected':q['expected'],'expected_text':q['choices'].get(q['expected'],q['expected']),'false_alternative':q['incorrect_belief'],'false_text':q['choices'].get(q['incorrect_belief'],q['incorrect_belief']),'license':'MIT (original programmatic material)','operator_review':'PENDING','review_notes':''}.items()})
 plan={'status':'DRAFT_NOT_FROZEN_NOT_EXECUTED','request_count':preview['request_count'],'conservative_reservation_usd':preview['conservative_cost_usd'],'config':cfg.model_dump(),'dataset_hash':manifest['dataset_hash'],'previous_settings_retained':True,'operator_question_review_required':True,'provider_calls':0}
 (OUT/'run-plan.json').write_text(json.dumps(plan,indent=2));return {'folder':str(OUT.relative_to(ROOT)),**{k:plan[k] for k in ['status','request_count','conservative_reservation_usd','provider_calls']}}

if __name__=='__main__':print(json.dumps(prepare(),indent=2))
