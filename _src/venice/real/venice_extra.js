/* ==== Venice only (2026-11-27): water-bus stops, traghetto crossings, 購物 ==== */
const ROUTES = []; function openRoute() {}   // Rome's drawer is shared; Venice has no City Walk

/* traghetti (€2 gondola ferries across the Grand Canal): teal pin + a short crossing line, as on the hand-drawn map */
SPOTS.forEach(s => { if (s.id.startsWith("tr_") && s.g) { s.g.style.setProperty("--c", "var(--ferry)"); s.g.style.setProperty("--pc", "var(--ferry)"); } });
SPOTS.forEach(s => { if (s.id.startsWith("tr_") && s.g) s.g.classList.add("is-ferry"); });   // dashed teal-tinted boxes
const ferryLayer = L.layerGroup().addTo(map);

/* the Grand Canal bridges: a bridge drawn across the canal (angle from the canal line, length = canal width + a little) */
const BRIDGE_IDS = ["rialto", "pontacc", "scalzi", "costituzione"];
{
  const P = ll => map.project(L.latLng(ll), 0);
  BRIDGE_IDS.forEach(id => {
    const s = SPOTS.find(x => x.id === id); if (!s || !s.g) return;
    const p = P(LL[id]); let best = null;
    for (let i = 0; i + 1 < CITY.river.length; i++) {
      const a = P(CITY.river[i]), b = P(CITY.river[i + 1]), d = b.subtract(a), t = Math.max(0, Math.min(1, ((p.x - a.x) * d.x + (p.y - a.y) * d.y) / (d.x * d.x + d.y * d.y || 1)));
      const dist = p.distanceTo(L.point(a.x + t * d.x, a.y + t * d.y)); if (!best || dist < best.dist) best = { dist, ang: Math.atan2(d.y, d.x) };
    }
    const ba = best.ang * 180 / Math.PI + 90; s.g.classList.add("is-bridge", "nolab"); s.g.style.setProperty("--ba", ba + "deg");
    // 2026-11-27: the name is written along the bridge, like a street name, beside the deck (no box)
    let ta = ((ba % 180) + 180) % 180; if (ta > 90) ta -= 180;   // keep the text upright
    const nm = L.marker(LL[id], { icon: L.divIcon({ className: "bridge-name", html: `<span class="lbl-obst" style="--ta:${ta}deg">${esc(s.name)}</span>`, iconSize: [0, 0] }), keyboard: false, zIndexOffset: 300 }).addTo(map);
    nm.on("click", e => { L.DomEvent.stopPropagation(e); if (picking || distMode) return; openSpot(id); });
    s.nameMark = nm;
  });
  const bw = () => { const w = Math.max(6, 26 * unitPx()); mapEl.style.setProperty("--bw", Math.round(w * 1.25 + 12) + "px"); mapEl.style.setProperty("--bh", Math.round(Math.max(8, Math.min(14, w * .35))) + "px"); };
  map.on("zoomend", bw); bw();
}
FERRY_CROSS.forEach(c => L.polyline(c, { className: "ferry-line", interactive: false }).addTo(ferryLayer));

/* water-bus (vaporetto): lines 1 and 2 drawn as dotted lines (2026-11-27, she asked for the stops joined into lines):
   1 = round dots, 2 = dashes; tap a line = its card, tap a stop = the stop card */
const vapLayer = L.layerGroup();
map.createPane("vap").style.zIndex = 380;   // above the canal, under the place pins
/* 2026-11-27 (later): the two lines are pushed apart on screen (11 px each side, where they run together) so a tap hits the right one.
   Every stop is a numbered circle on its line(s) — "1" on line 1, "2" on line 2 — drawn above the lines so the number is never covered
   (she asked for this); a stop of both lines has both circles side by side. The name sits on the bank side, off the lines.
   Place boxes keep clear of the lines (extraObstacles), so the water routes stay whole. */
const VGAP0 = 11; let VGAP = VGAP0;   // the gap and the circles shrink with the map when zoomed out (2026-11-27)
const vapLines = {}, vapHits = {}, vapOffPts = {};
const vapHit = ref => e => { L.DomEvent.stopPropagation(e); if (picking || distMode) return; openSpot("vline" + ref); };
VAP_ROUTES.forEach(r => {
  vapLines[r.ref] = L.polyline(r.pts, { pane: "vap", className: "vap-route vap-r" + r.ref, interactive: false }).addTo(vapLayer);
  vapHits[r.ref] = L.polyline(r.pts, { pane: "vap", className: "vap-hit", weight: 2 * VGAP - 2, opacity: 0 }).on("click", vapHit(r.ref)).addTo(vapLayer);
});
const vapMarks = VAP.map(v => {
  const own = ["1", "2"].filter(x => v.lines.includes(x));
  const circles = own.length ? own.map(x => `<span class="vc vc${x}">${x}</span>`).join("") : '<span class="vc vc0"></span>';
  const m = L.marker(v.ll, { icon: L.divIcon({ className: "vap-mark", html: `<span class="v" title="${esc(v.name)}（水上巴士站）">V</span>${circles}<span class="vl lbl-obst">${esc((SPOTS.find(x => x.id === v.id) || {}).name || v.name)} <i>${esc(v.name)}</i></span>`, iconSize: [0, 0] }), keyboard: false, zIndexOffset: 500 });   // above the place pins and the lines
  m.on("click", e => { L.DomEvent.stopPropagation(e); if (picking || distMode) return; openSpot(v.id); });
  m.addTo(vapLayer); return m;
});
const nearOn = (pts, p) => { let best = null; for (let i = 0; i + 1 < pts.length; i++) { const q = L.LineUtil.closestPointOnSegment(p, pts[i], pts[i + 1]), d = q.distanceTo(p); if (!best || d < best.d) best = { d, q, i }; } return best; };
function layoutVap() {
  const vs = Math.min(1, Math.max(.5, Math.pow(2, (map.getZoom() - 16) * .6))); VGAP = VGAP0 * vs; mapEl.style.setProperty("--vs", vs.toFixed(3));
  Object.values(vapHits).forEach(h => h.setStyle({ weight: Math.max(8, 2 * VGAP - 2) }));
  VAP_ROUTES.forEach(r => {
    const P = r.pts.map(x => map.latLngToLayerPoint(x));
    const O = P.map((p, i) => { if (!r.sh[i]) return p; const a = P[Math.max(0, i - 1)], b = P[Math.min(P.length - 1, i + 1)], dx = b.x - a.x, dy = b.y - a.y, l = Math.hypot(dx, dy) || 1;
      return L.point(p.x - dy / l * VGAP * r.sign, p.y + dx / l * VGAP * r.sign); });
    vapOffPts[r.ref] = O; const ll = O.map(p => map.layerPointToLatLng(p));
    vapLines[r.ref].setLatLngs(ll); vapHits[r.ref].setLatLngs(ll);
  });
  VAP.forEach((v, k) => {
    const el = vapMarks[k].getElement(), raw = map.latLngToLayerPoint(v.ll), own = ["1", "2"].filter(x => v.lines.includes(x));
    if (!own.length) { vapMarks[k].setLatLng(v.ll); if (el) { el.style.setProperty("--lx", "12px"); el.style.setProperty("--ly", "0px"); el.dataset.al = "l"; } return; }
    const pa = nearOn(vapOffPts[own[0]], raw), a = pa.q, b = own[1] ? nearOn(vapOffPts[own[1]], a).q : a, mid = L.point((a.x + b.x) / 2, (a.y + b.y) / 2);
    vapMarks[k].setLatLng(map.layerPointToLatLng(mid));
    if (!el) return;
    const cs = el.querySelectorAll(".vc");
    [a, b].slice(0, cs.length).forEach((q, n) => { cs[n].style.left = (q.x - mid.x) + "px"; cs[n].style.top = (q.y - mid.y) + "px"; });
    // the name: across the line(s), on the bank side of the real stop, clear of the circles
    const O = vapOffPts[own[0]], s0 = O[pa.i], s1 = O[pa.i + 1], tl = Math.hypot(s1.x - s0.x, s1.y - s0.y) || 1;
    let nx = -(s1.y - s0.y) / tl, ny = (s1.x - s0.x) / tl;
    const side = (raw.x - mid.x) * nx + (raw.y - mid.y) * ny; if (side < 0) { nx = -nx; ny = -ny; }
    const far = Math.max((a.x - mid.x) * nx + (a.y - mid.y) * ny, (b.x - mid.x) * nx + (b.y - mid.y) * ny) + 16;
    el.style.setProperty("--lx", (nx * far).toFixed(1) + "px"); el.style.setProperty("--ly", (ny * far).toFixed(1) + "px");
    el.dataset.al = Math.abs(nx) < .4 ? (ny > 0 ? "b" : "t") : nx > 0 ? "l" : "r";
  });
}
/* obstacles for the place boxes: small squares along both lines (on screen), plus the ferry crossings */
window.extraObstacles = () => {
  if (!vapOn) return [];
  const out = [], W = mapEl.clientWidth, H = mapEl.clientHeight, add = (p, r) => { if (p.x > -20 && p.y > -20 && p.x < W + 20 && p.y < H + 20) out.push({ x: p.x - r, y: p.y - r, w: 2 * r, h: 2 * r }); };
  Object.values(vapLines).forEach(pl => {
    const pts = pl.getLatLngs().map(x => map.latLngToContainerPoint(x));
    for (let i = 0; i + 1 < pts.length; i++) { const a = pts[i], b = pts[i + 1], n = Math.max(1, Math.ceil(a.distanceTo(b) / 8));
      for (let t = 0; t < n; t++) add(L.point(a.x + (b.x - a.x) * t / n, a.y + (b.y - a.y) * t / n), 4); }
  });
  return out;
};
map.on("zoomend", layoutVap);
let vapOn = true; try { vapOn = localStorage.getItem("trip-vap-venice") !== "0"; } catch (e) {}
function applyVap() {   // 【水路交通】: the water-bus lines and stops, and the traghetti (pins, boxes, crossing lines)
  if (vapOn) { vapLayer.addTo(map); ferryLayer.addTo(map); } else { vapLayer.remove(); ferryLayer.remove(); }
  if (vapOn) layoutVap();
  layoutLabels();
  document.querySelectorAll(".vap-chip").forEach(b => b.setAttribute("aria-pressed", vapOn));
  const sm = map.getZoom() < 16; if (mapEl.classList.contains("vap-small") !== sm) { mapEl.classList.toggle("vap-small", sm); layoutLabels(); }   // names only when zoomed in: place labels would cover them
}
document.querySelectorAll(".vap-chip").forEach(b => b.addEventListener("click", () => { vapOn = !vapOn; try { localStorage.setItem("trip-vap-venice", vapOn ? "1" : "0"); } catch (e) {} applyVap(); applySup(); }));
map.on("zoomend", applyVap);

/* ---- 購物: pink shopping streets are always on the map; the button adds the shops (solid boxes), like Rome ---- */
let shopOn = false;
{
  const _applySup = applySup;
  applySup = function () {
    _applySup();
    SPOTS.forEach(s => {
      if (s.shopStreet || s.cat === "vap" || s.isLine) { s.g.classList.add("gone"); return; }   // streets are the pink lines, stops are the yellow V
      if (s.id.startsWith("tr_")) { s.g.classList.toggle("gone", !vapOn); s.g.classList.remove("dim"); return; }   // ferries follow 水路交通 only, not 推薦／需購票
      if (s.tier === "購物") { s.g.classList.toggle("gone", !shopOn); s.g.classList.toggle("shopbox", shopOn); s.g.classList.remove("dim"); }
      else if (shopOn && s.cat !== "base") { if (s.sup) s.g.classList.add("gone"); s.g.classList.remove("dim"); }
    });
    document.querySelectorAll("#f-sup, .chip[data-cat], #f-cold").forEach(c => c.classList.toggle("muted", shopOn));
    layoutLabels();
  };
}
document.querySelectorAll(".shop-btn").forEach(b => b.addEventListener("click", () => {
  shopOn = !shopOn; window.SHOP_ON = shopOn; document.querySelectorAll(".shop-btn").forEach(x => x.setAttribute("aria-pressed", shopOn)); applySup();
}));
applyDays(); applySup(); applyVap();
