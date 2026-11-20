# ---- 小提醒 tab in every spot drawer (practical tips + the orange warning move there) ----
rep('''    ${s.warn ? `<div class="warn">⚠ ${esc(s.warn)}</div>` : ""}
    <dl>
      <div><dt>特色</dt><dd>${esc(s.feature)}</dd></div>
      ${s.tips ? `<div><dt>看點</dt><dd><ul>${s.tips.map(t => `<li>${esc(t)}</li>`).join("")}</ul></dd></div>` : ""}''',
'''    ${hasRemind ? `<div class="rt-tabs" role="tablist"><button class="rt-tab" role="tab" data-tab="info" aria-selected="true">介紹</button><button class="rt-tab" role="tab" data-tab="tips" aria-selected="false">💡 小提醒${s.warn ? '<span class="tab-alert" aria-label="有重要提醒">!</span>' : ""}</button></div>
    <div class="rt-panel" data-panel="tips" hidden>
      ${s.warn ? `<div class="warn">⚠ ${esc(s.warn)}</div>` : ""}
      ${remind.length ? `<ul>${remind.map(t => `<li>${esc(t)}</li>`).join("")}</ul>` : ""}
    </div>` : ""}
    <div class="rt-panel" data-panel="info">
    ${s.warn ? `<button class="warn-jump" type="button">⚠ 有開放時間限制，點這裡看「小提醒」</button>` : ""}
    <dl>
      <div><dt>特色</dt><dd>${esc(s.feature)}</dd></div>
      ${tips.length ? `<div><dt>看點</dt><dd><ul>${tips.map(t => `<li>${esc(t)}</li>`).join("")}</ul></dd></div>` : ""}''')
rep('''      ${s.pass ? `<div><dt>聯票包含</dt><dd><ul>${s.pass.map(p => `<li>${esc(p)}</li>`).join("")}</ul></dd></div>` : ""}
    </dl>`;
  drawer.hidden = false; scrim.hidden = false;
  document.getElementById("d-close").addEventListener("click", closeSpot);''',
'''      ${s.pass ? `<div><dt>聯票包含</dt><dd><ul>${s.pass.map(p => `<li>${esc(p)}</li>`).join("")}</ul></dd></div>` : ""}
    </dl></div>`;
  drawer.hidden = false; scrim.hidden = false;
  document.getElementById("d-close").addEventListener("click", closeSpot);
  bindTabs();''')
rep('''  drawer.style.setProperty("--c", CAT[s.cat].color);
  drawer.innerHTML = `''', '''  drawer.style.setProperty("--c", CAT[s.cat].color);
  const rIdx = REMIND[s.id] || [];
  const tips = (s.tips || []).filter((t, i) => !rIdx.includes(i));
  const remind = (s.tips || []).filter((t, i) => rIdx.includes(i)).concat(EXTRA_REMIND[s.id] || []);
  const hasRemind = !!(s.warn || remind.length);
  drawer.innerHTML = `''')
rep('function openSpot(id) {', '''// tips (by index) that are practical reminders -> shown in the 小提醒 tab
const REMIND = { giusto: [0, 1], alessandro: [0], mura: [0, 1] };
// extra reminders written from each spot's own hours / price data
const EXTRA_REMIND = {
  duomo: ["最後入場是休館前 30 分鐘；特殊宗教儀式期間開放時間可能調整。", "全見聯票 €10 一次包含主教座堂、鐘樓、主教座堂博物館、聖若望和雷帕拉塔教堂，現場可刷卡，買一次就好。"],
  campanile: ["含在主教座堂全見聯票內，不用另外買票。", "上午順光，俯瞰城景最清晰。"],
  museo: ["含在主教座堂全見聯票內，不用另外買票。", "可以和聖若望和雷帕拉塔教堂一起走完。"],
  giovanni: ["含在主教座堂全見聯票內，不用另外買票。", "最後入場是休館前 30 分鐘。"],
  guinigi: ["可買市立雙塔聯票，和時鐘塔一起買；現場售票處可刷卡。", "中午不休息，正好避開其他小景點的午休和餐廳尖峰。"],
  ore: ["建議和圭尼吉塔一起買市立聯票；現場售票處可刷卡。"],
  frediano: ["入內約 €4，獨立售票，不包含在大教堂聯票內。"],
  piazzamichele: ["下午順光時拍教堂立面最漂亮。"],
  anfiteatro: ["清晨 08:00～09:00 人最少，適合拍空景。"],
  shopping: ["街上商店通常 19:30 打烊；下午 16:00 後最熱鬧。"],
};
function showTab(tab) {
  drawer.querySelectorAll(".rt-tab").forEach(x => x.setAttribute("aria-selected", x.dataset.tab === tab));
  drawer.querySelectorAll(".rt-panel").forEach(p => p.hidden = p.dataset.panel !== tab);
  drawer.scrollTop = 0;
}
function bindTabs() {
  drawer.querySelectorAll(".rt-tab").forEach(b => b.addEventListener("click", () => showTab(b.dataset.tab)));
  drawer.querySelector(".warn-jump")?.addEventListener("click", () => showTab("tips"));
}
function openSpot(id) {''')
rep('.warn { background: var(--warn-bg);', """.rt-tabs { display: flex; margin: 4px 0 18px; border-bottom: 1px solid var(--line); }
.rt-tab { font: 700 15px var(--f-body); padding: 9px 12px; white-space: nowrap; background: none; border: 0; border-bottom: 3px solid transparent; margin-bottom: -1px; color: var(--muted); cursor: pointer; }
.rt-tab[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--c, var(--ink)); }
.rt-tab:focus-visible { outline: 2px solid var(--ink); outline-offset: -3px; }
.rt-panel[data-panel="tips"] > ul { margin: 0; padding-left: 1.2em; display: flex; flex-direction: column; gap: 10px; line-height: 1.7; }
.tab-alert { display: inline-grid; place-items: center; width: 18px; height: 18px; margin-left: 6px; border-radius: 50%; background: var(--warn-fg); color: var(--warn-bg); font-size: 12px; font-weight: 800; vertical-align: 2px; }
.warn-jump { display: block; width: 100%; text-align: left; font: 600 14px var(--f-body); padding: 9px 12px; margin: 0 0 16px; border-radius: 4px; border: 0; background: var(--warn-bg); color: var(--warn-fg); cursor: pointer; }
.warn { background: var(--warn-bg);""")

rep('<style>\n', '<style>\n/* hidden must win even where the page is shown without the artifact wrapper (e.g. project file preview) */\n[hidden] { display: none !important; }\n')
