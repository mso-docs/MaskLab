// TASK-012 / TEST-001–003/007/008/017–020: a real browser, backend and simulated worker.
import {test,expect} from '../../frontend/node_modules/@playwright/test';
import fs from 'node:fs';

test('full simulated researcher journey and evidence portability',async({page})=>{
 const crashes:string[]=[];page.on('pageerror',e=>crashes.push(e.message));
 let analysisRequests=0;page.on('request',r=>{if(/\/api\/runs\/[^/]+\/analysis$/.test(r.url()))analysisRequests++});
 await page.goto('/');
 await expect(page.getByRole('heading',{name:'Your research workspace'})).toBeVisible();
 await page.getByLabel('New study name').fill('Browser acceptance '+Date.now());
 await page.getByRole('button',{name:'Create study'}).click();
 await page.getByRole('button',{name:'Configure experiment'}).click();
 await page.getByRole('button',{name:'Use synthetic tooling fixtures'}).click();
 await expect(page.getByLabel('Dataset version')).not.toHaveValue('');
 await page.getByLabel('Repetitions',{exact:true}).fill('1');
 await page.getByRole('button',{name:'Preview complete matrix'}).click();
 await expect(page.getByRole('heading',{name:'A protocol you can reproduce'})).toBeVisible();
 await expect(page.locator('.review .stats')).toContainText('216'); // 24 x 3 x 3 x 1
 await page.getByRole('button',{name:'Freeze immutable protocol'}).click();
 await expect(page.getByRole('button',{name:'Start simulated run'})).toBeEnabled();
 await page.getByRole('button',{name:'Save durable run draft'}).click();
 await expect(page.getByRole('heading',{name:'Follow every request'})).toBeVisible();
 await expect(page.locator('.panel h2').first()).toHaveText('DRAFT');
 const analysesBeforeQueue=analysisRequests;
 await page.getByRole('button',{name:'Queue draft'}).click();
 await expect(page.locator('.panel h2').first()).toHaveText('COMPLETED',{timeout:30000});
 // Monitor must not run expensive scientific analysis on every progress tick.
 expect(analysisRequests-analysesBeforeQueue).toBeLessThanOrEqual(2);
 await page.reload();
 await expect(page.getByRole('heading',{name:'Follow every request'})).toBeVisible();
 await page.getByRole('button',{name:'Analyze current evidence'}).click();
 await expect(page.getByRole('heading',{name:'Read the evidence'})).toBeVisible();
 await expect(page.locator('.evidence-label')).toContainText('NOT NEMOTRON EVIDENCE');
 await expect(page.locator('.heatmap')).toContainText('neutral');
 await page.locator('.heatmap button').first().click();
 await expect(page.getByRole('heading',{name:'Response explorer'})).toBeVisible();
 await page.locator('tbody details summary').first().click();
 await expect(page.getByRole('heading',{name:'Exact rendered prompts'}).first()).toBeVisible();
 await page.getByLabel('Question comparison').selectOption('syn-001');
 await expect(page.getByRole('heading',{name:'Side-by-side: syn-001'})).toBeVisible();
 const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Download ZIP'}).click()]);
 const file='../artifacts/verification/browser-export.zip';await download.saveAs(file);
 await page.getByRole('button',{name:'Studies',exact:true}).click();
 await expect(page.locator('tbody').getByRole('button',{name:'Download ZIP'}).first()).toBeVisible();
 await page.getByLabel('New study name').fill('Download navigation '+Date.now());
 await page.getByRole('button',{name:'Create study'}).click();
 await expect(page.getByRole('button',{name:'Download ZIP'})).toHaveCount(0);
 await page.getByLabel('Import evidence archive').setInputFiles(file);
 await expect(page.getByText('Archive validated. Inspection only.')).toBeVisible();
 await page.locator('.import-button').first().click();
 await expect(page.getByText('IMPORTED · INSPECTION ONLY')).toBeVisible();
 await page.getByRole('button',{name:'Toggle appearance'}).click();
 await expect(page.locator('html')).toHaveAttribute('data-theme','light');
 await page.screenshot({path:'../artifacts/verification/workspace-light.png',fullPage:false});
 await page.getByRole('button',{name:'Toggle appearance'}).click();
 await page.screenshot({path:'../artifacts/verification/workspace-dark.png',fullPage:false});
 await page.getByRole('button',{name:'Methods & help'}).click();
 await expect(page.getByRole('heading',{name:'Study observable behavior, preserve the record.'})).toBeVisible();
 await page.setViewportSize({width:900,height:900});
 await expect(page.locator('.narrow')).toBeVisible();
 expect(crashes).toEqual([]);
});

test('inert imported text, validation, keyboard focus and archive history',async({page})=>{
 await page.goto('/');await page.getByLabel('New study name').fill('Safety '+Date.now());await page.getByRole('button',{name:'Create study'}).click();
 await page.getByRole('button',{name:'Configure experiment'}).click();
 await page.getByLabel('Import CSV / JSON').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{"questions":[]}')});
 await expect(page.getByRole('alert')).toContainText('Action needs attention');
 const data={schema_version:1,name:'Inert text',questions:[{id:'x',text:'<img src=x onerror="window.pwned=true">',answer_type:'single_choice',expected:'A',incorrect_belief:'B',choices:{A:'<script>bad</script>',B:'other'},category:'test',split:'development'}]};
 await page.getByLabel('Import CSV / JSON').setInputFiles({name:'safe.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(data))});
 await expect(page.locator('.dataset-preview')).toContainText('<img src=x');
 expect(await page.evaluate(()=>Boolean((window as any).pwned))).toBe(false);
 expect(await page.locator('.dataset-preview img').count()).toBe(0);
 await page.keyboard.press('Tab');expect(await page.evaluate(()=>document.activeElement?.tagName)).not.toBe('BODY');
 await page.getByRole('button',{name:'Studies',exact:true}).click();
 await page.getByRole('button',{name:'Archive study',exact:true}).click();
 await expect(page.getByRole('button',{name:'Reopen study',exact:true})).toBeVisible();
 await page.reload();await expect(page.getByRole('button',{name:'Reopen study',exact:true})).toBeVisible();
});


test('restricted demo shows saved simulation and bounds execution',async({page})=>{
 await page.goto('http://127.0.0.1:8766/');
 await expect(page.getByText('Curated public demo')).toBeVisible();
 await expect(page.getByRole('button',{name:'Experiment design'})).toBeDisabled();
 await expect(page.getByLabel('New study name')).toHaveCount(0);
 await expect(page.getByText('PRIVATE CANARY')).toHaveCount(0);
 await page.getByRole('button',{name:/Curated simulated example/}).click();
 await page.getByRole('button',{name:'Open run'}).first().click();
 await expect(page.getByRole('button',{name:'Pause',exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'Analyze current evidence'}).click();
 await expect(page.locator('.evidence-label')).toContainText('SIMULATED');
 await page.getByRole('button',{name:'Studies',exact:true}).click();
 await page.getByRole('button',{name:'Run curated experiment'}).click();
 await expect(page.getByRole('heading',{name:'Follow every request'})).toBeVisible();
 await expect(page.locator('.panel h2').first()).toHaveText('COMPLETED');
 await page.screenshot({path:'../artifacts/verification/demo-simulated.png'});
});


test('dataset draft status and retained licenses remain visible and inert',async({page,request})=>{
 const headers={'X-MaskLab-Request':'1'};
 const study=await (await request.post('/api/studies',{headers,data:{name:'Draft review '+Date.now()}})).json();
 const data={schema_version:1,name:'DRAFT review candidate',limitations:'DRAFT — operator review PENDING.\n\nSource attribution and retained license: fixture only. <script>bad</script>',questions:[{id:'review-q',text:'What is 2 + 2?',answer_type:'exact_decimal',expected:'4',incorrect_belief:'5',category:'arithmetic',split:'development',choices:{}}]};
 const imported=await request.post('/api/studies/'+study.id+'/datasets?kind=json',{headers,data});expect(imported.ok()).toBeTruthy();
 await page.goto('/#view=design&study='+study.id+'&run=');
 await expect(page.getByRole('note')).toContainText('DRAFT — operator review PENDING.');
 await page.getByText('Full dataset notes, sources and licenses').click();
 await expect(page.getByRole('note')).toContainText('Source attribution and retained license: fixture only. <script>bad</script>');
 await expect(page.getByRole('note').locator('script')).toHaveCount(0);
 const saved=await (await request.get('/api/studies/'+study.id)).json();expect(saved.runs).toHaveLength(0);expect(saved.protocols).toHaveLength(0);
});
