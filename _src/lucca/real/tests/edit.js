const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  p.on('pageerror', e=>console.log('ERR', e.message));
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(800);
  await p.evaluate(() => document.querySelector('.mapbox').scrollIntoView());
  await p.evaluate(() => setPlanOpen(true)); await p.click('#plan-addbtn'); await (await p.$('#plan-add')).screenshot({ path: 'form.png' });
  await p.fill('#pa-name', 'Gelato'); await p.fill('#pa-link', '43.8429, 10.5027'); await p.click('#pa-ok'); await p.waitForTimeout(200);
  const id = await p.evaluate(() => MINE[0].id); await p.evaluate(id => openSpot(id), id);
  await p.click('#d-editmine'); await p.fill('#me-name', 'Gelateria'); await p.fill('#me-note', '開心果口味'); await p.fill('#me-link', '43.8440, 10.5040'); await p.click('#me-save'); await p.waitForTimeout(200);
  console.log(await p.evaluate(() => [MINE[0].name, MINE[0].note, MINE[0].ll.join(','), document.getElementById('d-name').textContent]));
  await p.screenshot({ path: 'drawer-mine.png', clip: { x: 850, y: 0, width: 430, height: 520 } });
  // map pick re-edit
  await p.click('#d-editmine'); await p.click('#me-pick'); const mb = await (await p.$('#lmap')).boundingBox(); await p.mouse.click(mb.x + 700, mb.y + 400); await p.waitForTimeout(300);
  console.log(await p.textContent('#me-where')); await p.click('#me-save'); await p.waitForTimeout(200);
  console.log('ll after pick', await p.evaluate(() => MINE[0].ll.map(x => x.toFixed(4)).join(',')));
  await p.click('#d-unplan'); console.log('days after unplan', await p.evaluate(() => Object.values(plan.days).flat().length), 'mine', await p.evaluate(() => MINE.length));
  await b.close(); })();
