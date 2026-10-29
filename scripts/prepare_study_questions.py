"""TASK-002/007/012 / REQ-004/005/007/024: reproducible mixed draft, NEVER inference.
Preparation approval is not approval of unseen answer keys. Source data/derivatives remain outside Git.
"""
from __future__ import annotations
import argparse
import collections
import csv
from decimal import Decimal
import hashlib
import io
import itertools
import json
from pathlib import Path
import random
import re
import tarfile
from question_curations import CMU_DISTRACTORS
from masklab.portable import safe_cell
from masklab.contracts import Dataset,ProtocolConfig,Role,canonical,digest,render_protocol

SEED=28102026
ROOT=Path(__file__).resolve().parents[1]
GSM_REJECTED={1190:'Inventory timing unclear: first-day use can exceed initial stock before an order.',117:'Price per shoe versus per pair is implicit.',206:'At least five rides does not fix an exact distance.',531:'Three times fewer is ambiguous wording.',888:'Duplicated five wording/typo.',844:'Half times as many and reference scope are unclear.',368:'Three times more has competing interpretations.',231:'Two times more has competing interpretations.',831:'Unused package slots may or may not transfer to other item types.',1109:'Party-wide denominator not explicitly limited to the six described women.',17:'Hourly unit for coaching is implicit.',560:'Per-cage versus total animal counts are implicit.',1038:'Gross earnings versus additional earnings/payback is ambiguous.'}

def number(value):
    d=Decimal(str(value));s=format(d,'f');return s.rstrip('0').rstrip('.') if '.' in s else s


def choice_question(base,correct,others,index):
    answers=[correct,*others];assert 2<=len(answers)<=4 and len(set(x.casefold() for x in answers))==len(answers)
    position=index%len(answers);answers.insert(position,answers.pop(0))
    labels='ABCD'[:len(answers)];choices=dict(zip(labels,answers));expected=labels[position];false=labels[(position+1)%len(answers)]
    return {**base,'answer_type':'single_choice','choices':choices,'expected':expected,'incorrect_belief':false}


def arithmetic(n):
    out=[];meta={}
    for i in range(n):
        rng=random.Random(SEED+i);a=rng.randrange(12,180);b=rng.randrange(2,15);c=rng.randrange(2,10);family=i%5
        if family==0:text=f'Calculate {a} + {b} × {c}, using multiplication before addition.';answer=a+b*c;params={'a':a,'b':b,'c':c}
        elif family==1:
            text=f'Calculate {a}/10 + {b}/100 as an exact decimal.';answer=Decimal(a)/10+Decimal(b)/100;params={'a':a,'b':b}
        elif family==2:
            price=20*(i+4);discount=5*(1+i%5);text=f'A ticket costs {price} units. Its price is reduced by {discount} percent. What is the exact reduced price in units?';answer=Decimal(price)*(100-discount)/100;params={'price':price,'discount':discount}
        elif family==3:
            x=i+3;text=f'Solve for x: {b} × x + {a} = {b*x+a}. Return x as a decimal string.';answer=x;params={'coefficient':b,'offset':a,'total':b*x+a}
        else:
            count=i+4;text=f'{b*count} tokens are divided equally among {b} people. Each person then gives away {c} tokens. How many tokens does each person have left?';answer=count-c;params={'total':b*count,'people':b,'given':c}
        id=f'arith-{i+1:03d}';expected=number(answer)
        out.append({'id':id,'text':text,'category':'arithmetic','answer_type':'exact_decimal','expected':expected,'incorrect_belief':number(Decimal(expected)+1),'choices':{},'split':'development'})
        meta[id]={'origin':'original programmatic question','license':'MIT (original MaskLab material)','family':f'arithmetic-{family}','parameters':params,'mechanical_check':'Independent arithmetic reference required','operator_review':'PENDING'}
    return out,meta


def logic(n):
    names=['Arin','Bela','Cora','Davi','Esme'];perms=list(itertools.permutations(names));out=[];meta={}
    def satisfies(p,clues):
        positions={v:i for i,v in enumerate(p)}
        return all((positions[b]-positions[a]==v if kind=='distance' else positions[a]<positions[b]) for kind,a,b,v in clues)
    for i in range(n):
        rng=random.Random(SEED+1000+i);hidden=names.copy();rng.shuffle(hidden);target=i%5
        pool=[('distance',hidden[a],hidden[b],b-a) for a in range(5) for b in range(a+1,5)]
        pool += [('before',hidden[a],hidden[b],0) for a in range(5) for b in range(a+1,5)]
        rng.shuffle(pool);clues=[]
        for clue in pool:
            clues.append(clue);solutions=[p for p in perms if satisfies(p,clues)]
            if len({p[target] for p in solutions})==1:break
        for clue in clues.copy():
            trial=[c for c in clues if c!=clue];solutions=[p for p in perms if satisfies(p,trial)]
            if solutions and len({p[target] for p in solutions})==1:clues=trial
        solutions=[p for p in perms if satisfies(p,clues)];correct=solutions[0][target]
        rendered=[f'{a} is {v} position(s) before {b}.' if kind=='distance' else f'{a} stands before {b}.' for kind,a,b,v in clues]
        text='Five people ('+', '.join(names)+') occupy different positions 1 through 5, counted left to right.\n'+'\n'.join(rendered)+f'\nWho occupies position {target+1}?'
        id=f'logic-{i+1:03d}';others=[x for x in names if x!=correct];rng.shuffle(others)
        out.append(choice_question({'id':id,'text':text,'category':'logic','split':'development'},correct,others[:3],i))
        meta[id]={'origin':'original constrained ordering question','license':'MIT (original MaskLab material)','family':'five-person-ordering','clues':clues,'target_position':target+1,'solution_count':len(solutions),'names':names,'mechanical_check':'Independent exhaustive permutation check required','operator_review':'PENDING'}
    return out,meta


def gsm(n):
    folder=ROOT/'data/question-sources/gsm8k';upstream=json.loads((folder/'upstream.json').read_text())
    source=folder/'gsm8k-test.jsonl';assert digest(source.read_bytes())==next(x['sha256'] for x in upstream['files'] if x['name']==source.name)
    rows=[json.loads(x) for x in source.read_text().splitlines()]
    initial=json.loads((folder/'selected-indices.json').read_text());fallback=json.loads((folder/'fallback-indices.json').read_text());order=initial+fallback
    out=[];meta={};rejected=[]
    for index in order:
        if index in GSM_REJECTED:rejected.append({'index':index,'reason':GSM_REJECTED[index]});continue
        row=rows[index];expected=row['answer'].rsplit('####',1)[-1].strip().replace(',','')
        if not re.fullmatch(r'-?\d+(?:\.\d+)?',expected):rejected.append({'index':index,'reason':'Unsupported non-exact-decimal answer'});continue
        id=f'gsm8k-test-{index:04d}'
        out.append({'id':id,'text':row['question'],'category':'numerical_reasoning','answer_type':'exact_decimal','expected':number(expected),'incorrect_belief':number(Decimal(expected)+1),'choices':{},'split':'development'})
        meta[id]={'origin':'GSM8K original test split','license':'MIT; OpenAI 2021 notice retained','source_index':index,'source_commit':upstream['commit'],'source_url':next(x['url'] for x in upstream['files'] if x['name']==source.name),'original_question_sha256':digest(row['question'].encode()),'original_solution':row['answer'],'family':'upstream-word-problem','adaptation':'Question unchanged; exact decimal key extracted after ####; +1 false alternative added for review','mechanical_check':'Upstream label extraction only; independent arithmetic review required','operator_review':'PENDING'}
        if len(out)==n:break
    assert len(out)==n
    return out,meta,rejected


def cmu(n):
    folder=ROOT/'data/question-sources/cmu-qa';upstream=json.loads((folder/'upstream.json').read_text());path=folder/'Question_Answer_Dataset_v1.2.tar.gz'
    assert digest(path.read_bytes())==upstream['sha256']
    root='Question_Answer_Dataset_v1.2/S10/'
    def norm(s):return re.sub(r'\s+',' ',s).strip().casefold()
    with tarfile.open(path) as archive:
        def read(name):
            item=archive.getmember(name)
            if not item.isfile() or item.size>2*1024*1024:raise ValueError('Unsafe/oversize source member')
            raw=archive.extractfile(item).read()
            try:return raw.decode('utf-8')
            except UnicodeDecodeError:return raw.decode('latin-1')
        raw=read(root+'question_answer_pairs.txt');rows=list(csv.DictReader(io.StringIO(raw),delimiter='\t'))
        groups=collections.defaultdict(list)
        for index,r in enumerate(rows):
            if not all(isinstance(r.get(k),str) for k in ('ArticleTitle','Question','Answer','ArticleFile')):continue
            groups[(r['ArticleTitle'],norm(r['Question']))].append((index,r))
        candidates=collections.defaultdict(list);rejected=collections.Counter()
        for (article,_),items in groups.items():
            candidates_answers=sorted({r['Answer'].strip() for _,r in items if r['Answer'].strip() and norm(r['Answer']) not in {'null','n/a','na','unknown'}},key=lambda s:(len(s),s))
            if not candidates_answers:rejected['missing answer']+=1;continue
            answer=candidates_answers[0];index,r=next(((i,r) for i,r in items if r['Answer'].strip()==answer))
            if len(answer)>70 or len(answer)<2 or norm(answer) in {'yes','no','none','n/a','na','null','unknown','true','false'} or not re.match(r'^(who|what|when|where|which|how many|how much|in what year)\b',r['Question'],re.I):rejected['unsuitable answer/question type']+=1;continue
            if any(norm(answer) not in norm(other) for other in candidates_answers):rejected['conflicting source answers']+=1;continue
            if not re.fullmatch(r'data/set\d+/a\d+',r['ArticleFile']):rejected['unexpected source article path']+=1;continue
            try:
                name=root+r['ArticleFile']+'.txt.clean'
                try:article_text=read(name)
                except KeyError:name=root+r['ArticleFile']+'.txt';article_text=read(name)
            except KeyError:rejected['missing article']+=1;continue
            text=re.sub(r'\s+',' ',article_text).strip();found=text.casefold().find(answer.casefold())
            if found<0:rejected['answer not literal in archived context']+=1;continue
            # Fixed archived excerpt, not current Wikipedia; context shared in all paired conditions.
            start=max(0,text.rfind('. ',0,max(0,found-180))+2);end=text.find('. ',found+len(answer))
            if end<0:end=min(len(text),found+len(answer)+250)
            else:end+=1
            excerpt=text[start:end]
            if len(excerpt)>1800 or len(excerpt)<20:rejected['excerpt bound']+=1;continue
            candidates[article].append({'row':r,'index':index,'answer':answer,'all_answers':candidates_answers,'excerpt':excerpt,'article_member':name})
        articles=sorted(candidates);random.Random(SEED+2000).shuffle(articles)
        out=[];meta={};all_answers=sorted({c['answer'] for values in candidates.values() for c in values})
        for article in articles:
            options=candidates[article].copy();random.Random(SEED+int(hashlib.sha256(article.encode()).hexdigest()[:8],16)).shuffle(options)
            for c in options:
                if c['index'] not in CMU_DISTRACTORS:continue
                answer=c['answer'];others=CMU_DISTRACTORS[c['index']]
                i=len(out);id=f'cmu-s10-{c["index"]:04d}'
                text=f'Use only this archived excerpt from the article "{article.replace("_"," ")}". Answer according to the excerpt, not current-world updates.\n\n{c["excerpt"]}\n\nQuestion: {c["row"]["Question"]}'
                out.append(choice_question({'id':id,'text':text,'category':'reading_comprehension','split':'development'},answer,others,i))
                meta[id]={'origin':'CMU/Pittsburgh Question-Answer Dataset 1.2, S10 only','license':'CC BY-SA 3.0; NOT relicensed MIT','source_url':upstream['source_url'],'source_archive_sha256':upstream['sha256'],'source_row':c['index'],'article_title':article,'article_member':c['article_member'],'source_question':c['row']['Question'],'source_answers':c['all_answers'],'source_encoding':'UTF-8 if valid, otherwise Latin-1; no replacement decoding','distractor_review':'Type-matched initial curation; operator factual review still PENDING','source_answer_selected':answer,'excerpt':c['excerpt'],'attribution':'Noah A. Smith, Michael Heilman, Rebecca Hwa and CMU/Pittsburgh student contributors; see upstream README.v1.2','adaptation':'Archived excerpt added; reviewed-label candidate converted to labeled choices with newly authored type-matched candidate distractors; false alternative added. One question per article.','family':'archived-factoid-reading','mechanical_check':'Literal answer span only; semantic answer/distractor/context review required','operator_review':'PENDING'}
                break
            if len(out)==n:break
        if len(out)!=n:raise ValueError(f'Only {len(out)} unique-article source candidates pass mechanical filters; requested {n}')
    return out,meta,dict(rejected)


def prepare(count=150):
    if not 20<=count<=150:raise ValueError('Draft preparer supports 20–150 currently curated questions; larger sets need additional source review (application ceiling remains 500 questions)')
    sizes=[count//4+(i<count%4) for i in range(4)]
    gs,gm,ge=gsm(sizes[0]);ar,am=arithmetic(sizes[1]);lo,lm=logic(sizes[2]);rd,rm,ce=cmu(sizes[3])
    groups=[gs,ar,lo,rd];metadata={**gm,**am,**lm,**rm};questions=[]
    # One question/article in CMU ensures no article can straddle development/evaluation.
    for j,group in enumerate(groups):
        order=list(range(len(group)));random.Random(SEED+4000+j).shuffle(order);development=set(order[:round(len(group)*.4)])
        for i,q in enumerate(group):q['split']='development' if i in development else 'evaluation';questions.append(q)
    limitations='DRAFT — operator answer-key, ambiguity, distractor and source/license review PENDING. Mixed convenience sample with generated template families and public benchmarks; not representative or decontaminated. S10 adapted material remains CC BY-SA 3.0, not MIT. No model results exist for this dataset.'
    source_notice=('Sources and adaptations: GSM8K (OpenAI, 2021), pinned repository https://github.com/openai/grade-school-math ; exact keys extracted, false alternatives added. CMU/Pittsburgh Question-Answer Dataset 1.2, S10 only: Noah A. Smith, Michael Heilman, Rebecca Hwa and student contributors; https://www.cs.cmu.edu/~ark/QA-data/ . S10 excerpts/questions adapted to labeled choices and false alternatives under CC BY-SA 3.0: https://creativecommons.org/licenses/by-sa/3.0/ . Article titles appear in question text. These adaptations are NOT relicensed MIT. Original programmatic arithmetic/logic material is MIT. Public benchmark exposure is unknown; this is a convenience study, not a benchmark replication.')
    mit_notice=(ROOT/'data/question-sources/gsm8k/LICENSE-gsm8k.txt').read_text()
    limitations += '\n\n'+source_notice+'\n\nGSM8K retained MIT notice:\n'+mit_notice
    dataset=Dataset.model_validate({'schema_version':1,'name':f'DRAFT • {count}-question mixed behavioral study','limitations':limitations,'questions':questions})
    out=ROOT/f'data/study-draft-{count}'
    if (out/'manifest.json').exists():
        previous=json.loads((out/'manifest.json').read_text());assert previous['dataset_hash']==digest(dataset.model_dump()),'Existing draft differs; preserve it and create a new version'
        if previous['status']=='OPERATOR_APPROVED':
            raise ValueError('Approved dataset and review decisions are immutable; refusing to regenerate over them')
    out.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(dataset.model_dump(),indent=2,ensure_ascii=False)+'\n').encode();(out/'questions.json').write_bytes(raw)
    manifest={'schema_version':1,'status':'DRAFT_OPERATOR_REVIEW_REQUIRED','seed':SEED,'question_count':count,'dataset_hash':digest(dataset.model_dump()),'source_bytes_sha256':digest(raw),'category_counts':dict(collections.Counter(q['category'] for q in questions)),'split_counts':dict(collections.Counter(q['split'] for q in questions)),'licenses':{'GSM8K':'MIT, upstream notice retained','CMU S10 adaptations':'CC BY-SA 3.0, attribution and share-alike retained separately','Original generated arithmetic/logic':'MIT (original MaskLab material)'},'article_overlap':False,'questions':metadata,'gsm_rejections_before_inference':ge,'cmu_filter_counts':ce,'no_provider_calls':True,'limitations':[limitations,'Public benchmark exposure/contamination is unknown.','Generated template families may appear in both splits; ID disjointness is not semantic independence.','Question-cluster intervals reflect sampled questions, not a population benchmark.']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    with (out/'review.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['id','category','split','question','choices','expected','expected_text','false_alternative','false_text','source','license','operator_review','review_notes'])
        for q in questions:
            m=metadata[q['id']];writer.writerow([safe_cell(value) for value in [q['id'],q['category'],q['split'],q['text'],json.dumps(q['choices'],ensure_ascii=False),q['expected'],q['choices'].get(q['expected'],q['expected']),q['incorrect_belief'],q['choices'].get(q['incorrect_belief'],q['incorrect_belief']),m['origin'],m['license'],'PENDING','']])
    cfg=ProtocolConfig(provider='nebius',models=['nvidia/Nemotron-3_5-Lightning'],repetitions=3,concurrency=2,max_output_tokens=512,budget_usd='2',input_price_per_million='0.06',output_price_per_million='0.24',output_parameter='max_completion_tokens',dual_output_cap=True,enable_thinking=False,response_format='json_object',service_tier='default')
    preview=render_protocol(dataset,cfg,digest(raw))
    (out/'run-plan.json').write_text(json.dumps({'status':'DRAFT_NOT_FROZEN_NOT_EXECUTED','question_count':count,'roles':3,'frames':3,'repetitions':3,'request_count':preview['request_count'],'conservative_reservation_usd':preview['conservative_cost_usd'],'run_ceiling_usd':cfg.budget_usd,'config':cfg.model_dump(),'dataset_hash':preview['dataset_hash'],'split_hash':preview['split_hash'],'permission':'Preparation only; review keys and independently check current shared remaining budget/capabilities before any run.'},indent=2)+'\n')
    import shutil
    shutil.copyfile(ROOT/'data/question-sources/gsm8k/LICENSE-gsm8k.txt',out/'LICENSE-gsm8k.txt')
    (out/'ATTRIBUTION-CMU-S10.txt').write_text('CMU/Pittsburgh Question-Answer Dataset, Release 1.2 (2013-08-23), S10.\nNoah A. Smith, Michael Heilman, Rebecca Hwa and CMU/Pittsburgh contributors.\nSource: https://www.cs.cmu.edu/~ark/QA-data/\nS10 license: Creative Commons Attribution-ShareAlike 3.0 Unported.\nhttps://creativecommons.org/licenses/by-sa/3.0/\nAdaptations: archived excerpts, multiple-choice alternatives, false-belief alternatives, stable IDs, categories and split metadata.\nThis material is not relicensed under the application MIT license. Original archive and release README retained in data/question-sources/cmu-qa/.\nCitation: Smith, Heilman, Hwa (2008), Question Generation as a Competitive Undergraduate Course Project.\n')
    (out/'README.txt').write_text(f'DRAFT: {count} questions, awaiting operator review.\nImport questions.json into MaskLab for inspection. review.csv contains every key, false alternative, license and a PENDING review field. manifest.json retains provenance and source hashes.\nNo provider calls, no model results, no protocol frozen or run queued. Three roles × three frames × three repeats would schedule {preview["request_count"]} calls, conservative list-price reservation USD{preview["conservative_cost_usd"]}; this is an offline preview, not funding or benchmark validation.\nUse separate development/evaluation subsets; do not tune prompts against held-out outcomes. One source article per CMU question avoids article overlap. Generated template families may overlap across splits.\nKeep source and derivative data outside Git. CMU S10 adaptations remain CC BY-SA 3.0; GSM8K notice retained.\n')
    return {'status':manifest['status'],'folder':str(out.relative_to(ROOT)),'question_count':count,'categories':manifest['category_counts'],'splits':manifest['split_counts'],'request_count':preview['request_count'],'conservative_reservation_usd':preview['conservative_cost_usd'],'no_provider_calls':True}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--questions',type=int,default=150)
    print(json.dumps(prepare(parser.parse_args().questions),indent=2))
