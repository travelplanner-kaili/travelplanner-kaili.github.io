import json
h = open("/home/claude/lucca/base.html").read()
d = json.load(open("/home/claude/lucca/dist.json"))
def rep(a, c):
    global h
    assert h.count(a) == 1, ("not unique/missing", a[:80], h.count(a))
    h = h.replace(a, c)

# 1) category rename
rep('<span class="dot"></span>免費小教堂</button>', '<span class="dot"></span>免費景點</button>')
rep('free: { label: "免門票小教堂", color: "var(--free)" }', 'free: { label: "免費景點", color: "var(--free)" }')

# 2) distance mode
rep('.chip.sup .dot {', '''.chip.dist { border-color: var(--ink); font-weight: 700; }
.chip.dist[aria-pressed="false"] { opacity: 1; }
.chip.dist[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.chip.dist svg { width: 14px; height: 14px; }
.dist-bar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin: 0 0 10px; font-size: 13.5px; background: var(--paper); border: 1px solid var(--line); border-left: 3px solid var(--ink); padding: 8px 12px; border-radius: 4px; }
.dist-bar p { margin: 0; flex: 1 1 320px; min-width: 0; }
.seg { display: inline-flex; border: 1.5px solid var(--ink); border-radius: 999px; overflow: hidden; flex: none; }
.seg-btn { font: 700 13px var(--f-body); padding: 5px 14px; background: var(--paper); color: var(--ink); border: 0; cursor: pointer; }
.seg-btn[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.seg-btn:focus-visible { outline: 2px solid var(--free); outline-offset: -3px; }
.p2p-line { stroke: var(--paid); stroke-width: 3; stroke-dasharray: 2 8; stroke-linecap: round; fill: none; }
.p2p-pill { fill: var(--paid); }
.p2p-card { position: absolute; left: 12px; top: 12px; z-index: 2; max-width: calc(100% - 24px); box-sizing: border-box; display: flex; flex-direction: column; gap: 2px; padding: 10px 16px; border-radius: 12px; background: var(--paid); color: var(--paper); box-shadow: 0 4px 16px var(--shadow); pointer-events: none; }
.p2p-route { font: 500 15px/1.4 var(--f-body); overflow-wrap: anywhere; }
.p2p-dist { font: 700 28px/1.2 var(--f-body); font-variant-numeric: tabular-nums; }
.p2p-dist small { font-size: 14px; font-weight: 500; margin-left: 6px; }
@media (max-width: 640px) { .p2p-card { left: 8px; right: 8px; top: 8px; max-width: none; padding: 8px 14px; } .p2p-dist { font-size: 24px; } }
@media (max-width: 860px) { .p2p-lbl { display: none; } }
.p2p-text { font: 700 16px var(--f-body); fill: var(--paper); font-variant-numeric: tabular-nums; }
#map.dist .t-more { display: none; }
#map.dist .spot.picked .tab { stroke-width: 3; fill: var(--bg); }
.edge line { stroke: var(--ink); stroke-opacity: .6; stroke-width: 3; stroke-dasharray: 2 6; stroke-linecap: round; }
.edge .conn { stroke-width: 1; stroke-dasharray: none; stroke-opacity: .4; }
.edge rect { fill: var(--paper); stroke: var(--line); stroke-width: 1; }
.edge text { font: 500 15px var(--f-body); fill: var(--ink); font-variant-numeric: tabular-nums; }
.edge:not(.on) { display: none; }
.edge.dim { opacity: .12; }
.chip.sup .dot {''')
rep('''      <button class="chip sup" id="f-sup"''', '''      <button class="chip dist" id="f-dist" aria-pressed="false"><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="3" cy="13" r="2" fill="currentColor"/><circle cx="13" cy="3" r="2" fill="currentColor"/><path d="M4.5 11.5 L11.5 4.5" stroke="currentColor" stroke-width="1.6" stroke-dasharray="1.5 2.5" stroke-linecap="round"/></svg>距離模式</button>
      <button class="chip sup" id="f-sup"''')
rep('''  <div class="mapbox">''', '''  <div class="dist-bar" id="dist-note" hidden><div class="seg" role="group" aria-label="距離顯示方式"><button class="seg-btn" data-sub="p2p" aria-pressed="true">點到點</button><button class="seg-btn" data-sub="all" aria-pressed="false">全部顯示</button></div><p id="dist-text">先點起點，會顯示它到相鄰景點的距離；再點終點，就畫出兩點之間的距離與步行時間。點空白處重新選。步行距離以直線距離 ×1.3 估算，步速每分鐘 80 公尺；實際路線請以 Google 地圖導航為準。</p></div>
  <div class="mapbox">''')
rep('''      <g id="base"></g>
      <g id="spots"></g>''', '''      <g id="base"></g>
      <g id="edges" hidden></g>
      <g id="spots"></g>''')
rep('''/* ---- Wednesday hours ---- */''', "/* ---- Distance mode data ---- */\nconst SIMPLE = " + json.dumps(d["simple"]) + ";\nconst EDGES = " + json.dumps(d["edges"], ensure_ascii=False) + ";\n\n/* ---- Wednesday hours ---- */")
rep('tw = el("text", { class: "t-wed",', 'tw = el("text", { class: "t-wed t-more",')
rep('t2 = el("text", { class: "t-time",', 't2 = el("text", { class: "t-time t-more",')
rep('const t3 = el("text", { class: "t-price",', 'const t3 = el("text", { class: "t-price t-more",')
rep('''  s.g = g; s.tab = tab; s.leader = leader; s.texts = [t1, tw, t2, t3].filter(Boolean); s.timeText = t2;
  g.addEventListener("click", () => openSpot(s.id));
  g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openSpot(s.id); } });''',
'''  s.g = g; s.tab = tab; s.leader = leader; s.t1 = t1; s.texts = [t1, tw, t2, t3].filter(Boolean); s.timeText = t2;
  [s.slx, s.sly] = SIMPLE[s.id];
  const act = () => distMode ? pickSpot(s.id) : openSpot(s.id);
  g.addEventListener("click", e => { e.stopPropagation(); act(); });
  g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); act(); } });''')
rep('''function sizeTabs() {
  SPOTS.forEach(s => {
    let w = 0;
    s.texts.forEach(t => { try { w = Math.max(w, t.getComputedTextLength()); } catch (e) { w = Math.max(w, 180); } });
    if (!w) w = 180;
    const W = w + 24, H = s.H;
    s.tab.setAttribute("width", W); s.tab.setAttribute("height", H);
    const cx = Math.max(s.lx, Math.min(s.x, s.lx + W));
    const cy = Math.max(s.ly, Math.min(s.y, s.ly + H));''',
'''function sizeTabs() {
  SPOTS.forEach(s => {
    const lx = distMode ? s.slx : s.lx, ly = distMode ? s.sly : s.ly;
    let w = 0;
    (distMode ? [s.t1] : s.texts).forEach(t => { try { w = Math.max(w, t.getComputedTextLength()); } catch (e) { w = Math.max(w, 180); } });
    if (!w) w = 180;
    const W = w + 24, H = distMode ? 36 : s.H;
    s.tab.setAttribute("x", lx); s.tab.setAttribute("y", ly);
    s.tab.setAttribute("width", W); s.tab.setAttribute("height", H);
    s.t1.setAttribute("x", lx + 12); s.t1.setAttribute("y", ly + 25);
    const cx = Math.max(lx, Math.min(s.x, lx + W));
    const cy = Math.max(ly, Math.min(s.y, ly + H));''')
rep('''sizeTabs();
if (document.fonts''', '''let distMode = false;
sizeTabs();
if (document.fonts''')
# distance-mode wiring, before Filters
rep('''/* ---- Filters ---- */''', '''/* ---- Distance mode ---- */
const edgeLayer = document.getElementById("edges");
EDGES.forEach(e => {
  const g = el("g", { class: "edge" }, edgeLayer);
  el("line", { x1: e.a[0], y1: e.a[1], x2: e.b[0], y2: e.b[1] }, g);
  if (e.box) {
    const cx = (e.box[0] + e.box[2]) / 2, cy = (e.box[1] + e.box[3]) / 2;
    if (Math.hypot(cx - e.anc[0], cy - e.anc[1]) > 16) el("line", { class: "conn", x1: e.anc[0], y1: e.anc[1], x2: cx, y2: cy }, g);
    el("rect", { x: e.box[0], y: e.box[1], width: e.box[2] - e.box[0], height: e.box[3] - e.box[1], rx: 12 }, g);
    const t = el("text", { x: cx, y: cy + 5, "text-anchor": "middle" }, g); t.textContent = e.text;
  }
  e.g = g;
});
const mapSvg = document.getElementById("map");
let picked = null, pairEnd = null, sub = "p2p";
const M_PER_UNIT = 1;
const NOTES = { p2p: "先點起點，會顯示它到相鄰景點的距離；再點終點，就畫出兩點之間的距離與步行時間。點空白處重新選。", all: "顯示所有相鄰景點之間的步行距離與時間。" }, NOTE_TAIL = "步行距離以直線距離 ×1.3 估算，步速每分鐘 80 公尺；實際路線請以 Google 地圖導航為準。";
const p2pLine = el("g", {}); mapSvg.insertBefore(p2pLine, document.getElementById("spots"));
const p2pLabel = el("g", { class: "p2p-lbl" }, mapSvg);
function walkText(units) {
  const m = units * M_PER_UNIT * 1.3;
  const w = m < 100 ? Math.round(m / 10) * 10 : Math.round(m / 50) * 50;
  return (w < 1000 ? w + " m" : (w / 1000).toFixed(1) + " km") + "・" + Math.max(1, Math.round(w / 80)) + " 分";
}
function renderDist() {
  SPOTS.forEach(s => s.g.classList.toggle("picked", sub === "p2p" && (s.id === picked || s.id === pairEnd)));
  EDGES.forEach(e => e.g.classList.toggle("on", sub === "all" || (!!picked && !pairEnd && e.ids.includes(picked))));
  p2pLine.replaceChildren(); p2pLabel.replaceChildren();
  const card = document.getElementById("p2p-card");
  card.hidden = !(sub === "p2p" && picked && pairEnd);
  const nm = id => SPOTS.find(s => s.id === id).name;
  const dt = document.getElementById("dist-text");
  if (sub === "p2p") dt.textContent = !picked ? NOTES.p2p + NOTE_TAIL
    : !pairEnd ? "起點：" + nm(picked) + "。再點另一個景點當終點，就會顯示兩點之間的距離；點空白處取消。"
    : "起點 " + nm(picked) + " → 終點 " + nm(pairEnd) + "。點空白處可重新選起點。";
  if (sub !== "p2p" || !picked || !pairEnd) return;
  const a = SPOTS.find(s => s.id === picked), b = SPOTS.find(s => s.id === pairEnd);
  el("line", { class: "p2p-line", x1: a.x, y1: a.y, x2: b.x, y2: b.y }, p2pLine);
  const cx = (a.x + b.x) / 2, cy = (a.y + b.y) / 2;
  const pill = el("rect", { class: "p2p-pill" }, p2pLabel);
  const t = el("text", { class: "p2p-text", x: cx, y: cy + 5.8, "text-anchor": "middle" }, p2pLabel);
  const wt = walkText(Math.hypot(b.x - a.x, b.y - a.y));
  t.textContent = a.name + " → " + b.name + "　" + wt;
  document.getElementById("p2p-route").textContent = a.name + " → " + b.name;
  document.getElementById("p2p-dist").innerHTML = wt.replace("・", " ・ ") + "<small>步行估算</small>";
  let w = 300; try { w = t.getComputedTextLength() + 19; } catch (e) {}
  pill.setAttribute("x", cx - w / 2); pill.setAttribute("y", cy - 28 / 2);
  pill.setAttribute("width", w); pill.setAttribute("height", 28); pill.setAttribute("rx", 28 / 2);
}
function pickSpot(id) {
  if (id === null) { picked = pairEnd = null; }
  else if (sub !== "p2p") return;
  else if (!picked || pairEnd) { picked = id; pairEnd = null; }
  else if (id === picked) { picked = null; }
  else { pairEnd = id; }
  renderDist();
}
document.querySelectorAll(".seg-btn").forEach(b => b.addEventListener("click", () => {
  sub = b.dataset.sub;
  document.querySelectorAll(".seg-btn").forEach(x => x.setAttribute("aria-pressed", x === b));
  document.getElementById("dist-text").textContent = NOTES[sub] + NOTE_TAIL;
  pickSpot(null);
}));
document.getElementById("f-dist").addEventListener("click", ev => {
  distMode = !distMode;
  ev.currentTarget.setAttribute("aria-pressed", distMode);
  mapSvg.classList.toggle("dist", distMode);
  edgeLayer.toggleAttribute("hidden", !distMode);
  document.getElementById("dist-note").hidden = !distMode;
  pickSpot(null);
  sizeTabs();
});
mapSvg.addEventListener("click", () => { if (distMode && sub === "p2p" && picked) pickSpot(null); });
const syncEdges = () => EDGES.forEach(e => e.g.classList.toggle("dim", e.ids.some(id => SPOTS.find(s => s.id === id).g.classList.contains("dim"))));

/* ---- Filters ---- */''')
rep('document.querySelectorAll(".chip").forEach(ch => {', 'document.querySelectorAll(".chip:not(.dist)").forEach(ch => {')
rep('''    applySup();
    syncArea();
  });''', '''    applySup();
    syncArea(); syncEdges();
  });''')
rep('''    <div class="zoom">''', '''    <div class="p2p-card" id="p2p-card" hidden aria-live="polite"><span class="p2p-route" id="p2p-route"></span><span class="p2p-dist" id="p2p-dist"></span></div>
    <div class="zoom">''')
VISITED_PAIRS = [('.chip.sup .dot {', '.chip.done { border-style: dashed; border-color: var(--open); }\n.chip.done[aria-pressed="false"] { opacity: 1; }\n.chip.done[aria-pressed="true"] { background: var(--open); color: var(--paper); border-style: solid; }\n.visit-btn { display: inline-flex; align-items: center; gap: 6px; margin: 0 0 16px; padding: 7px 16px; border-radius: 999px; border: 1.5px solid var(--open); background: var(--paper); color: var(--open); font: 700 14px var(--f-body); cursor: pointer; }\n.visit-btn[aria-pressed="true"] { background: var(--open); color: var(--paper); }\n.visit-btn:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }\n.spot.visited { opacity: .45; }\n.spot.visited .tab { stroke-dasharray: 5 4; }\n.spot.hide-v, .area.hide-v, .edge.hide-v { display: none; }\n.chip.sup .dot {'), ('<button class="chip sup" id="f-sup"', '<button class="chip done" id="f-done" hidden aria-pressed="false" title="去過的景點記在這台裝置的瀏覽器裡">顯示去過的景點（<span id="done-n">0</span>）</button>\n      <button class="chip sup" id="f-sup"'), ('/* ---- Drawer ---- */', '/* ---- Visited ---- */\nconst VKEY = "trip-visited-lucca";\nlet visited = new Set();\ntry { visited = new Set(JSON.parse(localStorage.getItem(VKEY) || "[]")); } catch (e) {}\nlet showDone = false;\nconst saveVisited = () => { try { localStorage.setItem(VKEY, JSON.stringify([...visited])); } catch (e) {} };\nfunction applyVisited() {\n  const hid = id => visited.has(id) && !showDone;\n  SPOTS.forEach(s => {\n    s.g.classList.toggle("visited", visited.has(s.id));\n    s.g.classList.toggle("hide-v", hid(s.id));\n    if (s.areaEl) s.areaEl.classList.toggle("hide-v", hid(s.id));\n  });\n  EDGES.forEach(e => e.g.classList.toggle("hide-v", e.ids.some(hid)));\n  const n = visited.size, chip = document.getElementById("f-done");\n  if (n === 0) showDone = false;\n  chip.hidden = n === 0;\n  document.getElementById("done-n").textContent = n;\n  chip.setAttribute("aria-pressed", showDone);\n}\ndocument.getElementById("f-done").addEventListener("click", () => { showDone = !showDone; applyVisited(); });\napplyVisited();\n\n/* ---- Drawer ---- */'), ('<p class="latin">${esc(s.latin)}</p>', '<p class="latin">${esc(s.latin)}</p>\n    ${s.cat !== "base" ? `<button class="visit-btn" id="d-visit" aria-pressed="${visited.has(s.id)}">${visited.has(s.id) ? "✓ 已去過（點一下取消）" : "標記為已去過"}</button>` : ""}'), ('document.getElementById("d-close").addEventListener("click", closeSpot);', 'document.getElementById("d-close").addEventListener("click", closeSpot);\n  document.getElementById("d-visit")?.addEventListener("click", () => {\n    if (visited.has(s.id)) visited.delete(s.id); else visited.add(s.id);\n    saveVisited(); applyVisited();\n    if (visited.has(s.id) && !showDone) closeSpot(); else openSpot(s.id);\n  });'), ('document.querySelectorAll(".chip:not(.dist)")', 'document.querySelectorAll(".chip:not(.dist):not(.done)")')]
for a, c in VISITED_PAIRS: rep(a, c)
rep('<span class="dot"></span>補充景點</button>', '<span class="dot"></span>附加景點</button>')
GMAP_PAIRS = [('    ${s.cat !== "base" ? `<button class="visit-btn" id="d-visit" aria-pressed="${visited.has(s.id)}">${visited.has(s.id) ? "✓ 已去過（點一下取消）" : "標記為已去過"}</button>` : ""}', '    <div class="d-actions">${s.cat !== "base" ? `<button class="visit-btn" id="d-visit" aria-pressed="${visited.has(s.id)}">${visited.has(s.id) ? "✓ 已去過（點一下取消）" : "標記為已去過"}</button>` : ""}<a class="gmap" href="${esc(gmapUrl(s))}" target="_blank" rel="noopener"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5a4.5 4.5 0 0 0-4.5 4.5c0 3.4 4.5 8.5 4.5 8.5s4.5-5.1 4.5-8.5A4.5 4.5 0 0 0 8 1.5zm0 6.2a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4z" fill="currentColor"/></svg>Google 地圖 ↗</a></div>'), ('.visit-btn[aria-pressed="true"]', '.d-actions { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 16px; }\n.d-actions .visit-btn { margin: 0; }\n.gmap { display: inline-flex; align-items: center; gap: 6px; padding: 7px 16px; border-radius: 999px; border: 1.5px solid var(--free); color: var(--free); background: var(--paper); font: 700 14px var(--f-body); text-decoration: none; }\n.gmap svg { width: 15px; height: 15px; }\n.gmap:hover { background: var(--bg); }\n.gmap:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }\n.visit-btn[aria-pressed="true"]'), ('/* ---- Drawer ---- */', '/* ---- Google Maps link ---- */\nconst GQ = {"duomo": "Cattedrale di San Martino", "giovanni": "Chiesa dei Santi Giovanni e Reparata", "hotel": "Hotel Ilaria Via del Fosso", "station": "Stazione ferroviaria", "shopping": "Via Fillungo", "campanile": "Campanile Cattedrale di San Martino", "museo": "Museo della Cattedrale"};\nconst gmapUrl = s => "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent((GQ[s.id] || s.latin.split(/ \\/ | – /)[0]) + " Lucca");\n\n/* ---- Drawer ---- */')]
for a, c in GMAP_PAIRS: rep(a, c)
import sys; sys.path.insert(0, "/home/claude")
from upgrade_mobile import mobile
exec(open("/home/claude/lucca/remind_patch.py", encoding="utf-8").read())
from share_patch import share_icons
h = share_icons(h)
from tier_patch import tiers
h = tiers(h)
h = mobile(h, None)
# page has its own dark theme: stop browsers (e.g. Samsung Internet) from force-darkening it
h = h.replace(":root {\n  --bg: #E7E6E0;", ":root {\n  color-scheme: light dark;\n  --bg: #E7E6E0;", 1)
h = h.replace("<style>", '<meta name="color-scheme" content="light dark">\n<style>', 1)
open("/home/claude/lucca/盧卡地圖範本.html", "w").write(h)
print("ok", len(h))
