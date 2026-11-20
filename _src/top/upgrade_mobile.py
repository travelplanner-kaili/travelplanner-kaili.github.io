# Mobile upgrade for the trip maps:
#  - map gets a tall fixed-height viewport on small screens and opens zoomed in, so one-finger drag pans right away
#  - tap anywhere inside the detail sheet (not on a link/button) closes it
#  - mapView.fit(x0,y0,x1,y1) animates the view to a box (used when a City Walk route is opened)
import re

ZOOM_JS = r'''/* ---- Mobile pinch zoom ---- */
const mapView = (() => {
  const svg = document.getElementById("map");
  const b = svg.viewBox.baseVal;
  const full = { x: b.x, y: b.y, w: b.width, h: b.height };
  const mq = window.matchMedia("(max-width: __BP__px)");
  const PXU = 0.36;            // px per map unit when the map first opens on a phone
  const HOME = __HOME__;       // spot id to centre on, or null for the map centre
  let vb = { ...full }, raf = 0;
  const ratio = () => { const r = svg.getBoundingClientRect(); return mq.matches && r.width ? r.height / r.width : full.h / full.w; };
  const maxW = () => Math.max(full.w, full.h / ratio());
  const clampW = w => Math.min(maxW(), Math.max(full.w / 10, w));
  const axis = (p, size, lo, span) => size >= span ? lo + (span - size) / 2 : Math.min(lo + span - size, Math.max(lo, p));
  const clamp = () => {
    vb.w = clampW(vb.w); vb.h = vb.w * ratio();
    vb.x = axis(vb.x, vb.w, full.x, full.w); vb.y = axis(vb.y, vb.h, full.y, full.h);
  };
  const apply = () => svg.setAttribute("viewBox", `${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
  const set = (cx, cy, w) => { vb.w = clampW(w); vb.h = vb.w * ratio(); vb.x = cx - vb.w / 2; vb.y = cy - vb.h / 2; clamp(); };
  const animateTo = (cx, cy, w) => {
    cancelAnimationFrame(raf);
    const from = { cx: vb.x + vb.w / 2, cy: vb.y + vb.h / 2, w: vb.w };
    const keep = { ...vb }; set(cx, cy, w);
    const to = { cx: vb.x + vb.w / 2, cy: vb.y + vb.h / 2, w: vb.w }; vb = keep;
    const t0 = performance.now(), D = 420;
    const step = now => {
      const k = Math.min(1, (now - t0) / D), e = 1 - Math.pow(1 - k, 3);
      vb.w = from.w + (to.w - from.w) * e; vb.h = vb.w * ratio();
      vb.x = from.cx + (to.cx - from.cx) * e - vb.w / 2; vb.y = from.cy + (to.cy - from.cy) * e - vb.h / 2;
      apply(); if (k < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
  };
  const home = () => {
    cancelAnimationFrame(raf);
    if (!mq.matches) { vb = { ...full }; apply(); return; }
    const s = HOME && SPOTS.find(x => x.id === HOME);
    set(s ? s.x : full.x + full.w / 2, s ? s.y : full.y + full.h / 2, svg.getBoundingClientRect().width / PXU); apply();
  };
  const fit = (x0, y0, x1, y1) => {
    if (!mq.matches) return;
    const w = Math.max(x1 - x0, (y1 - y0) / ratio()) * 1.12;
    animateTo((x0 + x1) / 2, (y0 + y1) / 2, w);
  };
  const zoomAt = (f, px, py) => {
    const nw = clampW(vb.w / f);
    vb.x = px - (px - vb.x) * nw / vb.w; vb.y = py - (py - vb.y) * nw / vb.w;
    vb.w = nw; clamp(); apply();
  };
  const center = arr => arr.reduce((a, p) => ({ x: a.x + p.x / arr.length, y: a.y + p.y / arr.length }), { x: 0, y: 0 });
  const dist = arr => arr.length > 1 ? Math.hypot(arr[0].x - arr[1].x, arr[0].y - arr[1].y) : 0;
  const pts = new Map();
  let g0 = null, moved = false, lastMove = 0;
  const begin = () => {
    const arr = [...pts.values()];
    g0 = { vb: { ...vb }, r: svg.getBoundingClientRect(), c: center(arr), d: dist(arr), k: ratio() };
  };
  svg.addEventListener("pointerdown", e => {
    if (!mq.matches) return;
    cancelAnimationFrame(raf);
    if (e.isPrimary || pts.size === 0 || performance.now() - lastMove > 800) { pts.clear(); moved = false; }
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
    vb.w = w; vb.h = w * g0.k;
    vb.x = sx - (c.x - r.left) / r.width * vb.w;
    vb.y = sy - (c.y - r.top) / r.height * vb.h;
    clamp(); apply();
    lastMove = performance.now();
    if (arr.length > 1 || Math.hypot(c.x - g0.c.x, c.y - g0.c.y) > 6) moved = true;
  });
  const end = e => { if (!pts.delete(e.pointerId)) return; if (pts.size) begin(); else g0 = null; };
  window.addEventListener("pointerup", end);
  window.addEventListener("pointercancel", end);
  svg.addEventListener("click", e => { if (moved && performance.now() - lastMove < 600) { e.stopPropagation(); e.preventDefault(); moved = false; } }, true);
  const mid = () => [vb.x + vb.w / 2, vb.y + vb.h / 2];
  document.getElementById("z-in").addEventListener("click", () => zoomAt(1.6, ...mid()));
  document.getElementById("z-out").addEventListener("click", () => zoomAt(1 / 1.6, ...mid()));
  document.getElementById("z-reset").addEventListener("click", () => { cancelAnimationFrame(raf); set(full.x + full.w / 2, full.y + full.h / 2, maxW()); apply(); });
  if (mq.addEventListener) mq.addEventListener("change", home); else mq.addListener(home);
  let rw = 0;
  window.addEventListener("resize", () => {
    const w = svg.getBoundingClientRect().width; if (!mq.matches || w === rw) return; rw = w;
    const [cx, cy] = mid(); set(cx, cy, vb.w); apply();
  });
  home(); rw = svg.getBoundingClientRect().width;
  return { fit, home, mq };
})();'''

TAP_JS = '''
// small screens: one tap anywhere in the sheet (outside links/buttons) closes it
drawer.addEventListener("click", e => {
  if (!mapView.mq.matches) return;
  if (e.target.closest("a, button, input, select, textarea, summary, [role=button]")) return;
  if (window.getSelection && String(window.getSelection())) return;
  closeSpot();
});'''

def mobile(t, home):
    i = t.index("/* ---- Mobile pinch zoom ---- */"); j = t.index("})();", i) + 5
    bp = re.search(r'matchMedia\("\(max-width: (\d+)px\)"\)', t[i:j]).group(1)
    t = t[:i] + ZOOM_JS.replace("__BP__", bp).replace("__HOME__", f'"{home}"' if home else "null") + t[j:]
    # CSS: tall viewport on small screens + grab bar on the bottom sheet
    a = f"@media (max-width: {bp}px) {{\n  .mapbox svg {{ touch-action: none; }}"
    assert a in t
    t = t.replace(a, f"@media (max-width: {bp}px) {{\n  .mapbox {{ height: 70vh; height: min(70dvh, 900px); }}\n  .mapbox svg {{ touch-action: none; height: 100%; }}")
    a = "@media (max-width: 640px) {\n  .drawer { top: auto;"
    assert a in t
    t = t.replace(a, "@media (max-width: 640px) {\n  .drawer::before { content: \"\"; display: block; width: 44px; height: 5px; border-radius: 3px; background: var(--line); margin: -8px auto 12px; }\n  .drawer { top: auto;")
    a = 'scrim.addEventListener("click", closeSpot);'
    assert a in t
    t = t.replace(a, a + TAP_JS)
    t, n = re.subn(r'<span class="mobile-only">[^<]*</span>', '<span class="mobile-only">單指拖曳移動、雙指縮放，點景點看介紹；介紹頁點一下就會關閉</span>', t)
    assert n == 1
    return t

# ---- Desktop: mouse zoom (Ctrl/⌘ + wheel, trackpad pinch, double-click), drag to pan, zoom buttons always shown ----
WHEEL_JS = r'''  const atCursor = e => { const r = svg.getBoundingClientRect(); return [vb.x + (e.clientX - r.left) / r.width * vb.w, vb.y + (e.clientY - r.top) / r.height * vb.h]; };
  svg.addEventListener("wheel", e => {
    if (!(e.ctrlKey || e.metaKey)) return;   // plain wheel keeps scrolling the page
    e.preventDefault(); cancelAnimationFrame(raf);
    zoomAt(Math.exp(-e.deltaY * (e.deltaMode === 1 ? 0.05 : 0.0025)), ...atCursor(e));
  }, { passive: false });
  svg.addEventListener("dblclick", e => {
    if (e.target.closest(".spot, .route-pill, .route-hit")) return;
    e.preventDefault(); cancelAnimationFrame(raf); zoomAt(1.8, ...atCursor(e));
  });
'''
def desktop(t):
    reps = [
      ('  const apply = () => svg.setAttribute("viewBox", `${vb.x} ${vb.y} ${vb.w} ${vb.h}`);',
       '  const apply = () => { svg.setAttribute("viewBox", `${vb.x} ${vb.y} ${vb.w} ${vb.h}`); svg.parentElement.classList.toggle("zoomed", vb.w < full.w - 1); };'),
      ('''  const fit = (x0, y0, x1, y1) => {
    if (!mq.matches) return;
''', '''  const fit = (x0, y0, x1, y1) => {
'''),
      ('''  svg.addEventListener("pointerdown", e => {
    if (!mq.matches) return;
''', '''  svg.addEventListener("pointerdown", e => {
    if (!mq.matches && (e.pointerType !== "mouse" || e.button !== 0 || vb.w >= full.w - 1)) return;
    if (e.pointerType === "mouse") e.preventDefault();
'''),
      ('  const mid = () => [vb.x + vb.w / 2, vb.y + vb.h / 2];\n', WHEEL_JS + '  const mid = () => [vb.x + vb.w / 2, vb.y + vb.h / 2];\n'),
      ('.zoom { display: none; position: absolute;', '.zoom { display: flex; position: absolute;'),
      ('.mobile-only { display: none; }', '.mobile-only { display: none; }\n.desktop-only { display: inline; font-weight: 700; color: var(--ink); }\n.zoom-hint { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(20,22,24,.45); color: #fff; font: 700 20px var(--f-body); pointer-events: none; z-index: 3; }'),
      ('  .mobile-only { display: inline; font-weight: 700; color: var(--ink); }', '  .mobile-only { display: inline; font-weight: 700; color: var(--ink); }\n  .desktop-only { display: none; }'),
      ('<span class="mobile-only">', '<span class="desktop-only">滑鼠：按住 Ctrl 滾動縮放（Mac 觸控板可直接雙指縮放）、雙擊放大、放大後拖曳移動</span>\n    <span class="mobile-only">'),
    ]
    for a, c in reps:
        assert t.count(a) == 1, a
        t = t.replace(a, c)
    return t

_mobile_base = mobile
def mobile(t, home):
    return desktop(_mobile_base(t, home))

# ---- Small screens: full-screen map with a collapsible filter panel on top ----
FS_CSS = '''
/* full-screen map (small screens) */
.fs-only, .fs-bar { display: none; }
#z-full { display: none; font-size: 18px; }
@media (max-width: __BP__px) { #z-full { display: block; } .fs-open { display: inline-flex; } }
.mapbox.fs .zoom { bottom: calc(16px + env(safe-area-inset-bottom, 0px)); right: max(10px, env(safe-area-inset-right, 0px)); }
.mapbox.fs { position: fixed; inset: 0; z-index: 15; height: 100vh; height: 100dvh; border: 0; border-radius: 0; }
.mapbox.fs { display: flex; flex-direction: column; }
.mapbox.fs .fs-bar { position: relative !important; flex: none; order: -1; }
.mapbox.fs svg { flex: 1 1 auto; min-height: 0; height: auto !important; }
body.fs-on { overflow: hidden; }
.mapbox.fs .fs-bar { display: flex; position: absolute; top: 0; left: 0; right: 0; z-index: 4; align-items: center; gap: 8px;
  padding: calc(8px + env(safe-area-inset-top, 0px)) max(10px, env(safe-area-inset-right, 0px)) 8px max(10px, env(safe-area-inset-left, 0px));
  background: var(--paper); border-bottom: 1px solid var(--line); box-shadow: 0 2px 10px var(--shadow); }
.fs-title { flex: 1; min-width: 0; font: 700 16px var(--f-display); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.fs-btn { flex: none; font: 700 14px var(--f-body); padding: 7px 12px; border-radius: 999px; border: 1.5px solid var(--ink); background: var(--paper); color: var(--ink); cursor: pointer; }
.fs-btn[aria-expanded="true"] { background: var(--ink); color: var(--paper); }
.fs-panel { position: absolute; left: 0; right: 0; z-index: 4; max-height: 60%; overflow-y: auto; box-sizing: border-box;
  padding: 10px max(10px, env(safe-area-inset-right, 0px)) 12px max(10px, env(safe-area-inset-left, 0px));
  background: var(--paper); border-bottom: 1px solid var(--line); box-shadow: 0 6px 14px var(--shadow); }
.fs-panel .filters { justify-content: flex-start; }
.fs-dist { position: absolute; left: 0; right: 0; z-index: 3; padding: 0 8px; }
.fs-dist .dist-bar { margin: 6px 0 0; }
.mapbox.fs .p2p-card { top: auto; bottom: 12px; }
.fs-open { display: none; align-items: center; gap: 6px; font: 700 14px var(--f-body); padding: 8px 14px; border-radius: 999px; border: 1.5px solid var(--ink); background: var(--paper); color: var(--ink); box-shadow: 0 2px 8px var(--shadow); cursor: pointer; }
body.fs-on .fs-open { display: none !important; }
#z-full svg, .fs-open svg { display: block; flex: none; width: 16px !important; height: 16px !important; }
#z-full svg { margin: auto; width: 18px !important; height: 18px !important; }
.fs-open { white-space: nowrap; }
@media (max-width: __BP__px) { body:not(.fs-on) .fs-open { display: inline-flex; } .mapbox:not(.fs) { height: 82vh; height: min(84dvh, 1000px); } }
'''
FS_HTML = '''    <div class="fs-bar" id="fs-bar"><span class="fs-title" id="fs-title"></span><button class="fs-btn" id="fs-menu" type="button" aria-expanded="false" aria-controls="fs-panel">☰ 篩選・模式</button>__EXIT__</div>
    <div class="fs-panel" id="fs-panel" hidden></div>
    <div class="fs-dist" id="fs-dist"></div>
'''
FS_HTML = FS_HTML.replace('__EXIT__', '<button class="icon-btn" id="fs-exit" type="button" aria-pressed="true" aria-label="離開全螢幕" title="離開全螢幕">__ICON_SCREEN__</button>')
FS_JS = r'''
/* ---- Full-screen map (small screens) ---- */
(() => {
  const box = document.querySelector(".mapbox"), bar = document.getElementById("fs-bar"), panel = document.getElementById("fs-panel");
  const distSlot = document.getElementById("fs-dist"), menu = document.getElementById("fs-menu");
  const filters = document.querySelector(".filters"), distNote = document.getElementById("dist-note");
  const homeF = document.createComment("filters"), homeD = document.createComment("dist");
  filters.before(homeF); if (distNote) distNote.before(homeD);
  document.getElementById("fs-title").textContent = (document.querySelector("h1") || {}).textContent || "";
  const place = () => { const h = bar.offsetHeight; panel.style.top = h + "px"; distSlot.style.top = (h + (panel.hidden ? 0 : panel.offsetHeight)) + "px"; };
  const setMenu = open => { panel.hidden = !open; menu.setAttribute("aria-expanded", open); place(); };
  let on = false;
  const enter = () => {
    if (on) return; on = true;
    box.classList.add("fs"); document.body.classList.add("fs-on");
    panel.appendChild(filters); if (distNote) distSlot.appendChild(distNote);
    setMenu(false); mapView.refresh();
  };
  const exit = () => {
    if (!on) return; on = false;
    box.classList.remove("fs"); document.body.classList.remove("fs-on");
    homeF.after(filters); if (distNote) homeD.after(distNote);
    setMenu(false); mapView.refresh();
  };
  document.getElementById("z-full").addEventListener("click", () => on ? exit() : enter());
  document.getElementById("fs-exit").addEventListener("click", exit);
  document.getElementById("fs-open").addEventListener("click", enter);
  menu.addEventListener("click", () => setMenu(panel.hidden));
  // picking a filter or mode closes the panel so the map is visible again
  panel.addEventListener("click", e => { if (e.target.closest("button")) setTimeout(() => setMenu(false), 120); });
  window.addEventListener("resize", () => { if (on) place(); });
  const phone = window.matchMedia("(max-width: 640px)");
  if (phone.matches) enter();
  const onChange = () => { if (!mapView.mq.matches) exit(); };
  if (mapView.mq.addEventListener) mapView.mq.addEventListener("change", onChange);
})();
'''
FS_BTN = '<button class="fs-open" id="fs-open" type="button"><svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true"><path d="M2 6V2h4M10 2h4v4M14 10v4h-4M6 14H2v-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>全螢幕地圖</button>'
def fullscreen(t, bp):
    reps = [
      ('<div class="filters" role="group" aria-label="篩選類別">', '<div class="filters" role="group" aria-label="篩選類別">' + FS_BTN.replace('class="fs-open"', 'class="fs-open" style="order: 99"')),
      ('    <div class="zoom">\n      <button id="z-in"', FS_HTML + '    <div class="zoom">\n      <button id="z-full" aria-label="全螢幕地圖" title="全螢幕地圖"><svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M2 6V2h4M10 2h4v4M14 10v4h-4M6 14H2v-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>\n      <button id="z-in"'),
      ('  return { fit, home, mq };', '  const refresh = () => { const [cx, cy] = mid(); set(cx, cy, vb.w); apply(); };\n  return { fit, home, mq, refresh };'),
      ('</style>', FS_CSS.replace("__BP__", bp) + '</style>'),
    ]
    for a, c in reps:
        assert t.count(a) == 1, a[:50]
        t = t.replace(a, c)
    # script: right after the mobile pinch-zoom block
    i = t.index("/* ---- Mobile pinch zoom ---- */"); j = t.index("})();", i) + 5
    return t[:j] + FS_JS + t[j:]

_mobile_prev = mobile
def mobile(t, home):
    t = _mobile_prev(t, home)
    bp = re.search(r'matchMedia\("\(max-width: (\d+)px\)"\)', t).group(1)
    return fullscreen(t, bp)

# ---- Icon buttons outside the map: full screen (screen icon, small screens) + names-only view (eye icon, all sizes) ----
ICON_SCREEN = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 20h6M12 16v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M7.5 9.5V7.5h2M16.5 9.5V7.5h-2M7.5 12.5v2h2M16.5 12.5v2h-2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
ICON_EYE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg>'
NAMES_BTN = '<button class="icon-btn names-btn" type="button" aria-pressed="false" aria-label="簡潔模式：地圖只顯示景點名稱" title="簡潔模式（只顯示名稱）">' + ICON_EYE + '</button>'
NAMES_CSS = '''
/* icon buttons + names-only view */
.view-btns { order: 99; display: inline-flex; gap: 8px; }
body.fs-on .view-btns { display: none !important; }
.icon-btn { display: inline-grid; place-items: center; width: 38px; height: 38px; padding: 0; border-radius: 50%; border: 1.5px solid var(--ink); background: var(--paper); color: var(--ink); cursor: pointer; }
.icon-btn svg { display: block; width: 20px !important; height: 20px !important; }
.icon-btn[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.icon-btn:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }
.fs-bar .icon-btn { flex: none; width: 36px; height: 36px; }
#map.names .t-more { display: none; }
'''
NAMES_JS = r'''
/* ---- Names-only view (eye button) ---- */
(() => {
  const svgMap = document.getElementById("map");
  const set = on => {
    window.NAME_ONLY = on;
    svgMap.classList.toggle("names", on);
    document.querySelectorAll(".names-btn").forEach(b => b.setAttribute("aria-pressed", on));
    sizeTabs();
  };
  document.querySelectorAll(".names-btn").forEach(b => b.addEventListener("click", () => set(!window.NAME_ONLY)));
})();
'''
def names(t):
    # replace the text "全螢幕地圖" button with the icon pair
    m = re.search(r'<button class="fs-open"[^>]*id="fs-open" type="button">.*?</button>', t)
    t = t[:m.start()] + '<span class="view-btns"><button class="icon-btn fs-open" id="fs-open" type="button" aria-label="全螢幕地圖" title="全螢幕地圖">' + ICON_SCREEN + '</button>' + NAMES_BTN + '</span>' + t[m.end():]
    t = t.replace('.fs-open { display: none; align-items: center;', '.fs-open:not(.icon-btn) { display: none; align-items: center;')
    t = re.sub(r'body:not\(\.fs-on\) \.fs-open \{ display: inline-flex; \}', 'body:not(.fs-on) .fs-open { display: inline-grid; }', t)
    t = re.sub(r'(\{ #z-full \{ display: block; \}) \.fs-open \{ display: inline-flex; \}', r'\1', t)
    t = t.replace('#z-full svg, .fs-open svg {', '#z-full svg, .fs-open:not(.icon-btn) svg {')
    # the full-screen icon is only for small screens
    t = t.replace('</style>', NAMES_CSS + '.view-btns .fs-open { display: none; }\n</style>', 1)
    # fs bar: exit uses the same screen icon (pressed); the eye sits right after it, same order as the button row
    t = t.replace('__ICON_SCREEN__', ICON_SCREEN)
    t = re.sub(r'(<button id="z-full" aria-label="全螢幕地圖" title="全螢幕地圖">)<svg viewBox="0 0 16 16".*?</svg>(</button>)', lambda m: m.group(1) + ICON_SCREEN + m.group(2), t)
    a = 'aria-label="離開全螢幕" title="離開全螢幕">' + ICON_SCREEN + '</button>'
    assert t.count(a) == 1
    t = t.replace(a, a + NAMES_BTN)
    # labels: names-only uses the compact (distance-mode) label layout
    i = t.index('function sizeTabs() {'); j = t.index('\n}\n', i)
    body = t[i:j].replace('distMode', 'slim')
    body = body.replace('function sizeTabs() {', 'function sizeTabs() {\n  const slim = distMode || !!window.NAME_ONLY;', 1)
    t = t[:i] + body + t[j:]
    t = re.sub(r'#map\.dist (\.t-[a-z]+) \{', lambda m: '#map.dist %s, #map.names %s {' % (m.group(1), m.group(1)), t)
    i = t.index('/* ---- Full-screen map (small screens) ---- */'); j = t.index('})();', i) + 5
    return t[:j] + NAMES_JS + t[j:]

_mobile_prev2 = mobile
def mobile(t, home):
    return names(_mobile_prev2(t, home))

# ---- Distance mode becomes an icon next to the eye; every icon button gets a hover/tap label ----
TIP_CSS = '''
/* no big focus box around map items after a tap; keyboard focus thickens the label border instead */
#map [tabindex]:focus, #map [tabindex]:focus-visible { outline: none; }
#map .spot:focus-visible .tab { stroke-width: 4; }
#map .route-pill:focus-visible rect, #map .route-mark:focus-visible circle { stroke: var(--ink); stroke-width: 4; }
/* icon labels on hover / tap */
.icon-btn { position: relative; }
.icon-btn[data-tip]::after { content: attr(data-tip); position: absolute; top: calc(100% + 8px); left: 50%; transform: translateX(-50%); z-index: 30;
  white-space: nowrap; font: 700 13px var(--f-body); padding: 5px 10px; border-radius: 6px; background: var(--ink); color: var(--paper);
  box-shadow: 0 2px 8px var(--shadow); pointer-events: none; opacity: 0; transition: opacity .12s; }
.view-btns .icon-btn:first-child[data-tip]::after { left: 0; transform: none; }
.fs-bar .icon-btn:last-child[data-tip]::after { left: auto; right: 0; transform: none; }
@media (hover: hover) { .icon-btn[data-tip]:hover::after { opacity: 1; } }
.icon-btn[data-tip]:focus-visible::after, .icon-btn.tip-show[data-tip]::after { opacity: 1; }
.icon-btn.dist svg { width: 20px !important; height: 20px !important; }
'''
TIP_JS = r'''
/* ---- Icon labels on touch + distance icon in the full-screen bar ---- */
(() => {
  document.querySelectorAll(".icon-btn[data-tip]").forEach(b => b.addEventListener("pointerdown", e => {
    if (e.pointerType === "mouse") return;
    b.classList.add("tip-show"); clearTimeout(b._tip); b._tip = setTimeout(() => b.classList.remove("tip-show"), 1400);
  }));
  const main = document.getElementById("f-dist"), mirror = document.getElementById("fs-dist-btn");
  if (main && mirror) {
    mirror.addEventListener("click", () => main.click());
    new MutationObserver(() => mirror.setAttribute("aria-pressed", main.getAttribute("aria-pressed"))).observe(main, { attributes: true, attributeFilter: ["aria-pressed"] });
  }
})();
'''
def iconbar(t):
    # pull the distance chip out of the filter row and turn it into an icon button after the eye
    m = re.search(r'<button class="chip dist" id="f-dist" aria-pressed="false">(<svg.*?</svg>)距離模式</button>', t)
    assert m
    icon = m.group(1)
    t = t[:m.start()] + t[m.end():]
    dist_btn = '<button class="icon-btn dist" id="f-dist" type="button" aria-pressed="false" aria-label="距離模式" data-tip="距離模式">' + icon + '</button>'
    a = '</button></span>'   # end of .view-btns (after the eye)
    i = t.index('<span class="view-btns">'); j = t.index(a, i) + len('</button>')
    t = t[:j] + dist_btn + t[j:]
    # labels
    t = t.replace('id="fs-open" type="button" aria-label="全螢幕地圖" title="全螢幕地圖"', 'id="fs-open" type="button" aria-label="全螢幕" data-tip="全螢幕"')
    t = t.replace('aria-label="離開全螢幕" title="離開全螢幕"', 'aria-label="離開全螢幕" data-tip="離開全螢幕"')
    t = t.replace('aria-label="簡潔模式：地圖只顯示景點名稱" title="簡潔模式（只顯示名稱）"', 'aria-label="簡潔模式：地圖只顯示景點名稱" data-tip="簡潔模式"')
    # full-screen bar: "☰ 篩選" + distance icon after the eye
    t = t.replace('>☰ 篩選・模式</button>', '>☰ 篩選</button>')
    k = t.index('id="fs-bar"'); k = t.index('class="icon-btn names-btn"', k); k = t.index('</button>', k) + len('</button>')
    t = t[:k] + '<button class="icon-btn dist" id="fs-dist-btn" type="button" aria-pressed="false" aria-label="距離模式" data-tip="距離模式">' + icon + '</button>' + t[k:]
    t = t.replace('</style>', TIP_CSS + '</style>', 1)
    i = t.index('/* ---- Names-only view (eye button) ---- */'); j = t.index('})();', i) + 5
    return t[:j] + TIP_JS + t[j:]

_mobile_prev3 = mobile
def mobile(t, home):
    return iconbar(_mobile_prev3(t, home))
