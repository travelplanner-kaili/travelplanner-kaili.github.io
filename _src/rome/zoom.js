/* ---- Mobile pinch zoom ---- */
(() => {
  const svg = document.getElementById("map");
  const b = svg.viewBox.baseVal;
  const full = { x: b.x, y: b.y, w: b.width, h: b.height };
  let vb = { ...full };
  const mq = window.matchMedia("(max-width: 1240px)");
  const apply = () => svg.setAttribute("viewBox", `${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
  const clampW = w => Math.min(full.w, Math.max(full.w / 8, w));
  const clamp = () => {
    vb.w = clampW(vb.w); vb.h = vb.w * full.h / full.w;
    vb.x = Math.min(full.x + full.w - vb.w, Math.max(full.x, vb.x));
    vb.y = Math.min(full.y + full.h - vb.h, Math.max(full.y, vb.y));
  };
  const zoomAt = (f, px, py) => {
    const nw = clampW(vb.w / f);
    vb.x = px - (px - vb.x) * nw / vb.w;
    vb.y = py - (py - vb.y) * nw / vb.w;
    vb.w = nw; clamp(); apply();
  };
  const center = arr => arr.reduce((a, p) => ({ x: a.x + p.x / arr.length, y: a.y + p.y / arr.length }), { x: 0, y: 0 });
  const dist = arr => arr.length > 1 ? Math.hypot(arr[0].x - arr[1].x, arr[0].y - arr[1].y) : 0;
  const pts = new Map();
  let g0 = null, moved = false;
  const begin = () => {
    const arr = [...pts.values()];
    g0 = { vb: { ...vb }, r: svg.getBoundingClientRect(), c: center(arr), d: dist(arr) };
  };
  svg.addEventListener("pointerdown", e => {
    if (!mq.matches) return;
    if (pts.size === 0) moved = false;
    pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    begin();
  });
  window.addEventListener("pointermove", e => {
    if (!g0 || !pts.has(e.pointerId)) return;
    pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    const arr = [...pts.values()], c = center(arr), d = dist(arr);
    const { r, vb: v0 } = g0;
    const w = clampW(g0.d > 0 && d > 0 ? v0.w * g0.d / d : v0.w);
    const sx = v0.x + (g0.c.x - r.left) / r.width * v0.w;
    const sy = v0.y + (g0.c.y - r.top) / r.height * v0.h;
    vb.w = w; vb.h = w * full.h / full.w;
    vb.x = sx - (c.x - r.left) / r.width * vb.w;
    vb.y = sy - (c.y - r.top) / r.height * vb.h;
    clamp(); apply();
    if (arr.length > 1 || Math.hypot(c.x - g0.c.x, c.y - g0.c.y) > 6) moved = true;
  });
  const end = e => { if (!pts.delete(e.pointerId)) return; if (pts.size) begin(); else g0 = null; };
  window.addEventListener("pointerup", end);
  window.addEventListener("pointercancel", end);
  svg.addEventListener("click", e => { if (moved) { e.stopPropagation(); e.preventDefault(); moved = false; } }, true);
  const mid = () => [vb.x + vb.w / 2, vb.y + vb.h / 2];
  document.getElementById("z-in").addEventListener("click", () => zoomAt(1.6, ...mid()));
  document.getElementById("z-out").addEventListener("click", () => zoomAt(1 / 1.6, ...mid()));
  const reset = () => { vb = { ...full }; apply(); };
  document.getElementById("z-reset").addEventListener("click", reset);
  if (mq.addEventListener) mq.addEventListener("change", reset); else mq.addListener(reset);
})();
