// TASK-005/009/012 • REQ-014–017/024. Descriptive views of immutable scored records.
export const AGREEMENT_VIEW_VERSION='modal-answer-share-v1';
export interface ChartRow {
 id:string; key:[string,string,string,string,number]; category:string; state:string;
 score:{status:string;correct:boolean;normalized:string|null};
}
export interface Cell {
 ids:string[];scheduled:number;finalized:number;valid:number;correct:number;pending:number;uncertain:number;
 allAccuracy:number|null;validAccuracy:number|null;
}
export function cell(rows:ChartRow[]):Cell {
 const finalized=rows.filter(r=>r.state==='SUCCEEDED'||r.state==='FAILED');
 const valid=rows.filter(r=>r.score.status==='VALID');
 const correct=valid.filter(r=>r.score.correct).length;
 return {ids:rows.map(r=>r.id),scheduled:rows.length,finalized:finalized.length,valid:valid.length,correct,
 pending:rows.filter(r=>r.state==='PENDING'||r.state==='IN_FLIGHT').length,
 uncertain:rows.filter(r=>r.state==='UNCERTAIN').length,
 allAccuracy:finalized.length?correct/finalized.length:null,validAccuracy:valid.length?correct/valid.length:null};
}
export interface Agreement {
 value:number|null;eligibleQuestions:number;excludedQuestions:number;validResponses:number;
 ids:string[];excludedIds:string[];
}
export function agreement(rows:ChartRow[]):Agreement {
 const questions=new Map<string,ChartRow[]>();
 for(const r of rows){const key=JSON.stringify([r.key[0],r.key[1],r.key[2],r.key[3]]);questions.set(key,[...(questions.get(key)||[]),r]);}
 let total=0,eligibleQuestions=0,excludedQuestions=0,validResponses=0;
 const ids:string[]=[],excludedIds:string[]=[];
 for(const group of questions.values()){
  const valid=group.filter(r=>r.score.status==='VALID'&&r.score.normalized!==null);
  if(valid.length<2){excludedQuestions++;excludedIds.push(...group.map(r=>r.id));continue;}
  const frequencies=new Map<string,number>();
  for(const r of valid){const answer=r.score.normalized!;frequencies.set(answer,(frequencies.get(answer)||0)+1);}
  total+=Math.max(...frequencies.values())/valid.length;eligibleQuestions++;validResponses+=valid.length;
  ids.push(...valid.map(r=>r.id));excludedIds.push(...group.filter(r=>r.score.status!=='VALID').map(r=>r.id));
 }
 return {value:eligibleQuestions?total/eligibleQuestions:null,eligibleQuestions,excludedQuestions,validResponses,ids,excludedIds};
}
export function conditionData(rows:ChartRow[],model:string){
 const selected=rows.filter(r=>r.key[0]===model),groups=new Map<string,ChartRow[]>();
 for(const r of selected){const key=JSON.stringify([r.key[2],r.key[3]]);groups.set(key,[...(groups.get(key)||[]),r]);}
 const order=['absent','correct','incorrect'];
 return [...groups].map(([key,records])=>{const [role,frame]=JSON.parse(key);return {role:role as string,frame:frame as string,cell:cell(records),agreement:agreement(records)};}).sort((a,b)=>a.role.localeCompare(b.role)||order.indexOf(a.frame)-order.indexOf(b.frame));
}
export function questionCells(rows:ChartRow[],model:string){
 const selected=rows.filter(r=>r.key[0]===model),conditions=conditionData(rows,model);
 const groups=new Map<string,ChartRow[]>();
 for(const r of selected){const key=JSON.stringify([r.key[1],r.key[2],r.key[3]]);groups.set(key,[...(groups.get(key)||[]),r]);}
 return {conditions,questions:[...new Set(selected.map(r=>r.key[1]))].sort().map(id=>({id,category:selected.find(r=>r.key[1]===id)!.category,ids:selected.filter(r=>r.key[1]===id).map(r=>r.id),cells:conditions.map(c=>cell(groups.get(JSON.stringify([id,c.role,c.frame]))||[]))}))};
}
