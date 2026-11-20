const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:1280,height:850},{width:390,height:800}]){
const c=await b.newContext({viewport:vp});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{localStorage.setItem('trip-tour-lucca','1');localStorage.setItem('trip-tour-plan-lucca','1')});
await p.goto('file://'+process.cwd()+'/lucca-real.html');await p.waitForTimeout(700);
if(vp.width<641){await p.evaluate(()=>document.getElementById('fs-exit').click());await p.waitForTimeout(300);}
await p.locator('.custom-tour-again').scrollIntoViewIfNeeded();await p.click('.custom-tour-again');await p.waitForTimeout(1600);
for(let k=0;k<8;k++){const info=await p.evaluate(()=>{const c=document.querySelector('.tour-card'),h=document.querySelector('.tour-hole');if(!c)return null;const r=h.getBoundingClientRect();return {t:c.querySelector('h3').textContent,hole:[r.left|0,r.top|0,r.width|0,r.height|0]}});
console.log(vp.width,k,JSON.stringify(info));if(!info)break;if(k==3||k==4||k==6)await p.screenshot({path:`/tmp/claude-0/ct-${vp.width}-${k}.png`});await p.evaluate(()=>document.querySelector('.tour-next').click());await p.waitForTimeout(1400);}
console.log(errs, await p.evaluate(()=>[localStorage.getItem('trip-tour-custom-lucca'), document.body.classList.contains('fs-on')]));await c.close();}
await b.close();})();
