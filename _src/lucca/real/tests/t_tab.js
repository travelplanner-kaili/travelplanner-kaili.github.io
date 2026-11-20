const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:1280,height:850},{width:390,height:800}]){
const c=await b.newContext({viewport:vp});const p=await c.newPage();
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{try{localStorage.setItem('trip-tour-lucca','1')}catch(e){}});
await p.goto('file://'+process.cwd()+'/lucca-real.html');await p.waitForTimeout(700);
const ids=await p.evaluate(()=>[...document.querySelectorAll('.spot')].map(e=>e.dataset.id||e.id).slice(0,3));
await p.evaluate(ids=>{const k='trip-plan-lucca';localStorage.setItem(k,JSON.stringify({cur:'d1',days:{d1:ids.map(id=>({id,time:'',note:''})),d2:[]},list:[{k:'d1',date:'2/4',wd:4},{k:'d2',date:'2/5',wd:5}]}));},ids);
await p.reload();await p.waitForTimeout(800);
const st=async n=>console.log(vp.width,n,JSON.stringify(await p.evaluate(()=>({tab:!document.querySelector('.plan-tab').hidden,panel:!document.getElementById('plan').hidden,planning:document.getElementById('lmap').classList.contains('planning'),route:document.querySelectorAll('.plan-line').length,off:document.getElementById('plan').classList.contains('off')}))));
await st('closed-load');
await p.screenshot({path:`/tmp/claude-0/tab-${vp.width}-a.png`});
await p.click('.plan-tab');await p.waitForTimeout(300);await st('open');
await p.click('.pd-off');await p.waitForTimeout(200);await st('off');
await p.screenshot({path:`/tmp/claude-0/tab-${vp.width}-b.png`});
await p.click('#plan-days button[data-k]');await p.waitForTimeout(300);await st('day');
await p.click('#plan-x');await p.waitForTimeout(200);await st('collapsed');
console.log(ids,errs);await c.close();}
await b.close();})();
