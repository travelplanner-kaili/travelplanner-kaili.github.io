const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto('file:///home/claude/lucca/real/lucca-real.html'); await p.waitForTimeout(800);
  await p.evaluate(() => { planToggle('0203','ore'); planToggle('0203','guinigi'); setPlanOpen(true); }); await p.waitForTimeout(300);
  const out = [];
  for (const v of ['1415', '9:5', '930', '25:00']) { const t = (await p.$$('.p-time'))[1]; await t.fill(v); await t.press('Tab'); out.push(v + '→' + await t.inputValue()); }
  console.log(out.join('  ')); await b.close(); })();
