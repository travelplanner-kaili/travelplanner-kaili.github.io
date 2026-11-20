const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:1280,height:850},{width:390,height:800}]){
const c=await b.newContext({viewport:vp});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{localStorage.setItem('trip-tour-rome','1');localStorage.setItem('trip-tour-plan-rome','1')});
await p.goto('file:///home/claude/rome/real/rome-real.html');await p.waitForTimeout(700);
if(vp.width<641) await p.evaluate(()=>document.getElementById('fs-exit')&&document.getElementById('fs-exit').click());
await p.waitForTimeout(300);
const h=p.locator('h3.faq-sub',{hasText:'我的行程'});await h.scrollIntoViewIfNeeded();
await p.screenshot({path:`/tmp/claude-0/faq-${vp.width}.png`});
await p.click('.plan-tour-again');await p.waitForTimeout(1600);
console.log(vp.width,await p.evaluate(()=>{const c=document.querySelector('.tour-card');return c&&c.querySelector('h3').textContent}),await p.evaluate(()=>document.querySelectorAll('details.faq-more[open]').length),errs);
await c.close();}
await b.close();})();
