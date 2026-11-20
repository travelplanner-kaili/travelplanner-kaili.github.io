const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
 for (const [w,h,touch] of [[1280,900,false],[390,844,true]]) {
  const p = await b.newPage({ viewport: { width: w, height: h }, hasTouch: touch, isMobile: touch });
  p.on('pageerror', e=>console.log('ERR', e.message));
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(1000);
  const el = await p.$('.spot[data-id="duomo"] .tab');
  if (touch) await el.tap(); else await el.click();
  await p.waitForTimeout(600);
  console.log(w, await p.evaluate(() => !document.getElementById('drawer').hidden && document.getElementById('d-name').textContent));
  if (!touch) { await p.evaluate(() => closeSpot()); await el.dblclick(); await p.waitForTimeout(500); console.log('rad', await p.evaluate(() => RAD.id + ' ' + RAD.r + ' drawer:' + !document.getElementById('drawer').hidden)); }
 }
 await b.close(); })();
