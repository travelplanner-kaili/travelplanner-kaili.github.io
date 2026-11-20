const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  p.on('pageerror', e=>console.log('ERR', e.message));
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(900);
  await p.evaluate(() => { document.querySelector('.mapbox').scrollIntoView(); ['michele','ore','guinigi','anfiteatro'].forEach(i => planToggle('0203', i)); plan.days['0203'][0].time = '09:30'; plan.days['0203'][0].note = '先拍立面'; savePlan(); setPlanOpen(true); }); await p.waitForTimeout(500);
  for (const k of [0,1,2]) { const el = await p.$('#plan'); await el.screenshot({ path: `lv${k}.png` }); await p.click('#plan-lv'); await p.waitForTimeout(200); }
  console.log(await p.textContent('#plan-lv'));
  await b.close(); })();
