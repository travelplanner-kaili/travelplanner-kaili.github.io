const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(900);
  await p.evaluate(() => { document.querySelector('.mapbox').scrollIntoView(); openSpot('anfiteatro'); }); await p.waitForTimeout(500);
  console.log(await p.evaluate(() => { const r = document.getElementById('drawer').getBoundingClientRect(); const e = document.elementFromPoint(r.left + 60, r.top + 500); return e.closest('#drawer') ? 'drawer on top' : 'covered by ' + e.className; }));
  await b.close(); })();
