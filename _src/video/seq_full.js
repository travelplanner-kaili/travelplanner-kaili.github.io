// full promo sequence (times in real seconds; recorder slows the page)
module.exports = async (p, H) => {
  const LL = id => p.evaluate(id => LL[id], id);
  // S1 overview -> fly to Trevi
  await H.wait(1300);
  await H.fly(await LL('trevi'), 15.95, 1.1); await H.wait(1350);
  // S2 tap Trevi -> drawer
  H.mark('tap1'); await H.tapSpot('trevi'); await H.wait(2200);
  // S3 實用資訊 tab
  H.mark('tips'); await H.tapSel('#drawer .rt-tab[data-tab=tips]'); await H.wait(900);
  await p.evaluate(() => { const d = document.getElementById('drawer'); d.scrollBy({ top: 260, behavior: 'smooth' }); }); await H.wait(1900);
  H.mark('close1'); await H.tapSel('#d-close'); await H.wait(600);
  // S4 City Walk
  H.mark('walk'); await H.tapSel('#fs-route-btn'); await H.wait(900);
  await H.fly(await p.evaluate(() => ROUTES.find(r => r.id === 'bernini-walk').pill), 15.3, 0.9); await H.wait(1100);
  const pill = await p.evaluate(() => { const r = ROUTES.find(r => r.id === 'bernini-walk'); const e = r.pillM.getElement(); const b = (e.querySelector('span') || e).getBoundingClientRect(); return [b.x + b.width / 2, b.y + b.height / 2]; });
  H.mark('pill'); await p.screenshot({path:'/home/claude/video/dbg_pill.jpg',type:'jpeg'}); console.log('pill at',pill); await H.tap(pill); await H.wait(300); if (!(await p.evaluate(() => !document.getElementById('drawer').hidden && document.getElementById('drawer').dataset.route))) { console.log('pill miss'); await p.evaluate(() => openRoute('bernini-walk')); } await H.wait(2300);
  H.mark('close2'); await H.tapSel('#d-close'); await H.wait(500);
  await H.tapSel('#fs-route-btn'); await H.wait(500);   // City Walk off
  // S4b 點對點: tap two spots, the card shows the real walking distance
  H.mark('dist');
  await H.fly(await p.evaluate(() => [(LL.pantheon[0] + LL.trevi[0]) / 2, (LL.pantheon[1] + LL.trevi[1]) / 2]), 15.75, 0.8); await H.wait(950);
  await H.tapSel('#fs-dist-btn'); await H.wait(700);
  for (const id of ['pantheon', 'trevi']) {
    await H.tap(await H.xy(id)); await H.wait(900);
  }
  await H.wait(2400);
  H.mark('distoff'); await H.tapSel('#fs-dist-btn'); await H.wait(500);
  // S5 add three spots to day 1 from the drawer, then open 我的行程
  H.mark('plan');
  await H.fly(await LL('pantheon'), 15.6, 0.8); await H.wait(1000);
  for (const id of ['pantheon', 'trevi', 'spagna']) {
    await H.tapSpot(id); await H.wait(350);
    await H.tapSel('#drawer .plan-day'); await H.wait(650);
    await H.tapSel('#d-close'); await H.wait(450);
  }
  H.mark('tab'); await H.tapSel('.plan-tab'); await H.wait(2800);
  H.mark('end');
};
module.exports.pre = async p => { await p.evaluate(() => map.setView([41.8995, 12.4795], 15.4, { animate: false })); await p.waitForTimeout(900); };
