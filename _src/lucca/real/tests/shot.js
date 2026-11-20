const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
 for (const [w,h,o] of [[1280,900,'d'],[390,844,'m']]) {
  const p = await b.newPage({ viewport: { width: w, height: h } }); const errs=[]; p.on('pageerror', e=>errs.push(e.message)); p.on('console', m=>{ if(m.type()==='error') errs.push(m.text().slice(0,120)); });
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(1500);
  await p.screenshot({ path: `s_${o}1.png` });
  await p.evaluate(() => { planToggle('0203','duomo'); planToggle('0203','guinigi'); planToggle('0203','anfiteatro'); setPlanOpen(true); });
  await p.waitForTimeout(800); await p.screenshot({ path: `s_${o}2.png` });
  await p.evaluate(() => { setPlanOpen(false); openSpot('michele'); }); await p.waitForTimeout(400); await p.screenshot({ path: `s_${o}3.png` });
  console.log(o, errs.filter(e=>!/ERR_|Failed to load/.test(e)));
 }
 await b.close(); })();
