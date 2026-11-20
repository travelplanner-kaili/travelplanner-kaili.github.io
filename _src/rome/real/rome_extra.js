/* ==== Rome only: City Walk routes, 購物 view, ⚡搶票 badges (on the real street map) ==== */
const RX = {};
/* ⚡搶票: the spots whose tickets must be grabbed early get a thicker frame and a badge */
SPOTS.forEach(s => { if (s.rush && s.g) { s.g.classList.add("rush"); const n = s.g.querySelector(".t-name"); if (n && !n.querySelector(".t-rush")) n.insertAdjacentHTML("beforeend", '<span class="t-rush">⚡搶票</span>'); } });
/* every weekday picked: some spots keep their hand-written label text */
{
  const _applyDays = applyDays;
  applyDays = function () {
    _applyDays();
    const all = DAYS.filter(pressed).length === 7 || !DAYS.some(pressed);
    if (all) SPOTS.forEach(s => { if (WEEK_KEEP.has(s.id) && s.tw && s.sHours) { s.tw.textContent = s.sHours; s.tw.classList.remove("day-off"); } });
  };
}

/* ---- City Walk ---- */
const routeLayer = L.layerGroup();
let routeOn = false;
const routeColor = r => r.color ? `var(--route-${r.color})` : "var(--route)";
ROUTES.forEach(r => {
  const g = r.layer = L.layerGroup();
  const css = el => { if (el) el.style.setProperty("--rc", routeColor(r)); };
  r.line = L.polyline(r.ll, { className: "route-line", interactive: false }).addTo(g);
  r.hit = L.polyline(r.ll, { className: "route-hit" }).addTo(g);
  r.hit.on("click", e => { L.DomEvent.stopPropagation(e); openRoute(r.id); });
  const ends = [[r.ll[0], "起"], [r.ll[r.ll.length - 1], "終"]].map(([p, t]) => L.marker(p, { icon: L.divIcon({ className: "route-end", html: `<span>${t}</span>`, iconSize: [0, 0] }), interactive: false, keyboard: false, zIndexOffset: 400 }).addTo(g));
  r.marks.forEach(m => {
    const mk = L.marker(m.ll, { icon: L.divIcon({ className: "route-mark", html: `<span title="${esc(m.n + " " + m.name)}（Google 地圖）">${esc(m.n)}</span>`, iconSize: [0, 0] }), keyboard: false, zIndexOffset: 450 }).addTo(g);
    mk.on("click", e => { L.DomEvent.stopPropagation(e); openExternal("https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(m.q)); });
    mk.on("add", () => css(mk.getElement()));
  });
  r.pillM = L.marker(r.pill, { icon: L.divIcon({ className: "route-pill", html: `<span role="button" tabindex="0" title="點一下看路線介紹">${esc(r.pillText)}</span>`, iconSize: [0, 0] }), keyboard: false, zIndexOffset: 500 }).addTo(g);
  r.pillM.on("click", e => { L.DomEvent.stopPropagation(e); openRoute(r.id); });
  g.on("add", () => setTimeout(() => { [r.line, r.hit].forEach(l => css(l.getElement())); [...ends, r.pillM].forEach(m => css(m.getElement())); }, 0));
  // follow the real streets when the walking-route service answers (the drawn line is already close)
  const step = Math.max(1, Math.ceil(r.ll.length / 20)), way = r.ll.filter((p, i) => i % step === 0 || i === r.ll.length - 1);
  walkRoute(way).then(rt => { if (rt && rt.total < pathLen(r.ll) * 1.35) { r.line.setLatLngs(rt.coords); r.hit.setLatLngs(rt.coords); } });
});
let routeShow = new Set(ROUTES.map(r => r.id));
try { const v = JSON.parse(localStorage.getItem("routeShow-rome") || "null"); if (Array.isArray(v) && v.length) routeShow = new Set(v.filter(id => ROUTES.some(r => r.id === id))); } catch (e) {}
const pick = document.getElementById("route-pick");
const pickAll = document.createElement("button"); pickAll.type = "button"; pickAll.className = "all"; pickAll.textContent = "全部"; pick.appendChild(pickAll);
ROUTES.forEach(r => {
  const b = document.createElement("button"); b.type = "button"; b.dataset.route = r.id;
  b.textContent = r.tag || r.name.replace("City Walk：", "");
  if (r.color) b.style.setProperty("--rc", routeColor(r));
  b.addEventListener("click", () => {
    // first tap while everything is shown = only this walk; later taps add / remove
    if (routeShow.size === ROUTES.length) routeShow = new Set([r.id]);
    else if (routeShow.has(r.id)) { routeShow.delete(r.id); if (!routeShow.size) routeShow = new Set(ROUTES.map(x => x.id)); }
    else routeShow.add(r.id);
    saveShow(); applyRoute();
  });
  pick.appendChild(b);
});
pickAll.addEventListener("click", () => { routeShow = new Set(ROUTES.map(x => x.id)); saveShow(); applyRoute(); });
L.DomEvent.disableClickPropagation(pick); L.DomEvent.disableScrollPropagation(pick);
function saveShow() { try { localStorage.setItem("routeShow-rome", JSON.stringify([...routeShow])); } catch (e) {} }
const shownRoutes = () => ROUTES.filter(r => routeShow.has(r.id));
function applyRoute() {
  window.ROUTE_ON = routeOn;
  if (routeOn) routeLayer.addTo(map); else routeLayer.remove();
  ROUTES.forEach(r => { if (routeOn && routeShow.has(r.id)) routeLayer.addLayer(r.layer); else routeLayer.removeLayer(r.layer); });
  pick.hidden = !routeOn;
  const allOn = routeShow.size === ROUTES.length;
  pickAll.setAttribute("aria-pressed", allOn);
  pick.querySelectorAll("button[data-route]").forEach(b => b.setAttribute("aria-pressed", !allOn && routeShow.has(b.dataset.route)));
  document.querySelectorAll(".icon-btn.route").forEach(b => b.setAttribute("aria-pressed", routeOn));
  // a walk on the map: only the spots on the shown walks stay (their hidden 次要 spots come back too)
  const ids = new Set(routeOn ? shownRoutes().flatMap(r => [...r.stops, ...(r.areas || [])]) : []);
  SPOTS.forEach(s => {
    const off = routeOn && !ids.has(s.id) && s.cat !== "base";
    s.g.classList.toggle("off-route", off); s.g.classList.toggle("on-route", routeOn && ids.has(s.id));
    if (s.areaEl) s.areaEl.eachLayer(l => l._path && l._path.classList.toggle("off-route-area", off));
  });
  applySup();
}
document.querySelectorAll(".icon-btn.route").forEach(b => b.addEventListener("click", () => { routeOn = !routeOn; applyRoute(); }));
const routesOfAll = id => ROUTES.filter(r => r.stops.includes(id) || (r.areas || []).includes(id));
function openRoute(id) {
  drawer.dataset.spot = ""; drawer.dataset.route = id;
  const r = ROUTES.find(x => x.id === id); if (!r) return;
  lastFocus = document.activeElement;
  SPOTS.forEach(x => x.g.classList.remove("active"));
  drawer.style.setProperty("--c", routeColor(r));
  if (r.color) drawer.style.setProperty("--route", routeColor(r)); else drawer.style.removeProperty("--route");
  drawer.innerHTML = `
    <div class="d-top"><span class="cat">推薦散步路線</span><button class="close" id="d-close" aria-label="關閉">×</button></div>
    <h3 id="d-name">${esc(r.name)}</h3>
    <p class="latin">${esc(r.latin)}</p>
    <div class="d-plan rt-plan"><span>整條路線加入行程：</span>${PDAYS.map(d => `<button type="button" class="plan-day" data-day="${d.k}"></button>`).join("")}</div>
    <div class="rt-tabs" role="tablist"><button class="rt-tab" role="tab" data-tab="info" aria-selected="true">路線介紹</button>${r.food ? `<button class="rt-tab" role="tab" data-tab="food" aria-selected="false">🍴 吃什麼</button>` : ""}<button class="rt-tab" role="tab" data-tab="tips" aria-selected="false">💡 小提醒</button></div>
    <div class="rt-panel tips-panel" data-panel="tips" hidden>${list(r.tips)}</div>
    ${r.food ? `<div class="rt-panel" data-panel="food" hidden>
      <p class="food-intro">${esc(r.food.intro)}</p>
      <ul class="food-list">${r.food.places.map(f => `<li class="food">
        <p class="food-where">${esc(f.where)}</p>
        <p class="food-name">${esc(f.name)}</p>
        <p class="food-kind">${esc(f.kind)}</p>
        <p>${esc(f.desc)}</p>
        <p class="food-hours">${esc(f.hours)}</p>
        <a class="site" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(f.q + " Roma")}&query_place_id=${f.pid}" target="_blank" rel="noopener">Google 地圖 ↗</a>
      </li>`).join("")}</ul>
      ${r.food.why ? `<h4 class="food-h">推薦的用餐安排</h4>${list(r.food.why)}` : ""}
    </div>` : ""}
    <dl class="rt-panel" data-panel="info">
      <div><dt>路線概要</dt><dd>${esc(r.summary)}</dd></div>
      <div><dt>沿途景點（點名稱看介紹）</dt><dd><ol class="stops">${r.stopsText.map(([n, t], i) => `<li><button class="stop-link" data-id="${esc(r.stops[i])}">${esc(n)}</button>：${esc(t)}</li>`).join("")}</ol></dd></div>
      ${r.chain ? `<div><dt>${esc(r.chainTitle)}</dt><dd>${list(r.chain)}</dd></div>` : ""}
      ${r.flow ? `<div><dt>${esc(r.flowTitle)}</dt><dd><ol class="howto">${r.flow.map(x => `<li>${esc(x)}</li>`).join("")}</ol></dd></div>` : ""}
      ${r.why ? `<div><dt>為什麼推薦這段</dt><dd>${list(r.why)}</dd></div>` : ""}
      <div><dt>建議時間安排</dt><dd>${list(r.plan)}</dd></div>
      <div><dt>怎麼到起點</dt><dd>${esc(r.start)}</dd></div>
      <div><dt>走完之後</dt><dd>${esc(r.end)}</dd></div>
    </dl>`;
  if (!routeOn || !routeShow.has(r.id)) { routeOn = true; routeShow.add(r.id); saveShow(); applyRoute(); }
  drawer.hidden = false; scrim.hidden = false;
  // zoom to the walk, in the part of the map the drawer does not cover
  const b = L.latLngBounds(r.ll); r.stops.forEach(id => { const s = byId(id); if (s) b.extend(s.ll); });
  const wide = innerWidth > 860, dw = wide ? drawer.offsetWidth : 0, dh = wide ? 0 : drawer.offsetHeight;
  map.fitBounds(b, { paddingTopLeft: [30, 60], paddingBottomRight: [30 + dw, 30 + Math.min(dh, mapEl.offsetHeight * .5)], maxZoom: 17 });
  document.getElementById("d-close").addEventListener("click", closeSpot);
  drawer.querySelectorAll(".stop-link").forEach(b => b.addEventListener("click", () => openSpot(b.dataset.id)));
  bindRoutePlan(r);
  bindTabs();
  document.getElementById("d-close").focus({ preventScroll: true });
}

/* 整條路線加入行程 (2026-11-20): the walk's stops go into that day in the walk's order (ones already there stay where they are);
   when the whole walk is already in that day, the same button takes the walk's stops out again */
function bindRoutePlan(r) {
  const ids = r.stops.filter(id => byId(id) && byId(id).cat !== "base");
  const paint = () => drawer.querySelectorAll(".rt-plan .plan-day").forEach(b => {
    const d = PDAYS.find(x => x.k === b.dataset.day), all = ids.every(id => planHas(d.k, id));
    b.setAttribute("aria-pressed", all); b.textContent = (all ? "✓ " : "＋ ") + d.label;
    b.title = all ? "再按一次，把這條路線的景點從這天移除" : "把沿途 " + ids.length + " 個景點依路線順序加進這天";
  });
  drawer.querySelectorAll(".rt-plan .plan-day").forEach(b => b.addEventListener("click", () => {
    const k = b.dataset.day, a = plan.days[k];
    if (ids.every(id => planHas(k, id))) plan.days[k] = a.filter(x => !ids.includes(x.id));
    else ids.forEach(id => { if (!planHas(k, id)) a.push({ id, time: "", note: "" }); });
    plan.cur = k; plan.on = true; savePlan(); renderPlan(); paint();
  }));
  paint();
}

/* ---- 購物: pink shopping streets are always on the map; the button adds the shops (solid boxes) ---- */
let shopOn = false;
{
  const _applySup = applySup;
  applySup = function () {
    _applySup();
    SPOTS.forEach(s => {
      if (s.shopStreet) { s.g.classList.add("gone"); return; }   // shopping streets are the pink lines, not pins
      if (s.tier === "購物") { s.g.classList.toggle("gone", !shopOn); s.g.classList.toggle("shopbox", shopOn); s.g.classList.remove("dim"); }
      else if (shopOn && s.cat !== "base") { if (s.sup) s.g.classList.add("gone"); s.g.classList.remove("dim"); }   // 購物: 主要／推薦 stay as they are, other filters pause
      if (s.g.classList.contains("on-route")) s.g.classList.remove("gone");
    });
    document.querySelectorAll("#f-sup, .chip[data-cat], #f-cold").forEach(c => c.classList.toggle("muted", shopOn));
    layoutLabels();
  };
}
document.querySelectorAll(".shop-btn").forEach(b => b.addEventListener("click", () => {
  shopOn = !shopOn; window.SHOP_ON = shopOn; document.querySelectorAll(".shop-btn").forEach(x => x.setAttribute("aria-pressed", shopOn)); applySup();
}));
applyDays(); applySup();
