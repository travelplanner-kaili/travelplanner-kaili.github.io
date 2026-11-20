const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:390,height:800},{width:1280,height:850}]){
const c=await b.newContext({viewport:vp,colorScheme:'dark'});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{localStorage.setItem('trip-tour-lucca','1')});
await p.goto('file://'+process.cwd()+'/lucca-real.html');await p.waitForTimeout(700);
await p.click('.plan-tab');await p.waitForTimeout(1500);
await p.click('.tour-next');await p.waitForTimeout(1300);await p.click('.tour-next');await p.waitForTimeout(1400);
await p.screenshot({path:`/tmp/claude-0/demo-${vp.width}.png`});
await p.click('.tour-skip');await p.waitForTimeout(400);
console.log(vp.width,await p.evaluate(()=>[document.querySelectorAll('#plan-list li').length,document.getElementById('plan').classList.contains('demo'),localStorage.getItem('trip-plan-lucca')]),errs);
await c.close();}
await b.close();})();
