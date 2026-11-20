const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:1280,height:850},{width:390,height:800}]){
const c=await b.newContext({viewport:vp});const p=await c.newPage();
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{try{localStorage.setItem('trip-tour-rome','1');localStorage.setItem('trip-tour-plan-rome','1');localStorage.setItem('trip-plan-rome',JSON.stringify({cur:'d1',days:{d1:[{id:'colosseo',time:'',note:''},{id:'foro',time:'',note:''}],d2:[]},list:[{k:'d1',date:'2/4',wd:4},{k:'d2',date:'2/5',wd:5}]}))}catch(e){}});
await p.goto('file:///home/claude/rome/real/rome-real.html');await p.waitForTimeout(800);
const st=async n=>console.log(vp.width,n,JSON.stringify(await p.evaluate(()=>({panel:!document.getElementById('plan').hidden,planning:document.getElementById('lmap').classList.contains('planning'),off:document.getElementById('plan').classList.contains('off'),sel:[...document.querySelectorAll('#plan-days [aria-selected=true]')].length,tab:(r=>[r.left|0,r.top|0,r.width|0,r.height|0])(document.querySelector('.plan-tab').getBoundingClientRect()),pan:(r=>[r.left|0,r.top|0,r.right|0,r.bottom|0])(document.getElementById('plan').getBoundingClientRect())}))));
await p.screenshot({path:`/tmp/claude-0/t2-${vp.width}-a.png`});
await p.click('.plan-tab');await p.waitForTimeout(500);await st('open');
await p.screenshot({path:`/tmp/claude-0/t2-${vp.width}-b.png`});
await p.click('#plan-days button[aria-selected=true]');await p.waitForTimeout(300);await st('deselect');
await p.click('#plan-days button[data-k="d1"]');await p.waitForTimeout(300);await st('select');
await p.click('.plan-tab');await p.waitForTimeout(300);await st('closed');
console.log(errs);await c.close();}
await b.close();})();
