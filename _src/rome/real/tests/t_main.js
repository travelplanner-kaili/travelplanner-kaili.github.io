const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:1280,height:850},{width:390,height:800}]){
const c=await b.newContext({viewport:vp});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file:///home/claude/rome/real/rome-real.html');await p.waitForTimeout(2600);
for(let k=0;k<18;k++){const info=await p.evaluate(()=>{const c=document.querySelector('.tour-card');if(!c)return null;const h=document.querySelector('.tour-hole').getBoundingClientRect();return [c.querySelector('h3').textContent,h.left|0,h.top|0,h.width|0,h.height|0]});
 console.log(vp.width,k,JSON.stringify(info));if(!info)break;if(['City Walk','購物','記得設定你的住宿'].includes(info[0]))await p.screenshot({path:`/tmp/claude-0/rt-${vp.width}-${k}.png`});
 await p.evaluate(()=>document.querySelector('.tour-next').click());await p.waitForTimeout(1400);}
console.log(errs);await c.close();}
await b.close();})();
