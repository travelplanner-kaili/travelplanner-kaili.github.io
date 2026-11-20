/* put the 範圍 card in the map corner farthest from the circle, so it never sits on the labels being looked at */
function placeRadCard(c) {
  const card = document.getElementById("rad-card"), svg = document.getElementById("map"), box = card.parentElement;
  try {
    const m = svg.getScreenCTM(), p = svg.createSVGPoint(); p.x = c.x; p.y = c.y;
    const q = p.matrixTransform(m), r = box.getBoundingClientRect();
    const cx = q.x - r.left, cy = q.y - r.top, W = r.width;
    const fs = box.classList.contains("fs");
    // only the part of the map that is on screen counts (the map can be taller than the window)
    const visTop = Math.max(0, -r.top), visBot = Math.min(r.height, innerHeight - r.top);
    const top = visTop + (fs ? (document.getElementById("fs-bar")?.offsetHeight || 0) + 10 : 12);
    const bot = r.height - visBot + 12;
    // corners (bottom-right is kept for the zoom buttons)
    const opts = [{ l: 12, t: top, x: 0, y: top }, { r: 12, t: top, x: W, y: top }, { l: 12, b: bot, x: 0, y: visBot }];
    const best = opts.reduce((a, o) => Math.hypot(o.x - cx, o.y - cy) > Math.hypot(a.x - cx, a.y - cy) ? o : a, opts[0]);
    Object.assign(card.style, { left: best.l != null ? best.l + "px" : "auto", right: best.r != null ? best.r + "px" : "auto",
      top: best.t != null ? best.t + "px" : "auto", bottom: best.b != null ? "calc(" + best.b + "px + env(safe-area-inset-bottom, 0px))" : "auto" });
  } catch (e) {}
}
