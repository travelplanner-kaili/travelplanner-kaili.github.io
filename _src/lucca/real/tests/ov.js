const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
 for (const [w,h,o] of [[1280,900,'d'],[390,844,'m']]) {
  const p = await b.newPage({ viewport: { width: w, height: h } }); p.on('pageerror', e=>console.log('ERR', e.message));
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(900);
  for (const z of [15, 15.75, 16.5, 17.5]) {
    await p.evaluate(z => map.setZoom(z, { animate: false }), z); await p.waitForTimeout(300);
    const r = await p.evaluate(() => { const bs = [...document.querySelectorAll('.spot:not(.gone):not(.lbl-off) .tab')].map(t => t.getBoundingClientRect()).filter(r => r.width);
      let ov = 0; for (let i = 0; i < bs.length; i++) for (let j = i + 1; j < bs.length; j++) { const a = bs[i], c = bs[j]; if (a.left < c.right && a.right > c.left && a.top < c.bottom && a.bottom > c.top) ov++; }
      return { shown: bs.length, off: document.querySelectorAll('.spot.lbl-off').length, slim: document.querySelectorAll('.spot.slim1').length, ov }; });
    console.log(o, z, JSON.stringify(r));
    if (z === 16.5) await p.screenshot({ path: `ov_${o}.png` });
  }
 }
 await b.close(); })();
