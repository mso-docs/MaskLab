// TASK-009/012 / REQ-014–017/024: hand-derived chart expectations, no implementation-generated oracle.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {cell,agreement,conditionData,questionCells}=require('../../artifacts/chart-tests/chartData.js');
function row(id,q,answer,correct=false,state='SUCCEEDED',status='VALID',role='neutral',frame='absent'){
 return {id,key:['model',q,role,frame,Number(id.replace(/\D/g,''))||0],category:'fixture',state,score:{status,correct,normalized:answer}};
}
const mixed=[row('1','q','A',true),row('2','q',null,false,'SUCCEEDED','INVALID'),row('3','q',null,false,'FAILED','FAILED'),row('4','q',null,false,'PENDING','PENDING'),row('5','q',null,false,'UNCERTAIN','UNCERTAIN')];
assert.deepEqual(cell(mixed),{ids:['1','2','3','4','5'],scheduled:5,finalized:3,valid:1,correct:1,pending:1,uncertain:1,allAccuracy:1/3,validAccuracy:1});
assert.equal(cell([row('6','zero','B')]).allAccuracy,0);
assert.equal(cell([mixed[3]]).allAccuracy,null);
assert.equal(cell([]).allAccuracy,null);
const reps=[row('a1','q1','A'),row('a2','q1','A'),row('a3','q1','B'),row('a4','q1',null,false,'SUCCEEDED','INVALID'),row('b1','q2','C'),row('b2','q2','C'),row('c1','q3','D')];
const got=agreement(reps);
assert.ok(Math.abs(got.value-5/6)<1e-12); // ((2/3)+(2/2))/2, equal question weighting
assert.equal(got.eligibleQuestions,2);assert.equal(got.excludedQuestions,1);assert.equal(got.validResponses,5);
assert.deepEqual(got.ids,['a1','a2','a3','b1','b2']);assert.deepEqual(got.excludedIds,['a4','c1']);
assert.equal(agreement([reps[0]]).value,null); // one valid response cannot establish repeated agreement
assert.equal(agreement([row('x1','q','WRONG'),row('x2','q','WRONG')]).value,1); // stable is not correct
const frames=[...reps,row('z1','q1','A',true,'SUCCEEDED','VALID','neutral','incorrect')];
assert.deepEqual(conditionData(frames,'model').map(c=>c.frame),['absent','incorrect']);
const heat=questionCells(frames,'model');
assert.equal(heat.questions.length,3);assert.equal(heat.questions[1].cells[1].scheduled,0);
assert.equal(heat.questions[1].cells[1].allAccuracy,null); // not scheduled is never a measured zero
assert.equal(heat.questions[0].cells[1].allAccuracy,1);
console.log('PASS: hand-derived denominators, missing/zero, equal-question consistency, exclusions and heatmap drilldown IDs');
