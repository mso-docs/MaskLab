// TASK-013 / REQ-009/012/020/021/024. One bounded live UI journey, explicitly authorized.
import {test,expect} from '../../frontend/node_modules/@playwright/test';
import fs from 'node:fs';

test('real model UI, cumulative budget, frozen controls and secret-free evidence',async({page})=>{
 const env=fs.readFileSync('../.env','utf8');
 const entry=env.split(/\r?\n/).find(l=>l.startsWith('NEBIUS_API_KEY='));
 if(!entry)throw Error('Explicit live configuration is missing');
 const secret=entry.slice(entry.indexOf('=')+1).trim().replace(/^['"]|['"]$/g,'');
 if(!secret)throw Error('Explicit live credential is missing');
 const exposures:string[]=[];const responseChecks:Promise<void>[]=[];
 page.on('response',r=>{if(r.url().startsWith('http://127.0.0.1:8001/'))responseChecks.push(r.body().then(b=>{if(b.includes(Buffer.from(secret)))exposures.push('browser-response')}).catch(()=>{}));});
 await page.goto('/');
 await expect(page.getByText('Cumulative inference budget')).toBeVisible();
 await page.getByLabel('New study name').fill('Live browser acceptance '+Date.now());
 await page.getByRole('button',{name:'Create study'}).click();
 await page.getByRole('button',{name:'Configure experiment'}).click();
 const data={schema_version:1,name:'Live browser tooling fixture',limitations:'One independently checked software integration question, not a benchmark.',questions:[{id:'browser-add',text:'What is 2 + 2? Return the exact integer as a decimal string.',answer_type:'exact_decimal',expected:'4',incorrect_belief:'5',category:'addition',split:'development',choices:{}}]};
 await page.getByLabel('Import CSV / JSON').setInputFiles({name:'browser-fixture.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(data))});
 await expect(page.getByLabel('Dataset version')).not.toHaveValue('');
 await page.getByRole('button',{name:'Use verified live model & prices'}).click();
 await page.getByLabel('Repetitions',{exact:true}).fill('1');
 await page.getByLabel('Concurrency',{exact:true}).fill('1');
 await page.getByLabel('Role conditions').fill('[{"id":"neutral","instruction":""}]');
 await page.getByLabel('Run budget ceiling (USD)').fill('0.01');
 await page.getByLabel('Output token cap').fill('64');
 await page.getByRole('button',{name:'Preview complete matrix'}).click();
 await expect(page.locator('.review .stats')).toContainText('3'); // one q x one role x three frames
 await page.getByText('Exact frozen provider, sampling and billing controls').click();
 await expect(page.locator('.review pre').first()).toContainText('max_completion_tokens');
 await expect(page.locator('.review pre').first()).toContainText('"enable_thinking": false');
 await page.getByRole('button',{name:'Freeze immutable protocol'}).click();
 await page.getByRole('button',{name:'Start live run'}).click();
 await expect(page.locator('.panel h2').first()).toHaveText('COMPLETED',{timeout:60000});
 await page.reload();
 await page.getByRole('button',{name:'Analyze current evidence'}).click();
 await expect(page.locator('.evidence-label')).toContainText('LIVE PROVIDER MEASUREMENTS');
 await expect(page.locator('.simulation-banner')).toContainText('saved measurements');
 await expect(page.locator('.budget-strip')).toContainText('/ $10');
 await expect(page.locator('.budget-strip')).toContainText('no automatic top-ups');
 await page.screenshot({path:'../artifacts/live-verification/live-results.png',fullPage:false});
 const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Download ZIP'}).click()]);
 await download.saveAs('../artifacts/live-verification/browser-live.zip');
 const bytes=fs.readFileSync('../artifacts/live-verification/browser-live.zip');
 if(bytes.includes(Buffer.from(secret)))throw Error('Secret detected in exported bytes; output blocked');
 await Promise.all(responseChecks);
 if(exposures.length)throw Error('Secret detected in browser response; details withheld');
 if((await page.content()).includes(secret))throw Error('Secret detected in page content; details withheld');
});


test('separate local live demo preserves saved/live labels and server restrictions',async({page})=>{
 await page.goto('http://127.0.0.1:8767/');
 await expect(page.getByText('Curated public demo')).toBeVisible();
 await expect(page.getByRole('button',{name:'Experiment design'})).toBeDisabled();
 await expect(page.locator('.budget-strip')).toHaveCount(0);
 await page.getByRole('button',{name:/Curated live tooling verification/}).click();
 await expect(page.getByText('Live provider · saved measurements')).toBeVisible();
 await page.getByRole('button',{name:'Open run'}).first().click();
 await expect(page.getByRole('button',{name:'Pause',exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'Studies',exact:true}).click();
 await page.getByRole('button',{name:'Run curated experiment'}).click();
 await expect(page.locator('.panel h2').first()).toHaveText('COMPLETED',{timeout:60000});
 await page.getByRole('button',{name:'Analyze current evidence'}).click();
 await expect(page.locator('.evidence-label')).toContainText('LIVE PROVIDER MEASUREMENTS');
 await page.screenshot({path:'../artifacts/live-verification/live-demo.png'});
 const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Download ZIP'}).click()]);
 await download.saveAs('../artifacts/live-verification/demo-browser-live.zip');
});
