const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
  p.on('pageerror', e=>console.log('ERR', e.message));
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(1000);
  const bb = await (await p.$('.spot[data-id="michele"] .tab')).boundingBox();
  await p.touchscreen.tap(bb.x + 20, bb.y + 10); await p.waitForTimeout(600);
  console.log('tap', await p.evaluate(() => !document.getElementById('drawer').hidden && document.getElementById('d-name').textContent));
 await b.close(); })();
