// TASK-009/012 / REQ-014–017/024: browser charts use actual API-scored SIMULATED records.
import {test,expect} from '../../frontend/node_modules/@playwright/test';
const headers={'X-MaskLab-Request':'1'};
test('charts preserve denominators, repeated agreement and exact drilldown',async({page,request})=>{
 const study=await (await request.post('/api/studies',{headers,data:{name:'Chart verification '+Date.now()}})).json();
 const dataset=await (await request.post('/api/studies/'+study.id+'/sample',{headers})).json();
 const frozen=await (await request.post('/api/studies/'+study.id+'/freeze',{headers,data:{dataset_id:dataset.id,config:{roles:[{id:'neutral',instruction:''},{id:'expert',instruction:'You are a careful expert. Answer accurately.'}],frames:['absent','incorrect'],repetitions:3,models:['simulated/nemotron-contract'],provider:'simulated'}}})).json();
 const response=await request.post('/api/protocols/'+frozen.id+'/runs',{headers:{...headers,'Idempotency-Key':'chart-'+Date.now()}});expect(response.ok()).toBeTruthy();const run=await response.json();
 await expect.poll(async()=>(await (await request.get('/api/runs/'+run.id)).json()).state,{timeout:45000}).toBe('COMPLETED');
 await page.goto('/#view=results&study='+study.id+'&run='+run.id);
 for(const title of ['Correctness by role and belief','Repeated answer consistency','Paired correctness differences','Question × condition heatmap'])await expect(page.getByRole('heading',{name:title,exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'neutral, Absent belief: 4.2%, 3/72; inspect scheduled records',exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'neutral, Absent belief answer consistency: 100.0%; 24 eligible questions; inspect valid contributors',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'neutral, Absent belief answer consistency: 100.0%; 24 eligible questions; inspect valid contributors',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Response explorer',exact:true})).toBeVisible();
 await expect(page.locator('.panel .section-heading .badge')).toHaveText('72 / 288 RECORDS');
 await page.getByRole('button',{name:'Analysis',exact:true}).click();
 await page.locator('.paired-plot').getByRole('button').first().focus();await page.keyboard.press('Enter');
 await expect(page.locator('.panel .section-heading .badge')).toHaveText('144 / 288 RECORDS');
 await page.getByRole('button',{name:'Analysis',exact:true}).click();
 await page.getByRole('button',{name:'Next questions',exact:true}).click();
 await expect(page.getByText('Questions 21–24 of 24')).toBeVisible();
 await expect(page.getByRole('button',{name:'Next questions',exact:true})).toBeDisabled();
 await page.locator('.question-heatmap tbody tr').first().locator('td button').first().click();
 await expect(page.locator('.panel .section-heading .badge')).toHaveText('3 / 288 RECORDS');
});
