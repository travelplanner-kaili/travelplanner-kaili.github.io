
/* 讀 rome_art.md：作者直接在 GitHub 改這份檔案，網頁就會更新 */
function parseMD(src) {
  const secs = []; let cur = null, q = null;
  for (const raw of src.split(/\r?\n/)) {
    const s = raw.replace(/\s+$/, ""), t = s.trim();
    if (s.startsWith("## ")) { const i = s.lastIndexOf("@"); cur = { title: (i > 0 ? s.slice(3, i) : s.slice(3)).trim(), era: i > 0 ? s.slice(i + 1).trim() : "", qs: [] }; secs.push(cur); q = null; }
    else if (s.startsWith("### ") && /^### Q[\d-]+\s*\|/.test(s)) { const m = s.match(/^### (Q[\d-]+)\s*\|\s*(.*)$/); q = { id: m[1], q: m[2].trim(), s: "", b: [] }; cur.qs.push(q); }
    else if (!t) continue;
    else if (!cur) continue;
    else if (!q) (cur.intro = cur.intro || []).push(t);
    else if (s.startsWith("> ")) q.s = (q.s ? q.s + "\n" : "") + s.slice(2).trim();
    else if (s.startsWith("|")) { const cells = t.replace(/^\||\|$/g, "").split("|").map(c => c.trim()); if (cells.every(c => /^[-: ]*$/.test(c))) continue; const l = q.b[q.b.length - 1]; if (l && l[0] === "tbl") l[1].push(cells); else q.b.push(["tbl", [cells]]); }
    else if (t === "---") continue;
    else if (s.startsWith("#### ")) q.b.push(["h", s.slice(5).trim()]);
    else if (s.startsWith("### ")) q.b.push(["h", s.slice(4).trim()]);
    else if (s.startsWith(":: ")) { const l = q.b[q.b.length - 1]; if (l && l[0] === "box") l[1].push(s.slice(3).trim()); else q.b.push(["box", [s.slice(3).trim()]]); }
    else if (s.startsWith("* ")) q.b.push(["sub", s.slice(2).trim()]);
    else if (s.startsWith("- ")) q.b.push(["li", s.slice(2).trim()]);
    else if (/^\d+\.\s/.test(s)) q.b.push(["ol", s.replace(/^\d+\.\s/, "")]);
    else q.b.push(["p", t]);
  }
  return secs;
}
(async () => {
let SECS_ALL = SECS_EMBED;
try { const r = await fetch("rome_art.md", { cache: "no-cache" }); if (r.ok) { const p = parseMD(await r.text()); if (p.some(x => x.qs.length)) SECS_ALL = p; const lm = r.headers.get("last-modified"); if (lm) { const d = new Date(lm); window.__upd = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`; } } } catch (e) {}

const MAP_URL = "https://travelplanner-kaili.github.io/rome/";
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const ERA = Object.fromEntries(ERAS.map(e => [e.id, e]));
const cvar = e => e ? `var(--${e})` : "var(--ink2)";

/* ---------- questions ---------- */
const INTRO = SECS_ALL.find(x => x.era === "intro");
const PRE = SECS_ALL.find(x => x.era === "pre");
if (PRE) PRE.era = "";
const SECS = SECS_ALL.filter(x => x.era !== "intro" && x !== PRE);
const QA = (PRE ? [PRE] : []).concat(SECS).flatMap(s => s.qs.map(q => Object.assign(q, { era: s.era, sec: s })));
const Q = Object.fromEntries(QA.map(q => [q.id, q]));
const parentOf = id => { const p = id.replace(/-\d+$/, ""); return p !== id && Q[p] ? p : null; };
const kids = {}; QA.forEach(q => { const p = parentOf(q.id); if (p) (kids[p] = kids[p] || []).push(q.id); });

/* ---------- place names → links ---------- */
const AL = [...ALIASES].sort((a, b) => b[0].length - a[0].length);
const alRe = new RegExp(AL.map(a => a[0].replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|"), "g");
const alMap = Object.fromEntries(AL);
const mentions = {};
QA.forEach(q => { const all = q.q + q.s + q.b.map(x => [].concat(x[1]).join("")).join(""); all.replace(alRe, m => { const id = alMap[m]; if (id[0] !== "@") (mentions[id] = mentions[id] || new Set()).add(q.id); return m; }); });
const linkify = s => s.replace(alRe, m => { const id = alMap[m]; return id[0] === "@" ? `<button class="sp g" data-g="${esc(id.slice(1))}">${m}</button>` : `<button class="sp" data-s="${id}">${m}</button>`; });
const rich = s => linkify(esc(s)).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
function body(b) {
  let h = "", list = null;
  const close = () => { if (list) { h += `</${list}>`; list = null; } };
  b.forEach(([t, x]) => {
    if (t === "sub") { if (list) { h = h.replace(/<\/li>$/, "") + `<div class="subli">${rich(x)}</div></li>`; } else h += `<div class="subli">${rich(x)}</div>`; return; }
    if (t === "li" || t === "ol") { const tag = t === "li" ? "ul" : "ol"; if (list !== tag) { close(); h += `<${tag}>`; list = tag; } h += `<li>${rich(x)}</li>`; return; }
    close();
    close();
    if (t === "box") { h += `<div class="flowbox">${x.map(l => `<div>${rich(l)}</div>`).join("")}</div>`; return; }
    if (t === "tbl") { const [hd, ...rows] = x; h += `<div class="tbl"><table><thead><tr>${hd.map(c => `<th>${rich(c)}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${r.map((c, i) => `<td data-h="${esc(hd[i] || "")}">${rich(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`; return; }
    h += t === "h" ? (x.startsWith("↳") ? `<h4 class="fq"><span>接著問</span>${rich(x.slice(1).trim())}</h4>` : `<h4>${rich(x)}</h4>`) : `<p>${rich(x)}</p>`;
  });
  close(); return h;
}
const qChip = (id, withTitle) => Q[id] ? `<button class="qc" data-q="${id}" style="color:${cvar(Q[id].era)}">${id}${withTitle ? `<small>${esc(Q[id].q)}</small>` : ""}</button>` : "";
const spotEras = id => (SPOTINFO[id] || [""])[0].split(" ").filter(Boolean);
const spotChip = id => SPOTS[id] ? `<button class="chip" data-s="${id}" style="--c:${cvar(spotEras(id)[0])}"><span class="d"></span>${esc(SPOTS[id].n)}</button>` : "";

/* ---------- 問答：左邊目錄、右邊一次一段 ---------- */
const FROM = {};
const depth = id => id.split("-").length - 1;
let curSec = 0;
const SHORT = ["一 羅馬這座城市","二 古羅馬","三 中世紀","四 文藝復興起源","五 文藝復興在羅馬","六 轉向巴洛克","七 巴洛克在羅馬","八 巴洛克傳出","九 之後","十 總結"];
function card(id) {
  const q = Q[id], p = FROM[id] || parentOf(id);
  return `<article class="qi${p ? " sub" : ""}" id="qi-${id}" data-id="${id}" style="--c:${cvar(q.era)}">
    ${p ? `<div class="from">接續 ${p}　${esc(Q[p].q)}</div>` : ""}
    <div class="qt"><span class="id">${id}</span><h3>${esc(q.q)}</h3></div>
    <p class="sa">${rich(q.s).replace(/\n/g, "<br>")}</p><div class="qb">${body(q.b)}</div></article>`;
}
const secTitle = s => { const [a, b] = s.title.split("｜"); return b ? `<em>${esc(a)}</em>${esc(b)}` : esc(a); };
function buildOutline(el) {
  el.innerHTML = SECS.map((s, i) => `<div class="ol-grp" data-g="${i}" style="--c:${cvar(s.era)}"><button class="ol-sec" data-sec="${i}">${esc(s.title)}</button>${s.qs.map(q => `<button class="ol-q" data-oq="${q.id}" style="--dp:${depth(q.id)}"><i>${q.id}</i>${esc(q.q)}</button>`).join("")}</div>`).join("");
}
function showSec(i, qid) {
  curSec = i; const s = SECS[i];
  const prev = SECS[i - 1], next = SECS[i + 1];
  $("#pane").innerHTML = (i === 0 && INTRO ? `<div class="intro">${INTRO.intro.map(p => `<p>${rich(p)}</p>`).join("")}</div>` : "")
    + `<h2 class="sech" style="--c:${cvar(s.era)}">${secTitle(s)}</h2><p class="secnote">共 ${s.qs.length} 題</p>`
    + s.qs.map(q => card(q.id)).join("")
    + `<div class="pn">${prev ? `<button data-sec="${i - 1}"><small>← 上一段</small>${esc(prev.title)}</button>` : "<span></span>"}${next ? `<button class="nx" data-sec="${i + 1}"><small>下一段 →</small>${esc(next.title)}</button>` : "<span></span>"}</div>`;
  $$(".ol-grp").forEach(g => g.classList.toggle("cur", +g.dataset.g === i));
  $$("#secs button").forEach(b => b.classList.toggle("on", +b.dataset.sec === i));
  const chip = $(`#secs button[data-sec="${i}"]`); if (chip) chip.scrollIntoView({ inline: "center", block: "nearest" });
  if (qid) { const el = $("#qi-" + qid); if (el) el.scrollIntoView({ block: "start" }); } else window.scrollTo(0, 0);
  watch();
  try { localStorage.setItem("art-rome-sec", i); } catch (e) {}
}
let io;
function watch() {
  if (io) io.disconnect();
  io = new IntersectionObserver(es => {
    const vis = $$("#pane .qi").filter(el => { const r = el.getBoundingClientRect(); return r.top < innerHeight * .45 && r.bottom > 130; });
    const el = vis[0]; if (!el) return;
    $$("#outline .ol-q").forEach(b => b.classList.toggle("on", b.dataset.oq === el.dataset.id));
    const ob = $(`#outline .ol-q[data-oq="${el.dataset.id}"]`); if (ob) { const sd = $("#side"), r = ob.getBoundingClientRect(), rs = sd.getBoundingClientRect(); if (r.top < rs.top + 40 || r.bottom > rs.bottom - 20) sd.scrollTop += r.top - rs.top - rs.height / 3; }
  }, { rootMargin: "-120px 0px -50% 0px", threshold: [0, .01] });
  $$("#pane .qi").forEach(el => io.observe(el));
}
function buildQA() {
  buildOutline($("#outline"));
  $("#secs").innerHTML = SECS.map((s, i) => `<button data-sec="${i}" style="--c:${cvar(s.era)}">${SHORT[i] || esc(s.title)}</button>`).join("");
  let i0 = 0; try { i0 = +(localStorage.getItem("art-rome-sec") || 0); } catch (e) {}
  showSec(Math.min(i0, SECS.length - 1));
}
function search(v) {
  v = v.trim(); if (!v) return showSec(curSec);
  const lv = v.toLowerCase();
  const hits = QA.filter(q => (q.id + q.q + q.s + q.b.map(x => [].concat(x[1]).join("")).join("")).toLowerCase().includes(lv));
  $("#pane").innerHTML = `<h2 class="sech" style="--c:var(--ink)">搜尋「${esc(v)}」</h2><p class="hitinfo">找到 ${hits.length} 題。清空搜尋框回到原本的段落。</p>` + hits.map(q => card(q.id)).join("");
  const re = new RegExp(v.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
  $$("#pane .qi :is(p,li,h4,h3)").forEach(p => {
    const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT); const ns = []; while (w.nextNode()) ns.push(w.currentNode);
    ns.forEach(n => { re.lastIndex = 0; if (!re.test(n.data)) return; re.lastIndex = 0; const s = document.createElement("span"); s.innerHTML = esc(n.data).replace(re, m => `<mark class="hit">${m}</mark>`); n.replaceWith(...s.childNodes); });
  });
  window.scrollTo(0, 0);
}

/* ---------- 脈絡圖 ---------- */
function buildFlow() {
  if (PRE) $("#preqa").innerHTML = PRE.qs.map(q => card(q.id).replace('<div class="qb">', '<button class="fold" aria-expanded="false">展開完整回答 ▾</button><div class="qb">')).join("");
  const head = e => `<div class="eh" style="background:${cvar(e.id)}"><b>${e.n}. ${e.name}</b>${e.sub ? `<small>（${e.sub}）</small>` : ""}<small>${e.yr}</small></div>`;
  const sp = ([id, lab]) => id[0] === "@" ? `<button class="chip" data-g="${esc(id.slice(1))}" style="--c:${cvar("aft")}"><span class="d"></span>${esc(lab || id.slice(1))}</button>`
    : SPOTS[id] ? `<button class="chip" data-s="${id}" style="--c:${cvar(spotEras(id)[0])}"><span class="d"></span>${esc(lab || SPOTS[id].n)}</button>` : "";
  const rows = [
    ["羅馬的城市身分", e => `<div class="role">${esc(e.role)}</div>`],
    ["怎麼變過來<small>政經轉折＋技術突破</small>", e => `<div class="hg" style="--c:${cvar(e.id)}"><div class="ht">【${e.hinge.title}】</div>${rich(e.hinge.text)}<div style="margin-top:6px">${e.hinge.q.map(x => `<button class="qc" data-q="${x}" style="color:${cvar(Q[x] ? Q[x].era : e.id)}">👉 詳見 ${x}</button>`).join("")}</div></div>`],
    ["誰出錢・為何而做", e => `<div class="pay"><b>${esc(e.pay)}</b>${esc(e.why)}</div>`],
    ["風格關鍵字", e => `<div class="tags" style="--c:${cvar(e.id)}">${e.look.map(x => `<span>${x}</span>`).join("")}</div>`],
    ["現場一眼辨識密碼", e => `<div class="cue">${rich(e.cue)}</div>`],
    ["代表藝術家", e => `<div>${rich(e.who)}</div>`],
    ["羅馬去哪看", e => `<div class="chips">${e.spots.map(sp).join("")}</div>`],
  ];
  let h = `<div class="rl corner">檢索維度</div>` + ERAS.map(head).join("");
  rows.forEach(([lab, f]) => { h += `<div class="rl">${lab}</div>` + ERAS.map(f).join(""); });
  $("#mx").innerHTML = h;
  $("#stk").innerHTML = ERAS.map((e, i) => (i ? `<div class="hinge" style="--c:${cvar(e.id)}">${rows[1][1](e).replace('class="hg"', 'class="hg0"')}</div><div class="gap"></div>` : "")
    + `<div class="ec">${head(e)}${rows.filter((r, k) => k !== 1 || i === 0).map(([lab, f]) => `<div class="row"><i>${lab.replace(/<small>.*<\/small>/, "")}</i>${f(e)}</div>`).join("")}</div><div class="gap"></div>`).join("");
}

/* ---------- 景點對照 ---------- */
let drawn = false, efOn = new Set(ERAS.map(e => e.id));
function buildSpots() {
  $("#efilt").innerHTML = ERAS.map(e => `<button data-e="${e.id}" aria-pressed="true" style="--c:${cvar(e.id)}">${e.name}</button>`).join("");
  $("#layers").innerHTML = ERAS.map(e => {
    const list = Object.keys(SPOTINFO).filter(id => spotEras(id).includes(e.id));
    return `<div class="layer" data-e="${e.id}" style="--c:${cvar(e.id)}"><h3>${e.name}<small>${e.yr}</small></h3>${list.map(id => `<div class="sc" data-s="${id}" style="--c:${cvar(spotEras(id)[0])}"><span class="d"></span><div><b>${esc(SPOTS[id].n)}</b><small>${linkify(esc(SPOTINFO[id][1]))}</small></div></div>`).join("")}</div>`;
  }).join("");
  $("#walks").innerHTML = WALKS.map(w => `<div class="walk" style="--c:${cvar(w.era)}"><b>${w.name}</b>　<small>在羅馬地圖按 City Walk 就看得到</small><ol>${w.stops.map(s => `<li><button class="sp" data-s="${s}">${esc(SPOTS[s].n)}</button></li>`).join("")}</ol></div>`).join("");
  $("#r52").innerHTML = ROUTE.map(s => `<li><button class="sp" data-s="${s}">${esc(SPOTS[s].n)}</button></li>`).join("");
  $$("#efilt button").forEach(b => b.addEventListener("click", () => {
    const e = b.dataset.e;
    if (efOn.size === ERAS.length) efOn = new Set([e]); else if (efOn.has(e) && efOn.size > 1) efOn.delete(e); else efOn.add(e);
    $$("#efilt button").forEach(x => x.setAttribute("aria-pressed", efOn.has(x.dataset.e)));
    $$("#layers .layer").forEach(l => l.hidden = !efOn.has(l.dataset.e));
    dimDots();
  }));
}
const dimDots = () => $$("#mini .dot").forEach(d => d.classList.toggle("dim", !d.dataset.e.split(" ").some(x => efOn.has(x))));
function drawMini() {
  const all = [...new Set(Object.keys(SPOTINFO).concat(WALKS.flatMap(w => w.stops)))].filter(id => SPOTS[id]);
  const pts = all.concat("hotel").map(id => SPOTS[id]);
  const la0 = Math.min(...pts.map(p => p.lat)) - .0025, la1 = Math.max(...pts.map(p => p.lat)) + .0025;
  const lo0 = Math.min(...pts.map(p => p.lon)) - .006, lo1 = Math.max(...pts.map(p => p.lon)) + .006;
  const W = 600, k = Math.cos(41.9 * Math.PI / 180), sx = W / ((lo1 - lo0) * k), H = (la1 - la0) * sx;
  $("#mini").setAttribute("viewBox", `0 0 ${W} ${H.toFixed(0)}`);
  const P = s => [((s.lon - lo0) * k * sx), ((la1 - s.lat) * sx)];
  let g = "";
  all.forEach(id => {
    const [x, y] = P(SPOTS[id]); const es = spotEras(id); const main = SPOTINFO[id];
    const ring = es.length > 1 ? `<circle r="10" fill="none" stroke="${cvar(es[1])}" stroke-width="2.5"/>` : "";
    g += `<g class="dot" data-s="${id}" data-e="${es.join(" ") || "x"}" transform="translate(${x.toFixed(1)},${y.toFixed(1)})">${ring}<circle r="${main ? 6.5 : 4.5}" fill="${main ? cvar(es[0]) : "var(--mute)"}" stroke="var(--card)" stroke-width="1.5"/>${main ? `<text>${esc(SPOTS[id].n)}</text>` : ""}<circle r="16" fill="transparent"/></g>`;
  });
  const [hx, hy] = P(SPOTS.hotel);
  g += `<g transform="translate(${hx},${hy})"><rect x="-6" y="-6" width="12" height="12" fill="var(--ink)" stroke="var(--card)" stroke-width="1.5"/></g>`;
  $("#mini").innerHTML = g;
  const vb = $("#mini").viewBox.baseVal, ob = [];
  $$("#mini g").forEach(gr => { const m = gr.transform.baseVal[0].matrix; ob.push([m.e - 7, m.f - 7, m.e + 7, m.f + 7]); });
  const hit = r => r[0] < 2 || r[2] > vb.width - 2 || r[1] < 2 || r[3] > vb.height - 2 || ob.some(o => r[0] < o[2] && r[2] > o[0] && r[1] < o[3] && r[3] > o[1]);
  $$("#mini .dot text").forEach(t => {
    const b = t.getBBox(), m = t.parentNode.transform.baseVal[0].matrix, w = b.width, h = b.height;
    const opts = [[10, 4, "start"], [-10, 4, "end"], [-w / 2, -10, "start"], [-w / 2, 17, "start"], [10, -8, "start"], [10, 16, "start"], [-10, -8, "end"], [-10, 16, "end"]];
    for (const [dx, dy, an] of opts) {
      const x0 = an === "end" ? m.e + dx - w : m.e + dx, r = [x0, m.f + dy - h * .78, x0 + w, m.f + dy + h * .22];
      if (!hit(r)) { t.setAttribute("x", dx); t.setAttribute("y", dy); t.setAttribute("text-anchor", an); ob.push(r); return; }
    }
    t.remove();
  });
  dimDots();
}

/* ---------- drawer ---------- */
const dr = $("#dr"), scrim = $("#scrim");
function openDrawer(html) { dr.innerHTML = `<button class="x" aria-label="關閉">×</button>` + html; dr.classList.add("on"); scrim.classList.add("on"); dr.scrollTop = 0; }
function closeDrawer() { dr.classList.remove("on"); scrim.classList.remove("on"); }
function showQ(id) {
  const q = Q[id]; if (!q) return;
  const p = parentOf(id), k = kids[id] || [];
  openDrawer(`<div style="--c:${cvar(q.era)}"><div class="eyebrow">${esc(q.sec.title)}　${id}</div><h2>${esc(q.q)}</h2><p class="sub">${rich(q.s).replace(/\n/g, "<br>")}</p><div class="qb">${body(q.b)}</div>
    ${p ? `<div class="more"><b>上一題</b>${qChip(p, true)}</div>` : ""}
    ${k.length ? `<div class="more"><b>接著問</b>${k.map(x => qChip(x, true)).join("")}</div>` : ""}
    <div class="btns" style="margin-top:16px"><button class="btn" data-goto="${id}">在問答裡看</button></div></div>`);
}
function showSpot(id) {
  const s = SPOTS[id]; if (!s) return; const info = SPOTINFO[id], es = spotEras(id);
  const qs = [...new Set([...(mentions[id] || []), ...(info ? info[2].split(" ").filter(Boolean) : [])])].filter(x => Q[x]).sort((a, b) => QA.indexOf(Q[a]) - QA.indexOf(Q[b]));
  const walks = WALKS.filter(w => w.stops.includes(id));
  openDrawer(`<div class="eyebrow" style="--c:${cvar(es[0])}">${es.map(e => ERA[e].name).join("・") || "羅馬地圖上的景點"}</div><h2>${esc(s.n)}</h2><div style="color:var(--mute);font-size:14px">${esc(s.l)}</div>
    ${info ? `<p class="sub" style="margin-top:10px">${linkify(esc(info[1]))}</p>` : ""}
    <div class="btns"><a class="btn pri" href="${MAP_URL}#spot=${id}" target="_blank" rel="noopener">在我的羅馬地圖打開 ↗</a><a class="btn" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(s.l.includes("Roma") ? s.l : s.l + ", Roma")}" target="_blank" rel="noopener">Google 地圖 ↗</a></div>
    ${walks.length ? `<p style="font-size:15px"><b>地圖上的 City Walk：</b>${walks.map(w => w.name).join("、")}</p>` : ""}
    ${qs.length ? `<div class="more"><b>相關問答</b>${qs.map(x => qChip(x, true)).join("")}</div>` : ""}`);
}
function showG(name) {
  openDrawer(`<div class="eyebrow">羅馬地圖上還沒有這個點</div><h2>${esc(name)}</h2><div class="btns"><a class="btn pri" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(name + ", Roma")}" target="_blank" rel="noopener">Google 地圖 ↗</a></div>`);
}
function setView(v, keep) {
  $$("nav button").forEach(b => b.setAttribute("aria-selected", b.dataset.v === v));
  $$("section.view").forEach(s => s.classList.toggle("on", s.id === "v-" + v));
  if (!keep) window.scrollTo(0, 0);
  if (v === "spots" && !drawn) { drawMini(); drawn = true; }
  try { localStorage.setItem("art-rome-view2", v); } catch (e) {}
}
function gotoQ(id) {
  closeDrawer();
  if (Q[id].sec === PRE) { setView("flow", true); $("#qi-" + id).scrollIntoView({ block: "start" }); return; }
  setView("qa", true); $("#q").value = "";
  showSec(SECS.indexOf(Q[id].sec), id);
}
document.addEventListener("click", ev => {
  const f = ev.target.closest(".fold, #preqa .qt");
  if (f) { const qi = f.closest(".qi"), on = qi.classList.toggle("open"); const b = qi.querySelector(".fold"); b.setAttribute("aria-expanded", on); b.textContent = on ? "收起 ▴" : "展開完整回答 ▾"; return; }
  const t = ev.target.closest("[data-q],[data-s],[data-g],[data-goto],[data-sec],[data-oq],.x,#tocbtn");
  if (!t) return;
  if (t.classList.contains("x")) return closeDrawer();
  if (t.id === "tocbtn") { openDrawer(`<h2>目錄</h2><div id="outline2"></div>`); buildOutline($("#outline2")); return; }
  if (t.dataset.sec) { closeDrawer(); $("#q").value = ""; showSec(+t.dataset.sec); return; }
  if (t.dataset.oq) { closeDrawer(); $("#q").value = ""; const q = Q[t.dataset.oq]; showSec(SECS.indexOf(q.sec), q.id); return; }
  if (t.dataset.goto) return gotoQ(t.dataset.goto);
  ev.stopPropagation();
  if (t.dataset.q) showQ(t.dataset.q); else if (t.dataset.s) showSpot(t.dataset.s); else if (t.dataset.g) showG(t.dataset.g);
}, true);
scrim.addEventListener("click", closeDrawer);
document.addEventListener("keydown", e => { if (e.key === "Escape") closeDrawer(); });
$$("nav button").forEach(b => b.addEventListener("click", () => setView(b.dataset.v)));
let tm; $("#q").addEventListener("input", e => { clearTimeout(tm); tm = setTimeout(() => search(e.target.value), 200); });

buildQA(); buildFlow(); buildSpots();
const u = document.getElementById("upd"); if (u) u.textContent = window.__upd || BUILT;
try { const v = localStorage.getItem("art-rome-view2"); if (v && v !== "flow") setView(v); } catch (e) {}
})();
