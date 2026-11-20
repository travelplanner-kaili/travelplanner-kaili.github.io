const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:1280,height:850}});const p=await c.newPage();
await p.addInitScript(()=>{localStorage.setItem('trip-tour-lucca','1');localStorage.setItem('trip-tour-plan-lucca','1');localStorage.setItem('trip-plan-lucca',JSON.stringify({cur:'d1',days:{d1:[{id:'duomo',time:'',note:''},{id:'campanile',time:'',note:''}]},list:[{k:'d1',date:'2/4',wd:4}]}))});
await p.goto('file://'+process.cwd()+'/lucca-real.html');await p.waitForTimeout(600);
await p.click('.plan-tab');await p.waitForTimeout(500);await p.screenshot({path:'/tmp/claude-0/left-a.png'});
await p.click('.view-btns .fs-open');await p.waitForTimeout(800);await p.screenshot({path:'/tmp/claude-0/left-b.png'});
console.log(await p.evaluate(()=>[document.getElementById('plan').getBoundingClientRect().left,document.getElementById('lmap').getBoundingClientRect().left,document.querySelector('.plan-tab').getBoundingClientRect().left,document.getElementById('plan').getBoundingClientRect().right]));
await b.close();})();
