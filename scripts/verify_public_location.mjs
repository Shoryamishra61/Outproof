import { chromium } from '../apps/web/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const directory='.tools/public-location';
await fs.mkdir(directory,{recursive:true});
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:390,height:900}});
const page=await context.newPage();
const report={executed_at:new Date().toISOString(),url:'https://outproof-web.onrender.com',scope:'Actual public origin search and initial map imagery; subsequent keyboard/payload check controlled; no physical GPS or outing',errors:[],searches:[]};
page.on('pageerror',e=>report.errors.push(e.message));
try{
 report.version=await(await context.request.get('https://outproof-api.onrender.com/v1/version')).json();
 for(const query of ['Anna Nagar Chennai','London United Kingdom','Tokyo Japan']){
  const response=await context.request.post('https://outproof-api.onrender.com/v1/locations/search',{data:{query},timeout:65000});
  const body=await response.json();assert.equal(response.status(),200);assert.ok(body.results.length>0&&body.results.length<=5);
  for(const point of body.results){assert.ok(Number.isFinite(point.coordinates.latitude)&&Math.abs(point.coordinates.latitude)<=90);assert.ok(Number.isFinite(point.coordinates.longitude)&&Math.abs(point.coordinates.longitude)<=180);}
  report.searches.push({query,status:response.status(),results:body.results});await page.waitForTimeout(1200);
 }
 await page.goto(report.url,{waitUntil:'domcontentloaded',timeout:65000});
 await page.getByLabel('Search for your starting area').waitFor();
 assert.equal(await page.getByLabel('Latitude',{exact:true}).count(),0);
 await page.getByLabel('Search for your starting area').fill('Anna Nagar Chennai');
 await page.getByRole('button',{name:'Search places',exact:true}).click();
 const selected=report.searches[0].results[0];
 await page.getByRole('button',{name:selected.label,exact:true}).click();
 await page.getByRole('region',{name:'Starting location map'}).waitFor();
 await page.waitForFunction(()=>document.querySelectorAll('.leaflet-tile').length>0&&Array.from(document.querySelectorAll('.leaflet-tile')).every(i=>i.complete&&i.naturalWidth>1),{},{timeout:30000});
 report.actual_initial_map_tiles=await page.locator('.leaflet-tile').evaluateAll(images=>images.filter(i=>i.complete&&i.naturalWidth>1).length);
 assert.ok(report.actual_initial_map_tiles>0);
 assert.equal(await page.locator('.leaflet-tile').first().getAttribute('referrerpolicy'),'strict-origin-when-cross-origin');
 assert.ok(await page.locator('.leaflet-control-attribution').getByRole('link',{name:'OpenStreetMap'}).isVisible());
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.screenshot({path:`${directory}/mobile.png`,fullPage:true});
 // Automated panning uses controlled imagery rather than forcing public tile traffic.
 await page.route('https://tile.openstreetmap.org/**',r=>r.fulfill({contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j3ioAAAAASUVORK5CYII=','base64')}));
 await page.getByRole('region',{name:'Starting location map'}).focus();await page.keyboard.press('ArrowRight');
 await page.getByRole('button',{name:'Use map centre as start'}).click();
 let submittedOrigin;
 await page.route('**/v1/plans/compile',r=>{submittedOrigin=r.request().postDataJSON().controls.origin;return r.fulfill({status:503,json:{status:'FAILURE',code:'SOURCE_TEMPORARILY_UNAVAILABLE',message:'Controlled origin submission check'}});});
 const submit=page.getByRole('button',{name:'Compile one live plan'});
 await submit.waitFor();
 if(!await submit.isEnabled()&&await page.getByRole('button',{name:'Check connection',exact:true}).isVisible())await page.getByRole('button',{name:'Check connection',exact:true}).click();
 await page.waitForFunction(button=>!button.disabled,await submit.elementHandle(),{timeout:65000});await submit.click();
 await page.getByRole('alert').filter({hasText:'Controlled origin submission check'}).waitFor();
 assert.ok(submittedOrigin.longitude>selected.coordinates.longitude);report.submitted_origin=submittedOrigin;
 await page.setViewportSize({width:1440,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.screenshot({path:`${directory}/desktop.png`,fullPage:true});
 assert.deepEqual(report.errors,[]);report.status='PASS';
}catch(error){report.status='FAIL';report.failure=String(error);await page.screenshot({path:`${directory}/failure.png`,fullPage:true}).catch(()=>{});}
await context.close();await browser.close();
await fs.writeFile(`${directory}/receipt.json`,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
if(report.status!=='PASS')process.exitCode=1;
