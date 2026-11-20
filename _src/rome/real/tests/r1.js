const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:1280,height:850},{width:390,height:800}]){
const c=await b.newContext({viewport:vp});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push('console:'+m.text().slice(0,150))});
await p.addInitScript(()=>{try{localStorage.setItem('trip-tour-rome','1')}catch(e){}});
await p.goto('file:///home/claude/rome/real/rome-real.html');await p.waitForTimeout(1500);
console.log(vp.width,'spots',await p.evaluate(()=>[SPOTS.length,document.querySelectorAll('.spot:not(.gone)').length,document.querySelectorAll('.street-name.shop-street').length]));
await p.screenshot({path:`/tmp/claude-0/r-${vp.width}-a.png`});
await p.evaluate(()=>[...document.querySelectorAll('.icon-btn.route')].find(x=>x.offsetParent).click());await p.waitForTimeout(600);
await p.screenshot({path:`/tmp/claude-0/r-${vp.width}-b.png`});
await p.evaluate(()=>openRoute('bernini-walk'));await p.waitForTimeout(800);
await p.screenshot({path:`/tmp/claude-0/r-${vp.width}-c.png`});
await p.evaluate(()=>{closeSpot();[...document.querySelectorAll('.icon-btn.route')].find(x=>x.offsetParent).click();[...document.querySelectorAll('.shop-btn')].find(x=>x.offsetParent).click()});await p.waitForTimeout(600);
await p.screenshot({path:`/tmp/claude-0/r-${vp.width}-d.png`});
await p.evaluate(()=>openSpot('trevi'));await p.waitForTimeout(400);await p.screenshot({path:`/tmp/claude-0/r-${vp.width}-e.png`});
console.log(vp.width,errs.slice(0,5));await c.close();}
await b.close();})();
