import { chromium } from '../apps/web/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const suffix=process.env.PUBLIC_RUN_LABEL ?? 'initial';
const demo=process.env.DEMO_RECORDING==='true';
const directory=`artifacts/release/public-${suffix}`;
await fs.mkdir(directory,{recursive:true});
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:1440,height:900},recordVideo:{dir:directory,size:{width:1440,height:900}}});
await context.tracing.start({screenshots:true,snapshots:true,sources:true});
const page=await context.newPage();
const report={executed_at:new Date().toISOString(),url:'https://outproof-web.onrender.com',scope:'real public browser execution; no physical outing',errors:[],requests:[]};
page.on('pageerror',error=>report.errors.push(error.message));
let compiled;
page.on('response',async response=>{
 if(response.url().endsWith('/v1/plans/compile')){
  const body=await response.json(); compiled=body;
  report.requests.push({status:response.status(),request_id:response.headers()['x-request-id'],body});
  await fs.writeFile(`${directory}/compile-response.json`,JSON.stringify(body,null,2)+'\n');
  console.log(JSON.stringify({compile_status:response.status(),result:body.status,code:body.code}));
 }
});
try{
 await page.goto(report.url,{waitUntil:'networkidle',timeout:65000});
 report.version=await (await context.request.get('https://outproof-api.onrender.com/v1/version')).json();
 const button=page.getByRole('button',{name:'Compile one live plan'});
 await button.waitFor({timeout:65000});
 await page.screenshot({path:`${directory}/home.png`,fullPage:true});
 if(demo){await page.waitForTimeout(8000);await page.getByLabel('Budget in SGD',{exact:true}).fill('0');await page.waitForTimeout(8000);}
 await page.keyboard.press('Tab'); await button.focus(); assert.equal(await button.evaluate(e=>getComputedStyle(e).outlineStyle!=='none'),true);
 const started=Date.now();await page.keyboard.press('Enter');
 await Promise.race([
  page.getByRole('heading',{name:'One verified plan.',exact:true}).waitFor({timeout:190000}),
  page.getByRole('alert').waitFor({timeout:190000}).then(async()=>{throw new Error(await page.getByRole('alert').innerText());})
 ]);
 report.time_to_plan_ms=Date.now()-started;
 assert.equal(compiled.mode,'LIVE');assert.equal(compiled.status,'SUCCESS');
 assert.equal(compiled.proof.validation.checks.length,11);
 assert.equal(compiled.proof.validation.checks.every(c=>c.status==='PASS'),true);
 assert.equal(compiled.plan.stops.length,1);
 assert.equal(compiled.proof.cost.upper.currency_code,'SGD');assert.equal(compiled.proof.cost.upper.minor_units,0);
 assert.equal(compiled.proof.sources.some(s=>s.source==='FIXTURE'),false);
 await page.screenshot({path:`${directory}/plan.png`,fullPage:true});
 if(demo)await page.waitForTimeout(8000);
 await page.getByText(/Plan Proof ·/).click();
 await page.getByRole('heading',{name:'Source observations · LIVE'}).waitFor();
 await page.screenshot({path:`${directory}/proof.png`,fullPage:true});
 if(demo)await page.waitForTimeout(10000);
 await page.getByRole('button',{name:'GO',exact:true}).click();
 await page.getByText('Phone down.',{exact:true}).waitFor({timeout:5000});
 report.time_to_go_ms=Date.now()-started;
 const map=page.getByRole('link',{name:'Open walking map'});
 assert.match(await map.getAttribute('href'),/^https:\/\/www.openstreetmap.org\/directions\?engine=fossgis_valhalla_foot/);
 const audio=page.locator('audio');assert.equal(await audio.evaluate(e=>e.paused),true);
 await audio.evaluate(e=>e.play());await page.waitForTimeout(demo?6500:1000);report.voice_time_seconds=await audio.evaluate(e=>e.currentTime);assert.ok(report.voice_time_seconds>0);await audio.evaluate(e=>e.pause());
 await page.screenshot({path:`${directory}/go.png`,fullPage:true});
 await page.getByRole('button',{name:'Next step'}).click();
 if(demo)await page.waitForTimeout(6000);
 await page.getByRole('button',{name:'Back to plan',exact:true}).click();
 await page.getByRole('heading',{name:'One verified plan.',exact:true}).waitFor();
 await page.setViewportSize({width:390,height:844});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.screenshot({path:`${directory}/mobile.png`,fullPage:true});
 if(demo)await page.waitForTimeout(8000);
 assert.deepEqual(report.errors,[]);report.status='PASS';
}catch(error){report.status='FAIL';report.failure=String(error);await page.screenshot({path:`${directory}/failure.png`,fullPage:true}).catch(()=>{});}
await context.tracing.stop({path:`${directory}/trace.zip`});await context.close();await browser.close();
await fs.writeFile(`${directory}/receipt.json`,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,time_to_plan_ms:report.time_to_plan_ms,time_to_go_ms:report.time_to_go_ms,failure:report.failure}));
if(report.status!=='PASS')process.exitCode=1;
