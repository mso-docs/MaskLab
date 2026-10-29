// TASK-009/013: read-only inspection of completed mixed-study evidence.
import {chromium} from '@playwright/test';
import fs from 'node:fs';
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 for(const split of ['development','evaluation']){
  const r=JSON.parse(fs.readFileSync('../artifacts/mixed-study/'+split+'-run.json','utf8'));
  await page.goto('about:blank');
  await page.goto(`http://127.0.0.1:8001/#view=results&study=${r.study_id}&run=${r.id}`);
  await page.getByRole('heading',{name:'Correctness by role and belief',exact:true}).waitFor();
  const denominator=split==='development'?180:270;
  await page.getByText('/'+denominator,{exact:false}).first().waitFor();
  // Hide the fixed workspace footer in element-only captures to avoid obscuring chart rows.
  await page.addStyleTag({content:'.run-footer{visibility:hidden}'});
  const panels=page.locator('.research-charts .panel');
  for(const [i,name] of ['correctness','consistency','paired','heatmap'].entries())await panels.nth(i).screenshot({path:`../artifacts/mixed-study/${split}-${name}.png`});
 }
 if(errors.length)throw Error(errors.join(';'));
 console.log('PASS: both completed results render all four chart panels; no browser errors or inference actions');
}finally{await browser.close()}
