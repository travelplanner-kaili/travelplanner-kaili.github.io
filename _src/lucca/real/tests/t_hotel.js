const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for (const vp of [{width:1280,height:850},{width:390,height:800}]){
const c=await b.newContext({viewport:vp});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{if(!sessionStorage.y){sessionStorage.y=1;localStorage.setItem('trip-tour-lucca','1');localStorage.setItem('trip-tour-plan-lucca','1');}});
await p.goto('file://'+process.cwd()+'/lucca-real.html');await p.waitForTimeout(700);
await p.evaluate(()=>openSpot('guinigi'));await p.waitForTimeout(200);
await p.click('.rt-tab[data-tab=tips]');await p.waitForTimeout(150);
console.log(vp.width,'line:',await p.evaluate(()=>[...document.querySelectorAll('#drawer dt')].find(d=>d.textContent=='從住宿出發')?.nextElementSibling.innerText));
await p.screenshot({path:`/tmp/claude-0/h-${vp.width}-a.png`});
await p.click('.hotel-set');await p.waitForTimeout(300);
await p.fill('#h-name','Albergo Test');await p.fill('#h-link','43.8445, 10.4985');await p.waitForTimeout(100);
await p.screenshot({path:`/tmp/claude-0/h-${vp.width}-b.png`});
await p.click('#h-save');await p.waitForTimeout(300);
console.log(vp.width,'hotel:',await p.evaluate(()=>[byId('hotel').name,byId('hotel').ll,localStorage.getItem('trip-hotel-lucca'),document.querySelector('#drawer h3').textContent,shareData().hotel&&shareData().hotel.name]));
await p.evaluate(()=>openSpot('guinigi'));await p.click('.rt-tab[data-tab=tips]');
console.log(vp.width,'line2:',await p.evaluate(()=>[...document.querySelectorAll('#drawer dt')].find(d=>d.textContent=='從住宿出發')?.nextElementSibling.innerText));
await p.reload();await p.waitForTimeout(700);
console.log(vp.width,'after reload:',await p.evaluate(()=>[byId('hotel').name, byId('hotel').marker.getLatLng()]));
await p.evaluate(()=>openSpot('hotel'));await p.click('#h-reset');await p.waitForTimeout(200);
console.log(vp.width,'reset:',await p.evaluate(()=>[byId('hotel').name,localStorage.getItem('trip-hotel-lucca')]));
// tour step
await p.evaluate(()=>closeSpot());await p.evaluate(()=>TOUR.start());await p.waitForTimeout(900);await p.click('.tour-next');await p.waitForTimeout(1300);await p.click('.tour-next');await p.waitForTimeout(1300);
console.log(vp.width,'tour:',await p.evaluate(()=>document.querySelector('.tour-card h3').textContent));
await p.screenshot({path:`/tmp/claude-0/h-${vp.width}-c.png`});
console.log(errs);await c.close();}
await b.close();})();
