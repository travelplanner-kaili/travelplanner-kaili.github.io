/* ===================== real-map engine (Leaflet + OpenStreetMap/CARTO) ===================== */
const K = 0.74;   // label offsets: old-map units (m) → screen px, so the label layout matches the drawn map
const pressed = el => el.getAttribute("aria-pressed") === "true";
const byId = id => SPOTS.find(s => s.id === id);
const hav = (a, b) => { const R = 6371000, r = Math.PI / 180, dl = (b[0] - a[0]) * r, dn = (b[1] - a[1]) * r; const q = Math.sin(dl / 2) ** 2 + Math.cos(a[0] * r) * Math.cos(b[0] * r) * Math.sin(dn / 2) ** 2; return 2 * R * Math.asin(Math.sqrt(q)); };
function walkM(m) { const w = m * 1.3; const r = w < 100 ? Math.round(w / 10) * 10 : Math.round(w / 50) * 50; return { m: r, min: Math.max(1, Math.round(r / 80)) }; }
const walkText = m => { const w = walkM(m); return (w.m < 1000 ? w.m + " m" : (w.m / 1000).toFixed(1) + " km") + "・" + w.min + " 分"; };

/* real walking routes (OpenStreetMap foot routing, free, no key); falls back to the straight line when offline */
const ROUTE_CACHE = {};
async function walkRoute(pts) {
  const key = pts.map(p => p[1].toFixed(5) + "," + p[0].toFixed(5)).join(";");
  if (ROUTE_CACHE[key]) return ROUTE_CACHE[key];
  try {
    const r = await fetch("https://routing.openstreetmap.de/routed-foot/route/v1/driving/" + key + "?overview=full&geometries=geojson");
    const j = await r.json(); if (j.code !== "Ok") return null;
    const rt = j.routes[0];
    return ROUTE_CACHE[key] = { coords: rt.geometry.coordinates.map(c => [c[1], c[0]]), legs: rt.legs.map(l => l.distance), total: rt.distance };
  } catch (e) { return null; }
}
const realText = m => { const r = m < 100 ? Math.round(m / 10) * 10 : Math.round(m / 50) * 50; return (r < 1000 ? r + " m" : (r / 1000).toFixed(1) + " km") + "・" + Math.max(1, Math.round(r / 80)) + " 分"; };
const ll2 = p => p[0].toFixed(6) + "," + p[1].toFixed(6);
const gDir = pts => "https://www.google.com/maps/dir/?api=1&travelmode=walking&origin=" + ll2(pts[0]) + "&destination=" + ll2(pts[pts.length - 1]) + (pts.length > 2 ? "&waypoints=" + encodeURIComponent(pts.slice(1, -1).map(ll2).join("|")) : "");
const mapEl = document.getElementById("lmap");
const dark = matchMedia("(prefers-color-scheme: dark)").matches && document.documentElement.dataset.theme !== "light";
const map = L.map(mapEl, { zoomControl: false, zoomSnap: 0.25, zoomDelta: 0.5, wheelPxPerZoomLevel: 90, maxZoom: 20, minZoom: 12, tapTolerance: 12 });
/* base map: OpenStreetMap when served from a web address (it needs a referring site);
   Esri street map when the file is opened straight from the computer (file://), where OSM tiles are refused */
const FILE_MODE = location.protocol === "file:";
const BASE = (FILE_MODE
  ? L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", { maxZoom: 20, maxNativeZoom: 19,
      attribution: 'Tiles &copy; Esri &mdash; Esri, HERE, Garmin, &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors' })
  : L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 20, maxNativeZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors' })
).addTo(map);
map.attributionControl.setPrefix('<a href="https://leafletjs.com" target="_blank" rel="noopener">Leaflet</a>');
map.createPane("planRoute").style.zIndex = 640; map.getPane("planRoute").style.pointerEvents = "none";
map.createPane("planSpots").style.zIndex = 660;
map.createPane("planPills").style.zIndex = 670; map.getPane("planPills").style.pointerEvents = "none";   // distance pills above everything of the day (they avoid the labels themselves)
const OLD_TOWN = L.latLngBounds(CITY.bounds);
/* the river (Rome: Tiber), drawn like the hand-drawn map so it stays when the street map is faded or hidden */
const unitPx = () => (CITY.unitM ? 256 * Math.pow(2, map.getZoom()) / (40075016.686 * Math.cos(map.getCenter().lat * Math.PI / 180)) * CITY.unitM : 1);
if (CITY.river) {
  map.createPane("river").style.zIndex = 350;
  const rv = L.polyline(CITY.river, { pane: "river", className: "river-line", interactive: false }).addTo(map);
  const rl = CITY.riverLabel && L.marker(CITY.riverLabel.ll, { pane: "river", icon: L.divIcon({ className: "river-name", html: "<span>" + CITY.riverLabel.text + "</span>", iconSize: [0, 0] }), interactive: false, keyboard: false }).addTo(map);
  const rw = () => { const k = unitPx(); rv.setStyle({ weight: Math.max(6, 26 * k) }); if (rl && rl.getElement()) rl.getElement().style.fontSize = Math.max(10, 19 * k) + "px"; };
  map.on("zoomend", rw); map.whenReady(rw);
}
/* city walls (Lucca: 11 bastions, approximate outline) */
if (CITY.wall) {
  const wallBand = L.polygon(CITY.wall, { className: "wall-band", interactive: false, weight: 12 }).addTo(map);
  L.polygon(CITY.wall, { className: "wall-core", interactive: false }).addTo(map);
  const wallW = () => { const z = map.getZoom(); wallBand.setStyle({ weight: Math.max(4, Math.min(40, 16 * Math.pow(2, z - 16))) }); };
  map.on("zoomend", wallW); wallW();
}
const areaW = () => SPOTS.forEach(s => s.areaBand && s.areaBand.setStyle({ weight: Math.max(6, Math.min(36, 14 * Math.pow(2, map.getZoom() - 16))) }));
map.on("zoomend", areaW);
/* main streets (as on the hand-drawn map), from Google house-number points; snapped to the real street when the walking-route service answers */
const STREETS = CITY.streets || [];
const streetLayer = L.layerGroup().addTo(map);
function pathLen(p) { let m = 0; for (let i = 1; i < p.length; i++) m += hav(p[i - 1], p[i]); return m; }
function streetLabelAt(p, f) {   // point + screen angle at fraction f of the line
  const L0 = pathLen(p) * f; let acc = 0;
  for (let i = 1; i < p.length; i++) { const d = hav(p[i - 1], p[i]); if (acc + d >= L0) { const t = (L0 - acc) / d, ll = [p[i - 1][0] + (p[i][0] - p[i - 1][0]) * t, p[i - 1][1] + (p[i][1] - p[i - 1][1]) * t];
      const a = map.latLngToLayerPoint(p[i - 1]), b = map.latLngToLayerPoint(p[i]); let ang = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI; if (ang > 90) ang -= 180; if (ang < -90) ang += 180; return { ll, ang }; } acc += d; }
  return { ll: p[p.length - 1], ang: 0 };
}
STREETS.forEach(st => {
  // a street with an id (Rome's shopping streets) is clickable and opens that spot's drawer
  const open = e => { if (picking) return; L.DomEvent.stopPropagation(e); openSpot(st.id); };
  st.line = L.polyline(st.pts, { className: "street-band" + (st.cls ? " " + st.cls : ""), interactive: !!st.id }).addTo(streetLayer);
  if (st.id) st.line.on("click", open);
  if (st.name) { st.label = L.marker(st.pts[0], { icon: L.divIcon({ className: "street-name" + (st.cls ? " " + st.cls : ""), html: "<span></span>", iconSize: [0, 0] }), interactive: !!st.id, keyboard: false, zIndexOffset: -1000 }).addTo(streetLayer);
    if (st.id) st.label.on("click", open); }
  walkRoute(st.pts).then(r => { if (r && r.total < pathLen(st.pts) * 1.25) { st.pts = r.coords; st.line.setLatLngs(r.coords); placeStreets(); } });
});
function placeStreets() {
  if (!map._loaded) return;
  const z = map.getZoom(), w = Math.max(5, Math.min(30, 11 * Math.pow(2, z - 16)));
  let lm = "auto"; try { lm = LMODE; } catch (e) {}   // 2026-11-21: street names follow the eye like the spot labels
  STREETS.forEach(st => { st.line.setStyle({ weight: w });
    if (!st.label) return; const { ll, ang } = streetLabelAt(st.pts, st.at);
    st.label.setLatLng(ll); const sp = st.label.getElement() && st.label.getElement().querySelector("span");
    if (sp) { sp.textContent = st.name; sp.style.transform = `translate(-50%, -50%) rotate(${ang}deg)`; }
    st.label.getElement() && st.label.getElement().classList.toggle("off", lm === "auto" && z < (st.minZoom || 14.5)); });
  if (typeof SPOTS !== "undefined" && SPOTS.length && SPOTS[0].g) layoutLabels();
}
map.on("zoomend", placeStreets); map.whenReady(placeStreets);
const mq = matchMedia("(max-width: 860px)");
function home() {
  map.invalidateSize();
  if (mq.matches) map.setView(byId(CITY.homeSpot).ll, CITY.homeZoom); else map.fitBounds(OLD_TOWN, { padding: [10, 10] });
}

/* ---- spots: pin + the same stone-tablet label as the drawn map, kept at the same screen offset ---- */
function makeSpot(s) {
  if (!s.ll) s.ll = LL[s.id];
  const g = document.createElement("div");
  g.className = "spot" + (s.sup ? " is-sup" : "") + (s.cat === "base" ? " is-base" : "") + (s.custom ? " is-mine" : "") + (s.mid ? " mid" : "") + (s.compact ? " compact" : "");   // like the hand-drawn map: mid = smaller label, compact = name only
  Object.assign(g.dataset, { id: s.id, cat: s.cat });
  g.tabIndex = 0; g.setAttribute("role", "button"); g.setAttribute("aria-label", [s.name, s.sTime, s.sPrice].filter(Boolean).join("，"));
  g.style.setProperty("--c", CAT[s.cat].color);
  g.style.setProperty("--pc", ({ paid: "#E5484D", free: "#3B82F6", open: "#3DAA5A", base: "#3A3633", mine: "#A855F7" })[s.cat] || CAT[s.cat].color);   // bright dot colours for the busy street map
  const allDay = s.cat === "open" || s.cat === "base";
  g.innerHTML = `<svg class="leader"><line x1="0" y1="0"/></svg><div class="tab"><div class="t-name"></div>${allDay || !(WEEK[s.id] || s.sHours) ? "" : '<div class="t-wed t-more"></div>'}${s.sPrice ? '<div class="t-price t-more"></div>' : ""}</div><span class="pin"></span><span class="plan-no"></span>`;
  g.querySelector(".t-name").textContent = s.id === "hotel" ? "HOTEL" : s.name;   // 2026-11-21: the full name is in the card
  if (g.querySelector(".t-price")) { if (s.id === "hotel") g.querySelector(".t-price").remove(); else g.querySelector(".t-price").textContent = s.sPrice; }
  if (!WEEK[s.id] && s.sHours && g.querySelector(".t-wed")) g.querySelector(".t-wed").textContent = s.sHours;
  s.g = g; s.tab = g.querySelector(".tab"); s.tw = g.querySelector(".t-wed"); s.line = g.querySelector(".leader line");
  s.marker = L.marker(s.ll, { icon: L.divIcon({ className: "lm-spot", html: g, iconSize: [0, 0] }), keyboard: false, interactive: false,
    zIndexOffset: s.tier === "主要" ? 300 : s.tier === "推薦" ? 200 : s.cat === "base" ? 250 : 100 }).addTo(map);
  if (s.area && s.area.length) {
    // same outline as the hand-drawn map; click opens the spot's drawer
    const A = s.area;
    const band = L.polygon(A, { className: "area-band" }), edge = L.polygon(A, { className: "area-core", interactive: false });
    const dots = [];   // the three corner dots were removed (2026-11-18)
    s.areaEl = L.featureGroup([band, edge, ...dots]).addTo(map); s.areaBand = band;
    band.on("click", e => { if (picking) return; L.DomEvent.stopPropagation(e); distMode ? pickSpot(s.id) : openSpot(s.id); });
  }
}
/* 我的住宿: the hotel on the map is the author's (Hotel Ilaria) until you set your own (kept in this browser; goes with 匯出地圖) */
const HKEY = "trip-hotel-" + CITY.key;
const HOTEL0 = (() => { const h = byId("hotel"); return h ? { name: h.name, latin: h.latin, feature: h.feature, hours: h.hours, sPrice: h.sPrice, ll: LL.hotel } : null; })();
let myHotel = null; try { myHotel = JSON.parse(localStorage.getItem(HKEY) || "null"); } catch (e) {}
function applyHotelData() {
  const h = byId("hotel"); if (!h || !HOTEL0) return;
  if (myHotel && myHotel.ll) Object.assign(h, { sPrice: "我的住宿", name: myHotel.name, latin: "你設定的住宿", feature: "你設定的住宿。" + (myHotel.note ? "備註：" + myHotel.note : ""), hours: null, ll: myHotel.ll, gurl: myHotel.gurl || "", myHotel: true });
  else Object.assign(h, { sPrice: HOTEL0.sPrice, name: HOTEL0.name, latin: HOTEL0.latin, feature: HOTEL0.feature, hours: HOTEL0.hours, ll: HOTEL0.ll, gurl: "", myHotel: false });
}
applyHotelData();
SPOTS.forEach(makeSpot); areaW();
const areaVis = (s, v) => s.areaEl.eachLayer(l => { if (l._path) { l._path.style.opacity = v; l._path.style.pointerEvents = v ? "" : "none"; } });
let distMode = false;
/* labels are placed again at every zoom: important sights first, each label takes the first free spot around its pin;
   if the full label (hours, price) cannot fit it shrinks to the name, and if even that cannot fit only the pin stays */
const ORDER = s => s.tier === "主要" ? 0 : s.cat === "base" ? 1 : s.tier === "推薦" ? 2 : 3;
/* 眼睛 (label mode): 自動 = place what fits (a label that cannot fit shrinks to its name, then to just the pin);
   全覽 = every label in full; 簡潔 = every label name only (as the hand-drawn map did) */
const LMODES = ["auto", "full", "names"], LMODE_TXT = { auto: "自動", full: "全覽", names: "簡潔" };
const LMKEY = "trip-lmode-" + CITY.key;
let LMODE = "auto"; try { const v = localStorage.getItem(LMKEY); if (LMODES.includes(v)) LMODE = v; } catch (e) {}
function layoutLabels() {
  // label size follows the zoom: small when zoomed out, bigger when zoomed in (like the hand-drawn map)
  mapEl.style.setProperty("--ls", (Math.max(.62, Math.min(1.45, Math.pow(2, (map.getZoom() - 16) * .55))) * (innerWidth > 860 ? 1.3 : 1)).toFixed(3));   // a big screen gets a little more
  const geo = LMODE !== "auto" && !distMode && SPOTS.some(s => s.lab);
  mapEl.classList.toggle("geo", geo);
  if (geo) mapEl.style.setProperty("--k", unitPx().toFixed(4));
  const z = map.getZoom(), forceSlim = distMode || LMODE === "names", forceAll = LMODE !== "auto" && !distMode, none = z < 13.5 && !geo && LMODE === "auto";
  mapEl.classList.toggle("lbl-none", none);
  if (none) return;
  const vis = SPOTS.filter(s => !s.g.classList.contains("gone") && !s.g.classList.contains("hide-v") && !s.g.classList.contains("off-route"));
  // sizes of the full and the name-only label
  vis.forEach(s => {
    s.g.classList.remove("lbl-off", "slim1");
    s.full = { w: s.tab.offsetWidth, h: s.tab.offsetHeight };
    s.g.classList.add("slim1"); s.slim = { w: s.tab.offsetWidth, h: s.tab.offsetHeight }; s.g.classList.remove("slim1");
    s.p = map.latLngToContainerPoint(s.ll);
  });
  if (geo) {
    /* 全覽／簡潔 = the hand-drawn map's own layout: every label at its drawn spot, sized with the map,
       so zooming out shrinks everything together and the whole city stays readable as one picture */
    const routeOn_ = !!window.ROUTE_ON, shopOn_ = !!window.SHOP_ON;   // set by the city's extra code (Rome)
    const full = !shopOn_ && ((document.getElementById("f-sup") || {}).getAttribute?.("aria-pressed") === "true" || routeOn_);
    vis.forEach(s => {
      const L0 = s.lab || {}, sl = LMODE === "names" || s.compact || (shopOn_ && L0.sh && s.cat !== "base");
      s.g.classList.toggle("slim1", sl);
      const ll = shopOn_ && L0.sh ? L0.sh : LMODE === "names" ? (L0.n || L0.sl || L0.l) : (full && L0.u ? L0.u : L0.l);
      const W = s.tab.offsetWidth, H = s.tab.offsetHeight;
      let dx = 12, dy = -H / 2;
      if (ll) { const q = map.latLngToContainerPoint(ll); dx = q.x - s.p.x; dy = q.y - s.p.y; }
      s.tab.style.left = dx + "px"; s.tab.style.top = dy + "px";
      const cx = Math.max(dx, Math.min(0, dx + W)), cy = Math.max(dy, Math.min(0, dy + H));
      s.line.setAttribute("x2", cx); s.line.setAttribute("y2", cy);
    });
    placeLegPills(); return;
  }
  // 我的行程 open (2026-11-20, phone overlaps): that day's spots are placed first, their numbered circles (30px) are obstacles,
  // and in 自動 the other (faded) spots only get a name label where there is room
  const planOn = mapEl.classList.contains("planning"), inP = s => planOn && s.g.classList.contains("in-plan");
  const pOrder = {}; if (planOn) (plan.days[plan.cur] || []).forEach((x, i) => { if (!(x.id in pOrder)) pOrder[x.id] = i; });
  const boxes = vis.map(s => { const r = inP(s) ? 16 : 9; return { x: s.p.x - r, y: s.p.y - r, w: 2 * r, h: 2 * r }; });   // pins (and plan numbers) are obstacles too
  // street names too: spot labels must not cover them
  const mr = mapEl.getBoundingClientRect();
  STREETS.forEach(st => { const el = st.label && st.label.getElement(); if (!el || el.classList.contains("off")) return; const r = el.querySelector("span").getBoundingClientRect(); if (r.width) boxes.push({ x: r.left - mr.left, y: r.top - mr.top, w: r.width, h: r.height }); });
  coverBoxes(mr).forEach(b => boxes.push(b));
  // a day open: labels stay inside the map's visible edges (they are placed again after every pan then)
  const mw = mapEl.clientWidth, mh = mapEl.clientHeight, outside = r => planOn && (r.x < 2 || r.y < 2 || r.x + r.w > mw - 2 || r.y + r.h > mh - 2);
  const hit = r => outside(r) || boxes.some(o => r.x < o.x + o.w + 3 && r.x + r.w + 3 > o.x && r.y < o.y + o.h + 3 && r.y + r.h + 3 > o.y);
  const cands = (W, H, g0) => { const out = []; [12, 34, 60, 95, 135].map(g => g + (g0 || 0)).forEach(g => out.push([g, -H / 2], [-W - g, -H / 2], [-W / 2, -H - g], [-W / 2, g], [g * .7, -H - g * .7], [-W - g * .7, -H - g * .7], [g * .7, g * .7], [-W - g * .7, g * .7])); return out; };
  const rank = s => inP(s) ? -100 + (pOrder[s.id] || 0) / 100 : ORDER(s);
  [...vis].sort((a, b) => rank(a) - rank(b)).forEach(s => {
    const g0 = inP(s) ? 7 : 0;
    const sl = forceSlim || (s.compact && LMODE !== "full");   // compact spots (crowded centre, 次要) keep a name-only label, as on the hand-drawn map
    let placed = null, slim = sl;
    for (const mode of sl ? ["slim"] : forceAll ? ["full"] : ["full", "slim"]) {
      const { w, h } = s[mode];
      for (const [dx, dy] of cands(w, h, g0)) { const r = { x: s.p.x + dx, y: s.p.y + dy, w, h }; if (!hit(r)) { placed = [dx, dy, w, h]; slim = mode === "slim"; break; } }
      if (placed) break;
    }
    if (!placed && forceAll) {   // 全覽／簡潔: no free room, still show it where it covers the least
      const mode = sl ? "slim" : "full", { w, h } = s[mode]; let best = null, bo = Infinity;
      for (const [dx, dy] of cands(w, h, g0)) { const r = { x: s.p.x + dx, y: s.p.y + dy, w, h };
        const o = boxes.reduce((t, b) => t + Math.max(0, Math.min(r.x + r.w, b.x + b.w) - Math.max(r.x, b.x)) * Math.max(0, Math.min(r.y + r.h, b.y + b.h) - Math.max(r.y, b.y)), 0);
        if (o < bo) { bo = o; best = [dx, dy, w, h]; } }
      placed = best; slim = mode === "slim";
    }
    s.g.classList.toggle("slim1", slim);
    if (!placed) { s.g.classList.add("lbl-off"); return; }
    const [dx, dy, W, H] = placed;
    boxes.push({ x: s.p.x + dx, y: s.p.y + dy, w: W, h: H });
    s.tab.style.left = dx + "px"; s.tab.style.top = dy + "px";
    const cx = Math.max(dx, Math.min(0, dx + W)), cy = Math.max(dy, Math.min(0, dy + H));
    s.line.setAttribute("x2", cx); s.line.setAttribute("y2", cy);
  });
  placeLegPills();
}
/* what lies on top of the map (我的行程 panel and its tab, zoom buttons, walk chips): labels and pills keep out of it */
function coverBoxes(mr) {
  const out = [];
  ["plan", "route-pick"].map(id => document.getElementById(id)).concat([...document.querySelectorAll(".mapbox .zoom, .plan-tab")]).forEach(el => {
    if (!el || el.hidden || !el.offsetParent) return; const q = el.getBoundingClientRect(); if (!q.width) return;
    out.push({ x: q.left - mr.left, y: q.top - mr.top, w: q.width, h: q.height });
  });
  return out;
}
/* 我的行程 distance pills (shown after tapping the dashed line): each goes where it covers no label, number or other pill —
   along its leg (middle first, then toward the ends) and a little to either side; with no free room, where it covers the least */
let legPills = [];
function placeLegPills() {
  if (!legPills.length || !mapEl.classList.contains("legs-on")) return;
  const mr = mapEl.getBoundingClientRect(), ob = [];
  const add = el => { if (!el || !el.offsetParent) return; const q = el.getBoundingClientRect(); if (q.width && getComputedStyle(el).visibility !== "hidden") ob.push({ x: q.left - mr.left, y: q.top - mr.top, w: q.width, h: q.height }); };
  coverBoxes(mr).forEach(b => ob.push(b));
  SPOTS.forEach(s => { if (s.g.offsetParent && !s.g.classList.contains("lbl-off") && !mapEl.classList.contains("lbl-none")) add(s.tab); add(s.g.querySelector(".plan-no")); add(s.g.querySelector(".pin")); });
  const over = r => ob.reduce((t, b) => { const ox = Math.min(r.x + r.w, b.x + b.w) - Math.max(r.x, b.x) + 3, oy = Math.min(r.y + r.h, b.y + b.h) - Math.max(r.y, b.y) + 3; return t + (ox > 0 && oy > 0 ? ox * oy : 0); }, 0);   // 3px breathing room
  legPills.forEach(pl => {
    const el = pl.getElement(), sp = el && el.querySelector("span"); if (!sp) return;
    el.classList.remove("leg-hide");   // measure it shown
    const w = sp.offsetWidth, h = sp.offsetHeight, a = map.latLngToContainerPoint(pl._ab[0]), b = map.latLngToContainerPoint(pl._ab[1]);
    const len = Math.hypot(b.x - a.x, b.y - a.y) || 1, nx = -(b.y - a.y) / len, ny = (b.x - a.x) / len, side = Math.abs(nx) * w / 2 + Math.abs(ny) * h / 2 + 6;
    let best = null, bo = Infinity;
    for (const t of [.5, .38, .62, .26, .74, .15, .85]) for (const o of [0, side, -side, side * 2, -side * 2]) {
      const cx = a.x + (b.x - a.x) * t + nx * o, cy = a.y + (b.y - a.y) * t + ny * o, r = { x: cx - w / 2, y: cy - h / 2, w, h };
      const v = over(r) + Math.abs(o) * .5 + Math.abs(t - .5) * 20;   // a free spot near the middle of the leg wins
      if (v < bo) { bo = v; best = [cx, cy, r]; }
      if (v < 30 && o === 0) break;
    }
    // no clear room (the day is zoomed out): leave this pill off; the list still says the distance, zoom in to see it
    const free = over(best[2]) === 0; el.classList.toggle("leg-hide", !free);
    pl.setLatLng(map.containerPointToLatLng(L.point(best[0], best[1]))); if (free) ob.push(best[2]);
  });
}
const sizeTabs = layoutLabels;   // name used by the shared code
map.on("zoomend", layoutLabels);
// with 我的行程 open, which labels the panel would cover changes as the map moves: place them again after a pan
map.on("moveend", () => { const pe = document.getElementById("plan"); if (pe && !pe.hidden) layoutLabels(); });

/* ---- one tap / click on a spot (a drag that starts on a label pans the map instead) ---- */
const onPanes = (...a) => [map.getPane("markerPane"), map.getPane("planSpots")].forEach(p => p.addEventListener(...a));
let downAt = null;
onPanes("pointerdown", e => { downAt = { x: e.clientX, y: e.clientY }; }, true);
const moved = e => downAt && Math.hypot(e.clientX - downAt.x, e.clientY - downAt.y) > 8;
onPanes("click", e => {
  const g = e.target.closest(".spot"); if (!g) return;
  e.stopPropagation();
  if (picking) { const ll = map.mouseEventToLatLng(e); map.fire("click", { latlng: ll }); return; }   // picking a position: a click on a label counts too
  if (e.isTrusted && moved(e)) return;   // the replayed click after the double-click wait has no position
  const id = g.dataset.id;
  distMode ? pickSpot(id) : openSpot(id);
});
onPanes("dblclick", e => { if (e.target.closest(".spot")) { e.stopPropagation(); e.preventDefault(); } });
onPanes("keydown", e => { const g = e.target.closest(".spot"); if (g && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); distMode ? pickSpot(g.dataset.id) : openSpot(g.dataset.id); } });

/* ---- distance mode: point to point (straight line ×1.3) ---- */
const distLayer = L.layerGroup().addTo(map);
let picked = null, pairEnd = null;
const NOTE = "先點起點，會顯示它到相鄰景點的距離（直線 ×1.3 估算）；再點終點，就沿著巷子畫出實際的步行路線和時間，也可以一鍵開 Google 地圖導航。點空白處重新選。步速以每分鐘 80 公尺計算。";
const pill = (ll, text, cls) => L.marker(ll, { icon: L.divIcon({ className: "mid-pill " + (cls || ""), html: `<span>${text}</span>`, iconSize: [0, 0] }), interactive: false, keyboard: false });
const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
function renderDist() {
  distLayer.clearLayers();
  SPOTS.forEach(s => s.g.classList.toggle("picked", s.id === picked || s.id === pairEnd));
  const card = document.getElementById("p2p-card"); card.hidden = !(picked && pairEnd);
  const dt = document.getElementById("dist-text");
  dt.textContent = !picked ? NOTE : !pairEnd ? "起點：" + byId(picked).name + "。再點另一個景點當終點；點空白處取消。" : "起點 " + byId(picked).name + " → 終點 " + byId(pairEnd).name + "。點空白處可重新選起點。";
  // picking only the start shows nothing extra: no lines to the neighbouring spots (removed 2026-11-18)
  if (!picked || !pairEnd) return;
  const a = byId(picked), b = byId(pairEnd), wt = walkText(hav(a.ll, b.ll));
  const line = L.polyline([a.ll, b.ll], { className: "p2p-line", interactive: false }).addTo(distLayer);
  const lbl = pill(mid(a.ll, b.ll), wt, "p2p").addTo(distLayer);
  document.getElementById("p2p-route").textContent = a.name + " → " + b.name;
  const dEl = document.getElementById("p2p-dist");
  dEl.innerHTML = wt.replace("・", " ・ ") + "<small>直線估算，路線計算中…</small>";
  document.getElementById("p2p-go").href = gDir([a.ll, b.ll]);
  const want = picked + ">" + pairEnd;
  walkRoute([a.ll, b.ll]).then(rt => {
    if (!rt || picked + ">" + pairEnd !== want) { if (!rt) dEl.querySelector("small").textContent = "直線 ×1.3 估算"; return; }
    line.setLatLngs(rt.coords);
    const t = realText(rt.total), m = rt.coords[Math.floor(rt.coords.length / 2)];
    lbl.setLatLng(m); lbl.getElement().querySelector("span").textContent = t;
    dEl.innerHTML = t.replace("・", " ・ ") + "<small>實際步行路線</small>";
  });
}
function pickSpot(id) {
  if (id === null) picked = pairEnd = null;
  else if (!picked || pairEnd) { picked = id; pairEnd = null; }
  else if (id === picked) picked = null;
  else pairEnd = id;
  renderDist();
}
function setDist(on) {
  distMode = on;
  document.querySelectorAll(".icon-btn.dist").forEach(b => b.setAttribute("aria-pressed", on));
  mapEl.classList.toggle("dist", on);
  document.getElementById("dist-note").hidden = !on;
  pickSpot(null); layoutLabels();
}
document.querySelectorAll(".icon-btn.dist").forEach(b => b.addEventListener("click", () => { setDist(!distMode); if (distMode) tripMode("dist"); }));
/* 2026-11-27: 點對點, 我的行程 and City Walk each draw lines; turning one on (by the user) turns the others' lines off:
   點對點 or 我的行程 → City Walk off; 我的行程 or City Walk → 點對點 off. The city's own parts listen for "trip-mode". */
function tripMode(m) { if (m !== "dist" && distMode) setDist(false); document.dispatchEvent(new CustomEvent("trip-mode", { detail: m })); }
document.addEventListener("trip-mode", e => { if (e.detail === "walk" && distMode) setDist(false); });
document.getElementById("dist-text").textContent = NOTE;

/* ---- filters ---- */
function applySup() {
  const tiers = new Set([...document.querySelectorAll(".chip[data-tier]")].filter(pressed).map(c => c.dataset.tier));
  const cats = new Set([...document.querySelectorAll(".chip[data-cat]")].filter(pressed).map(c => c.dataset.cat));
  if (!cats.size) ["paid", "free", "mine"].forEach(c => cats.add(c));
  if (cats.has("free")) cats.add("open");
  const cold = pressed(document.getElementById("f-cold"));
  SPOTS.forEach(s => {
    const gone = !!s.tier && !tiers.has(s.tier), dim = s.cat === "base" ? false : s.cat === "mine" ? !cats.has("mine") : (!cats.has(s.cat) || (cold && !s.cold) || !!s.dayClosed);
    s.g.classList.toggle("gone", gone); s.g.classList.toggle("dim", dim);
    if (s.areaEl) areaVis(s, dim ? .25 : 1);   // the area stays even when its tier is hidden (like the hand-drawn map)
  });
  if (RAD.id) renderRad();
  renderDist(); layoutLabels();
}
function applyDays() {
  let sel = DAYS.filter(pressed).map(b => +b.dataset.day);
  if (!sel.length) sel = [0, 1, 2, 3, 4, 5, 6];
  SPOTS.forEach(s => {
    s.dayClosed = false;
    if (!s.tw || !WEEK[s.id]) return;
    const lbl = sel.length === 7 ? compactLabel(WEEK[s.id], WEEK_PREFIX[s.id] || "") : weekLabel(s.id, sel), closed = lbl === null;
    s.dayClosed = closed && !WEEK_NODIM.has(s.id);
    s.tw.textContent = closed ? "你選的日子休館" : lbl;
    s.tw.classList.toggle("day-off", closed);
  });
}
DAYS.forEach(b => b.addEventListener("click", () => {
  b.setAttribute("aria-pressed", pressed(b) ? "false" : "true");
  try { localStorage.setItem(DKEY, JSON.stringify(DAYS.filter(pressed).map(x => +x.dataset.day))); } catch (e) {}
  applyDays(); applySup(); renderPlan();
}));
const FKEY = "trip-filters-" + CITY.key, FCHIPS = [...document.querySelectorAll(".chip[data-tier], .chip[data-cat], #f-cold")];
const chipKey = ch => ch.id || ch.dataset.tier || ch.dataset.cat;
try { const saved = JSON.parse(localStorage.getItem(FKEY) || "null"); if (saved) FCHIPS.forEach(ch => { const k = chipKey(ch); if (k in saved) ch.setAttribute("aria-pressed", saved[k] ? "true" : "false"); }); } catch (e) {}
const saveFilters = () => { try { localStorage.setItem(FKEY, JSON.stringify(Object.fromEntries(FCHIPS.map(ch => [chipKey(ch), pressed(ch)])))); } catch (e) {} };
FCHIPS.forEach(ch => ch.addEventListener("click", () => { ch.setAttribute("aria-pressed", pressed(ch) ? "false" : "true"); saveFilters(); applySup(); }));

/* ---- 方圓 100 公尺: long-press (touch) or click twice (mouse) on a spot; real metres on the real map ---- */
var RAD = { id: null, r: 0, closedAt: 0 };
const radLayer = L.layerGroup().addTo(map), radCard = document.getElementById("rad-card");
function renderRad() {
  radLayer.clearLayers();
  SPOTS.forEach(s => s.g.classList.remove("rad-out", "rad-center"));
  radCard.hidden = !RAD.id;
  if (!RAD.id) return;
  const c = byId(RAD.id);
  for (let k = 100; k < RAD.r; k += 100) L.circle(c.ll, { radius: k, className: "rad-ring", interactive: false }).addTo(radLayer);
  L.circle(c.ll, { radius: RAD.r, className: "rad-circle", interactive: false }).addTo(radLayer);
  let n = 0;
  SPOTS.forEach(s => {
    if (s.g.classList.contains("gone")) return;
    const inside = Math.round(hav(s.ll, c.ll) / 5) * 5 <= RAD.r;
    s.g.classList.toggle("rad-out", !inside);
    if (inside && s.id !== c.id && s.cat !== "base") n++;
  });
  c.g.classList.add("rad-center");
  radCard.innerHTML = "";
  const h = document.createElement("div");
  h.innerHTML = `<b></b>　半徑 ${RAD.r} 公尺內 ${n} 個景點<button class="rad-x" type="button">關閉</button>`;
  h.querySelector("b").textContent = c.name;
  h.querySelector(".rad-x").addEventListener("click", closeRad);
  const t = document.createElement("div"); t.style.color = "var(--muted)"; t.style.fontSize = "12px";
  t.textContent = "再長按一次（電腦：在景點上點兩下）擴大 100 公尺；點一下地圖空白處關閉（直線距離）";
  radCard.append(h, t);
  const b = L.circle(c.ll, { radius: RAD.r }).addTo(map); const bb = b.getBounds(); map.removeLayer(b);
  if (!map.getBounds().contains(bb)) map.fitBounds(bb, { padding: [40, 40], maxZoom: map.getZoom() });
}
function closeRad() { if (!RAD.id) return; RAD.id = null; RAD.r = 0; RAD.closedAt = performance.now(); renderRad(); }
const growRad = id => { if (RAD.id === id) RAD.r += 100; else { RAD.id = id; RAD.r = 100; } renderRad(); };
(() => {
  let timer = null, fired = 0, lastType = "mouse", pend = null, bypass = false;
  const cancel = () => { clearTimeout(timer); timer = null; };
  onPanes("pointerdown", e => {
    lastType = e.pointerType || "mouse";
    const g = e.target.closest(".spot"); if (!g || lastType === "mouse") return;
    cancel();
    timer = setTimeout(() => { timer = null; fired = performance.now(); if (navigator.vibrate) try { navigator.vibrate(15); } catch (_) {} growRad(g.dataset.id); }, 550);
  }, true);
  window.addEventListener("pointermove", e => { if (timer && moved(e)) cancel(); });
  window.addEventListener("pointerup", cancel); window.addEventListener("pointercancel", cancel);
  onPanes("contextmenu", e => { if (e.target.closest(".spot")) e.preventDefault(); });
  onPanes("click", e => {
    const g = e.target.closest(".spot"); if (!g) return;
    if (performance.now() - fired < 700) { e.stopPropagation(); e.preventDefault(); return; }   // the click that ends a long press
    if (bypass || lastType !== "mouse" || distMode || picking || moved(e)) return;
    e.stopPropagation(); e.preventDefault();
    if (pend && pend.g === g) { clearTimeout(pend.t); pend = null; growRad(g.dataset.id); return; }   // mouse: second click = 範圍
    if (pend) clearTimeout(pend.t);
    pend = { g, t: setTimeout(() => { pend = null; bypass = true; g.dispatchEvent(new MouseEvent("click", { bubbles: true })); bypass = false; }, 260) };
  }, true);
})();
map.on("click", () => { if (picking) return; if (RAD.id) closeRad(); if (distMode && picked) pickSpot(null); });

/* ---- 我的景點: the reader's own spots (right-click / long-press on the map, or from the plan panel) ---- */
CAT.mine = { label: "我自己加的景點", color: "#7B3C8C" };
const CKEY = "trip-custom-" + CITY.key;
let MINE = []; try { MINE = JSON.parse(localStorage.getItem(CKEY) || "[]"); } catch (e) {}
const saveMine = () => { try { localStorage.setItem(CKEY, JSON.stringify(MINE.map(({ id, name, ll, note, gurl }) => ({ id, name, ll, note, gurl })))); } catch (e) {} };
function mineSpot(m) {
  return Object.assign(m, { cat: "mine", custom: true, ll: m.ll, latin: "我自己加的景點", feature: m.note || "（沒有備註）", sPrice: "我的景點", cold: true, x: 0, y: 0, lx: 0, ly: 0 });
}
MINE.forEach(m => { SPOTS.push(mineSpot(m)); makeSpot(m); });
function addMine(name, ll, note, gurl) {
  const m = mineSpot({ id: "c_" + Date.now().toString(36), name, ll, note, gurl });
  MINE.push(m); SPOTS.push(m); makeSpot(m); saveMine(); applySup(); return m;
}
function delMine(id) {
  const i = MINE.findIndex(m => m.id === id); if (i < 0) return;
  const m = MINE[i]; m.marker.remove(); MINE.splice(i, 1); SPOTS.splice(SPOTS.indexOf(m), 1);
  Object.values(plan.days).forEach(a => { const j = a.findIndex(x => x.id === id); if (j >= 0) a.splice(j, 1); });
  saveMine(); savePlan(); closeSpot(); renderPlan(); layoutLabels();
}
function bindMineEdit(m) {
  const box = document.getElementById("m-edit"), $ = id => document.getElementById(id);
  let newLL = null;
  const showEdit = () => { box.hidden = false; $("me-name").value = m.name; $("me-link").value = m.gurl || ""; $("me-note").value = m.note || ""; $("me-where").textContent = "✓ 位置不變"; $("me-where").classList.add("ok"); $("me-name").focus(); };
  $("d-editmine").addEventListener("click", () => box.hidden ? showEdit() : (box.hidden = true));
  if (m._reEdit) { const ll = m._reEdit; delete m._reEdit; showEdit(); newLL = ll; $("me-where").textContent = "✓ 已改成地圖上點的新位置"; }
  $("me-link").addEventListener("input", () => { const r = parseGmap($("me-link").value); if (!r) return;
    if (r.ll) { newLL = r.ll; $("me-where").textContent = "✓ 已從 Google 地圖連結抓到新位置"; $("me-where").classList.add("ok"); }
    else if (r.short) { $("me-where").textContent = "短網址抓不到位置：請打開它、複製網址列的完整網址，或貼座標"; $("me-where").classList.remove("ok"); } });
  $("me-pick").addEventListener("click", () => { closeSpot(); picking = true; mapEl.classList.add("picking"); pickCb = ll => { m._reEdit = ll; openSpot(m.id); }; });
  $("me-cancel").addEventListener("click", () => { box.hidden = true; });
  $("me-save").addEventListener("click", () => {
    const name = $("me-name").value.trim(); if (!name) { $("me-name").focus(); return; }
    m.name = name; m.note = $("me-note").value.trim(); m.feature = m.note || "（沒有備註）";
    const link = $("me-link").value.trim(); m.gurl = /^https?:\/\//.test(link) ? link : "";
    if (newLL) { m.ll = newLL; m.marker.setLatLng(newLL); }
    m.g.querySelector(".t-name").textContent = name; m.g.setAttribute("aria-label", name);
    saveMine(); renderPlan(); layoutLabels(); openSpot(m.id);
  });
  // delete: asks first — 刪除（行程與景點會一起刪除）or 取消; taking it off a day is done in 我的行程 itself
  $("d-delmine").addEventListener("click", () => { $("d-sure").hidden = false; });
  $("d-delno").addEventListener("click", () => { $("d-sure").hidden = true; });
  $("d-delyes").addEventListener("click", () => delMine(m.id));
}
/* read a position (and a name) out of whatever the reader pastes from Google Maps */
function parseGmap(t) {
  t = (t || "").trim(); if (!t) return null;
  let m = t.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/) || t.match(/@(-?\d+\.\d+),\s*(-?\d+\.\d+)/) || t.match(/[?&](?:q|query|ll|destination|center)=(-?\d+\.\d+)(?:,|%2C)\s*(-?\d+\.\d+)/i) || t.match(/^\s*(-?\d{1,2}\.\d+)\s*[,，\s]\s*(-?\d{1,3}\.\d+)\s*$/);
  const name = (t.match(/\/place\/([^/@?]+)/) || [])[1];
  if (!m) return { short: /goo\.gl|g\.co\//.test(t), name: name ? decodeURIComponent(name.replace(/\+/g, " ")) : "" };
  return { ll: [+m[1], +m[2]], name: name ? decodeURIComponent(name.replace(/\+/g, " ")) : "" };
}

/* ---- 我的行程: per-day list, drag to reorder, time + note, numbered pins and a dashed route on the map ---- */
const PKEY = "trip-plan-" + CITY.key;
const WD = "一二三四五六日";
let plan = { cur: CITY.days[0].k, days: {}, list: null };
try { const sv = JSON.parse(localStorage.getItem(PKEY) || "null"); if (sv && sv.days) plan = sv; } catch (e) {}
// days are the reader's own: date typed in, weekday picked (0 = Monday); default = this trip's Lucca days
if (!Array.isArray(plan.list) || !plan.list.length) plan.list = CITY.days.map(d => Object.assign({}, d));
const PDAYS = plan.list;
const dayLabel = d => (d.date || "未定") + "（" + WD[d.wd] + "）";
PDAYS.forEach(d => { d.label = dayLabel(d); if (!Array.isArray(plan.days[d.k])) plan.days[d.k] = []; });
if (!PDAYS.some(d => d.k === plan.cur)) plan.cur = PDAYS[0].k;
const visSet = () => { try { return visited; } catch (e) { return null; } };   // 去過 is set up after the engine
const savePlan = () => { try { localStorage.setItem(PKEY, JSON.stringify(plan)); } catch (e) {} };
const planHas = (k, id) => plan.days[k].some(x => x.id === id);
function planToggle(k, id) {
  const a = plan.days[k], i = a.findIndex(x => x.id === id);
  if (i >= 0) a.splice(i, 1); else a.push({ id, time: "", note: "" });
  plan.cur = k; plan.on = true; savePlan(); renderPlan();
}
const planEl = document.getElementById("plan"), planList = document.getElementById("plan-list"), planLayer = L.layerGroup().addTo(map);
let planOpen = false, legsOn = false;   // legsOn: the distance pills on the plan's dashed line (tap the line to show / hide)
try { planOpen = localStorage.getItem(PKEY + "-open") === "1"; } catch (e) {}
/* plan.on = false: 「不選」 no day chosen, so 我的行程 is off and the map looks as usual (the days stay saved).
   Collapsing the panel (the 「我的行程」 tab) only hides the panel: the chosen day's route stays on the map. */
function renderPlan() {
  const dayOn = plan.on !== false, nItems = plan.days[plan.cur].filter(x => byId(x.id)).length;
  const active = dayOn && (planOpen || nItems > 0);   // a collapsed empty day does not grey out the map
  if (!planOpen) unMode = false;
  planEl.hidden = !planOpen;
  planEl.classList.toggle("off", !dayOn);
  document.querySelectorAll(".plan-btn").forEach(b => { b.setAttribute("aria-expanded", planOpen); b.setAttribute("aria-label", planOpen ? "收起我的行程" : "打開我的行程"); b.classList.toggle("open", planOpen); b.classList.toggle("big", planEl.classList.contains("big")); });
  placeTab();
  mapEl.classList.toggle("planning", active);
  const days = document.getElementById("plan-days");
  days.innerHTML = PDAYS.map(d => `<button type="button" role="tab" data-k="${d.k}" aria-selected="${dayOn && d.k === plan.cur}">${d.label.replace(/[&<>"]/g, c => "&#" + c.charCodeAt(0) + ";")}<span class="n">${plan.days[d.k].length || ""}</span></button>`).join("") + '<button type="button" class="pd-add" aria-label="新增一天">＋</button><button type="button" class="pd-paste">＋ 匯入本日行程</button>';
  // drag a day tab to change the order of the days (the date goes with it; the user edits dates by hand)
  if (!days._sortable) days._sortable = Sortable.create(days, { draggable: "button[data-k]", animation: 150, delay: 300, delayOnTouchOnly: true, touchStartThreshold: 6, onEnd: () => {   // phone: long press drags, a swipe scrolls the row
    const order = [...days.querySelectorAll("button[data-k]")].map(b => b.dataset.k);
    const moved = order.map(k => PDAYS.find(d => d.k === k)); PDAYS.splice(0, PDAYS.length, ...moved); savePlan(); renderPlan();
  } });
  // tap a day to open it; tap the open day again to close it (no day chosen = 我的行程 off, the map looks as usual)
  days.querySelectorAll("button[data-k]").forEach(b => b.addEventListener("click", () => {
    if (dayOn && plan.cur === b.dataset.k) { plan.on = false; unMode = false; savePlan(); renderPlan(); return; }
    plan.cur = b.dataset.k; plan.on = true; savePlan(); renderPlan(); fitPlan(); tripMode("plan"); }));
  days.querySelector(".pd-paste").addEventListener("click", () => togglePaste(true, "day"));   // 2026-11-27: import one day right here
  days.querySelector(".pd-add").addEventListener("click", () => {
    const last = PDAYS[PDAYS.length - 1], k = "d" + Date.now().toString(36);
    let date = "";
    const m = last && /^(\d{1,2})\/(\d{1,2})$/.exec(last.date || ""); if (m) { const t = new Date(2027, +m[1] - 1, +m[2] + 1); date = (t.getMonth() + 1) + "/" + t.getDate(); }
    const d = { k, date, wd: last ? (last.wd + 1) % 7 : 0 }; d.label = dayLabel(d);
    PDAYS.push(d); plan.days[k] = []; plan.cur = k; plan.on = true; savePlan(); renderPlan();
  });
  // the chosen day's own date + weekday
  const cd = PDAYS.find(d => d.k === plan.cur), ed = document.getElementById("plan-dayedit");
  ed.innerHTML = `<label>日期 <input class="pd-date" type="text" maxlength="10" placeholder="例如 2/3"></label><label>星期 <select class="pd-wd">${[...WD].map((w, i) => `<option value="${i}">${w}</option>`).join("")}</select></label>${PDAYS.length > 1 ? '<button type="button" class="pd-del">刪除這天</button>' : ""}`;
  const di = ed.querySelector(".pd-date"), ws = ed.querySelector(".pd-wd");
  di.value = cd.date || ""; ws.value = cd.wd;
  di.addEventListener("change", () => { cd.date = di.value.trim(); cd.label = dayLabel(cd); savePlan(); renderPlan(); });
  ws.addEventListener("change", () => { cd.wd = +ws.value; cd.label = dayLabel(cd); savePlan(); renderPlan(); });
  ed.querySelector(".pd-del")?.addEventListener("click", e => {
    const b = e.currentTarget;
    if (plan.days[cd.k].length && b.dataset.sure !== "1") { b.dataset.sure = "1"; b.textContent = "確定刪除這天？"; return; }
    PDAYS.splice(PDAYS.indexOf(cd), 1); delete plan.days[cd.k]; plan.cur = PDAYS[0].k; savePlan(); renderPlan();
  });
  const items = plan.days[plan.cur].filter(x => byId(x.id));
  const memo = document.getElementById("plan-daymemo");
  memo.innerHTML = '<input class="pd-memo" type="text" maxlength="60" placeholder="這天的筆記（例如：導遊導覽日）" aria-label="這天的筆記"><button type="button" class="pd-done"></button>';
  const mi = memo.querySelector(".pd-memo"); mi.value = cd.memo || "";
  mi.addEventListener("change", () => { cd.memo = mi.value.trim(); savePlan(); });
  // 10. one tap: every spot of this day 去過 / not 去過 (the same 「已去過」 as in a spot's own page)
  const V = visSet(), vIds = items.map(x => x.id).filter(id => byId(id).cat !== "base"), allV = !!V && vIds.length > 0 && vIds.every(id => V.has(id));
  const db = memo.querySelector(".pd-done");
  db.hidden = !V || !vIds.length; db.textContent = allV ? "✓ 這天全部去過" : "這天全部去過"; db.title = allV ? "再按一次，這天全部改回沒去過" : "這天的景點全部標成去過"; db.setAttribute("aria-pressed", allV);
  db.addEventListener("click", () => { vIds.forEach(id => allV ? V.delete(id) : V.add(id)); saveVisited(); applyVisited(); renderPlan(); });
  document.getElementById("plan-empty").hidden = items.length > 0;
  planList.innerHTML = "";
  let total = 0;
  items.forEach((x, i) => {
    const s = byId(x.id), li = document.createElement("li");
    li.dataset.id = x.id;
    li.innerHTML = `<span class="p-drag" aria-label="拖曳調整順序">⋮⋮</span><span class="p-no">${i + 1}</span><span class="p-time-txt"></span><button type="button" class="p-name"></button><input class="p-time" type="text" inputmode="numeric" maxlength="5" placeholder="--:--" aria-label="幾點到（24 小時制，例如 09:30）"><button type="button" class="p-vis" aria-label="去過了沒" title="去過了沒（點一下切換）">去過</button><button type="button" class="p-del" aria-label="從這天的行程移除（景點還留在地圖上）" title="從這天的行程移除">×</button><div class="p-info"></div><input class="p-note" type="text" placeholder="備註" aria-label="備註">`;
    li.querySelector(".p-name").textContent = s.name;
    const isV = !!visSet() && visSet().has(s.id), vb = li.querySelector(".p-vis");
    li.classList.toggle("p-visited", isV); vb.setAttribute("aria-pressed", isV); vb.hidden = !visSet() || s.cat === "base";
    vb.title = isV ? "已去過（點一下取消）" : "標記為已去過"; vb.textContent = isV ? "✓ 去過" : "去過";
    vb.addEventListener("click", () => { const V = visSet(); if (!V) return; V.has(s.id) ? V.delete(s.id) : V.add(s.id); saveVisited(); applyVisited(); renderPlan(); });
    li.querySelector(".p-name").addEventListener("click", () => { openSpot(s.id); setTimeout(() => focusOn(s), 320); });
    const tm = li.querySelector(".p-time"); tm.value = x.time || ""; li.querySelector(".p-time-txt").textContent = x.time || "";
    // 24-hour, like the hours on the map: "930" / "9:30" / "0930" → 09:30
    tm.addEventListener("change", () => { const raw = tm.value.trim(), d = raw.replace(/[^0-9]/g, ""); let v = "", h, m;
      if (/[:：.]/.test(raw)) { const [a, b] = raw.split(/[:：.]/); h = +a; m = +(b || 0); } else if (d) { h = d.length <= 2 ? +d : +d.slice(0, d.length - 2); m = d.length <= 2 ? 0 : +d.slice(-2); }
      if (d && h < 24 && m < 60) v = String(h).padStart(2, "0") + ":" + String(m).padStart(2, "0");
      tm.value = v; x.time = v; li.querySelector(".p-time-txt").textContent = v; savePlan(); });
    // the same hours / price lines as the spot's label on the map (they follow 星期幾去)
    // hours on this day's weekday (from the same week table the map uses); closed that day = red
    const info = li.querySelector(".p-info"), wv = WEEK[s.id] ? WEEK[s.id][cd.wd] : null;
    const hrs = WEEK[s.id] ? (wv ? "週" + WD[cd.wd] + " " + wv : "週" + WD[cd.wd] + "休館") : (s.cat === "open" && s.hours ? s.hours[0] : "");
    info.textContent = [hrs, s.sPrice].filter(Boolean).join("・");
    info.classList.toggle("closed", !!WEEK[s.id] && !wv);
    const nt = li.querySelector(".p-note"); nt.value = x.note || ""; nt.addEventListener("change", () => { x.note = nt.value; savePlan(); });
    li.querySelector(".p-del").addEventListener("click", e => {
      // asks once: the first tap turns × into 「確定移除？」, the second tap removes (resets after 4 s)
      const b = e.currentTarget;
      if (b.dataset.sure !== "1") { b.dataset.sure = "1"; b.classList.add("sure"); b.textContent = "確定移除？"; setTimeout(() => { if (b.isConnected) { b.dataset.sure = ""; b.classList.remove("sure"); b.textContent = "×"; } }, 4000); return; }
      planToggle(plan.cur, x.id);
      // own spots: × only takes it off this day; the spot stays on the map (delete it from its own drawer)
      if (s.custom) { const t = document.getElementById("plan-share-note"); t.hidden = false; t.textContent = "已從這天的行程移除「" + s.name + "」，景點還留在地圖上；要刪除景點，請在地圖上點它再按「刪除景點」。"; } });
    const nxt = items[i + 1];
    if (nxt) {
      const m = hav(s.ll, byId(nxt.id).ll); total += m;
      const leg = document.createElement("div"); leg.className = "p-leg";
      leg.innerHTML = '<span class="p-leg-t"></span>（<a class="p-leg-go" target="_blank" rel="noopener">直線估算・導航 ↗</a>）';
      leg.querySelector(".p-leg-t").textContent = "↓ 步行約 " + walkText(m);
      const a = leg.querySelector("a"); a.href = gDir([s.ll, byId(nxt.id).ll]);
      a.setAttribute("aria-label", "用 Google 地圖導航：" + s.name + " 到 " + byId(nxt.id).name);
      li.appendChild(leg);
    }
    planList.appendChild(li);
  });
  const w = walkM(total);
  document.getElementById("plan-sum").textContent = items.length > 1 ? `走路共約 ${w.m < 1000 ? w.m + " m" : (w.m / 1000).toFixed(1) + " km"}・${w.min} 分` : "";
  // map: numbers on the pins + dashed route in order
  planLayer.clearLayers(); legPills = [];
  SPOTS.forEach(s => { s.g.classList.remove("in-plan"); s.g.querySelector(".plan-no").textContent = ""; });
  planEl.classList.toggle("un-mode", unMode);
  document.getElementById("plan-un").setAttribute("aria-pressed", unMode);
  const sched = new Set(Object.values(plan.days).flat().map(x => x.id));
  const unSpots = SPOTS.filter(s => s.cat !== "base" && !sched.has(s.id));
  renderUnList(unSpots);
  const inDay = new Set(!active && !(planOpen && unMode) ? [] : unMode ? unSpots.map(s => s.id) : items.map(x => x.id));
  mapEl.classList.toggle("planning", active || (planOpen && unMode));
  if (planOpen && unMode) {
    SPOTS.forEach(s => { s.g.classList.remove("in-plan"); s.g.querySelector(".plan-no").textContent = ""; });
    SPOTS.forEach(s => { const want = inDay.has(s.id) ? "planSpots" : "markerPane"; if (s.marker.options.pane !== want) { s.marker.remove(); s.marker.options.pane = want; s.marker.addTo(map); } s.g.classList.toggle("un-hi", inDay.has(s.id)); });
    document.getElementById("plan-go").hidden = true; layoutLabels(); return;
  }
  SPOTS.forEach(s => s.areaEl && s.areaEl.eachLayer(l => l._path && l._path.classList.toggle("plan-dim", mapEl.classList.contains("planning") && !inDay.has(s.id))));   // areas dim with the other spots unless in this day
  SPOTS.forEach(s => s.g.classList.remove("un-hi"));
  SPOTS.forEach(s => { const want = inDay.has(s.id) ? "planSpots" : "markerPane"; if (s.marker.options.pane !== want) { s.marker.remove(); s.marker.options.pane = want; s.marker.addTo(map); } });
  document.getElementById("plan-go").hidden = true;
  if (!active) { layoutLabels(); return; }
  items.forEach((x, i) => { const s = byId(x.id); s.g.classList.add("in-plan"); const n = s.g.querySelector(".plan-no"); n.textContent = n.textContent ? n.textContent + "," + (i + 1) : i + 1; });
  layoutLabels();
  const go = document.getElementById("plan-go");
  go.hidden = items.length < 2;
  if (items.length > 1) {
    const pts = items.map(x => byId(x.id).ll);
    go.href = gDir(pts.slice(0, 10));
    const line = L.polyline(pts, { className: "plan-line", interactive: false, pane: "planRoute" }).addTo(planLayer);
    const pills = [];
    // 2026-11-21: no distance pills on the map (the list says each leg); legPills stays empty
    const want = plan.cur + ":" + items.map(x => x.id).join(",");
    walkRoute(pts).then(rt => {
      if (!rt || want !== plan.cur + ":" + plan.days[plan.cur].filter(x => byId(x.id)).map(x => x.id).join(",")) return;
      line.setLatLngs(rt.coords);
      rt.legs.forEach((m, i) => { const el = pills[i] && pills[i].getElement(); if (el) el.querySelector("span").textContent = realText(m); const lg = planList.children[i] && planList.children[i].querySelector(".p-leg-t"); if (lg) { lg.textContent = "↓ 步行約 " + realText(m); lg.parentNode.querySelector(".p-leg-go").textContent = "實際路線 ↗"; } });
      placeLegPills();
      const w = rt.total; document.getElementById("plan-sum").textContent = `走路共約 ${realText(w).replace("・", "・約 ")}`;
    });
  }
}
/* from the plan list: bring that spot's number into the part of the map nothing covers (plan panel, drawer), then make it pulse */
function focusOn(s) { panFree(s.ll, Math.max(map.getZoom(), 17)); s.g.classList.remove("pulse"); void s.g.offsetWidth; s.g.classList.add("pulse"); setTimeout(() => s.g.classList.remove("pulse"), 2200); }
function panFree(ll, z) {
  z = z || map.getZoom(); const mr = mapEl.getBoundingClientRect();
  let l = mr.left, r = mr.right, t = mr.top, b = mr.bottom;
  [planEl, document.getElementById("drawer"), addPop].forEach(el => {
    if (!el || el.hidden) return; const q = el.getBoundingClientRect(); if (!q.width || !q.height || q.right <= mr.left || q.left >= mr.right || q.top >= mr.bottom) return;
    if (q.width > mr.width * .75) b = Math.min(b, Math.max(q.top, mr.top + 60));   // bottom sheet (phone)
    else if (q.left + q.width / 2 < mr.left + mr.width / 2) l = Math.max(l, q.right); else r = Math.min(r, q.left);
  });
  const tx = (l + r) / 2 - mr.left, ty = (t + b) / 2 - mr.top;
  const c = map.project(ll, z).add([mr.width / 2 - tx, mr.height / 2 - ty]);
  map.setView(map.unproject(c, z), z, { animate: true });
}
function fitPlan() {
  if (plan.on === false) return;
  const items = plan.days[plan.cur].filter(x => byId(x.id)); if (!items.length) return;
  const b = L.latLngBounds(items.map(x => byId(x.id).ll));
  const left = !mq.matches || innerWidth > 640 ? planEl.offsetWidth + 30 : 20, bottom = innerWidth <= 640 ? planEl.offsetHeight + 20 : 20;
  map.fitBounds(b, { paddingTopLeft: [left, 60], paddingBottomRight: [60, bottom], maxZoom: 17.5 });
}
Sortable.create(planList, { handle: ".p-drag", animation: 150, onEnd: () => {
  const order = [...planList.children].map(li => li.dataset.id), a = plan.days[plan.cur];
  plan.days[plan.cur] = order.map(id => a.find(x => x.id === id)).filter(Boolean); savePlan(); renderPlan();
} });
/* 簡潔程度: 完整 → 簡潔 → 最簡 → 完整 (remembered on this device) */
const LV = ["全覽", "簡潔", "最簡"];
let planLv = 0; try { planLv = +(localStorage.getItem(PKEY + "-lv") || 0) % 3; } catch (e) {}
function applyLv() { planEl.classList.toggle("c1", planLv === 1); planEl.classList.toggle("c2", planLv === 2); document.getElementById("plan-lv-t").textContent = LV[planLv]; }
document.getElementById("plan-lv").addEventListener("click", () => { planLv = (planLv + 1) % 3; try { localStorage.setItem(PKEY + "-lv", planLv); } catch (e) {} applyLv(); });
applyLv();
/* 自己加景點 form */
const addBox = document.getElementById("plan-add"), addLL = { ll: null, marker: null };
let picking = false, pickCb = null;
function setAddLL(ll, how) {
  addLL.ll = ll;
  if (addLL.marker) addLL.marker.remove();
  addLL.marker = ll ? L.circleMarker(ll, { radius: 9, className: "add-pin", interactive: false }).addTo(map) : null;
  document.getElementById("pa-where").textContent = ll ? "✓ 位置已選好（" + how + "）" : "或";
  document.getElementById("pa-where").classList.toggle("ok", !!ll);
  document.getElementById("pa-pick").textContent = ll ? "重新選位置" : "點這裡去設定地圖";
}
function openAdd(ll) {
  if (addFromMap) closeAdd();
  // the same 「地圖沒有的點」 form, whether it was opened from the map (right-click / long-press) or from 我的行程
  if (!document.getElementById("drawer").hidden) { try { closeSpot(); } catch (e) {} }
  if (unMode) { unMode = false; }
  plan.on = true; savePlan();
  if (!planOpen) setPlanOpen(true); else renderPlan();
  addBox.hidden = false; document.getElementById("pa-name").value = ""; document.getElementById("pa-link").value = ""; document.getElementById("pa-note").value = "";
  setAddLL(ll || null, ll ? "地圖上點的位置" : "");
  setTimeout(() => { addBox.scrollIntoView({ block: "nearest", behavior: "smooth" }); if (ll) panFree(ll); document.getElementById("pa-name").focus({ preventScroll: true }); }, 60);
}
/* from the map (right-click / long-press): only the same form, in its own small window — 我的行程 stays as it is */
const addHome = addBox.parentNode, addNext = addBox.nextSibling;
let addFromMap = false, addPop = null;
function openAddPop(ll) {
  if (!document.getElementById("drawer").hidden) { try { closeSpot(); } catch (e) {} }
  if (!addPop) { addPop = document.createElement("div"); addPop.className = "add-pop"; addPop.setAttribute("role", "dialog"); addPop.setAttribute("aria-label", "加自己的點");
    addPop.innerHTML = '<div class="add-pop-head"><b>加自己的點</b><button type="button" class="add-pop-x" aria-label="取消">×</button></div>';
    addPop.querySelector(".add-pop-x").addEventListener("click", () => closeAdd());
    document.body.append(addPop); L.DomEvent.disableClickPropagation(addPop); L.DomEvent.disableScrollPropagation(addPop); }
  addFromMap = true; addPop.append(addBox); addPop.hidden = false;
  addBox.hidden = false; document.getElementById("pa-name").value = ""; document.getElementById("pa-link").value = ""; document.getElementById("pa-note").value = "";
  setAddLL(ll, "地圖上點的位置");
  setTimeout(() => { panFree(ll); document.getElementById("pa-name").focus({ preventScroll: true }); }, 60);
}
function closeAdd() {
  addBox.hidden = true; picking = false; mapEl.classList.remove("picking"); setAddLL(null);
  if (addFromMap) { addFromMap = false; addPop.hidden = true; addHome.insertBefore(addBox, addNext); }
}
document.getElementById("plan-addbtn").addEventListener("click", () => addBox.hidden ? openAdd() : closeAdd());
document.getElementById("pa-cancel").addEventListener("click", closeAdd);
document.getElementById("pa-pick").addEventListener("click", () => { picking = true; mapEl.classList.add("picking"); document.getElementById("pa-where").textContent = "請點地圖上的位置…"; });
document.getElementById("pa-link").addEventListener("input", e => {
  const r = parseGmap(e.target.value), msg = document.getElementById("pa-where");
  if (!r) return;
  if (r.ll) { setAddLL(r.ll, "從 Google 地圖連結"); map.panTo(r.ll); }
  else if (r.short) { msg.textContent = "這是短網址，抓不到位置：請在瀏覽器打開它，再複製網址列的完整網址貼上；或在 Google 地圖對著地點按右鍵，複製第一行的座標貼上"; msg.classList.remove("ok"); }
  if (r.name && !document.getElementById("pa-name").value) document.getElementById("pa-name").value = r.name;
});
document.getElementById("pa-ok").addEventListener("click", () => {
  const name = document.getElementById("pa-name").value.trim(), msg = document.getElementById("pa-where");
  if (!name) { document.getElementById("pa-name").focus(); msg.textContent = "請先填名稱"; msg.classList.remove("ok"); return; }
  if (!addLL.ll) { msg.textContent = "還沒有位置：貼 Google 地圖網址或座標，或"; msg.classList.remove("ok"); return; }
  const link = document.getElementById("pa-link").value.trim();
  const m = addMine(name, addLL.ll, document.getElementById("pa-note").value.trim(), /^https?:\/\//.test(link) ? link : "");
  if (!addFromMap) { plan.days[plan.cur].push({ id: m.id, time: "", note: "" }); savePlan(); }   // from the map: only a spot on the map, not in a day
  closeAdd(); renderPlan();
});
map.on("click", e => { if (!picking) return; picking = false; mapEl.classList.remove("picking"); const ll = [e.latlng.lat, e.latlng.lng]; if (pickCb) { const f = pickCb; pickCb = null; f(ll); } else { setAddLL(ll, "地圖上點的位置"); addBox.scrollIntoView({ block: "nearest", behavior: "smooth" }); } });
// right-click (computer) or long-press (phone) on an empty part of the map = add a spot there
map.on("contextmenu", e => { if (e.originalEvent && e.originalEvent.target.closest && e.originalEvent.target.closest(".spot")) return; openAddPop([e.latlng.lat, e.latlng.lng]); });
[addBox].forEach(x => { L.DomEvent.disableClickPropagation(x); L.DomEvent.disableScrollPropagation(x); });
/* 待選景點: spots not in any day, with a button to put each into the day that is open */
let unMode = false;
document.getElementById("plan-un").addEventListener("click", () => { unMode = !unMode; if (unMode) plan.on = true; renderPlan(); });
const TORD = { "主要": 0, "推薦": 1, "次要": 2 };
/* 公休日 from the week table: 「週一休」「週一、二休」 ("" = open every day, or no table) */
function offDays(id) { const w = WEEK[id]; if (!w) return ""; const d = [...WD].filter((_, i) => !w[i]), o = [...WD].filter((_, i) => w[i]); return !d.length || !o.length ? "" : d.length > 3 ? "只開週" + o.join("、") : "週" + d.join("、") + "休"; }
function renderUnList(list) {
  const box = document.getElementById("plan-unlist"); box.hidden = !unMode; if (!unMode) return;
  const cd = PDAYS.find(d => d.k === plan.cur), groups = [["主要景點", s => s.tier === "主要"], ["推薦", s => s.tier === "推薦"], ["次要", s => s.tier === "次要"], ["自己加的點", s => s.cat === "mine"]];
  box.innerHTML = list.length ? `<h4>還沒排進任何一天的景點（${list.length}）・按「＋」加進 ${dayLabel(cd)}</h4>` : "<h4>所有景點都排進行程了。</h4>";
  groups.forEach(([t, f]) => {
    const g = list.filter(f); if (!g.length) return;
    const h = document.createElement("h4"); h.textContent = t; box.append(h);
    g.forEach(s => {
      const r = document.createElement("div"); r.className = "un-row";
      r.innerHTML = '<button type="button" class="un-name"></button><span class="un-off"></span><button type="button" class="un-add">＋ 加入</button>';
      r.querySelector(".un-name").textContent = s.name;
      const off = offDays(s.id); if (off) { const o = r.querySelector(".un-off"); o.textContent = off; o.classList.toggle("today", WEEK[s.id] && !WEEK[s.id][cd.wd]); if (o.classList.contains("today")) o.title = dayLabel(cd) + " 休館"; }
      r.querySelector(".un-name").addEventListener("click", () => { map.panTo(s.ll); openSpot(s.id); });
      r.querySelector(".un-add").addEventListener("click", () => planToggle(plan.cur, s.id));
      box.append(r);
    });
  });
  if (typeof CITY.unExtra === "function") CITY.unExtra(box, cd);
}
L.DomEvent.disableScrollPropagation(document.getElementById("plan-unlist"));
const setPlanOpen = on => { planOpen = on; try { localStorage.setItem(PKEY + "-open", on ? "1" : "0"); } catch (e) {} renderPlan(); if (on) fitPlan(); };
/* phone: the tab goes 開啟 → 全螢幕 → 關閉; computer: 開啟 ↔ 關閉 */
document.querySelectorAll(".plan-btn").forEach(b => b.addEventListener("click", () => {
  if (innerWidth <= 640 && planOpen && !planEl.classList.contains("big")) { planEl.classList.add("big"); renderPlan(); return; }
  planEl.classList.remove("big"); setPlanOpen(!planOpen); if (planOpen) tripMode("plan");
}));
document.getElementById("plan-x").addEventListener("click", () => setPlanOpen(false));
/* the 我的行程 tab sticks to the panel's edge: computer = its right side, phone = its top; closed = the map's edge */
function placeTab() {
  const t = document.querySelector(".plan-tab"); if (!t) return;
  t.style.left = t.style.top = t.style.bottom = "";
  if (!planOpen) return;
  if (innerWidth <= 640) t.style.bottom = (planEl.offsetParent ? planEl.offsetParent.clientHeight - planEl.offsetTop : planEl.offsetHeight) + "px";
  // computer: placed by CSS (sticks to the panel's right edge, also in full screen)
}
if (window.ResizeObserver) { let rz = 0; new ResizeObserver(() => { placeTab(); clearTimeout(rz); rz = setTimeout(() => { if (!planEl.hidden) layoutLabels(); }, 120); }).observe(planEl); }
addEventListener("resize", placeTab);
L.DomEvent.disableClickPropagation(planEl); L.DomEvent.disableScrollPropagation(planEl);
/* 轉文字: this day as text (copied), as complete as the panel's current level (全覽 / 簡潔 / 最簡) */
document.getElementById("plan-copy").addEventListener("click", async e => {
  const d = PDAYS.find(x => x.k === plan.cur), items = plan.days[plan.cur].filter(x => byId(x.id));
  const lis = [...planList.children], head = CITY.name + " " + dayLabel(d) + (d.memo ? "　" + d.memo : "");
  let txt;
  if (planLv === 2) txt = head + "\n" + items.map((x, i) => `${i + 1} ${x.time ? x.time + " " : ""}${byId(x.id).name}`).join(" → ");
  else {
    const rows = items.map((x, i) => {
      const s = byId(x.id), li = lis[i], out = [`${i + 1}. ${x.time ? x.time + " " : ""}${s.name}`];
      if (planLv === 0) {
        const info = li && li.querySelector(".p-info").textContent; if (info) out.push("   " + info);
        if (x.note) out.push("   備註：" + x.note);
      }
      const leg = li && li.querySelector(".p-leg-t");
      if (leg) out.push("   " + leg.textContent + (planLv === 0 ? "（導航：" + leg.parentNode.querySelector("a").href + "）" : ""));
      return out.join("\n");
    });
    txt = head + "\n\n" + rows.join("\n") + "\n";
    const sum = document.getElementById("plan-sum").textContent; if (sum) txt += "\n" + sum + "\n";
    const go = document.getElementById("plan-go"); if (planLv === 0 && !go.hidden) txt += "整天 Google 導航：" + go.href + "\n";
  }
  // copy, ready to paste into LINE etc.; if the browser refuses, show the text so it can be selected by hand
  const b = e.currentTarget, note = document.getElementById("plan-share-note");
  try { await navigator.clipboard.writeText(txt); b.textContent = "已複製"; note.hidden = false; note.textContent = "行程文字已複製，可以直接貼給別人。"; }
  catch (err) { note.hidden = false; note.textContent = "請自己全選複製："; const t = document.createElement("textarea"); t.value = txt; t.rows = 6; t.readOnly = true; t.className = "plan-txt"; note.append(t); t.focus(); t.select(); }
  setTimeout(() => { b.textContent = "轉文字"; }, 1500);
});


/* ---- 分享我的行程: a link that carries the days + own spots; opening it asks before merging (never overwrites) ---- */
const b64e = t => btoa(String.fromCharCode(...new TextEncoder().encode(t))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const b64d = t => new TextDecoder().decode(Uint8Array.from(atob(t.replace(/-/g, "+").replace(/_/g, "/")), c => c.charCodeAt(0)));
/* 分享我的地圖: one link carries every day, own spots and visited spots; the receiver chooses add / replace for spots and for the plan */
function shareData() {
  return { v: 2, all: 1, t: MAP_UPDATED, cur: Math.max(0, PDAYS.findIndex(x => x.k === plan.cur)),
    days: PDAYS.map(x => ({ date: x.date, wd: x.wd, ...(x.memo ? { memo: x.memo } : {}), items: plan.days[x.k].filter(y => byId(y.id)).map(y => [y.id, y.time || "", y.note || ""]) })),
    mine: MINE.map(m => [m.id, m.name, +m.ll[0].toFixed(6), +m.ll[1].toFixed(6), m.note || "", m.gurl || ""]),
    visited: typeof visited !== "undefined" ? [...visited] : [],
    hotel: myHotel || null,
    wdays: (() => { try { const v = JSON.parse(localStorage.getItem(DKEY) || "null"); return Array.isArray(v) ? v : null; } catch (e) { return null; } })() };
}
document.querySelectorAll("#plan-all, .plan-all-fs:not(.tour-again):not(.imp-open), .plan-all-faq").forEach(btn => btn.addEventListener("click", async e => {
  const url = location.href.split("#")[0] + "#all=" + b64e(JSON.stringify(shareData())), b = e.currentTarget;
  const note = b.id === "plan-all" ? document.getElementById("all-note") : toastEl();
  note.hidden = false;
  note.textContent = location.protocol === "file:" ? "提醒：這個檔案還沒放上網址，連結只有這台電腦打得開。" : "連結已複製。對方（或你的另一台裝置）直接打開連結，或按地圖上方的「匯入地圖」貼上。";
  try { await navigator.clipboard.writeText(url); const was = b.textContent; b.textContent = "已複製"; setTimeout(() => { b.textContent = was; }, 1800); setTimeout(() => { note.hidden = true; }, 9000); }
  catch (err) { note.textContent = "請自己全選複製這段連結："; const i = document.createElement("textarea"); i.value = url; i.rows = 3; i.readOnly = true; i.className = "plan-txt"; note.append(i); i.select(); }
}));
/* reading a link or a code: #share=… (one day from a friend) or #all=… (the whole map, for my other devices) */
function readCode(str) {
  const m = String(str || "").trim().match(/#?(share|all)=([\w-]+)/) || String(str || "").trim().match(/^()([\w-]{20,})$/);
  if (!m) return null;
  try { const d = JSON.parse(b64d(m[2])); if (!d || !Array.isArray(d.days)) return null; return d; } catch (e) { return null; }
}
function verNote(d) { return d.t && d.t > MAP_UPDATED ? `<p class="sa-warn">這份資料來自比較新的地圖（${d.t} 更新），你的地圖是 ${MAP_UPDATED} 版，有些新景點可能還沒有；先換成新地圖再加入會比較完整。</p>` : ""; }
function askImport(d) {
  const nI = d.days.reduce((a, x) => a + x.items.length, 0), nM = (d.mine || []).length, nV = (d.visited || []).length;
  const box = document.createElement("div"); box.className = "share-ask"; box.setAttribute("role", "dialog");
  box.innerHTML = `<div class="sa-card"><b>匯入分享的地圖</b><p class="sa-sum"></p>${verNote(d)}
    <fieldset class="sa-opt"><legend>要怎麼匯入？</legend><label><input type="radio" name="sa-mode" value="add" checked> <b>加上去：</b>保留你原本的，把對方的景點和行程加進來</label><label><input type="radio" name="sa-mode" value="replace"> <b>全部換成對方的：</b>你原本的景點、行程、去過的標記、星期幾去、住宿，全部換成這份</label><label><input type="radio" name="sa-mode" value="one"> <b>只匯入其中一天：</b>加成你的新的一天，其他都不動 <select class="sa-day" aria-label="匯入哪一天"></select></label></fieldset>
    <p class="sa-warn sa-msg" aria-live="polite"></p><div class="pa-btns"><button type="button" class="pa-ok" id="sa-yes">確認</button><button type="button" id="sa-no">取消</button></div></div>`;
  box.querySelector(".sa-sum").textContent = `${d.days.length} 天行程（${nI} 個點）、${nM} 個自己加的點、${nV} 個去過的景點`;
  const sel = box.querySelector(".sa-day"); fillDays(sel, d);
  sel.addEventListener("change", () => { box.querySelector('input[value="one"]').checked = true; });
  document.body.append(box);
  box.querySelector("#sa-no").addEventListener("click", () => box.remove());
  box.querySelector("#sa-yes").addEventListener("click", () => {
    const spots = box.querySelector('input[name="sa-mode"]:checked').value, planMode = spots;   // one choice for everything
    if (spots === "one") { const r = importDay(d, +sel.value); if (r) { box.querySelector(".sa-msg").textContent = r; } else box.remove(); return; }
    // own spots
    let mine = spots === "replace" ? [] : MINE.map(m => ({ id: m.id, name: m.name, ll: m.ll, note: m.note, gurl: m.gurl }));
    const idMap = {};
    (d.mine || []).forEach(([id, name, la, ln, note, gurl]) => {
      const same = mine.find(m => m.name === name && Math.abs(m.ll[0] - la) < 1e-4 && Math.abs(m.ll[1] - ln) < 1e-4);
      if (same) idMap[id] = same.id; else { const nid = mine.some(m => m.id === id) ? id + "-" + Date.now().toString(36) : id; mine.push({ id: nid, name, ll: [la, ln], note, gurl }); idMap[id] = nid; }
    });
    const vis = spots === "replace" ? new Set(d.visited || []) : new Set([...(typeof visited !== "undefined" ? visited : []), ...(d.visited || [])]);
    const exists = id => !!byId(id) && !(byId(id).custom) || mine.some(m => m.id === id);
    // plan
    const keep = planMode === "replace" ? [] : PDAYS.map(x => ({ date: x.date, wd: x.wd, memo: x.memo || "", items: plan.days[x.k].map(y => [y.id, y.time || "", y.note || ""]) }));
    const sig = dd => dd.date + "|" + dd.wd + "|" + dd.items.map(it => it[0]).join(",");
    const have = new Set(keep.map(sig));
    d.days.forEach(sd => { const dd = { date: sd.date, wd: sd.wd, memo: sd.memo || "", items: sd.items.map(([id, t, n]) => [idMap[id] || id, t, n]) }; if (!have.has(sig(dd))) { keep.push(dd); have.add(sig(dd)); } });   // the very same day twice is skipped
    const list = keep.map((x, k) => ({ k: "d" + k, date: x.date, wd: x.wd, ...(x.memo ? { memo: x.memo } : {}) })); list.forEach(x => x.label = dayLabel(x));
    const days = {}; keep.forEach((x, k) => days["d" + k] = x.items.filter(it => exists(it[0])).map(([id, time, note]) => ({ id, time, note })));
    if (!list.length) { list.push({ k: "d0", date: "", wd: 3 }); list[0].label = dayLabel(list[0]); days.d0 = []; }
    const cur = planMode === "replace" ? list[Math.max(0, Math.min(list.length - 1, d.cur || 0))].k : (list[PDAYS.length] || list[0]).k;
    try {
      localStorage.setItem(PKEY, JSON.stringify({ cur, days, list }));
      localStorage.setItem(CKEY, JSON.stringify(mine));
      localStorage.setItem(VKEY, JSON.stringify([...vis]));
      localStorage.setItem(PKEY + "-open", "1");
      if (spots === "replace" && Array.isArray(d.wdays) && d.wdays.length) localStorage.setItem(DKEY, JSON.stringify(d.wdays));
      if (spots === "replace" && "hotel" in d) { d.hotel && d.hotel.ll ? localStorage.setItem(HKEY, JSON.stringify(d.hotel)) : localStorage.removeItem(HKEY); }   // 我的住宿: only when replacing   // 星期幾去: only when replacing
    } catch (e) {}
    location.replace(location.pathname + location.search);
  });
}
/* ---- one day (2026-11-27, back from the 11-18 version she liked): 匯出本日行程 / ＋ 匯入本日行程 / 匯入地圖「只匯入其中一天」 ----
   the day always comes in as a NEW day (never merged into a date you have); its own spots come along (same name + place = the same spot);
   visited, 星期幾去 and hotel are left alone; the very same day (date, weekday, spots) is not added twice */
const dayTxt = (sd, x) => { const l = dayLabel({ date: sd.date, wd: sd.wd }); return `${l}${sd.memo ? "　" + sd.memo : ""}・${sd.items.length} 個點`; };
function fillDays(sel, d) {
  sel.innerHTML = ""; d.days.forEach((sd, i) => { const o = document.createElement("option"); o.value = i; o.textContent = dayTxt(sd); sel.append(o); });
  sel.value = Math.max(0, Math.min(d.days.length - 1, d.cur || 0));
}
function importDay(d, i) {
  const sd = d.days[i]; if (!sd) return "找不到這一天。";
  const mine = MINE.map(m => ({ id: m.id, name: m.name, ll: m.ll, note: m.note, gurl: m.gurl })), idMap = {}, used = new Set(sd.items.map(it => it[0]));
  (d.mine || []).filter(m => used.has(m[0])).forEach(([id, name, la, ln, note, gurl]) => {
    const same = mine.find(m => m.name === name && Math.abs(m.ll[0] - la) < 1e-4 && Math.abs(m.ll[1] - ln) < 1e-4);
    if (same) idMap[id] = same.id; else { const nid = mine.some(m => m.id === id) || byId(id) ? id + "-" + Date.now().toString(36) : id; mine.push({ id: nid, name, ll: [la, ln], note, gurl }); idMap[id] = nid; }
  });
  const exists = id => !!byId(id) && !(byId(id).custom) || mine.some(m => m.id === id);
  const items = sd.items.map(([id, t, n]) => [idMap[id] || id, t, n]).filter(it => exists(it[0]));
  const sig = (date, wd, ids) => date + "|" + wd + "|" + ids.join(",");
  if (PDAYS.some(x => sig(x.date, x.wd, plan.days[x.k].map(y => y.id)) === sig(sd.date, sd.wd, items.map(it => it[0])))) return "這一天的行程你已經有了，沒有重複加入。";
  const keep = PDAYS.map(x => ({ date: x.date, wd: x.wd, memo: x.memo || "", items: plan.days[x.k].map(y => [y.id, y.time || "", y.note || ""]) }));
  keep.push({ date: sd.date, wd: sd.wd, memo: sd.memo || "", items });
  const list = keep.map((x, k) => ({ k: "d" + k, date: x.date, wd: x.wd, ...(x.memo ? { memo: x.memo } : {}) })), days = {};
  keep.forEach((x, k) => days["d" + k] = x.items.map(([id, time, note]) => ({ id, time, note })));
  try { localStorage.setItem(PKEY, JSON.stringify({ cur: "d" + (keep.length - 1), on: true, days, list })); localStorage.setItem(CKEY, JSON.stringify(mine)); localStorage.setItem(PKEY + "-open", "1"); } catch (e) {}
  location.replace(location.pathname + location.search); return "";
}
function askDay(d) {
  const box = document.createElement("div"); box.className = "share-ask"; box.setAttribute("role", "dialog");
  const many = d.days.length > 1;
  box.innerHTML = `<div class="sa-card"><b>匯入本日行程</b><p class="sa-sum"></p>${verNote(d)}
    ${many ? '<label class="sa-pick">要匯入哪一天？ <select class="sa-day" aria-label="匯入哪一天"></select></label>' : ""}
    <ul class="sa-list"><li><b>加入：</b>加成你的新的一天，你原本的行程和景點都不會被改。</li></ul>
    <p class="sa-warn sa-msg" aria-live="polite"></p><div class="pa-btns"><button type="button" class="pa-ok" id="sa-yes">加入</button><button type="button" id="sa-no">取消</button></div></div>`;
  box.querySelector(".sa-sum").textContent = many ? `這份有 ${d.days.length} 天行程，選一天加進你的行程。` : dayTxt(d.days[0]);
  if (many) fillDays(box.querySelector(".sa-day"), d);
  document.body.append(box);
  box.querySelector("#sa-no").addEventListener("click", () => box.remove());
  box.querySelector("#sa-yes").addEventListener("click", () => { const r = importDay(d, many ? +box.querySelector(".sa-day").value : 0); if (r) box.querySelector(".sa-msg").textContent = r; else box.remove(); });
}
/* 匯出本日行程: only the open day and the own spots it uses */
document.getElementById("plan-share").addEventListener("click", async e => {
  const x = PDAYS.find(y => y.k === plan.cur); if (!x) return;
  const items = plan.days[x.k].filter(y => byId(y.id)), ids = new Set(items.map(y => y.id));
  const data = { v: 2, one: 1, t: MAP_UPDATED, cur: 0, days: [{ date: x.date, wd: x.wd, ...(x.memo ? { memo: x.memo } : {}), items: items.map(y => [y.id, y.time || "", y.note || ""]) }],
    mine: MINE.filter(m => ids.has(m.id)).map(m => [m.id, m.name, +m.ll[0].toFixed(6), +m.ll[1].toFixed(6), m.note || "", m.gurl || ""]) };
  const url = location.href.split("#")[0] + "#share=" + b64e(JSON.stringify(data)), b = e.currentTarget, note = document.getElementById("plan-share-note");
  note.hidden = false;
  note.textContent = location.protocol === "file:" ? "提醒：這個檔案還沒放上網址，連結只有這台電腦打得開。" : "連結已複製，請開啟另一個裝置的「我的行程」，選「＋ 匯入本日行程」。";
  try { await navigator.clipboard.writeText(url); b.textContent = "已複製"; setTimeout(() => { b.textContent = "匯出本日行程"; }, 1800); }
  catch (err) { note.textContent = "請自己全選複製這段連結："; const i = document.createElement("textarea"); i.value = url; i.rows = 3; i.readOnly = true; i.className = "plan-txt"; note.append(i); i.select(); }
});
function checkShare() {
  if (!/^#(share|all)=/.test(location.hash)) return;
  const d = readCode(location.hash);
  history.replaceState(null, "", location.href.split("#")[0]);
  if (d) d.one ? askDay(d) : askImport(d);
}
/* 匯入地圖: the paste box in its own small window (opened from the links by 匯出地圖) */
const impPop = document.createElement("div"); impPop.className = "imp-pop"; impPop.hidden = true; impPop.setAttribute("role", "dialog"); impPop.setAttribute("aria-label", "匯入地圖");
impPop.innerHTML = '<div class="add-pop-head"><b>匯入地圖</b><button type="button" class="add-pop-x" aria-label="取消">×</button></div>';
document.body.append(impPop); impPop.append(document.getElementById("plan-paste"));
let impMode = "all";   // "all" = 匯入地圖 (whole map or one day), "day" = 我的行程「＋ 匯入分享行程」 (one day)
function togglePaste(show, mode) {
  const b = document.getElementById("plan-paste"), on = typeof show === "boolean" ? show : impPop.hidden;
  if (on) { impMode = mode || "all"; impPop.querySelector(".add-pop-head b").textContent = impMode === "day" ? "匯入本日行程" : "匯入地圖";
    document.getElementById("pp-lbl").textContent = impMode === "day" ? "貼上「匯出本日行程」複製的連結" : "貼上「匯出地圖」或「匯出本日行程」複製的連結"; }
  impPop.hidden = !on; b.hidden = !on;
  document.getElementById("pp-ver").textContent = "你的地圖更新時間：" + MAP_UPDATED;
  if (on) document.getElementById("pp-text").focus();
}
impPop.querySelector(".add-pop-x").addEventListener("click", () => togglePaste(false));
document.querySelectorAll(".imp-open").forEach(b => b.addEventListener("click", () => togglePaste(true)));
document.getElementById("pp-cancel").addEventListener("click", () => togglePaste(false));
document.getElementById("pp-ok").addEventListener("click", () => {
  const t = document.getElementById("pp-text"), d = readCode(t.value), v = document.getElementById("pp-ver");
  if (!d) { v.textContent = impMode === "day" ? "看不懂這段文字：請貼「匯出本日行程」複製出來的整段連結。" : "看不懂這段文字：請貼「匯出地圖」或「匯出本日行程」複製出來的整段連結。"; v.classList.add("warn"); return; }
  // 2026-11-27: 我的行程 only takes one day; a whole map goes through 匯入地圖 at the top
  if (impMode === "day" && !d.one) { v.textContent = "這是整份地圖的連結，請到地圖上方的「匯入地圖」匯入（那裡也可以只匯入其中一天）。"; v.classList.add("warn"); return; }
  v.classList.remove("warn"); t.value = ""; const m = impMode; togglePaste(false); m === "day" || d.one ? askDay(d) : askImport(d);
});
L.DomEvent.disableClickPropagation(document.getElementById("plan-paste"));
function toastEl() { let t = document.getElementById("toast"); if (!t) { t = document.createElement("div"); t.id = "toast"; t.className = "toast"; t.setAttribute("role", "status"); t.addEventListener("click", e => { if (e.target === t) t.hidden = true; }); document.body.append(t); } t.innerHTML = ""; return t; }
checkShare(); window.addEventListener("hashchange", checkShare);

/* ---- 功能導覽: the first time the map opens, a few cards point at the main buttons one by one; ▶ 功能導覽 replays it ---- */
const TOUR = (() => {
  const KEY = "trip-tour-" + CITY.key;
  const vis = sel => [...document.querySelectorAll(sel)].find(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== "hidden"; });
  const spotTab = () => { const order = CITY.tourSpots; for (const id of order) { const s = byId(id); if (s && s.g && !s.g.classList.contains("lbl-off") && !s.g.classList.contains("gone")) { const r = s.tab.getBoundingClientRect(); const m = mapEl.getBoundingClientRect(); if (r.width && r.top > m.top && r.bottom < m.bottom && r.left > m.left && r.right < m.right) return s.tab; } } return null; };
  const filterRow = () => { const gs = [...document.querySelectorAll(".filters .chip-group")].filter(g => g.getBoundingClientRect().width); if (!gs.length) return null;
    const rs = gs.map(g => g.getBoundingClientRect()), u = { left: Math.min(...rs.map(r => r.left)), top: Math.min(...rs.map(r => r.top)), right: Math.max(...rs.map(r => r.right)), bottom: Math.max(...rs.map(r => r.bottom)) };
    u.width = u.right - u.left; u.height = u.bottom - u.top; return { getBoundingClientRect: () => u }; };
  const MAIN = [
    { menu: true, el: () => document.body.classList.contains("fs-on") ? vis(".plan-all-fs.tour-again") : vis(".sub .tour-again"), el2: () => vis(".help-btn"),
    t: "歡迎！", x: () => document.body.classList.contains("fs-on") ? "30 秒帶你看主要功能。想再看一次，打開「☰ 篩選」，按「▶ 功能導覽」；想看文字說明，按右上角的「?」。" : "30 秒帶你看主要功能。想再看一次，按「▶ 功能導覽」；想看文字說明，按地圖上方的「?」。" },
    { el: spotTab, t: "點景點看介紹", x: "各種景點介紹都在裡面，也能直接開 Google 地圖。" },
    { pre: () => { const h = byId("hotel"); if (h && h.tab && !h.tab.getBoundingClientRect().width) map.setView(h.ll, Math.max(map.getZoom(), 16), { animate: false }); },
      el: () => { const h = byId("hotel"); if (!h || !h.tab) return null; const r = h.tab.getBoundingClientRect(), m = mapEl.getBoundingClientRect(); return r.width && r.top > m.top && r.bottom < m.bottom && r.left > m.left && r.right < m.right ? h.tab : null; },
      t: "記得設定你的住宿", x: () => byId("hotel") && byId("hotel").myHotel ? "地圖上的黑色方塊是你設定的住宿，點它可以修改。" : "地圖上的 " + HOTEL0.name + " 是作者住的旅館。點它按「改成我的住宿」，換成你的旅館，每個景點介紹裡「從住宿出發」的步行時間就會照你的旅館算。" },
    { menu: true, el: () => filterRow() || vis("#fs-menu"), t: "篩選", x: "景點可以按重要性分級顯示、是否免費。選你星期幾去，地圖上的營業時間就只顯示那幾天。" },
    { menu: true, el: () => vis("#f-cold") || vis("#fs-menu"), t: "冷門時段", x: "按「冷門時段」，只亮早上 9 點前或晚上 7 點後還能去的景點，其他的變淡。" },
    { el: () => vis(".plan-btn"), t: "我的行程", x: "把景點排進每一天，地圖上會畫出步行路線，還能一鍵 Google 導航。" },
    { el: () => vis(".view-btns .fs-open") || vis("#fs-exit"), t: "全螢幕", x: () => document.body.classList.contains("fs-on") ? "手機一打開就是全螢幕地圖。按這顆可以離開全螢幕，看標題和地圖下方的說明；右下角同樣圖示的按鈕可以再回到全螢幕。" : "地圖全螢幕，更大更清楚；再按一次回到原本的頁面。" },
    { el: () => vis(".names-btn"), t: "眼睛：景點框怎麼顯示", x: "按一下切換三種：自動（預設，放不下的框會自動縮小）、全覽（每個框都完整顯示）、簡潔（只留景點名稱）。" },
    { el: () => vis(".base-btn"), t: "底圖（地圖）濃淡", x: "按一次街道淡一點，最後只留城牆、道路和景點。" },
    { el: () => vis(".icon-btn.dist"), t: "距離模式", x: "依序點兩個景點，就知道走路多遠、幾分鐘。" },
    ...(CITY.tourExtra || []).map(x => Object.assign({}, x, { el: () => vis(x.sel) })),
    { el: () => vis(".help-btn"), t: "使用說明", x: "按「?」會跳到地圖下方的使用方式，每個功能都有文字說明，我的行程、客製你的地圖也有自己的快速導覽。" },
    { el: () => vis("#z-me"), t: "我在哪", x: "按一下 GPS，地圖上會出現你的位置。" },
    { t: "看附近有哪些景點", f: `<svg viewBox="0 0 260 120" class="tour-fig" aria-hidden="true"><rect x="1" y="1" width="258" height="118" rx="10" class="tf-bg"/><path d="M0 84 L260 70 M90 0 L120 120 M0 30 L260 44" class="tf-road"/><circle cx="118" cy="62" r="50" class="tf-ring"/><circle cx="118" cy="62" r="28" class="tf-ring"/><circle cx="62" cy="40" r="6" class="tf-dot" style="fill:#3B82F6"/><circle cx="150" cy="44" r="6" class="tf-dot" style="fill:#3DAA5A"/><circle cx="214" cy="96" r="6" class="tf-dot tf-out" style="fill:#3B82F6"/><circle cx="118" cy="62" r="8" class="tf-dot" style="fill:#E5484D"/><text x="134" y="98" class="tf-hand">👆</text><text x="172" y="24" class="tf-lbl">滑鼠按兩下</text><text x="172" y="42" class="tf-lbl">或手機長按</text><text x="174" y="112" class="tf-lbl tf-sub">100 m 內 2 個</text></svg>`, x: "滑鼠按兩下或手機長按，會以景點為圓心畫 100 公尺的圈，每按一次圈擴大 100 公尺。點空白處關掉。" },
    { t: "加自己的點", f: `<svg viewBox="0 0 260 120" class="tour-fig" aria-hidden="true"><rect x="1" y="1" width="258" height="118" rx="10" class="tf-bg"/><path d="M0 70 L260 58 M170 0 L190 120" class="tf-road"/><g transform="translate(92 66)"><circle r="16" class="tf-ripple"/><circle r="26" class="tf-ripple tf-ripple2"/><path d="M0 -2 C-9 -11 -9 -24 0 -24 C9 -24 9 -11 0 -2 Z" style="fill:#A855F7;stroke:#fff;stroke-width:2"/></g><text x="98" y="104" class="tf-hand">👆</text><rect x="130" y="16" width="118" height="30" rx="15" class="tf-chip"/><text x="189" y="36" text-anchor="middle" class="tf-lbl tf-chipt">＋ 地圖沒有的點</text><text x="12" y="24" class="tf-lbl">滑鼠右鍵</text><text x="12" y="42" class="tf-lbl">或手機長按空白處</text></svg>`, x: "地圖上沒有的餐廳、店，在那個位置按右鍵（手機長按空白處）就能加成紫色的點，也能排進行程。更多說明在地圖下方的「使用方式」。" }
  ];
  /* 我的行程 has its own short tour (▶ 導覽 in the panel head; runs once the first time the panel is opened) */
  const PLAN_KEY = "trip-tour-plan-" + CITY.key, pv = sel => () => vis(sel);
  const PLAN = [
    { el: pv("#plan-days"), t: "一天一個分頁", x: "點選日期開啟行程。按「＋」可加天數，按住日期拖曳可以換順序。" },
    { el: pv("#plan-dayedit"), t: "日期和星期", x: "日期自己填、星期幾用選的。清單上的營業時間照那天的星期顯示。" },
    { el: () => vis("#plan-list") || vis("#plan-empty"), t: "排進來的景點", x: "點地圖上的景點，在介紹裡按「加入行程」就會排進來。⋮⋮ 拖曳換順序，可以填幾點到和備註，按 × 移除。" },
    { el: pv("#plan-lv"), t: "清單顯示多少", x: "按眼睛切換全覽、簡潔、最簡，行程長的時候比較好看。" },
    { el: pv("#plan-un"), t: "待選景點", x: "列出還沒排進任何一天的景點，按「＋ 加入」就放進這天。" },
    { el: pv("#plan-addbtn"), t: "地圖沒有的點", x: "地圖上沒有的餐廳、店，可以自己加進這天，會變成紫色的點。" },
    { el: pv(".plan-foot"), t: "走路多遠、導航、轉文字", x: "下面寫這天走路共多遠。「Google 導航」整天依序導航，「轉文字」把行程複製下來貼給朋友。" }
  ];
  /* 客製你的地圖: its own tour (from the Q&A only) */
  const CUSTOM_KEY = "trip-tour-custom-" + CITY.key, addFig = (MAIN.find(x => x.t === "加自己的點") || {}).f;
  const hotelTab = () => { const h = byId("hotel"); if (!h || !h.tab) return null; const r = h.tab.getBoundingClientRect(), m = mapEl.getBoundingClientRect(); return r.width && r.top > m.top && r.bottom < m.bottom && r.left > m.left && r.right < m.right ? h.tab : null; };
  const doneChip = on => { const c = document.getElementById("f-done"); if (!c) return;
    if (on && c.hidden) { c.hidden = false; c.dataset.demo = "1"; }
    if (!on && c.dataset.demo) { delete c.dataset.demo; c.hidden = true; } };
  const CUSTOM = [
    { t: "把地圖變成你的", x: "加自己的景點、藏起不想看的、換成你的住宿，都只存在你現在打開的這個頁面。" },
    { t: "新增景點", f: addFig, x: "電腦在地圖空白處按右鍵、手機長按，就能加成紫色的私人景點；在「我的行程」按「＋ 地圖沒有的點」也可以。" },
    { menu: true, el: () => vis("#f-mine") || vis("#fs-menu"), t: "私人景點", x: "自己加的點都歸在「私人景點」，關掉就先藏起來。點開私人景點可以編輯，或按「刪除景點」刪掉。" },
    { pre: () => { doneChip(false); openSpot(CITY.hideSpot); }, el: () => vis("#d-visit"), t: "不想看的景點", x: "地圖本來的景點不能刪除。點開景點，在介紹最上面按「標記為已去過」，它就會從地圖上隱藏。" },
    { pre: () => { if (!document.getElementById("drawer").hidden) { lastFocus = null; closeSpot(); } doneChip(true); }, menu: true, el: () => vis("#f-done") || filterRow() || vis("#fs-menu"), t: "找回藏起來的景點", x: "有藏起來的景點時，篩選會多一顆「顯示去過的景點」。按它，藏起來的景點會半透明出現，點開再按一次「已去過」就回來了。也可以用篩選把整層（主要景點／推薦／次要）關掉。" },
    { pre: () => { doneChip(false); const h = byId("hotel"); if (h) map.setView(h.ll, Math.max(map.getZoom(), 16), { animate: false }); }, el: hotelTab, t: "換成你的住宿", x: "點地圖上的 " + HOTEL0.name + "，按「改成我的住宿」。每個景點介紹裡「從住宿出發」的步行時間，就會照你的旅館算。" },
    { menu: true, el: () => { const fs = document.body.classList.contains("fs-on");
        const a = fs ? vis(".plan-all-fs:not(.tour-again):not(.imp-open)") : vis("#plan-all"), b = fs ? vis(".plan-all-fs.imp-open") : vis(".sub .imp-open");
        if (!a || !b) return a || b; const r = [a, b].map(x => x.getBoundingClientRect());
        const u = { left: Math.min(r[0].left, r[1].left), top: Math.min(r[0].top, r[1].top), right: Math.max(r[0].right, r[1].right), bottom: Math.max(r[0].bottom, r[1].bottom) };
        u.width = u.right - u.left; u.height = u.bottom - u.top; return { getBoundingClientRect: () => u }; },
      t: "帶著走", x: "這些設定換手機、換瀏覽器都看不到。按「匯出地圖」複製連結，到另一台裝置按「匯入地圖」貼上就好。最好在桌面設一個捷徑，每次從同一個入口進來。" }
  ];
  let STEPS = MAIN, CUR_KEY = KEY, afterEnd = null;
  let i = 0, hole = null, card = null, shield = null;
  const end = () => { const fm = document.getElementById("fs-menu"); if (fm && fm.getAttribute("aria-expanded") === "true") fm.click(); if (hole) hole.remove(); if (hole2) { hole2.remove(); hole2 = null; } if (card) card.remove(); if (shield) shield.remove(); hole = card = shield = null; try { localStorage.setItem(CUR_KEY, "1"); } catch (e) {} removeEventListener("resize", place); if (afterEnd) { const f = afterEnd; afterEnd = null; f(); } };
  let hole2 = null;
  function place2(st) {
    const e2 = st.el2 && st.el2();
    if (!e2) { if (hole2) hole2.style.display = "none"; return; }
    if (!hole2) { hole2 = document.createElement("div"); hole2.className = "tour-hole tour-hole2"; document.body.append(hole2); }
    const r = e2.getBoundingClientRect(), pad = 6; hole2.style.display = "block";
    Object.assign(hole2.style, { left: r.left - pad + "px", top: r.top - pad + "px", width: r.width + pad * 2 + "px", height: r.height + pad * 2 + "px" });
  }
  function place() {
    if (!card) return; const st = STEPS[i], el = st.el && st.el(); place2(st);
    const vw = innerWidth, vh = innerHeight, cw = card.offsetWidth, ch = card.offsetHeight;
    if (el) { { const q = el.getBoundingClientRect(); if (q.bottom > vh || q.top < 0) { if (el.scrollIntoView) el.scrollIntoView({ block: "center" }); else scrollBy(0, q.top + q.height / 2 - vh / 2); } }   // frames made of several buttons have no scrollIntoView
      const r = el.getBoundingClientRect(), pad = 6; hole.style.display = "block";
      Object.assign(hole.style, { left: r.left - pad + "px", top: r.top - pad + "px", width: r.width + pad * 2 + "px", height: r.height + pad * 2 + "px" });
      const e2 = st.el2 && st.el2(), r2 = e2 && e2.getBoundingClientRect(), rb = r2 && r2.width ? Math.max(r.bottom, r2.bottom) : r.bottom, rt = r2 && r2.width ? Math.min(r.top, r2.top) : r.top;   // keep the card clear of both frames
      let top = rb + 14; if (top + ch > vh - 10) top = rt - ch - 14; if (top < 10) top = Math.min(vh - ch - 10, rb + 14);
      let left = Math.min(Math.max(10, r.left + r.width / 2 - cw / 2), vw - cw - 10);
      card.style.top = top + "px"; card.style.left = left + "px";
    } else { hole.style.display = "block"; Object.assign(hole.style, { left: vw / 2 + "px", top: vh / 2 + "px", width: "0px", height: "0px" }); card.style.top = Math.max(10, (vh - ch) / 2) + "px"; card.style.left = (vw - cw) / 2 + "px"; }
  }
  function show() {
    const st = STEPS[i]; if (st.pre) try { st.pre(); } catch (e) {}
    card.innerHTML = `<h3></h3><p></p><div class="tour-foot"><span class="tour-dots">${STEPS.map((_, k) => `<i class="${k === i ? "on" : ""}"></i>`).join("")}</span>${i < STEPS.length - 1 ? '<button type="button" class="tour-skip">跳過</button>' : ""}${i ? '<button type="button" class="tour-prev" aria-label="上一步">←</button>' : ""}<button type="button" class="tour-next" aria-label="${i === STEPS.length - 1 ? "開始使用" : "下一步"}">${i === STEPS.length - 1 ? "開始使用" : "→"}</button></div>`;
    card.querySelector("h3").textContent = st.t; card.querySelector("p").textContent = typeof st.x === "function" ? st.x() : st.x; if (st.f) card.querySelector("h3").insertAdjacentHTML("afterend", st.f);
    card.querySelector(".tour-next").addEventListener("click", () => { if (i === STEPS.length - 1) return end(); i++; show(); });
    const pv = card.querySelector(".tour-prev"); if (pv) pv.addEventListener("click", () => { i--; show(); });
    const sk = card.querySelector(".tour-skip"); if (sk) sk.addEventListener("click", end);
    // small screens: open ☰ 篩選 for the steps about things inside it, close it for the others
    const fm = document.getElementById("fs-menu");
    if (fm && document.body.classList.contains("fs-on")) { const open = fm.getAttribute("aria-expanded") === "true"; if (!!st.menu !== open) fm.click(); }
    [90, 380, 800, 1300].forEach(t => setTimeout(place, t));   // again after the ☰ panel has finished opening, so the frame fits the real button
  }
  function start(steps, key) {
    if (card) return; closeSpot && document.getElementById("drawer") && closeSpot();
    STEPS = steps || MAIN; CUR_KEY = key || KEY;
    i = 0; hole = document.createElement("div"); hole.className = "tour-hole";
    shield = document.createElement("div"); shield.className = "tour-shield";   /* swallows taps on the dimmed page so nothing underneath gets pressed */ card = document.createElement("div"); card.className = "tour-card"; card.setAttribute("role", "dialog"); card.setAttribute("aria-label", STEPS === PLAN ? "我的行程導覽" : STEPS === CUSTOM ? "客製你的地圖導覽" : "功能導覽");
    document.body.append(shield, hole, card); addEventListener("resize", place); show();
  }
  document.querySelectorAll(".tour-again").forEach(b => b.addEventListener("click", e => { e.preventDefault(); setTimeout(() => start(), 150); }));
  function toMap() { if (innerWidth <= 640 && !document.body.classList.contains("fs-on")) { const b = vis(".fs-open"); if (b) b.click(); } else mapEl.scrollIntoView({ block: "center" }); }
  function startPlan() {
    if (card) return;
    if (plan.on === false) { plan.on = true; savePlan(); }
    // an empty day has nothing to point at: show a sample day during the tour (never saved; cleared when the tour ends)
    const k = plan.cur, demo = !plan.days[k].some(x => byId(x.id));
    if (demo) {
      plan.days[k] = CITY.demo.map(x => Object.assign({}, x)).filter(x => byId(x.id));
      planEl.classList.add("demo");
    }
    if (!planOpen) setPlanOpen(true); else renderPlan();
    setTimeout(() => { start(PLAN, PLAN_KEY); if (demo) afterEnd = () => { plan.days[k] = []; planEl.classList.remove("demo"); renderPlan(); }; }, 250);
  }
  document.getElementById("plan-tour").addEventListener("click", startPlan);
  document.querySelectorAll(".custom-tour-again").forEach(b => b.addEventListener("click", e => { e.preventDefault(); if (planOpen) setPlanOpen(false); toMap(); setTimeout(() => { start(CUSTOM, CUSTOM_KEY); afterEnd = () => { doneChip(false); if (!document.getElementById("drawer").hidden) { lastFocus = null; closeSpot(); } }; }, 500); }));
  document.querySelectorAll(".plan-tour-again").forEach(b => b.addEventListener("click", e => { e.preventDefault(); toMap(); setTimeout(startPlan, 500); }));
  // the first time 我的行程 is opened (and the main tour is not running)
  document.querySelectorAll(".plan-btn").forEach(b => b.addEventListener("click", () => { let done = false; try { done = localStorage.getItem(PLAN_KEY) === "1"; } catch (e) {} if (!done && !card) setTimeout(startPlan, 400); }));
  let seen = false; try { seen = localStorage.getItem(KEY) === "1"; } catch (e) {}
  if (!seen) setTimeout(() => { if (!document.querySelector(".share-ask")) start(); }, 1500);
  return { start };
})();
if (/[?&]v=/.test(location.search)) history.replaceState(null, "", location.pathname + location.hash);   // tidy the address after an update
/* ---- 地圖有更新: when the page comes back into view (or every 30 min), check version.json; if the map was updated, offer a one-tap reload (your own data stays) ---- */
(() => {
  if (location.protocol !== "https:") return;
  let shown = false;
  const check = () => { if (shown || document.hidden) return;
    fetch("version.json?t=" + Date.now(), { cache: "no-store" }).then(r => r.ok ? r.json() : null).then(v => {
      if (!v || !v.updated || v.updated <= MAP_UPDATED || shown) return; shown = true;
      const bar = document.createElement("div"); bar.className = "upd-bar"; bar.setAttribute("role", "status");
      bar.innerHTML = '<button type="button" class="upd-go">更新</button><small>只更新圖資，不會動到您的本機設定</small><button type="button" class="upd-x" aria-label="先不要">×</button>';
      bar.querySelector(".upd-go").addEventListener("click", () => location.replace(location.pathname + "?v=" + encodeURIComponent(v.updated) + location.hash));   // a new address skips any stored old copy
      bar.querySelector(".upd-x").addEventListener("click", () => bar.remove());
      document.body.append(bar);
    }).catch(() => {}); };
  document.addEventListener("visibilitychange", check); setInterval(check, 30 * 60 * 1000); setTimeout(check, 5000);
})();
/* ---- 底圖濃淡: each tap fades the street map one step — 100% → 60% → 30% → hidden → back to 100%; remembered ---- */
(() => {
  const KEY = "trip-nobase-" + CITY.key, STEPS = [1, .6, .3, 0], NAMES = ["底圖：清楚", "底圖：淡一點", "底圖：很淡", "底圖：隱藏"];
  let lv = 1;   // first visit: 淡一點 (60%); after that, whatever this browser chose last
  try { const v = localStorage.getItem(KEY); if (v !== null) { lv = v === "1" ? 3 : Math.max(0, Math.min(3, +(v || 0) || 0)); if (v.startsWith("lv")) lv = +v.slice(2) || 0; } } catch (e) {}
  const apply = () => {
    map.getPane("tilePane").style.opacity = STEPS[lv];
    mapEl.classList.toggle("no-base", lv === 3);
    mapEl.classList.toggle("base-faded", lv > 0);
    document.querySelectorAll(".base-btn").forEach(b => { b.setAttribute("aria-pressed", lv > 0); b.dataset.lv = lv; b.dataset.tip = NAMES[lv] + "（再按一次" + (lv === 3 ? "恢復" : "更淡") + "）"; b.setAttribute("aria-label", b.dataset.tip); });
  };
  document.querySelectorAll(".base-btn").forEach(b => b.addEventListener("click", () => { lv = (lv + 1) % 4; try { localStorage.setItem(KEY, "lv" + lv); } catch (e) {} apply(); }));
  apply();
})();
/* ---- 我在哪: blue dot from the phone's location (asks permission the first time; works once the map is on https or opened as a file) ---- */
(() => {
  const btn = document.getElementById("z-me"); let watch = null, dot = null, acc = null, first = true;
  const CENTER = CITY.center, FAR = CITY.farKm;
  const say = msg => { const t = toastEl(); t.hidden = false; t.textContent = msg; setTimeout(() => { t.hidden = true; }, 6000); };
  const stop = () => { if (watch !== null) navigator.geolocation.clearWatch(watch); watch = null; if (dot) dot.remove(); if (acc) acc.remove(); dot = acc = null; btn.setAttribute("aria-pressed", "false"); btn.classList.remove("wait"); };
  btn.addEventListener("click", () => {
    // already on: tap = bring the dot back to the middle; if it is already there (or you are far from Lucca), tap = turn off
    if (watch !== null) {
      if (dot) { const me = dot.getLatLng(), c = map.getCenter(), here = [me.lat, me.lng];
        if (hav(here, CENTER) < FAR * 1000 && hav(here, [c.lat, c.lng]) > 30) { map.setView(me, Math.max(map.getZoom(), 17)); return; } }
      stop(); return;
    }
    if (!navigator.geolocation) { say("這個瀏覽器不能定位。"); return; }
    first = true; btn.classList.add("wait"); btn.setAttribute("aria-pressed", "true");
    watch = navigator.geolocation.watchPosition(p => {
      const ll = [p.coords.latitude, p.coords.longitude]; btn.classList.remove("wait");
      if (!dot) { acc = L.circle(ll, { radius: p.coords.accuracy, className: "me-acc", interactive: false }).addTo(map);
        dot = L.marker(ll, { icon: L.divIcon({ className: "me-dot", iconSize: [18, 18] }), interactive: false, keyboard: false, zIndexOffset: 1000 }).addTo(map); }
      else { dot.setLatLng(ll); acc.setLatLng(ll).setRadius(p.coords.accuracy); }
      if (first) { first = false; const km = hav(ll, CENTER) / 1000;
        if (km < FAR) map.setView(ll, Math.max(map.getZoom(), 17));
        else say("已開啟定位：你現在離" + CITY.name + "約 " + Math.round(km).toLocaleString() + " 公里，到了" + CITY.name + "就會在地圖上看到藍點。再按一次可以關掉。"); }
    }, err => { stop(); say(err.code === 1 ? "沒有拿到定位權限：請在瀏覽器網址列左邊的設定裡允許「位置」，再按一次。" : "暫時抓不到位置，請到空曠一點的地方再試一次。"); },
    { enableHighAccuracy: true, maximumAge: 10000, timeout: 20000 });
  });
})();
/* ---- zoom buttons, full screen, names-only ---- */
document.getElementById("z-in").addEventListener("click", () => map.zoomIn());
document.getElementById("z-out").addEventListener("click", () => map.zoomOut());
document.getElementById("z-reset").addEventListener("click", home);
const mapView = { mq, refresh: () => setTimeout(() => { map.invalidateSize(); layoutLabels(); }, 30) };
(() => {
  const box = document.querySelector(".mapbox"), bar = document.getElementById("fs-bar"), panel = document.getElementById("fs-panel");
  const distSlot = document.getElementById("fs-dist"), menu = document.getElementById("fs-menu");
  const filters = document.querySelector(".filters"), distNote = document.getElementById("dist-note");
  const homeF = document.createComment("filters"), homeD = document.createComment("dist");
  filters.before(homeF); distNote.before(homeD);
  document.getElementById("fs-title").textContent = CITY.title;
  const place = () => { const h = bar.offsetHeight; box.style.setProperty("--fsbar", h + "px"); panel.style.top = h + "px"; distSlot.style.top = (h + (panel.hidden ? 0 : panel.offsetHeight)) + "px"; };
  const setMenu = open => { panel.hidden = !open; menu.setAttribute("aria-expanded", open); place(); };
  let on = false;
  const enter = () => { if (on) return; on = true; box.classList.add("fs"); document.body.classList.add("fs-on"); panel.appendChild(filters); distSlot.appendChild(distNote); setMenu(false); mapView.refresh(); };
  const exit = () => { if (!on) return; on = false; box.classList.remove("fs"); document.body.classList.remove("fs-on"); homeF.after(filters); homeD.after(distNote); setMenu(false); mapView.refresh(); };
  document.getElementById("fs-exit").addEventListener("click", exit);
  document.getElementById("fs-open").addEventListener("click", enter);
  menu.addEventListener("click", () => setMenu(panel.hidden));
  map.on("click", () => { if (!panel.hidden) setMenu(false); });
  [panel, bar, distSlot].forEach(x => { L.DomEvent.disableClickPropagation(x); L.DomEvent.disableScrollPropagation(x); });
  window.addEventListener("resize", () => { if (on) place(); });
  if (matchMedia("(max-width: 640px)").matches) enter();
})();
/* 眼睛: 自動 → 全覽 → 簡潔 → 自動 */
function setLMode(m) {
  LMODE = m; window.NAME_ONLY = m === "names"; try { localStorage.setItem(LMKEY, m); } catch (e) {}
  mapEl.classList.toggle("names", m === "names");
  document.querySelectorAll(".names-btn").forEach(x => {
    x.setAttribute("aria-pressed", m !== "auto"); x.dataset.mode = m; x.dataset.tip = "顯示：" + LMODE_TXT[m];
    x.setAttribute("aria-label", "景點框顯示方式：" + LMODE_TXT[m] + "（按一下切換：自動、全覽、簡潔）");
  });
  if (map._loaded) placeStreets();   // (places the labels too) at start-up the map places the labels itself once it has a view
}
document.querySelectorAll(".names-btn").forEach(b => b.addEventListener("click", () => setLMode(LMODES[(LMODES.indexOf(LMODE) + 1) % 3])));
setLMode(LMODE);
document.querySelectorAll(".icon-btn[data-tip]").forEach(b => b.addEventListener("pointerdown", e => {
  if (e.pointerType === "mouse") return;
  b.classList.add("tip-show"); clearTimeout(b._tip); b._tip = setTimeout(() => b.classList.remove("tip-show"), 1400);
}));
["rad-card", "p2p-card"].forEach(id => { const x = document.getElementById(id); L.DomEvent.disableClickPropagation(x); });
L.DomEvent.disableClickPropagation(document.querySelector(".mapbox .zoom"));

/* ---- start ---- */
home();
try { const sv = JSON.parse(localStorage.getItem(DKEY) || "null"); if (Array.isArray(sv) && sv.length) DAYS.forEach(b => b.setAttribute("aria-pressed", sv.includes(+b.dataset.day) ? "true" : "false")); } catch (e) {}
applyDays(); applySup(); renderPlan();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(layoutLabels);
window.addEventListener("resize", () => map.invalidateSize());

/* 我的住宿: set / change / back to the sample, from the hotel's own drawer (or the 「從住宿出發」 line in any spot) */
function saveHotel(h) {
  myHotel = h; try { h ? localStorage.setItem(HKEY, JSON.stringify(h)) : localStorage.removeItem(HKEY); } catch (e) {}
  const s = byId("hotel"); applyHotelData();
  s.marker.setLatLng(s.ll); s.g.setAttribute("aria-label", s.name + "，我的住宿");
  renderPlan(); layoutLabels();
}
function hotelFromLine(s) {
  const h = byId("hotel"); if (!h || s.cat === "base") return "";
  const who = h.myHotel ? "從「" + esc(h.name) + "」" : "從範例住宿「" + esc(h.name) + "」";
  return `<div><dt>從住宿出發</dt><dd>${who}步行約 ${walkText(hav(h.ll, s.ll))}（直線估算）${h.myHotel ? "" : '<br><button type="button" class="hotel-set">改成我的住宿 →</button><small class="hotel-hint">這是作者住的旅館，換成你的旅館，步行時間就會照你的算。</small>'}</dd></div>`;
}
function bindHotel(s) {
  drawer.querySelectorAll(".hotel-set").forEach(b => b.addEventListener("click", () => { openSpot("hotel"); setTimeout(() => document.getElementById("h-edit") && showHotelEdit(), 30); }));
  if (s.id !== "hotel") return;
  const $ = id => document.getElementById(id);
  $("h-change")?.addEventListener("click", showHotelEdit);
  $("h-reset")?.addEventListener("click", () => { saveHotel(null); openSpot("hotel"); map.panTo(byId("hotel").ll); });
  if (s._reEdit) { const ll = s._reEdit; delete s._reEdit; showHotelEdit(); hotelLL = ll; $("h-where").textContent = "✓ 已選好地圖上的位置"; $("h-where").classList.add("ok"); }
}
let hotelLL = null;
function showHotelEdit() {
  const $ = id => document.getElementById(id), box = $("h-edit"); if (!box) return;
  box.hidden = false; hotelLL = null;
  $("h-name").value = myHotel ? myHotel.name : ""; $("h-link").value = myHotel ? (myHotel.gurl || "") : ""; $("h-note").value = myHotel ? (myHotel.note || "") : "";
  $("h-where").textContent = myHotel ? "✓ 位置不變" : "或"; $("h-where").classList.toggle("ok", !!myHotel);
  $("h-link").oninput = () => { const r = parseGmap($("h-link").value); if (!r) return;
    if (r.ll) { hotelLL = r.ll; $("h-where").textContent = "✓ 已從 Google 地圖連結抓到位置"; $("h-where").classList.add("ok"); map.panTo(r.ll); }
    else if (r.short) { $("h-where").textContent = "短網址抓不到位置：請打開它、複製網址列的完整網址，或貼座標"; $("h-where").classList.remove("ok"); }
    if (r.name && !$("h-name").value) $("h-name").value = r.name; };
  $("h-pick").onclick = () => { closeSpot(); picking = true; mapEl.classList.add("picking"); pickCb = ll => { byId("hotel")._reEdit = ll; openSpot("hotel"); }; };
  $("h-cancel").onclick = () => { box.hidden = true; };
  $("h-save").onclick = () => {
    const name = $("h-name").value.trim(); if (!name) { $("h-name").focus(); $("h-where").textContent = "請先填旅館名稱"; $("h-where").classList.remove("ok"); return; }
    const ll = hotelLL || (myHotel && myHotel.ll); if (!ll) { $("h-where").textContent = "還沒有位置：貼 Google 地圖網址或座標，或"; $("h-where").classList.remove("ok"); return; }
    const link = $("h-link").value.trim();
    saveHotel({ name, ll, note: $("h-note").value.trim(), gurl: /^https?:\/\//.test(link) ? link : "" });
    openSpot("hotel"); map.panTo(ll);
  };
  setTimeout(() => $("h-name").focus({ preventScroll: true }), 30);
}

/* Q&A: tap the map's address to copy it */
document.querySelectorAll(".faq-copyurl").forEach(b => b.addEventListener("click", async () => {
  const url = b.dataset.url, t = b.textContent;
  try { await navigator.clipboard.writeText(url); b.textContent = "已複製網址"; }
  catch (e) { const r = document.createRange(); r.selectNodeContents(b); const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r); b.textContent = t; return; }
  setTimeout(() => { b.textContent = t; }, 1600);
}));
/* ? buttons: jump to that question in 使用方式 below the map (opens its folded section, leaves full screen on phones) */
document.querySelectorAll(".help-q").forEach(b => b.addEventListener("click", () => {
  const li = [...document.querySelectorAll(".faq-item")].find(x => (x.querySelector(".faq-q") || x).textContent.includes(b.dataset.faq)); if (!li) return;
  const d = li.closest("details"); if (d) d.open = true;
  if (document.body.classList.contains("fs-on")) { const x = document.getElementById("fs-exit"); if (x) x.click(); }
  setTimeout(() => { li.scrollIntoView({ block: "center", behavior: "smooth" }); li.classList.remove("flash"); void li.offsetWidth; li.classList.add("flash"); }, 250);
}));

document.querySelectorAll(".help-btn").forEach(b => b.addEventListener("click", () => {
  if (document.body.classList.contains("fs-on")) { const x = document.getElementById("fs-exit"); if (x) x.click(); }
  setTimeout(() => document.getElementById("faq").scrollIntoView({ block: "start", behavior: "smooth" }), 250);
}));
