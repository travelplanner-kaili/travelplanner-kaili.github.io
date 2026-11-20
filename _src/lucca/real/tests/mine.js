const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  p.on('pageerror', e=>console.log('ERR', e.message));
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(800);
  await p.evaluate(() => document.querySelector('.mapbox').scrollIntoView()); await p.waitForTimeout(200);
  // 1) right-click on empty map
  const mb = await (await p.$('#lmap')).boundingBox();
  await p.mouse.click(mb.x + mb.width - 300, mb.y + 120, { button: 'right' }); await p.waitForTimeout(300);
  console.log('form open:', await p.evaluate(() => !document.getElementById('plan-add').hidden), await p.textContent('#pa-where'));
  await p.fill('#pa-name', '午餐 Buca'); await p.click('#pa-ok'); await p.waitForTimeout(300);
  // 2) google link paste
  await p.click('#plan-addbtn'); await p.fill('#pa-link', 'https://www.google.com/maps/place/Buca+di+Sant\'Antonio/@43.8436,10.5012,17z/data=!3m1!4b1!4m6!3m5!1s0x0:0x0!8m2!3d43.8435771!4d10.5013549');
  await p.waitForTimeout(200); console.log('link:', await p.inputValue('#pa-name'), '|', await p.textContent('#pa-where'));
  await p.click('#pa-ok'); await p.waitForTimeout(300);
  // 3) short link message
  await p.click('#plan-addbtn'); await p.fill('#pa-link', 'https://maps.app.goo.gl/abc123'); await p.waitForTimeout(100); console.log('short:', (await p.textContent('#pa-where')).slice(0, 30)); await p.click('#pa-cancel');
  console.log('plan:', await p.evaluate(() => plan.days[plan.cur].map(x => byId(x.id).name).join(' → ')), 'mine:', await p.evaluate(() => MINE.length));
  await p.screenshot({ path: 'mine.png' });
  // open + delete
  const id = await p.evaluate(() => MINE[0].id); await p.evaluate(id => openSpot(id), id); await p.waitForTimeout(200);
  console.log('drawer:', await p.textContent('#d-name'), await p.getAttribute('.icon-act', 'href'));
  await p.click('#d-delmine'); await p.click('#d-delmine'); await p.waitForTimeout(200);
  console.log('after del mine:', await p.evaluate(() => MINE.length), await p.evaluate(() => plan.days[plan.cur].length));
  await p.reload(); await p.waitForTimeout(800); console.log('persist:', await p.evaluate(() => MINE.map(m => m.name).join(',')));
  await b.close(); })();
