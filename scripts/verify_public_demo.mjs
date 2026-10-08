import {chromium} from '../apps/web/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';import crypto from 'node:crypto';import assert from 'node:assert/strict';
const base=process.env.ASSET_BASE??'http://127.0.0.1:5174';const browser=await chromium.launch({headless:true});
const context=await browser.newContext();const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto(base+'/demo.html',{waitUntil:'networkidle'});
for(const width of [320,390,768,1440]){await page.setViewportSize({width,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);}
const video=page.locator('video');await video.evaluate(e=>new Promise((resolve,reject)=>{if(e.readyState>=1)resolve();else{e.addEventListener('loadedmetadata',resolve,{once:true});e.addEventListener('error',reject,{once:true});}}));
const duration=await video.evaluate(e=>e.duration);assert.ok(duration>=60&&duration<=90);assert.equal(await video.evaluate(e=>e.paused),true);
await video.evaluate(e=>e.play());await page.waitForTimeout(1000);assert.ok(await video.evaluate(e=>e.currentTime)>0);await video.evaluate(e=>e.pause());
const audio=page.locator('audio');assert.equal(await audio.evaluate(e=>e.paused),true);await audio.evaluate(e=>e.play());await page.waitForFunction(()=>document.querySelector('audio')?.currentTime>0,null,{timeout:10000});assert.ok(await audio.evaluate(e=>e.currentTime)>0);await audio.evaluate(e=>e.pause());
const link=page.getByRole('link',{name:'Open the live application'});await link.focus();assert.equal(await link.evaluate(e=>getComputedStyle(e).outlineStyle!=='none'),true);
const remote=await context.request.get(base+'/demo.webm');assert.equal(remote.status(),200);const data=await remote.body();const sha=crypto.createHash('sha256').update(data).digest('hex');assert.equal(sha,crypto.createHash('sha256').update(await fs.readFile('apps/web/public/demo.webm')).digest('hex'));
const partial=await context.request.get(base+'/demo.webm',{headers:{Range:'bytes=0-1023'}});assert.equal(partial.status(),206);assert.equal((await partial.body()).length,1024);
assert.deepEqual(errors,[]);await context.close();await browser.close();
const report={executed_at:new Date().toISOString(),base_url:base,status:'PASS',duration_seconds:duration,size_bytes:data.length,sha256:sha,http_status:remote.status(),range_status:partial.status(),viewports:[320,390,768,1440],video_decoded_and_played:true,voice_decoded_and_played:true,autoplay:false,keyboard_focus:true,console_errors:errors};
await fs.writeFile(`evals/reports/release-demo-${base.startsWith('https:')?'public':'local'}.json`,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
