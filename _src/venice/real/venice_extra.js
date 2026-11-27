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
   1 = round dots, 2 = dashes, a small numbered badge on each line; the stops are small dots (+ the name when zoomed in); tap = the stop's card */
const vapLayer = L.layerGroup();
map.createPane("vap").style.zIndex = 380;   // above the canal, under the place pins
VAP_ROUTES.forEach(r => {
  L.polyline(r.pts, { pane: "vap", className: "vap-route vap-r" + r.ref, interactive: false }).addTo(vapLayer);
  r.badges.forEach(b => L.marker(b, { pane: "vap", icon: L.divIcon({ className: "vap-badge vap-b" + r.ref, html: `<span>${r.ref}</span>`, iconSize: [0, 0] }), interactive: false, keyboard: false }).addTo(vapLayer));
});
VAP.forEach(v => {
  const m = L.marker(v.ll, { icon: L.divIcon({ className: "vap-mark", html: `<span class="v" title="${esc(v.name)}（水上巴士站）">V</span><span class="vn"><span class="vl">${esc(v.name)}</span></span>`, iconSize: [0, 0] }), keyboard: false, zIndexOffset: 400 });   // above the place pins, or a tap on V opens the pin under it
  m.on("click", e => { L.DomEvent.stopPropagation(e); if (picking || distMode) return; openSpot(v.id); });
  m.addTo(vapLayer);
});
let vapOn = true; try { vapOn = localStorage.getItem("trip-vap-venice") !== "0"; } catch (e) {}
function applyVap() {   // 【水路交通】: the water-bus lines and stops, and the traghetti (pins, boxes, crossing lines)
  if (vapOn) { vapLayer.addTo(map); ferryLayer.addTo(map); } else { vapLayer.remove(); ferryLayer.remove(); }
  document.querySelectorAll(".vap-chip").forEach(b => b.setAttribute("aria-pressed", vapOn));
  mapEl.classList.toggle("vap-small", map.getZoom() < 16.5);   // names only when zoomed in: place labels would cover them
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
      if (s.shopStreet || s.cat === "vap") { s.g.classList.add("gone"); return; }   // streets are the pink lines, stops are the yellow V
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
