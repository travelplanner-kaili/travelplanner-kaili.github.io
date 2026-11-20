const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const url='file:///home/claude/rome/real/rome-real.html';
const ctx=async init=>{const c=await b.newContext({viewport:{width:1280,height:850}});await c.addInitScript(init);const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.errs=errs;await p.goto(url);await p.waitForTimeout(600);return p;};
const A=await ctx(()=>{if(!sessionStorage.x){sessionStorage.x=1;localStorage.setItem('trip-tour-rome','1');localStorage.setItem('trip-tour-plan-rome','1');localStorage.setItem('trip-days-rome','[5,6]');localStorage.setItem('trip-plan-rome',JSON.stringify({cur:'d1',days:{d1:[{id:'colosseo',time:'09:00',note:'a'}]},list:[{k:'d1',date:'2/4',wd:4}]}))}});
const code=await A.evaluate(()=>location.href.split('#')[0]+'#all='+b64e(JSON.stringify(shareData())));
for(const mode of ['add','replace']){
 const B=await ctx(()=>{if(!sessionStorage.x){sessionStorage.x=1;localStorage.setItem('trip-tour-rome','1');localStorage.setItem('trip-tour-plan-rome','1');localStorage.setItem('trip-days-rome','[2]');localStorage.setItem('trip-plan-rome',JSON.stringify({cur:'d1',days:{d1:[{id:'foro',time:'',note:''}]},list:[{k:'d1',date:'2/3',wd:3}]}))}});
 await B.goto(code);await B.waitForTimeout(800);
 const txt=await B.evaluate(()=>document.querySelector('.share-ask')?.innerText);
 if(mode==='add') console.log(txt);
 await B.check(`input[name=sa-mode][value=${mode}]`);await B.click('#sa-yes');await B.waitForTimeout(900);
 console.log(mode,await B.evaluate(()=>[localStorage.getItem('trip-plan-rome'),localStorage.getItem('trip-days-rome'),JSON.parse(localStorage.getItem('trip-plan-rome')).list.map(x=>x.date).join(','),[...document.querySelectorAll('.chip.day[aria-pressed=true]')].map(x=>x.textContent).join('')]),B.errs);
}
console.log(A.errs);await b.close();})();
