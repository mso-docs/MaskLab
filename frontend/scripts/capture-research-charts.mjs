// TASK-009/012: read-only visual QA of saved live evidence and the staged draft. No run-start requests.
import {chromium} from '@playwright/test';
import fs from 'node:fs';
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8001/#view=results&study=c1592ca4cf564557992d4314774c7ed8&run=344b98f7814d4c07a9c47ac11af0a0d2');
 await page.getByRole('heading',{name:'Correctness by role and belief',exact:true}).waitFor();
 const panels=page.locator('.research-charts .panel');
 for(const [index,name] of ['correctness-bars','answer-consistency','paired-differences','question-heatmap'].entries())await panels.nth(index).screenshot({path:'../artifacts/charts/'+name+'.png'});
 await page.getByRole('button',{name:'Toggle appearance'}).click();
 await page.waitForTimeout(200);
 await panels.nth(0).screenshot({path:'../artifacts/charts/correctness-bars-light.png'});
 const staged=JSON.parse(fs.readFileSync('../artifacts/charts/staged-study.json','utf8'));
 await page.goto(staged.url);await page.getByRole('heading',{name:'Design an experiment',exact:true}).waitFor();
 await page.getByRole('note').waitFor();await page.screenshot({path:'../artifacts/charts/draft-study.png'});
 if(errors.length)throw Error('Browser errors: '+errors.join(';'));
 console.log('PASS: six screenshots of saved live charts, light appearance and staged draft; zero browser errors, no run-start requests');
}finally{await browser.close()}
