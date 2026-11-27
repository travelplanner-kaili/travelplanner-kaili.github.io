/* ==== Venice only (2026-11-27): water-bus stops, traghetto crossings, 購物 ==== */
const ROUTES = []; function openRoute() {}   // Rome's drawer is shared; Venice has no City Walk

/* traghetti (€2 gondola ferries across the Grand Canal): teal pin + a short crossing line, as on the hand-drawn map */
SPOTS.forEach(s => { if (s.id.startsWith("tr_") && s.g) { s.g.style.setProperty("--c", "var(--ferry)"); s.g.style.setProperty("--pc", "var(--ferry)"); } });
const ferryLayer = L.layerGroup().addTo(map);
FERRY_CROSS.forEach(c => L.polyline(c, { className: "ferry-line", interactive: false }).addTo(ferryLayer));

/* water-bus (vaporetto) stops: yellow V + the lines that stop there; tap = the stop's card */
const vapLayer = L.layerGroup();
VAP.forEach(v => {
  const m = L.marker(v.ll, { icon: L.divIcon({ className: "vap-mark", html: `<span class="v" title="${esc(v.name)}（水上巴士站）">V</span><span class="vl">${esc(v.name)} <b>${v.lines.join("・")}</b></span>`, iconSize: [0, 0] }), keyboard: false, zIndexOffset: 400 });   // above the place pins, or a tap on V opens the pin under it
  m.on("click", e => { L.DomEvent.stopPropagation(e); if (picking || distMode) return; openSpot(v.id); });
  m.addTo(vapLayer);
});
let vapOn = true; try { vapOn = localStorage.getItem("trip-vap-venice") !== "0"; } catch (e) {}
function applyVap() {
  if (vapOn) vapLayer.addTo(map); else vapLayer.remove();
  document.querySelectorAll(".vap-chip").forEach(b => b.setAttribute("aria-pressed", vapOn));
  mapEl.classList.toggle("vap-small", map.getZoom() < 16.5);   // names only when zoomed in: place labels would cover them
}
document.querySelectorAll(".vap-chip").forEach(b => b.addEventListener("click", () => { vapOn = !vapOn; try { localStorage.setItem("trip-vap-venice", vapOn ? "1" : "0"); } catch (e) {} applyVap(); }));
map.on("zoomend", applyVap);

/* ---- 購物: pink shopping streets are always on the map; the button adds the shops (solid boxes), like Rome ---- */
let shopOn = false;
{
  const _applySup = applySup;
  applySup = function () {
    _applySup();
    SPOTS.forEach(s => {
      if (s.shopStreet || s.cat === "vap") { s.g.classList.add("gone"); return; }   // streets are the pink lines, stops are the yellow V
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
