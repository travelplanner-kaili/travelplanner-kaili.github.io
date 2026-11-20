const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(900);
  await p.evaluate(() => document.querySelector('.mapbox').scrollIntoView());
  await (await p.$('.spot[data-id="michele"] .tab')).dblclick(); await p.waitForTimeout(600);
  console.log(await p.evaluate(() => { const c = document.querySelector('path.rad-circle'); const r = c.getBoundingClientRect(); const s = c.ownerSVGElement.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), Math.round(s.width), Math.round(s.height)]; }));
  await p.screenshot({ path: 'rad.png', clip: { x: 0, y: 0, width: 1280, height: 900 } });
  await b.close(); })();
