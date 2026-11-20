const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:1280,height:850},{width:390,height:800}]){
const c=await b.newContext({viewport:vp,permissions:['clipboard-read','clipboard-write']});const p=await c.newPage();
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+process.cwd()+'/lucca-real.html');await p.waitForTimeout(800);
await p.evaluate(()=>document.querySelector('.tour-skip,.tour-x')&&document.querySelector('.tour-skip,.tour-x').click());
const r=await p.evaluate(()=>({share:!!document.getElementById('plan-share'),paste:!!document.querySelector('.pd-paste'),imp:document.querySelectorAll('.imp-open').length,foot:[...document.querySelectorAll('.plan-foot button,.plan-foot a')].map(x=>x.textContent.trim())}));
// open import from visible button
const btn=p.locator('.imp-open:visible').first();
if(!(await btn.count())){await p.locator('.fs-menu, #fs-menu, .fs-open').first().click().catch(()=>{});}
await p.evaluate(()=>{[...document.querySelectorAll('.imp-open')].find(x=>x.offsetParent)?.click()});
await p.waitForTimeout(200);
const vis=await p.evaluate(()=>{const e=document.querySelector('.imp-pop');return !e.hidden && e.getBoundingClientRect().width});
await p.fill('#pp-text','hello'); await p.click('#pp-ok'); await p.waitForTimeout(100);
const warn=await p.textContent('#pp-ver').catch(()=>'' );
await p.screenshot({path:`/tmp/claude-0/imp-${vp.width}.png`});
console.log(vp.width,JSON.stringify(r),'popW',vis,errs);
await c.close();}
await b.close();})();
