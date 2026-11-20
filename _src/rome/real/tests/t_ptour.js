const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:1280,height:850},{width:390,height:800},{width:360,height:740}]){
const c=await b.newContext({viewport:vp});const p=await c.newPage();
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{try{localStorage.setItem('trip-tour-rome','1');localStorage.setItem('trip-plan-rome',JSON.stringify({cur:'d1',on:false,days:{d1:[{id:'colosseo',time:'',note:''},{id:'foro',time:'',note:''}]},list:[{k:'d1',date:'2/4',wd:4}]}))}catch(e){}});
await p.goto('file:///home/claude/rome/real/rome-real.html');await p.waitForTimeout(700);
await p.click('.plan-tab');await p.waitForTimeout(1200);
const head=await p.evaluate(()=>{const h=document.querySelector('.plan-head');return [h.offsetHeight,h.scrollWidth,h.clientWidth]});
for(let k=0;k<9;k++){
  const info=await p.evaluate(()=>{const c=document.querySelector('.tour-card'),h=document.querySelector('.tour-hole');if(!c)return null;const r=h.getBoundingClientRect(),q=c.getBoundingClientRect();return {t:c.querySelector('h3').textContent,hole:[r.left|0,r.top|0,r.width|0,r.height|0],ov:!(q.bottom<r.top||q.top>r.bottom||q.right<r.left||q.left>r.right)}});
  console.log(vp.width,k,JSON.stringify(info));
  if(k==3||k==7) await p.screenshot({path:`/tmp/claude-0/pt-${vp.width}-${k}.png`});
  if(!info)break; await p.click('.tour-next');await p.waitForTimeout(1400);
}
const again=await p.evaluate(()=>localStorage.getItem('trip-tour-plan-rome'));
console.log('head',head,'saved',again,errs);await c.close();}
await b.close();})();
