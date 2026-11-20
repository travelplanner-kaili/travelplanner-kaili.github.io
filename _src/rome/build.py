import json
D = json.load(open("/home/claude/rome/data.json"))
from streetzh import STREET_ZH
for _z in D["spots"]:   # shopping-street drawers: Chinese title, Italian name underneath
    if _z.get("name") in STREET_ZH and _z.get("latin") == _z["name"]: _z["name"] = STREET_ZH[_z["name"]]
SP = []
for s in D["spots"]:
    o = {k: s[k] for k in ("id","cat","x","y","lx","ly","slx","sly","name","latin","feature") if k in s}
    for k in ("sHours","sTime","sPrice","warn","tips","when","stay","hours","price","site","areaPts","stars","fromHotel","sup","links","transport","sMass","walk","howto","compact","ux","uy","tier","rush","cold","mid","shop","shx","shy","mapLines","mapName","nx","ny","shopStreet","week","W","sHours2"):
        if k in s: o[k] = s[k]
    if "pass_" in s: o["pass"] = s["pass_"]
    # 冷門時段: can be visited before 09:00 or after 19:00 (open all day, or any listed time outside 09–19)
    import re as _re
    _txt = (s.get("sHours") or "") + " " + " ".join(s.get("hours") or [])
    _ts = [int(h) * 60 + int(m) for h, m in _re.findall(r"(\d{1,2}):(\d{2})", _txt)]
    if s.get("cat") != "base" and (_re.search(r"全天|24 ?小時", _txt) or any(t < 540 or t > 1140 for t in _ts)): o["cold"] = True
    rm = __import__("notes").REMIND.get(s["id"], [])
    if rm and "tips" in o:
        o["remind"] = [x for i, x in enumerate(o["tips"]) if i in rm]
        o["tips"] = [x for i, x in enumerate(o["tips"]) if i not in rm] or None
        if not o["tips"]: del o["tips"]
    ex = __import__("notes").EXTRA_REMIND.get(s["id"])
    if ex: o["remind"] = o.get("remind", []) + ex
    SP.append(o)
vb = D["vb"]
data_js = "const SPOTS = " + json.dumps(SP, ensure_ascii=False, indent=0) + ";\n" + \
    "const ROUTES = " + json.dumps(__import__("route").ROUTES, ensure_ascii=False) + ";\n" + "const EDGES = " + json.dumps(D["edges"], ensure_ascii=False) + ";\n" + "const BASE = " + json.dumps({k: D[k] for k in ("streets","tiber","park","vat","river","scale","vatlbl","shopStreets","shopStreetLabels")}, ensure_ascii=False) + ";\n"

html = r'''<title>羅馬景點地圖</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@600;700&family=Noto+Sans+TC:wght@400;500;700&family=Cormorant+Garamond:ital,wght@1,500;1,600&display=swap">
<meta name="color-scheme" content="light dark">
<style>
/* hidden must win even where the page is shown without the artifact wrapper (e.g. project file preview) */
[hidden] { display: none !important; }
/* Layout: Rome plan drawn from Google Maps coordinates (SVG, 1 unit = __S__ m); labels as stone tablets; details open in a side drawer / bottom sheet */
:root {
  color-scheme: light dark;   /* tells the browser the page has its own dark theme, so it does not force-darken it */
  --bg: #E7E6E0; --paper: #F7F6F2; --ink: #22262A; --muted: #676B66; --line: #CBC9C0;
  --park: #DCE3C8; --park-edge: #A3B27A; --park-lit: #C4D9A0; --river: #BCD3DE; --street: #D8D5CA;
  --paid: #A3282D; --free: #3A5880; --open: #57772F; --route: #B4610E; --route-bernini: #1F6FB5; --route-cara: #7B3C8C; --route-michel: #0E7C72;
  --warn-bg: #F6E7D5; --warn-fg: #8A4A12; --shadow: rgba(30,32,28,.12);
  --lm-stone: #E8CFA4; --lm-mid: #C4A06C; --lm-dark: #9C7A4E; --lm-hole: #6E5233; --lm-edge: #FFFDF8; --lm-light: #F4E7CE; --lm-water: #7FBCD6; --lm-wave: #E4F4FA;
  --f-display: "Noto Serif TC", "Songti TC", "PMingLiU", serif;
  --f-body: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
  --f-latin: "Cormorant Garamond", "Garamond", "Times New Roman", serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #15171A; --paper: #1E2124; --ink: #E9E7E2; --muted: #9C9F99; --line: #353A3D;
  --park: #26301F; --park-edge: #4D5C35; --park-lit: #3A5226; --river: #24394A; --street: #2C3033;
  --paid: #E26A68; --free: #85A7D3; --open: #A2C473; --route: #F0A55A; --route-bernini: #6FB0EE; --route-cara: #C891DA; --route-michel: #5CCABD;
  --warn-bg: #3A2A19; --warn-fg: #F0B678; --shadow: rgba(0,0,0,.4); --lm-stone: #CDB088; --lm-mid: #9E7F55; --lm-dark: #6E5536; --lm-hole: #3B2C1C; --lm-edge: #EFE6D6; --lm-light: #DCCBAA; --lm-water: #4E8FAA; --lm-wave: #BFE3F0; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #15171A; --paper: #1E2124; --ink: #E9E7E2; --muted: #9C9F99; --line: #353A3D;
  --park: #26301F; --park-edge: #4D5C35; --park-lit: #3A5226; --river: #24394A; --street: #2C3033;
  --paid: #E26A68; --free: #85A7D3; --open: #A2C473; --route: #F0A55A; --route-bernini: #6FB0EE; --route-cara: #C891DA; --route-michel: #5CCABD;
  --warn-bg: #3A2A19; --warn-fg: #F0B678; --shadow: rgba(0,0,0,.4); --lm-stone: #CDB088; --lm-mid: #9E7F55; --lm-dark: #6E5536; --lm-hole: #3B2C1C; --lm-edge: #EFE6D6; --lm-light: #DCCBAA; --lm-water: #4E8FAA; --lm-wave: #BFE3F0; color-scheme: dark }

body { background: var(--bg); color: var(--ink); font-family: var(--f-body); font-size: 15px; line-height: 1.65; margin: 0; }
.wrap { max-width: 1400px; margin: 0 auto; padding-block: 28px 56px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
header { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 16px 32px; margin-bottom: 18px; }
.eyebrow { font-family: var(--f-latin); font-style: italic; font-size: 20px; color: var(--paid); line-height: 1; }
h1 { font-family: var(--f-display); font-size: clamp(26px, 4vw, 38px); line-height: 1.25; margin: 6px 0 4px; text-wrap: balance; letter-spacing: .02em; }
.sub { color: var(--muted); margin: 0; font-size: 14px; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { font: 500 13px var(--f-body); display: inline-flex; align-items: center; gap: 7px; padding: 6px 12px; border-radius: 999px;
  border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.chip .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--c); }
.chip[aria-pressed="false"] { opacity: .45; }
.chip:focus-visible, .spot:focus-visible, .close:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }
.chip[hidden] { display: none; }
.chip.dist { border-color: var(--ink); font-weight: 700; }
.chip.dist[aria-pressed="false"] { opacity: 1; }
.chip.dist[aria-pressed="true"] { background: var(--ink); color: var(--paper); opacity: 1; }
.chip.dist svg { width: 14px; height: 14px; }
.dist-bar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin: 0 0 10px; font-size: 13.5px; background: var(--paper); border: 1px solid var(--line); border-left: 3px solid var(--ink); padding: 8px 12px; border-radius: 4px; }
.dist-bar p { margin: 0; flex: 1 1 320px; min-width: 0; }
.seg { display: inline-flex; border: 1.5px solid var(--ink); border-radius: 999px; overflow: hidden; flex: none; }
.seg-btn { font: 700 13px var(--f-body); padding: 5px 14px; background: var(--paper); color: var(--ink); border: 0; cursor: pointer; }
.seg-btn[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.seg-btn:focus-visible { outline: 2px solid var(--free); outline-offset: -3px; }
.p2p-line { stroke: var(--paid); stroke-width: 4; stroke-dasharray: 2 8; stroke-linecap: round; fill: none; }
.p2p-pill { fill: var(--paid); }
/* 長按範圍模式 */
#map { -webkit-touch-callout: none; -webkit-user-select: none; user-select: none; }
.rad-circle { fill: var(--route); fill-opacity: .08; stroke: var(--route); stroke-width: 3; stroke-dasharray: 10 7; pointer-events: none; }
.rad-ring { fill: none; stroke: var(--route); stroke-opacity: .35; stroke-width: 1.5; stroke-dasharray: 4 6; pointer-events: none; }
.spot.rad-out, .area.rad-out { opacity: .13 !important; }
.spot.rad-center .tab { stroke-width: 4; }
.rad-card { position: absolute; left: 12px; top: 12px; z-index: 2; max-width: min(360px, calc(100% - 84px)); box-sizing: border-box; padding: 9px 14px; border-radius: 12px;
  background: var(--paper); color: var(--ink); border: 2px solid var(--route); box-shadow: 0 4px 16px var(--shadow); font: 500 13px/1.5 var(--f-body); }
.mapbox.fs .rad-card { top: auto; bottom: calc(12px + env(safe-area-inset-bottom, 0px)); }
.rad-card b { font-size: 16px; color: var(--route); }
.rad-card .rad-x { margin-left: 8px; border: 0; background: none; color: var(--muted); font: 700 13px var(--f-body); cursor: pointer; padding: 2px 4px; text-decoration: underline; }
.p2p-card { position: absolute; left: 12px; top: 12px; z-index: 2; max-width: calc(100% - 24px); box-sizing: border-box; display: flex; flex-direction: column; gap: 2px; padding: 10px 16px; border-radius: 12px; background: var(--paid); color: var(--paper); box-shadow: 0 4px 16px var(--shadow); pointer-events: none; }
.p2p-route { font: 500 15px/1.4 var(--f-body); overflow-wrap: anywhere; }
.p2p-dist { font: 700 28px/1.2 var(--f-body); font-variant-numeric: tabular-nums; }
.p2p-dist small { font-size: 14px; font-weight: 500; margin-left: 6px; }
@media (max-width: 640px) { .p2p-card { left: 8px; right: 8px; top: 8px; max-width: none; padding: 8px 14px; } .p2p-dist { font-size: 24px; } }
@media (max-width: 1240px) { .p2p-lbl { display: none; } }
.p2p-text { font: 700 26px var(--f-body); fill: var(--paper); font-variant-numeric: tabular-nums; }
#map.dist .t-name, #map.names .t-name { font-size: 26px; }
#map.dist .t-more, #map.names .t-more { display: none; }
.edge line { stroke: var(--ink); stroke-opacity: .6; stroke-width: 3.5; stroke-dasharray: 2 7; stroke-linecap: round; }
.edge .conn { stroke-width: 1.2; stroke-dasharray: none; stroke-opacity: .4; }
.edge rect { fill: var(--paper); stroke: var(--line); stroke-width: 1.2; }
.edge text { font: 500 19px var(--f-body); fill: var(--ink); font-variant-numeric: tabular-nums; }
.edge.dim { opacity: .12; }
.edge:not(.on) { display: none; }
#map.dist .spot.picked .tab { stroke-width: 3.5; fill: var(--bg); }
.chip.done { border-style: dashed; border-color: var(--open); }
.chip.done[aria-pressed="false"] { opacity: 1; }
.chip.done[aria-pressed="true"] { background: var(--open); color: var(--paper); border-style: solid; }
.visit-btn { display: inline-flex; align-items: center; gap: 6px; margin: 0 0 16px; padding: 7px 16px; border-radius: 999px; border: 1.5px solid var(--open); background: var(--paper); color: var(--open); font: 700 14px var(--f-body); cursor: pointer; }
.d-actions { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 16px; }
.d-actions .visit-btn { margin: 0; }
.gmap { display: inline-flex; align-items: center; gap: 6px; padding: 7px 16px; border-radius: 999px; border: 1.5px solid var(--free); color: var(--free); background: var(--paper); font: 700 14px var(--f-body); text-decoration: none; }
.gmap svg { width: 15px; height: 15px; }
.gmap:hover { background: var(--bg); }
.gmap:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }
.d-icons { display: inline-flex; gap: 8px; }
.icon-act { display: inline-grid; place-items: center; width: 40px; height: 40px; border-radius: 50%; border: 1.5px solid var(--free); color: var(--free); background: var(--paper); cursor: pointer; padding: 0; text-decoration: none; }
.icon-act svg { width: 20px !important; height: 20px !important; }
.icon-act:hover { background: var(--bg); }
.icon-act:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }
.icon-act.report { border-color: var(--paid); color: var(--paid); }
.icon-act.report:focus-visible { outline-color: var(--paid); }
.foot-report { color: var(--paid); font-weight: 700; }
.share-note { font-size: 13px; color: var(--muted); }
.share-note input { font: 12px var(--f-body); width: min(260px, 60vw); }
.visit-btn[aria-pressed="true"] { background: var(--open); color: var(--paper); }
.visit-btn:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }
.spot.visited { opacity: .45; }
.spot.visited .tab { stroke-dasharray: 5 4; }
.spot.hide-v, .area.hide-v, .edge.hide-v { display: none; }
.icon-btn.route { border-color: var(--route); color: var(--route); }
.icon-btn.shop-btn { border-color: var(--open); color: var(--open); }
.icon-btn.shop-btn[aria-pressed="true"] { background: var(--open); color: var(--paper); }
.icon-btn.route[aria-pressed="true"] { background: var(--route); color: var(--paper); }
.chip.route { border-color: var(--route); color: var(--route); font-weight: 700; }
.chip.route[aria-pressed="false"] { opacity: 1; }
.chip.route[aria-pressed="true"] { background: var(--route); color: var(--paper); }
.chip.route svg { width: 16px; height: 16px; }
.route-line { fill: none; stroke: var(--route); stroke-width: 8; stroke-dasharray: 16 10; stroke-linecap: round; stroke-linejoin: round; }
.route-hit { fill: none; stroke: transparent; stroke-width: 44; cursor: pointer; pointer-events: stroke; }
.route-end { fill: var(--route); stroke: var(--paper); stroke-width: 4; }
.route-end-t { font: 700 20px var(--f-body); fill: var(--paper); }
.spot.gone.on-route { display: inline; }
.spot.off-route, .area.off-route, .edge.off-route { display: none !important; }
.route-pill { cursor: pointer; }
.route-pill rect { fill: var(--route); stroke: var(--paper); stroke-width: 3; }
.route-pill text { font: 700 24px var(--f-body); fill: var(--paper); font-variant-numeric: tabular-nums; }
.route-card { position: absolute; left: 12px; bottom: 12px; z-index: 2; max-width: calc(100% - 90px); box-sizing: border-box; display: flex; flex-direction: column; align-items: flex-start; gap: 2px; padding: 9px 16px; border: 0; border-radius: 12px; background: var(--route); color: var(--paper); box-shadow: 0 4px 16px var(--shadow); text-align: left; pointer-events: none; font-family: var(--f-body); }
.route-pick { position: absolute; left: max(10px, env(safe-area-inset-left, 0px)); top: 10px; z-index: 3; max-width: calc(100% - 80px); display: flex; flex-wrap: wrap; gap: 6px; }
.route-pick button { --rc: var(--route); font: 700 13px var(--f-body); padding: 5px 11px; border-radius: 999px; border: 2px solid var(--rc); background: var(--paper); color: var(--rc); cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,.12); }
.route-pick button[aria-pressed="true"] { background: var(--rc); color: var(--paper); }
.route-pick button.all { --rc: var(--ink); }
@media (max-width: 640px) { .route-pick { top: 6px; left: 6px; right: 6px; max-width: none; gap: 4px; flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; padding-bottom: 2px; } .route-pick::-webkit-scrollbar { display: none; } .route-pick button { font-size: 12px; padding: 4px 9px; flex: none; } }
.route-card b { font-size: 16px; }
.route-card span { font-size: 13px; }
@media (max-width: 640px) { .route-card { left: 8px; bottom: 8px; padding: 6px 12px; } .route-card b { font-size: 14px; } .route-card span { display: none; } }
.route-card:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
ol.stops { margin: 0; padding-left: 1.3em; }
.rt-tabs { display: flex; gap: 0; margin: 4px 0 18px; border-bottom: 1px solid var(--line); }
.rt-tab { font: 700 15px var(--f-body); padding: 9px 12px; white-space: nowrap; background: none; border: 0; border-bottom: 3px solid transparent; margin-bottom: -1px; color: var(--muted); cursor: pointer; }
.rt-tab[aria-selected="true"] { color: var(--route); border-bottom-color: var(--route); }
.rt-tab:focus-visible { outline: 2px solid var(--route); outline-offset: -3px; }
.rt-panel[data-panel="tips"] > ul { margin: 0; padding-left: 1.2em; display: flex; flex-direction: column; gap: 10px; line-height: 1.7; }
.rt-panel[data-panel="tips"] > .warn { margin-bottom: 16px; }
.tab-alert { display: inline-grid; place-items: center; width: 18px; height: 18px; margin-left: 6px; border-radius: 50%; background: var(--warn-fg); color: var(--warn-bg); font-size: 12px; font-weight: 800; vertical-align: 2px; }
.warn-jump { display: block; width: 100%; text-align: left; font: 600 14px var(--f-body); padding: 9px 12px; margin: 0 0 16px; border-radius: 8px; border: 0; background: var(--warn-bg); color: var(--warn-fg); cursor: pointer; }
.tips-panel ul { margin: 0; padding-left: 1.2em; display: flex; flex-direction: column; gap: 10px; line-height: 1.7; }
.food-intro { margin: 0 0 18px; line-height: 1.7; }
.food-h { font-size: 13px; letter-spacing: .06em; color: var(--muted); margin: 0 0 10px; }
.food-list { list-style: none; margin: 0 0 22px; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.food { border: 1px solid var(--line); border-left: 4px solid var(--route); border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }
.food p { margin: 0; line-height: 1.6; }
.food-where { font-size: 12px; font-weight: 700; color: var(--route); letter-spacing: .04em; }
.food-name { font: 700 17px var(--f-body); }
.food-kind, .food-hours { font-size: 13px; color: var(--muted); }
.food .gmap { margin-top: 6px; }
.stop-link { font: 700 15px var(--f-body); color: var(--route); background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; }
.chip.sup .dot { background: none; border: 2px dashed var(--c); width: 8px; height: 8px; }
.chip-group { display: inline-flex; flex-wrap: wrap; gap: 6px; padding-right: 8px; margin-right: 2px; border-right: 1px solid var(--line, rgba(0,0,0,.12)); }
.chip-group:last-of-type { border-right: 0; }
.chip.tier[data-tier="推薦"] .dot { background: none; border: 2.5px solid var(--c); width: 7px; height: 7px; }
.chip[data-cat="free"] .dot { background: linear-gradient(90deg, var(--free) 50%, var(--open) 50%); }   /* 免費 covers free sights (blue) and squares / districts / streets (green) */
.chip.shop .dot { border-radius: 2px; }
.chip.shop[aria-pressed="true"] { background: var(--route); color: var(--paper); opacity: 1; }
.chip.shop[aria-pressed="true"] .dot { background: var(--paper); }
.chip.muted { opacity: .35 !important; }
.shop-street { cursor: pointer; }
.shop-street:hover, .shop-street:focus-visible { text-decoration: underline; outline: none; }
.chip.cold .dot { background: linear-gradient(90deg, var(--c) 50%, transparent 50%); border: 1.5px solid var(--c); width: 8px; height: 8px; }
.spot.rush .tab { stroke-width: 3.5; }
.rush-tag rect { fill: var(--paid); }
.rush-tag text { fill: var(--paper); font: 700 15px var(--f-body); }

.mapbox { position: relative; background: var(--paper); border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }
.mapbox svg { display: block; width: 100%; height: auto; }
.zoom { display: flex; position: absolute; right: 10px; bottom: 10px; flex-direction: column; gap: 6px; }
.zoom button { width: 42px; height: 42px; border-radius: 8px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font: 500 22px/1 var(--f-body); box-shadow: 0 2px 8px var(--shadow); cursor: pointer; }
.zoom button:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }
.mobile-only { display: none; }
.desktop-only { display: inline; font-weight: 700; color: var(--ink); }
.zoom-hint { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(20,22,24,.45); color: #fff; font: 700 20px var(--f-body); pointer-events: none; z-index: 3; }
@media (max-width: 1240px) {
  .mapbox { height: 70vh; height: min(70dvh, 900px); }
  .mapbox svg { touch-action: none; height: 100%; }
  .zoom { display: flex; }
  .mobile-only { display: inline; font-weight: 700; color: var(--ink); }
  .desktop-only { display: none; }
}
.hint { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px 16px; font-size: 12.5px; color: var(--muted); margin-top: 8px; }

.spot { cursor: pointer; }
.spot .tab { fill: var(--paper); stroke: var(--c); stroke-width: 1.8; transition: fill .15s; }
.spot:hover .tab, .spot.active .tab { fill: var(--bg); }
.spot.active .tab { stroke-width: 3.5; }
.spot .pin { fill: var(--c); stroke: var(--paper); stroke-width: 3; }
/* 立體地標 */
.lm-shadow { fill: var(--ink); opacity: .16; }
.lm-depth { fill: var(--lm-dark); }
.lm-stone { fill: var(--lm-stone); stroke: var(--lm-edge); stroke-width: 1.6; stroke-linejoin: round; }
.lm-band { stroke: var(--lm-mid); stroke-width: 1.6; fill: none; }
.lm-hole { fill: var(--lm-hole); }
.lm .lm-mid { fill: var(--lm-mid); stroke: var(--lm-edge); stroke-width: 1.2; stroke-linejoin: round; }
.lm-light { fill: var(--lm-light); stroke: var(--lm-edge); stroke-width: 1.2; stroke-linejoin: round; }
.lm-water { fill: var(--lm-water); stroke: var(--lm-edge); stroke-width: 1.2; }
.lm-wave { fill: none; stroke: var(--lm-wave); stroke-width: 1.4; stroke-linecap: round; }
.lm-statue { fill: var(--lm-edge); }
.spot .lm { transition: transform .15s; }
.spot .pin.icon-base { stroke-width: 2; }
.spot .leader { stroke: var(--c); stroke-width: 1.6; fill: none; }
.spot .t-name { font: 700 28px var(--f-body); fill: var(--ink); }
.spot .t-stars { font-size: 19px; font-weight: 400; fill: var(--paid); letter-spacing: 1px; }
#map.dist .t-stars, #map.names .t-stars { font-size: 18px; }
.chip-group.days { align-items: center; gap: 4px; }
.days-lbl { font: 700 12.5px var(--f-body); color: var(--muted); margin-right: 2px; white-space: nowrap; }
.chip.day { width: 30px; height: 30px; padding: 0; justify-content: center; border-radius: 50%; font: 700 14px var(--f-body); border-color: var(--ink); }
.chip.day[aria-pressed="true"] { background: var(--ink); color: var(--paper); opacity: 1; }
.chip.day[aria-pressed="false"] { opacity: .5; }
.spot .t-wed.day-off { fill: var(--paid); font-weight: 700; }
.spot .t-wed { font: 500 21px var(--f-body); fill: var(--ink); font-variant-numeric: tabular-nums; }
.spot .t-mass { font: 700 21px var(--f-body); fill: var(--route); }
.spot .t-time { font: 400 21px var(--f-body); fill: var(--muted); font-variant-numeric: tabular-nums; }
.spot .t-price { font: 700 21px var(--f-body); fill: var(--c); font-variant-numeric: tabular-nums; }
.spot.mid .t-name { font-size: 24px; }
.spot.shopbox .tab, .spot.shopbox:hover .tab { fill: var(--c); }   /* 購物 view: shop labels are solid so they read as shops */
.spot.shopbox .t-name { fill: var(--paper); }
.spot.mid .t-wed, .spot.mid .t-price, .spot.mid .t-mass { font-size: 18px; }
.spot.dim { opacity: .28; }   /* faded by a filter, but still clickable */
.spot.gone, .area.gone { display: none; }
.area.lit polygon { fill: var(--park-lit); fill-opacity: 1; stroke: var(--route); stroke-width: 4; stroke-dasharray: 14 8; }
.route-pill .route-hand { font-size: 52px; pointer-events: none; filter: drop-shadow(0 2px 2px rgba(0,0,0,.35)); }
.route-mark { cursor: pointer; }
.route-mark circle { fill: var(--paper); stroke: var(--route); stroke-width: 3.5; }
.route-mark text { font: 700 21px var(--f-body); fill: var(--route); }
.route-mark:hover circle { fill: var(--route); } .route-mark:hover text { fill: var(--paper); }
.walk-link { margin-top: 10px; font: 700 15px var(--f-body); padding: 8px 14px; border-radius: 999px; border: 2px solid var(--route); background: none; color: var(--route); cursor: pointer; }
.walk-link:hover { background: var(--route); color: var(--paper); }
.howto-intro { margin: 0 0 8px; line-height: 1.7; }
.howto { margin: 0; padding-left: 1.3em; display: flex; flex-direction: column; gap: 8px; line-height: 1.65; }
.tip-map { display: inline-block; font-size: 13px; font-weight: 600; color: var(--free); text-decoration: none; border-bottom: 1px solid currentColor; margin-left: 2px; }
.park.lit { fill: var(--park-lit); stroke: var(--route); stroke-width: 4; stroke-dasharray: 14 8; }
.spot.is-sup .tab { stroke-dasharray: 6 4; }
.edge.hide-s { display: none; }
.area polygon { fill: var(--c); fill-opacity: .13; stroke: var(--c); stroke-width: 3; stroke-dasharray: 12 8; stroke-linejoin: round; }
.area.dim { opacity: .12; }

.scrim { position: fixed; inset: 0; background: rgba(10,12,14,.35); z-index: 20; }
.drawer { position: fixed; z-index: 21; background: var(--paper); color: var(--ink); box-shadow: 0 10px 40px var(--shadow);
  top: 0; right: 0; bottom: 0; width: min(420px, 100%); overflow-y: auto; box-sizing: border-box; overscroll-behavior: contain;
  padding: calc(22px + env(safe-area-inset-top, 0px)) max(24px, env(safe-area-inset-right, 0px)) calc(28px + env(safe-area-inset-bottom, 0px)) 24px; }
@media (max-width: 640px) {
  .drawer::before { content: ""; display: block; width: 44px; height: 5px; border-radius: 3px; background: var(--line); margin: -8px auto 12px; }
  .drawer { top: auto; left: 0; width: 100%; max-height: 82vh; max-height: 82dvh; border-radius: 14px 14px 0 0;
    padding: 20px max(18px, env(safe-area-inset-right, 0px)) calc(28px + env(safe-area-inset-bottom, 0px)) max(18px, env(safe-area-inset-left, 0px)); }
}
.d-top { display: flex; justify-content: space-between; align-items: start; gap: 12px; }
.cat { display: inline-block; font-size: 12px; font-weight: 700; letter-spacing: .08em; color: var(--c); border: 1px solid var(--c); padding: 2px 9px; border-radius: 999px; }
.close { flex: none; width: 36px; height: 36px; border-radius: 50%; border: 1px solid var(--line); background: var(--bg); color: var(--ink); font-size: 20px; line-height: 1; cursor: pointer; }
.drawer h3 { font-family: var(--f-display); font-size: 26px; line-height: 1.3; margin: 12px 0 0; text-wrap: balance; }
.latin { font-family: var(--f-latin); font-style: italic; font-size: 19px; color: var(--muted); margin: 2px 0 18px; }
.stars { margin: -8px 0 16px; color: var(--paid); font-size: 17px; letter-spacing: .12em; display: flex; align-items: center; gap: 10px; }
.stars span { font-size: 12px; font-weight: 700; letter-spacing: .1em; color: var(--muted); }
.stars i { font-style: normal; color: var(--line); }
.warn { background: var(--warn-bg); color: var(--warn-fg); font-weight: 500; font-size: 14px; padding: 9px 12px; border-radius: 4px; margin-bottom: 16px; }
dl { margin: 0; display: grid; gap: 14px; }
dt { font-size: 12px; font-weight: 700; letter-spacing: .1em; color: var(--muted); }
dd { margin: 2px 0 0; font-variant-numeric: tabular-nums; }
dd ul { margin: 0; padding-left: 1.1em; }
.tr h4 { font: 700 14.5px/1.5 var(--f-body); margin: 10px 0 2px; color: var(--ink); }
.tr h4:first-child { margin-top: 0; }
.site { color: var(--free); font-weight: 500; text-underline-offset: 3px; word-break: break-all; }
@media (prefers-reduced-motion: no-preference) {
  .drawer:not([hidden]) { animation: slide .22s ease-out; }
  @keyframes slide { from { transform: translateX(24px); opacity: 0; } }
  @media (max-width: 640px) { @keyframes slide { from { transform: translateY(30px); opacity: 0; } } }
}

/* full-screen map (small screens) */
.fs-only, .fs-bar { display: none; }
#z-full { display: none; font-size: 18px; }
@media (max-width: 1240px) { #z-full { display: block; } }
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
.fs-open:not(.icon-btn) { display: none; align-items: center; gap: 6px; font: 700 14px var(--f-body); padding: 8px 14px; border-radius: 999px; border: 1.5px solid var(--ink); background: var(--paper); color: var(--ink); box-shadow: 0 2px 8px var(--shadow); cursor: pointer; }
body.fs-on .fs-open { display: none !important; }
#z-full svg, .fs-open:not(.icon-btn) svg { display: block; flex: none; width: 16px !important; height: 16px !important; }
#z-full svg { margin: auto; width: 18px !important; height: 18px !important; }
.fs-open { white-space: nowrap; }
@media (max-width: 1240px) { body:not(.fs-on) .fs-open { display: inline-grid; } .mapbox:not(.fs) { height: 82vh; height: min(84dvh, 1000px); } }

/* icon buttons + names-only view */
.view-btns { order: 99; display: inline-flex; gap: 8px; }
body.fs-on .view-btns { display: none !important; }
.icon-btn { display: inline-grid; place-items: center; width: 38px; height: 38px; padding: 0; border-radius: 50%; border: 1.5px solid var(--ink); background: var(--paper); color: var(--ink); cursor: pointer; }
.icon-btn svg { display: block; width: 20px !important; height: 20px !important; }
.icon-btn[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.icon-btn:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }
.fs-bar .icon-btn { flex: none; width: 36px; height: 36px; }
#map.names .t-more { display: none; }
.view-btns .fs-open { display: none; }
/* 全螢幕 on every screen size, desktop too */
body:not(.fs-on) .view-btns .fs-open { display: inline-grid !important; }
#z-full { display: block; }


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

/* no big focus box around map items after a tap; keyboard focus thickens the label border instead */
#map [tabindex]:focus, #map [tabindex]:focus-visible { outline: none; }
#map .spot:focus-visible .tab { stroke-width: 4; }
#map .route-pill:focus-visible rect, #map .route-mark:focus-visible circle { stroke: var(--ink); stroke-width: 4; }
</style>

<div class="wrap">
  <header>
    <div>
      <div class="eyebrow">Roma · Lazio</div>
      <h1>羅馬景點地圖</h1>
    </div>
    <div class="filters" role="group" aria-label="篩選類別"><span class="view-btns"><button class="icon-btn fs-open" id="fs-open" type="button" aria-label="全螢幕" data-tip="全螢幕"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 20h6M12 16v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M7.5 9.5V7.5h2M16.5 9.5V7.5h-2M7.5 12.5v2h2M16.5 12.5v2h-2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button><button class="icon-btn names-btn" type="button" aria-pressed="false" aria-label="簡潔模式：地圖只顯示景點名稱" data-tip="簡潔模式"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg></button><button class="icon-btn dist" id="f-dist" type="button" aria-pressed="false" aria-label="距離模式" data-tip="距離模式"><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="3" cy="13" r="2" fill="currentColor"/><circle cx="13" cy="3" r="2" fill="currentColor"/><path d="M4.5 11.5 L11.5 4.5" stroke="currentColor" stroke-width="1.6" stroke-dasharray="1.5 2.5" stroke-linecap="round"/></svg></button><button class="icon-btn route" id="f-route" type="button" aria-pressed="false" aria-label="City Walk 散步路線" data-tip="City Walk"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="14" cy="3.6" r="2.5" fill="currentColor"/><path d="M13 7.4 L11 13.6 M12.5 8.6 L7.6 11.2 M12.7 9 L16.8 12 M11 13.6 L7.4 21.2 M11 13.6 L14.6 16.6 L16.2 21.2" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></button><button class="icon-btn shop-btn" id="f-shop" type="button" aria-pressed="false" aria-label="購物：在地圖上加上購物的店家" data-tip="購物"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 8h14l-1.2 12.2a1 1 0 0 1-1 .8H7.2a1 1 0 0 1-1-.8z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 10V6.5a3 3 0 0 1 6 0V10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></span>
      <span class="chip-group" role="group" aria-label="景點層級"><button class="chip tier" data-tier="主要" aria-pressed="true" style="--c:var(--ink)"><span class="dot"></span>主要景點</button><button class="chip tier" data-tier="推薦" aria-pressed="true" style="--c:var(--ink)"><span class="dot"></span>推薦</button><button class="chip tier sup" id="f-sup" data-tier="次要" aria-pressed="false" style="--c:var(--muted)"><span class="dot"></span>次要</button></span>
      <span class="chip-group days" role="group" aria-label="星期幾去：景點框只顯示這幾天的營業時間"><span class="days-lbl">星期幾去</span><button class="chip day" type="button" data-day="0" aria-pressed="true" aria-label="星期一">一</button><button class="chip day" type="button" data-day="1" aria-pressed="true" aria-label="星期二">二</button><button class="chip day" type="button" data-day="2" aria-pressed="true" aria-label="星期三">三</button><button class="chip day" type="button" data-day="3" aria-pressed="true" aria-label="星期四">四</button><button class="chip day" type="button" data-day="4" aria-pressed="true" aria-label="星期五">五</button><button class="chip day" type="button" data-day="5" aria-pressed="true" aria-label="星期六">六</button><button class="chip day" type="button" data-day="6" aria-pressed="true" aria-label="星期日">日</button></span><span class="chip-group" role="group" aria-label="景點類型"><button class="chip" data-cat="paid" aria-pressed="true" style="--c:var(--paid)"><span class="dot"></span>需購票景點</button><button class="chip" data-cat="free" aria-pressed="true" style="--c:var(--free)"><span class="dot"></span>免費景點</button><button class="chip cold" id="f-cold" aria-pressed="false" style="--c:var(--ink)" data-tip="只看早上 9 點前或晚上 7 點後還能去的景點" title="只看早上 9 點前或晚上 7 點後還能去的景點"><span class="dot"></span>冷門時段（9 點前或晚上 7 點後）</button></span>
      
      
      <button class="chip done" id="f-done" hidden aria-pressed="false" title="去過的景點記在這台裝置的瀏覽器裡">顯示去過的景點（<span id="done-n">0</span>）</button>
    </div>
  </header>

  <div class="dist-bar" id="dist-note" hidden><p id="dist-text">先點起點，會顯示它到相鄰景點的距離；再點終點，就畫出兩點之間的距離與步行時間。點空白處重新選。步行距離以直線距離 ×1.3 估算，步速每分鐘 80 公尺；實際路線請以 Google 地圖導航為準。</p></div>
  <div class="mapbox">
    <svg id="map" viewBox="__VB__" role="img" aria-label="羅馬市中心景點分布圖">
      <defs>
        <pattern id="hatch" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="14" stroke="var(--line)" stroke-width="1" opacity=".5"/>
        </pattern>
      </defs>
      <rect x="__VBX__" y="__VBY__" width="__VBW__" height="__VBH__" fill="var(--paper)"/>
      <g id="base"></g>
      <g id="routes" hidden></g>
      <g id="edges" hidden></g>
      <g id="spots"></g>
    </svg>
    <div class="route-pick" id="route-pick" role="group" aria-label="選擇要顯示的 City Walk" hidden></div>
    <div class="route-card" id="route-card" hidden><b id="route-card-name"></b><span>點地圖上的路線或距離標籤，看路線介紹</span></div>
    <div class="rad-card" id="rad-card" hidden aria-live="polite"></div>
    <div class="p2p-card" id="p2p-card" hidden aria-live="polite"><span class="p2p-route" id="p2p-route"></span><span class="p2p-dist" id="p2p-dist"></span></div>
    <div class="fs-bar" id="fs-bar"><span class="fs-title" id="fs-title"></span><button class="fs-btn" id="fs-menu" type="button" aria-expanded="false" aria-controls="fs-panel">☰ 篩選</button><button class="icon-btn" id="fs-exit" type="button" aria-pressed="true" aria-label="離開全螢幕" data-tip="離開全螢幕"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 20h6M12 16v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M7.5 9.5V7.5h2M16.5 9.5V7.5h-2M7.5 12.5v2h2M16.5 12.5v2h-2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button><button class="icon-btn names-btn" type="button" aria-pressed="false" aria-label="簡潔模式：地圖只顯示景點名稱" data-tip="簡潔模式"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg></button><button class="icon-btn dist" id="fs-dist-btn" type="button" aria-pressed="false" aria-label="距離模式" data-tip="距離模式"><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="3" cy="13" r="2" fill="currentColor"/><circle cx="13" cy="3" r="2" fill="currentColor"/><path d="M4.5 11.5 L11.5 4.5" stroke="currentColor" stroke-width="1.6" stroke-dasharray="1.5 2.5" stroke-linecap="round"/></svg></button><button class="icon-btn route" id="fs-route-btn" type="button" aria-pressed="false" aria-label="City Walk 散步路線" data-tip="City Walk"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="14" cy="3.6" r="2.5" fill="currentColor"/><path d="M13 7.4 L11 13.6 M12.5 8.6 L7.6 11.2 M12.7 9 L16.8 12 M11 13.6 L7.4 21.2 M11 13.6 L14.6 16.6 L16.2 21.2" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></button><button class="icon-btn shop-btn" id="fs-shop-btn" type="button" aria-pressed="false" aria-label="購物：在地圖上加上購物的店家" data-tip="購物"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 8h14l-1.2 12.2a1 1 0 0 1-1 .8H7.2a1 1 0 0 1-1-.8z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 10V6.5a3 3 0 0 1 6 0V10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></div>
    <div class="fs-panel" id="fs-panel" hidden></div>
    <div class="fs-dist" id="fs-dist"></div>
    <div class="zoom">
      <button id="z-full" aria-label="全螢幕地圖" title="全螢幕地圖"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 20h6M12 16v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M7.5 9.5V7.5h2M16.5 9.5V7.5h-2M7.5 12.5v2h2M16.5 12.5v2h-2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button>
      <button id="z-in" aria-label="放大">+</button>
      <button id="z-out" aria-label="縮小">−</button>
      <button id="z-reset" aria-label="顯示整張地圖">⤢</button>
    </div>
  </div>
  <div class="hint">
    <span class="desktop-only">滑鼠：按住 Ctrl 滾動縮放（Mac 觸控板可直接雙指縮放）、雙擊放大、放大後拖曳移動</span>
    <span class="mobile-only">單指拖曳移動、雙指縮放，點景點看介紹；介紹頁點一下就會關閉</span>
    <span>景點依 Google 地圖座標標示；台伯河、公園與街道為簡化示意</span>
    <span><a class="foot-report" id="foot-report" href="https://docs.google.com/forms/d/e/1FAIpQLSfczsbVIwVeT78rpvKnk8CF1upTBqEKsf6viWWYu5iBn532Lg/viewform?usp=pp_url&entry.772922063=%E7%BE%85%E9%A6%AC" target="_blank" rel="noopener">⚠ 發現錯誤？匿名回報給作者</a></span>
    <span>營業時間為旅程期間（1–2 月冬季）的時間；營業時間與票價出發前請再到官網確認</span>
  </div>
  <!--FAQ-->
</div>

<div class="scrim" id="scrim" hidden></div>
<aside class="drawer" id="drawer" hidden role="dialog" aria-modal="true" aria-labelledby="d-name"></aside>

<script>
const CAT = {
  paid: { label: "需購票／有營業時限", color: "var(--paid)" },
  free: { label: "免費景點", color: "var(--free)" },
  open: { label: "全天開放", color: "var(--open)" },
  base: { label: "住宿與交通", color: "var(--ink)" }
};
__DATA__
const NS = "http://www.w3.org/2000/svg";
const el = (tag, attrs = {}, parent) => {
  const n = document.createElementNS(NS, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(n);
  return n;
};
const pts = a => a.map(p => p.join(",")).join(" ");
const path = a => "M" + a.map(p => p.join(" ")).join(" L");

/* ---- Base map ---- */
const base = document.getElementById("base");
el("polygon", { points: pts(BASE.vat), fill: "url(#hatch)", stroke: "var(--line)", "stroke-width": 2, "stroke-dasharray": "6 6" }, base);
const vt = el("text", { x: BASE.vatlbl.x, y: BASE.vatlbl.y, "text-anchor": "middle", transform: `rotate(-90 ${BASE.vatlbl.x} ${BASE.vatlbl.y})`, "font-family": "Noto Sans TC, sans-serif", "font-size": 18, "letter-spacing": "4", fill: "var(--muted)" }, base);
vt.textContent = "梵蒂岡城國";
const parkEl = el("polygon", { class: "park", points: pts(BASE.park), fill: "var(--park)", stroke: "var(--park-edge)", "stroke-width": 2, "stroke-linejoin": "round" }, base);
const areaBase = el("g", {}, base);   // neighbourhood areas sit with the park, under streets and routes
BASE.streets.forEach(s => el("path", { d: path(s.d), fill: "none", stroke: s.hl ? "var(--route)" : "var(--street)", "stroke-opacity": s.hl ? .5 : 1, "stroke-width": s.hl ? 14 : 12, "stroke-linecap": "round", "stroke-linejoin": "round" }, base));
el("path", { d: path(BASE.tiber), fill: "none", stroke: "var(--river)", "stroke-width": 26, "stroke-linecap": "round", "stroke-linejoin": "round" }, base);
const rl = el("text", { x: BASE.river.x, y: BASE.river.y, "font-family": "Noto Sans TC, sans-serif", "font-size": 19, "font-weight": 500, fill: "var(--free)", opacity: .8 }, base);
rl.textContent = BASE.river.text;
// 購物 view: shopping streets drawn as thick orange lines (hidden unless 購物 is on)
const shopLayer = el("g", { id: "shop-streets" }, base);   // shopping streets: always shown
(BASE.shopStreets || []).forEach(st => el("path", { d: path(st.d), fill: "none", stroke: "var(--route)", "stroke-opacity": .55, "stroke-width": 16, "stroke-linecap": "round", "stroke-linejoin": "round" }, shopLayer));
// 購物 view: street names for the shopping streets, in the same style as the map's street names; tap to open the side panel
const shopLabels = el("g", { id: "shop-street-labels" }, document.getElementById("map"));
(BASE.shopStreetLabels || []).forEach(l => {
  const t = el("text", { class: "shop-street", x: l.x, y: l.y, transform: `rotate(${l.rot} ${l.x} ${l.y})`, role: "button", tabindex: 0, "data-id": l.id,
    "font-family": "Noto Sans TC, Helvetica, Arial, sans-serif", "font-size": 21, "font-weight": 700, fill: "var(--route)",
    stroke: "var(--paper)", "stroke-width": 5, "stroke-linejoin": "round", "paint-order": "stroke" }, shopLabels);
  t.textContent = l.name;
  const go = () => openSpot(l.id);
  t.addEventListener("click", e => { e.stopPropagation(); go(); });
  t.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
});
BASE.streets.forEach(s => {
  if (!s.name) return;
  const t = el("text", { class: "base-street" + (s.soft ? " soft-street" : ""), x: s.tx, y: s.ty, transform: `rotate(${s.rot} ${s.tx} ${s.ty})`,
    "font-family": "Noto Sans TC, Helvetica, Arial, sans-serif", "font-size": 23, "font-weight": s.hl ? 700 : 600, "letter-spacing": ".3", fill: s.hl ? "var(--route)" : "var(--muted)",
    stroke: "var(--paper)", "stroke-width": 5, "stroke-linejoin": "round", "paint-order": "stroke" }, base);
  t.textContent = s.name;
});
// compass + scale bar
const [VX, VY, VW, VH] = "__VB__".split(" ").map(Number);
const comp = el("g", { transform: `translate(${VX + VW - 70} ${VY + 80})` }, base);
el("path", { d: "M0 -38 L11 0 L0 -8 L-11 0 Z", fill: "var(--ink)" }, comp);
const nT = el("text", { x: 0, y: 24, "text-anchor": "middle", "font-family": "Cormorant Garamond, serif", "font-size": 24, "font-weight": 600, fill: "var(--ink)" }, comp);
nT.textContent = "N";
const sc = el("g", { transform: `translate(${VX + VW - 60 - BASE.scale} ${VY + VH - 40})` }, base);
el("rect", { x: 0, y: 0, width: BASE.scale / 2, height: 8, fill: "var(--ink)" }, sc);
el("rect", { x: BASE.scale / 2, y: 0, width: BASE.scale / 2, height: 8, fill: "var(--paper)", stroke: "var(--ink)", "stroke-width": 1.5 }, sc);
[["0", 0], ["250", BASE.scale / 2], ["500 m", BASE.scale]].forEach(([t, x]) => {
  const tt = el("text", { x, y: -8, "text-anchor": x === BASE.scale ? "start" : "middle", "font-family": "Noto Sans TC, sans-serif", "font-size": 15, fill: "var(--muted)" }, sc);
  tt.textContent = t;
});

/* ---- Spots ---- */
/* ---- 立體地標: paper-cut landmarks standing on their pins (base of the drawing = the pin) ---- */
const ICON_SCALE = { pantheon: 0.85, trevi: 1.0, spagna: 1.0 };   // smaller where the map is crowded (keep in step with ICON_BOX in gen.py)
const ICONS = {
  colosseo: g => {
    el("ellipse", { class: "lm-shadow", cx: 4, cy: 1, rx: 38, ry: 7 }, g);
    const body = "M-34 0 L-34 -45 Q-34 -49 -30 -49 L3 -49 L9 -43 L15 -41 L19 -35 L27 -33 L34 -30 L34 0 Z";
    el("path", { class: "lm-depth", d: body, transform: "translate(3.5 3)" }, g);
    el("path", { class: "lm-stone", d: body }, g);
    // storeys
    [[-15, 34], [-29, 34], [-41, 3]].forEach(([y, x1]) => el("path", { class: "lm-band", d: `M-34 ${y} H${x1}` }, g));
    // arches: three rows, the top one only on the tall (left) side
    for (let x = -30; x <= 26; x += 9.2) el("rect", { class: "lm-hole", x, y: -12.5, width: 5.2, height: 10.5, rx: 2.6 }, g);
    for (let x = -30; x <= 26; x += 9.2) el("rect", { class: "lm-hole", x, y: -26.5, width: 5.2, height: 9.5, rx: 2.6 }, g);
    for (let x = -30; x <= -3; x += 9.2) el("rect", { class: "lm-hole", x, y: -39, width: 5.2, height: 8, rx: 2.6 }, g);
    for (let x = -29; x <= 0; x += 7) el("rect", { class: "lm-hole", x, y: -47, width: 3, height: 3.5, rx: .8 }, g);
  },
  pantheon: g => {
    el("ellipse", { class: "lm-shadow", cx: 4, cy: 1, rx: 36, ry: 7 }, g);
    const out = "M-31 0 L-31 -34 L-27 -34 A27 20 0 0 1 27 -34 L31 -34 L31 0 Z";
    el("path", { class: "lm-depth", d: out, transform: "translate(3.5 3)" }, g);
    el("path", { class: "lm-mid", d: "M-27 -34 A27 20 0 0 1 27 -34 Z" }, g);              // dome
    el("rect", { class: "lm-hole", x: -3, y: -56, width: 6, height: 3, rx: 1 }, g);           // oculus ring
    el("rect", { class: "lm-stone", x: -31, y: -36, width: 62, height: 36 }, g);              // rotunda
    el("rect", { class: "lm-hole", x: -22, y: -26, width: 44, height: 23 }, g);               // portico shade
    for (let i = 0; i < 8; i++) el("rect", { class: "lm-light", x: -22 + i * 6.05, y: -26, width: 3.4, height: 23 }, g);   // columns
    el("rect", { class: "lm-light", x: -25, y: -30, width: 50, height: 4.5 }, g);               // entablature
    el("path", { class: "lm-light", d: "M-26 -30 L0 -43 L26 -30 Z" }, g);                     // pediment
    el("path", { class: "lm-band", d: "M-19 -32 L0 -40.5 L19 -32" }, g);
    el("rect", { class: "lm-light", x: -26, y: -3.5, width: 52, height: 3.5 }, g);             // steps
  },
  trevi: g => {
    el("ellipse", { class: "lm-shadow", cx: 4, cy: 2, rx: 39, ry: 7 }, g);
    const out = "M-34 -6 L-34 -48 L34 -48 L34 -6 Z";
    el("path", { class: "lm-depth", d: out, transform: "translate(3.5 3)" }, g);
    el("path", { class: "lm-light", d: out }, g);                                               // palazzo facade
    el("rect", { class: "lm-mid", x: -34, y: -48, width: 68, height: 5 }, g);                   // attic cornice
    [-30, -22, 18, 26].forEach(x => el("rect", { class: "lm-hole", x, y: -38, width: 4, height: 7, rx: 1 }, g));   // windows
    [-30, -22, 18, 26].forEach(x => el("rect", { class: "lm-hole", x, y: -26, width: 4, height: 7, rx: 1 }, g));
    el("rect", { class: "lm-stone", x: -12, y: -46, width: 24, height: 34 }, g);                // triumphal arch
    el("path", { class: "lm-hole", d: "M-6.5 -14 L-6.5 -33 A6.5 6.5 0 0 1 6.5 -33 L6.5 -14 Z" }, g);   // central niche
    el("circle", { class: "lm-statue", cx: 0, cy: -30.5, r: 2.2 }, g);                          // Oceanus
    el("path", { class: "lm-statue", d: "M-3 -16 L-2.5 -27.5 L2.5 -27.5 L3 -16 Z" }, g);
    [-11, -8.5, 7, 9.5].forEach(x => el("rect", { class: "lm-mid", x, y: -44, width: 1.6, height: 30 }, g));       // columns
    el("path", { class: "lm-mid", d: "M-27 -6 Q-22 -16 -14 -13 Q-8 -19 0 -14 Q8 -19 14 -13 Q22 -16 27 -6 Z" }, g);   // rocks
    el("path", { class: "lm-water", d: "M-37 -6 H37 Q37 1 30 2 H-30 Q-37 1 -37 -6 Z" }, g);     // basin
    el("path", { class: "lm-wave", d: "M-26 -2.5 q3 -2 6 0 t6 0 t6 0 M6 -2.5 q3 -2 6 0 t6 0 t6 0" }, g);
    el("path", { class: "lm-water", d: "M-3 -14 Q-6 -9 -9 -6 H9 Q6 -9 3 -14 Z" }, g);         // cascade
  },
  spagna: g => {
    el("ellipse", { class: "lm-shadow", cx: 4, cy: 1, rx: 36, ry: 7 }, g);
    const out = "M-31 0 L-12 -34 L-16 -34 L-16 -58 L-10 -58 L-10 -52 L10 -52 L10 -58 L16 -58 L16 -34 L12 -34 L31 0 Z";
    el("path", { class: "lm-depth", d: out, transform: "translate(3.5 3)" }, g);
    // Trinità dei Monti: facade + two bell towers
    el("rect", { class: "lm-light", x: -16, y: -50, width: 32, height: 17 }, g);
    el("path", { class: "lm-light", d: "M-10 -50 L0 -56 L10 -50 Z" }, g);
    [-16, 10].forEach(x => { el("rect", { class: "lm-light", x, y: -60, width: 6, height: 27 }, g); el("path", { class: "lm-mid", d: `M${x} -60 Q${x + 3} -66 ${x + 6} -60 Z` }, g); el("rect", { class: "lm-hole", x: x + 1.8, y: -56, width: 2.4, height: 4, rx: 1.2 }, g); });
    el("path", { class: "lm-hole", d: "M-3 -33 L-3 -41 A3 3 0 0 1 3 -41 L3 -33 Z" }, g);
    // the steps fanning out down the hill
    const steps = 7;
    for (let i = 0; i < steps; i++) {
      const y0 = -33 + i * 4.7, y1 = y0 + 4.7, w0 = 12 + i * 2.7, w1 = 12 + (i + 1) * 2.7;
      el("path", { class: i % 2 ? "lm-mid" : "lm-stone", d: `M${-w0} ${y0} L${w0} ${y0} L${w1} ${y1} L${-w1} ${y1} Z` }, g);
    }
    el("path", { class: "lm-band", d: "M0 -33 V0" }, g);                                         // central balustrade
  }
};
const layer = document.getElementById("spots");
const areaLayer = areaBase;
const syncArea = () => SPOTS.forEach(s => { if (s.areaEl) s.areaEl.classList.toggle("dim", s.g.classList.contains("dim")); });
SPOTS.forEach(s => {
  const allDay = s.cat === "open" || s.cat === "base";
  const g = el("g", { class: "spot", tabindex: 0, role: "button", "data-id": s.id, "data-cat": s.cat,
    "aria-label": allDay ? `${s.name}，${s.sPrice}` : `${s.name}，${s.sHours}，適合 ${s.sTime}，${s.sMass ? "彌撒 " + s.sMass + "，" : ""}${s.sPrice}`, style: `--c:${CAT[s.cat].color}` }, layer);
  if (s.areaPts) {
    s.areaEl = el("g", { class: "area", style: `--c:${CAT[s.cat].color}` }, areaLayer);
    el("polygon", { points: pts(s.areaPts) }, s.areaEl);
  }
  const leader = el("path", { class: "leader" }, g);
  const tab = el("rect", { class: "tab", x: s.lx, y: s.ly, rx: 4 }, g);
  const t1 = el("text", { class: "t-name", x: s.lx + 13, y: s.ly + 36 }, g); t1.textContent = s.mapName || s.name;
  // small lines from gen.py: hours (not for all-day places), mass, price (left out when free); no stars on the map
  const smalls = (s.mapLines || []).map((txt, i) => {
    const cls = txt.startsWith("彌撒 ") ? "t-mass" : (i === (s.mapLines.length - 1) && txt === s.sPrice) ? "t-price" : "t-wed";
    const t = el("text", { class: cls + " t-more", x: s.lx + 13, y: s.ly + 68 + 30 * i }, g); t.textContent = txt; return t;
  });
  if (s.week) { s.hoursEl = smalls.find(t => t.textContent === s.sHours) || null; s.hours0 = s.sHours; s.hours2El = s.sHours2 ? smalls.find(t => t.textContent === s.sHours2) || null : null; }
  const tw = null, t2 = null, tm = null, t3 = null;
  if (s.cat === "base") el("rect", { class: "pin", x: s.x - 12, y: s.y - 12, width: 24, height: 24, rx: 3 }, g);
  else if (ICONS[s.id]) { el("circle", { class: "pin icon-base", cx: s.x, cy: s.y, r: 6 }, g); ICONS[s.id](el("g", { class: "lm", transform: `translate(${s.x} ${s.y - 4}) scale(${ICON_SCALE[s.id] || 1.3})` }, g)); }
  else el("circle", { class: "pin", cx: s.x, cy: s.y, r: 12 }, g);
  if (s.sup) g.classList.add("is-sup");
  if (s.rush) {   // 要搶票: thicker frame + a red 搶票 tag on the label corner
    g.classList.add("rush");
    s.rushTag = el("g", { class: "rush-tag", "aria-hidden": "true" }, g);
    el("rect", { width: 58, height: 26, rx: 13 }, s.rushTag);
    el("text", { x: 29, y: 18.5, "text-anchor": "middle" }, s.rushTag).textContent = "⚡搶票";
  }
  s.g = g; s.tab = tab; s.leader = leader; s.t1 = t1; s.texts = [t1, ...smalls]; s.H0 = smalls.length ? 68 + 30 * (smalls.length - 1) + 14 : 50;   // same rule as gen.py
  s.texts.forEach(t => { t._dy = +t.getAttribute("y") - s.ly; });   // so the label can move between layouts
  const act = () => distMode ? pickSpot(s.id) : openSpot(s.id);
  g.addEventListener("click", e => { e.stopPropagation(); act(); });
  g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); act(); } });
});
let distMode = false;
function sizeTabs() {
  const slim = distMode || !!window.NAME_ONLY;
  document.querySelectorAll(".soft-street").forEach(t => t.style.display = slim ? "none" : "");
  // 附加景點 or City Walk on → the full layout (ux/uy); otherwise the roomier main-only layout (lx/ly)
  const supBtn = document.getElementById("f-sup");
  const full = !window.SHOP_ON && ((supBtn && supBtn.getAttribute("aria-pressed") === "true") || !!window.ROUTE_ON);   // 購物 view sits on the default layout
  SPOTS.forEach(s => {
    const shopV = !!window.SHOP_ON && s.shx != null;   // 購物 view: its own layout, name-only labels
    const bx = shopV ? s.shx : full && s.ux != null ? s.ux : s.lx, by = shopV ? s.shy : full && s.uy != null ? s.uy : s.ly;
    const namesV = !!window.NAME_ONLY && !distMode && s.nx != null;   // 簡潔模式: its own name-only layout, next to the pins
    const lx = shopV ? bx : namesV ? s.nx : slim ? s.slx : bx, ly = shopV ? by : namesV ? s.ny : slim ? s.sly : by;
    if (!slim) s.texts.forEach(t => { t.setAttribute("x", lx + 13); t.setAttribute("y", ly + t._dy); });
    const sl = slim || !!s.compact || (shopV && s.cat !== "base");   // compact spots show only their name in every mode
    const mid = !sl && !!s.mid;         // 推薦: name + hours + price only
    const H = sl ? 44 : mid ? (s.texts.length > 1 ? 55 + 22 * (s.texts.length - 2) + 11 : 44) : s.H0;
    s.g.classList.toggle("mid", mid);
    s.g.classList.toggle("shopbox", shopV && !s.shopStreet);
    const midShown = mid ? s.texts : null;
    const shown = sl ? [s.t1] : mid ? midShown : s.texts;
    if (!mid) s.texts.slice(1).forEach(t => t.style.display = (s.compact || (shopV && s.cat !== "base")) ? "none" : "");
    if (mid) s.texts.forEach(t => {
      t.style.display = midShown.includes(t) ? "" : "none";
      t.setAttribute("x", lx + 11);
      const k = s.texts.indexOf(t); if (k > 0) t.setAttribute("y", ly + 55 + 22 * (k - 1));
    });
    let w = 0;
    shown.forEach(t => { try { w = Math.max(w, t.getComputedTextLength()); } catch (e) { w = Math.max(w, 200); } });
    if (!w) w = 200;
    const W = w + (sl ? 24 : mid ? 22 : 26);
    s.tab.setAttribute("x", lx); s.tab.setAttribute("y", ly);
    s.tab.setAttribute("width", W); s.tab.setAttribute("height", H);
    s.t1.setAttribute("x", lx + (sl ? 12 : mid ? 11 : 13)); s.t1.setAttribute("y", ly + (sl ? 31 : mid ? 31 : 36));
    const cx = Math.max(lx, Math.min(s.x, lx + W));
    const cy = Math.max(ly, Math.min(s.y, ly + H));
    s.leader.setAttribute("d", `M${s.x} ${s.y} L${cx} ${cy}`);
    if (s.rushTag) s.rushTag.setAttribute("transform", `translate(${lx + W - 50} ${ly - 14})`);
  });
}
sizeTabs();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(sizeTabs);

/* ---- Distance mode ---- */
const edgeLayer = document.getElementById("edges");
EDGES.forEach(e => {
  const g = el("g", { class: "edge" }, edgeLayer);
  el("line", { x1: e.a[0], y1: e.a[1], x2: e.b[0], y2: e.b[1] }, g);
  if (e.box) {
    const cx = (e.box[0] + e.box[2]) / 2, cy = (e.box[1] + e.box[3]) / 2;
    if (Math.hypot(cx - e.anc[0], cy - e.anc[1]) > 20) el("line", { class: "conn", x1: e.anc[0], y1: e.anc[1], x2: cx, y2: cy }, g);
    el("rect", { x: e.box[0], y: e.box[1], width: e.box[2] - e.box[0], height: e.box[3] - e.box[1], rx: 15 }, g);
    const t = el("text", { x: cx, y: cy + 7, "text-anchor": "middle" }, g); t.textContent = e.text;
  }
  e.g = g;
});
const svg = document.getElementById("map");
document.getElementById("f-dist").addEventListener("click", ev => {
  distMode = !distMode;
  ev.currentTarget.setAttribute("aria-pressed", distMode);
  svg.classList.toggle("dist", distMode);
  edgeLayer.toggleAttribute("hidden", !distMode);
  document.getElementById("dist-note").hidden = !distMode;
  pickSpot(null);
  sizeTabs();
});
let picked = null, pairEnd = null, sub = "p2p";
const M_PER_UNIT = 2.2;
const NOTES = { p2p: "先點起點，會顯示它到相鄰景點的距離；再點終點，就畫出兩點之間的距離與步行時間。點空白處重新選。", all: "顯示所有相鄰景點之間的步行距離與時間。" }, NOTE_TAIL = "步行距離以直線距離 ×1.3 估算，步速每分鐘 80 公尺；實際路線請以 Google 地圖導航為準。";
const p2pLine = el("g", {}); svg.insertBefore(p2pLine, document.getElementById("spots"));
const p2pLabel = el("g", { class: "p2p-lbl" }, svg);
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
  const t = el("text", { class: "p2p-text", x: cx, y: cy + 9.4, "text-anchor": "middle" }, p2pLabel);
  const wt = walkText(Math.hypot(b.x - a.x, b.y - a.y));
  t.textContent = a.name + " → " + b.name + "　" + wt;
  document.getElementById("p2p-route").textContent = a.name + " → " + b.name;
  document.getElementById("p2p-dist").innerHTML = wt.replace("・", " ・ ") + "<small>步行估算</small>";
  let w = 300; try { w = t.getComputedTextLength() + 32; } catch (e) {}
  pill.setAttribute("x", cx - w / 2); pill.setAttribute("y", cy - 44 / 2);
  pill.setAttribute("width", w); pill.setAttribute("height", 44); pill.setAttribute("rx", 44 / 2);
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
svg.addEventListener("click", () => { if (distMode && sub === "p2p" && picked) pickSpot(null); });
const syncEdges = () => EDGES.forEach(e => e.g.classList.toggle("dim", e.ids.some(id => SPOTS.find(s => s.id === id).g.classList.contains("dim"))));

/* ---- Filters: tier (主要／推薦／次要) hides, type (需購票／免費) and 冷門時段 dim ---- */
const pressed = el => el.getAttribute("aria-pressed") === "true";
function applySup() {
  const tiers = new Set([...document.querySelectorAll(".chip[data-tier]")].filter(pressed).map(c => c.dataset.tier));
  const cats = new Set([...document.querySelectorAll(".chip[data-cat]")].filter(pressed).map(c => c.dataset.cat));
  if (!cats.size) ["paid", "free"].forEach(c => cats.add(c));   // nothing picked = no type filter
  if (cats.has("free")) cats.add("open");   // 免費 covers the free squares and streets too
  const cold = pressed(document.getElementById("f-cold"));
  const shopOn = window.SHOP_ON = pressed(document.getElementById("f-shop"));   // 購物: 主要／推薦 boxes stay, shop boxes join them
  document.querySelectorAll("#f-sup, .chip[data-cat], #f-cold").forEach(c => c.classList.toggle("muted", shopOn));
  document.querySelectorAll(".base-street").forEach(t => t.style.display = shopOn ? "none" : "");   // shop view shows its own street names
  SPOTS.forEach(s => {
    const gone = shopOn ? (s.cat !== "base" && !(s.shx != null && !s.shopStreet) && (s.sup || !!s.shopStreet || (!!s.tier && !tiers.has(s.tier)))) : (!!s.tier && !tiers.has(s.tier));
    s.g.classList.toggle("gone", gone); if (s.areaEl) s.areaEl.classList.toggle("gone", gone);
    s.g.classList.toggle("dim", !shopOn && s.cat !== "base" && (!cats.has(s.cat) || (cold && !s.cold) || !!s.dayClosed));
  });
  EDGES.forEach(e => e.g.classList.toggle("hide-s", e.ids.some(id => SPOTS.find(s => s.id === id).g.classList.contains("gone"))));
  if (picked && SPOTS.find(s => s.id === picked).g.classList.contains("gone")) pickSpot(null);
  if (pairEnd && SPOTS.find(s => s.id === pairEnd).g.classList.contains("gone")) pickSpot(null);
  syncArea(); syncEdges(); sizeTabs();
  if (RAD && RAD.id) renderRad();
}
document.querySelectorAll(".shop-btn").forEach(b => b.addEventListener("click", () => {
  const on = !pressed(b); document.querySelectorAll(".shop-btn").forEach(x => x.setAttribute("aria-pressed", on)); applySup();
}));
/* ---- 我去的日子: pick weekdays (multi), labels show only those days' hours; spots closed on all of them fade ---- */
const DKEY = "trip-days-rome", DAYS = [...document.querySelectorAll(".chip.day")], DN = "一二三四五六日";
try { const sv = JSON.parse(localStorage.getItem(DKEY) || "null"); if (Array.isArray(sv) && sv.length) DAYS.forEach(b => b.setAttribute("aria-pressed", sv.includes(+b.dataset.day) ? "true" : "false")); } catch (e) {}
function dayRuns(ds) {   // [0,1,2,4] → "週一至三、五"; [4,5] → "週五六"; [0,6] → "週一、日" (週 so 一 doesn't read as a dash)
  const runs = []; ds.forEach(d => { const r = runs[runs.length - 1]; if (r && d === r[1] + 1) r[1] = d; else runs.push([d, d]); });
  return "週" + runs.map(r => r[1] - r[0] >= 2 ? DN[r[0]] + "至" + DN[r[1]] : DN.slice(r[0], r[1] + 1)).join("、");
}
function weekLabel(wk, sel) {
  const groups = [];
  sel.forEach(d => { const v = wk.d[d]; const g = groups.find(x => x.v === v); if (g) g.days.push(d); else groups.push({ v, days: [d] }); });
  const open = groups.filter(g => g.v), closed = groups.filter(g => !g.v).flatMap(g => g.days);
  if (!open.length) return null;
  if (open.length === 1 && !closed.length) return wk.p + open[0].v;
  const parts = open.map(g => ({ d: g.days[0], t: dayRuns(g.days) + " " + g.v }));
  if (closed.length) parts.push({ d: closed[0], t: dayRuns(closed) + "休" });
  return wk.p + parts.sort((a, b) => a.d - b.d).map(x => x.t).join("｜");   // in weekday order
}
function twoLines(lbl, sel) {   // a two-line label: split the parts; one part → the time, then which days it is for
  const parts = lbl.split("｜");
  if (parts.length === 1) return [lbl, "（" + dayRuns(sel) + "）"];
  const k = Math.ceil(parts.length / 2); return [parts.slice(0, k).join("｜"), parts.slice(k).join("｜")];
}
/* every day picked: one main time + the exceptions in brackets, e.g. 「09:00–19:00（週一休）」「收費 09:00–22:00（週一、五 11:30 起）」 */
const _tm = v => { const m = String(v).match(/^\d{2}:\d{2}–\d{2}:\d{2}(、\d{2}:\d{2}–\d{2}:\d{2})*$/); return m ? v.split("、").flatMap(x => x.split("–")) : null; };
function exceptionText(main, v) {
  if (!v) return "休";
  const a = _tm(main), b = _tm(v);
  const sp = t => (/^\d/.test(t) ? " " : "") + t;   // a space only before a time
  if (!a || !b || a.length !== b.length) return sp(v);
  const diff = a.map((x, i) => x !== b[i] ? i : -1).filter(i => i >= 0), last = a.length - 1;
  if (diff.length === 1 && diff[0] === 0) return " " + b[0] + " 起";
  if (diff.length === 1 && diff[0] === last) return "到 " + b[last];
  if (a.length === 4 && diff.every(i => i === 1 || i === 2)) return diff.length === 2 ? "午休 " + b[1] + "–" + b[2] : diff[0] === 1 ? " " + b[1] + " 起午休" : "午休到 " + b[2];
  return sp(v);
}
function compactLabel(vals, prefix) {   // vals: the 7 day values, Monday first
  const groups = [];
  vals.forEach((v, d) => { const g = groups.find(x => x.v === v); if (g) g.days.push(d); else groups.push({ v, days: [d] }); });
  const open = groups.filter(g => g.v);
  if (!open.length) return null;
  const score = g => g.days.length * 2 + (_tm(g.v) ? 1 : 0);   // most days wins; on a tie prefer a real time
  const main = open.reduce((m, g) => score(g) > score(m) ? g : m, open[0]);
  const ex = groups.filter(g => g !== main).sort((x, y) => x.days[0] - y.days[0]);
  const merged = [];   // same note on several days → one entry (週六日時間不同)
  ex.forEach(g => { let t = exceptionText(main.v, g.v); if (t.length > 16) t = "時間不同"; const m = merged.find(x => x.t === t); if (m) m.days.push(...g.days); else merged.push({ t, days: [...g.days] }); });
  return prefix + main.v + (merged.length ? "（" + merged.map(x => dayRuns(x.days.sort((p, q) => p - q)) + x.t).join("；") + "）" : "");
}
function applyDays() {
  let sel = DAYS.filter(pressed).map(b => +b.dataset.day);
  const full = !sel.length || sel.length === 7;
  SPOTS.forEach(s => {
    s.dayClosed = false;
    if (!s.week || !s.hoursEl) return;
    const lbl = full ? s.hours0 : weekLabel(s.week, sel);   // full week: gen.py already wrote main time + exceptions
    const closed = lbl === null;
    s.dayClosed = closed && !s.week.nodim;
    let lines;
    if (s.hours2El) lines = full ? [s.hours0, s.sHours2] : closed ? ["你選的日子休館", "（" + dayRuns(sel) + "）"] : twoLines(lbl, sel);
    else lines = [closed ? "你選的日子休館" : lbl];
    [s.hoursEl, s.hours2El].forEach((t, i) => {
      if (!t) return;
      t.textContent = lines[i] || "";
      t.classList.toggle("day-off", closed && i === 0);
      t.style.fontSize = ""; t.removeAttribute("textLength"); t.removeAttribute("lengthAdjust");
      // keep the box the size the layout planned for: shrink the line instead of widening the box
      const lim = (s.W || 300) - 26;
      try {
        const w = t.getComputedTextLength();
        if (w > lim && w > 0) {
          const k = Math.max(.7, lim / w); t.style.fontSize = (parseFloat(getComputedStyle(t).fontSize) * k) + "px";
          if (w * k > lim + 1) { t.setAttribute("textLength", lim); t.setAttribute("lengthAdjust", "spacingAndGlyphs"); }
        }
      } catch (e) {}
    });
  });
}
DAYS.forEach(b => b.addEventListener("click", () => {
  b.setAttribute("aria-pressed", pressed(b) ? "false" : "true");
  try { localStorage.setItem(DKEY, JSON.stringify(DAYS.filter(pressed).map(x => +x.dataset.day))); } catch (e) {}
  applyDays(); applySup();
}));
applyDays();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { applyDays(); sizeTabs(); });
/* remember the filter chips from the last visit (this device's browser) */
const FKEY = "trip-filters-rome", FCHIPS = [...document.querySelectorAll(".chip[data-tier], .chip[data-cat], #f-cold")];
const chipKey = ch => ch.id || ch.dataset.tier || ch.dataset.cat;
try { const saved = JSON.parse(localStorage.getItem(FKEY) || "null"); if (saved) FCHIPS.forEach(ch => { const k = chipKey(ch); if (k in saved) ch.setAttribute("aria-pressed", saved[k] ? "true" : "false"); }); } catch (e) {}
const saveFilters = () => { try { localStorage.setItem(FKEY, JSON.stringify(Object.fromEntries(FCHIPS.map(ch => [chipKey(ch), pressed(ch)])))); } catch (e) {} };
FCHIPS.forEach(ch => ch.addEventListener("click", () => {
  ch.setAttribute("aria-pressed", pressed(ch) ? "false" : "true"); saveFilters(); applySup();
}));
applySup();

/* ---- 長按範圍模式: long-press a spot → spots within 100 m; long-press it again → +100 m; double-tap the map background to close ---- */
var RAD = { id: null, r: 0, closedAt: 0 };
const radLayer = el("g", {}); document.getElementById("map").insertBefore(radLayer, document.getElementById("spots"));
const radCard = document.getElementById("rad-card");
function renderRad() {
  radLayer.replaceChildren();
  SPOTS.forEach(s => { s.g.classList.remove("rad-out", "rad-center"); if (s.areaEl) s.areaEl.classList.remove("rad-out"); });
  radCard.hidden = !RAD.id;
  if (!RAD.id) return;
  const c = SPOTS.find(s => s.id === RAD.id), ru = RAD.r / M_PER_UNIT;
  for (let k = 100; k < RAD.r; k += 100) el("circle", { class: "rad-ring", cx: c.x, cy: c.y, r: k / M_PER_UNIT }, radLayer);
  el("circle", { class: "rad-circle", cx: c.x, cy: c.y, r: ru }, radLayer);
  const near = [];
  SPOTS.forEach(s => {
    if (s.g.classList.contains("gone")) return;
    const m = Math.hypot(s.x - c.x, s.y - c.y) * M_PER_UNIT;
    const inside = Math.round(m / 5) * 5 <= RAD.r;   // 5 m tolerance: pins are approximate
    s.g.classList.toggle("rad-out", !inside); if (s.areaEl) s.areaEl.classList.toggle("rad-out", !inside);
    if (inside && s.id !== c.id && s.cat !== "base") near.push(s);
  });
  c.g.classList.add("rad-center");
  radCard.innerHTML = "";
  const h = document.createElement("div");
  h.innerHTML = `<b></b>　半徑 ${RAD.r} 公尺內 ${near.length} 個景點<button class="rad-x" type="button">關閉</button>`;
  h.querySelector("b").textContent = c.mapName || c.name;
  h.querySelector(".rad-x").addEventListener("click", closeRad);
  const t = document.createElement("div"); t.style.color = "var(--muted)"; t.style.fontSize = "12px";
  t.textContent = "再長按一次（電腦：在景點上點兩下）擴大 100 公尺；點一下地圖空白處關閉（直線距離）";
  radCard.append(h, t);
  placeRadCard(c);
}
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

function closeRad() { if (!RAD.id) return; RAD.id = null; RAD.r = 0; RAD.closedAt = performance.now(); renderRad(); }
(() => {
  const spotsEl = document.getElementById("spots");
  let timer = null, start = null, fired = 0;
  const cancel = () => { clearTimeout(timer); timer = null; };
  spotsEl.addEventListener("pointerdown", e => {
    const g = e.target.closest(".spot"); if (!g || (e.pointerType === "mouse" && e.button !== 0)) return;
    cancel(); start = { x: e.clientX, y: e.clientY };
    timer = setTimeout(() => {
      timer = null; fired = performance.now();
      const id = g.dataset.id;
      if (RAD.id === id) RAD.r += 100; else { RAD.id = id; RAD.r = 100; }
      if (navigator.vibrate) try { navigator.vibrate(15); } catch (_) {}
      renderRad();
    }, 550);
  });
  window.addEventListener("pointermove", e => { if (timer && start && Math.hypot(e.clientX - start.x, e.clientY - start.y) > 10) cancel(); });
  window.addEventListener("pointerup", cancel); window.addEventListener("pointercancel", cancel);
  spotsEl.addEventListener("contextmenu", e => { if (e.target.closest(".spot")) e.preventDefault(); });
  // the click that ends a long press must not open the drawer
  spotsEl.addEventListener("click", e => { if (performance.now() - fired < 700) { e.stopPropagation(); e.preventDefault(); } }, true);
  // a tap on the map background closes it (a drag to pan does not)
  const svg = document.getElementById("map");
  svg.addEventListener("click", e => {
    if (!RAD.id || e.target.closest(".spot, .route-pill, .route-hit, .shop-street-label, #shop-street-labels")) return;
    closeRad();   // one tap on the map background closes it
  });
})();
/* ---- 電腦：在景點上點兩下 = 長按（畫出 / 擴大 100 公尺範圍）；點一下照常開介紹（等 0.25 秒確定不是點兩下） ---- */
(() => {
  const spotsEl = document.getElementById("spots");
  let lastType = "mouse", pend = null, bypass = false;
  spotsEl.addEventListener("pointerdown", e => { lastType = e.pointerType || "mouse"; }, true);
  spotsEl.addEventListener("click", e => {
    if (bypass || lastType !== "mouse" || (typeof distMode !== "undefined" && distMode)) return;
    const g = e.target.closest(".spot"); if (!g) return;
    e.stopPropagation(); e.preventDefault();
    if (pend && pend.g === g) {   // second click on the same spot
      clearTimeout(pend.t); pend = null;
      const id = g.dataset.id;
      if (RAD.id === id) RAD.r += 100; else { RAD.id = id; RAD.r = 100; }
      renderRad(); return;
    }
    if (pend) clearTimeout(pend.t);
    pend = { g, t: setTimeout(() => { pend = null; bypass = true; g.dispatchEvent(new MouseEvent("click", { bubbles: true })); bypass = false; }, 260) };
  }, true);
})();


/* ---- Mobile pinch zoom ---- */
const mapView = (() => {
  const svg = document.getElementById("map");
  const b = svg.viewBox.baseVal;
  const full = { x: b.x, y: b.y, w: b.width, h: b.height };
  const mq = window.matchMedia("(max-width: 1240px)");
  const PXU = 0.36;            // px per map unit when the map first opens on a phone
  const HOME = "hotel";       // spot id to centre on, or null for the map centre
  let vb = { ...full }, raf = 0;
  const ratio = () => { const r = svg.getBoundingClientRect(); return mq.matches && r.width ? r.height / r.width : full.h / full.w; };
  const maxW = () => Math.max(full.w, full.h / ratio());
  const clampW = w => Math.min(maxW(), Math.max(full.w / 10, w));
  const axis = (p, size, lo, span) => size >= span ? lo + (span - size) / 2 : Math.min(lo + span - size, Math.max(lo, p));
  const clamp = () => {
    vb.w = clampW(vb.w); vb.h = vb.w * ratio();
    vb.x = axis(vb.x, vb.w, full.x, full.w); vb.y = axis(vb.y, vb.h, full.y, full.h);
  };
  const apply = () => { svg.setAttribute("viewBox", `${vb.x} ${vb.y} ${vb.w} ${vb.h}`); svg.parentElement.classList.toggle("zoomed", vb.w < full.w - 1); };
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
    if (!mq.matches && (e.pointerType !== "mouse" || e.button !== 0 || vb.w >= full.w - 1)) return;
    if (e.pointerType === "mouse") e.preventDefault();
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
  const atCursor = e => { const r = svg.getBoundingClientRect(); return [vb.x + (e.clientX - r.left) / r.width * vb.w, vb.y + (e.clientY - r.top) / r.height * vb.h]; };
  svg.addEventListener("wheel", e => {
    if (!(e.ctrlKey || e.metaKey)) return;   // plain wheel keeps scrolling the page
    e.preventDefault(); cancelAnimationFrame(raf);
    zoomAt(Math.exp(-e.deltaY * (e.deltaMode === 1 ? 0.05 : 0.0025)), ...atCursor(e));
  }, { passive: false });
  svg.addEventListener("dblclick", e => {
    if (e.target.closest(".spot, .route-pill, .route-hit")) return;
    if (RAD && (RAD.id || performance.now() - RAD.closedAt < 600)) { e.preventDefault(); return; }
    e.preventDefault(); cancelAnimationFrame(raf); zoomAt(1.8, ...atCursor(e));
  });
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
  const refresh = () => { const [cx, cy] = mid(); set(cx, cy, vb.w); apply(); };
  return { fit, home, mq, refresh };
})();
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
  const rMain = document.getElementById("f-route"), rMirror = document.getElementById("fs-route-btn");
  if (rMain && rMirror) {
    rMirror.addEventListener("click", () => rMain.click());
    new MutationObserver(() => rMirror.setAttribute("aria-pressed", rMain.getAttribute("aria-pressed"))).observe(rMain, { attributes: true, attributeFilter: ["aria-pressed"] });
  }
})();




/* ---- Visited ---- */
const VKEY = "trip-visited-rome";
let visited = new Set();
try { visited = new Set(JSON.parse(localStorage.getItem(VKEY) || "[]")); } catch (e) {}
let showDone = false;
const saveVisited = () => { try { localStorage.setItem(VKEY, JSON.stringify([...visited])); } catch (e) {} };
function applyVisited() {
  const hid = id => visited.has(id) && !showDone;
  SPOTS.forEach(s => {
    s.g.classList.toggle("visited", visited.has(s.id));
    s.g.classList.toggle("hide-v", hid(s.id));
    if (s.areaEl) s.areaEl.classList.toggle("hide-v", hid(s.id));
  });
  EDGES.forEach(e => e.g.classList.toggle("hide-v", e.ids.some(hid)));
  const n = visited.size, chip = document.getElementById("f-done");
  if (n === 0) showDone = false;
  chip.hidden = n === 0;
  document.getElementById("done-n").textContent = n;
  chip.setAttribute("aria-pressed", showDone);
}
document.getElementById("f-done").addEventListener("click", () => { showDone = !showDone; applyVisited(); });
applyVisited();

/* ---- City Walk ---- */
const routeLayer = document.getElementById("routes");
let routeOn = false;
ROUTES.forEach(r => {
  const d = "M" + r.pts.map(p => p.join(" ")).join(" L");
  const g = el("g", {}, routeLayer); r.g = g;
  if (r.color) g.style.setProperty("--route", `var(--route-${r.color})`);   // themed walks (貝尼尼／卡拉瓦喬) get their own colour
  el("path", { class: "route-line", d }, g);
  [[r.pts[0], "起"], [r.pts[r.pts.length - 1], "終"]].forEach(([p, t]) => {
    el("circle", { class: "route-end", cx: p[0], cy: p[1] - 34, r: 17 }, g);
    const tt = el("text", { class: "route-end-t", x: p[0], y: p[1] - 27, "text-anchor": "middle" }, g); tt.textContent = t;
  });
  const hit = el("path", { class: "route-hit", d }, g);
  hit.addEventListener("click", e => { e.stopPropagation(); openRoute(r.id); });
  (r.marks || []).forEach(m => {
    // SVG <a> links don't open reliably inside the artifact viewer, so the badge clicks a real HTML link instead
    const mg = el("g", { class: "route-mark", role: "link", tabindex: 0, "aria-label": m.n + " " + m.name + "（Google 地圖）" }, g);
    const go = e => { e.stopPropagation(); openExternal("https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(m.q)); };
    mg.addEventListener("click", go);
    mg.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(e); } });
    const tt = el("title", {}, mg); tt.textContent = m.n + " " + m.name;
    el("circle", { cx: m.x, cy: m.y, r: 16 }, mg);
    const mt = el("text", { x: m.x, y: m.y + 7, "text-anchor": "middle" }, mg); mt.textContent = m.n;
  });
  const pill = el("g", { class: "route-pill", role: "button", tabindex: 0, "aria-label": r.name + " " + r.label.text }, g);
  r.pillRect = el("rect", { rx: 22, height: 44 }, pill);
  r.pillText = el("text", { x: r.label.x, y: r.label.y + 8, "text-anchor": "middle" }, pill);
  r.pillText.textContent = r.label.text;
  r.pillHand = el("text", { class: "route-hand", "text-anchor": "middle" }, pill); r.pillHand.textContent = "👆";
  el("title", {}, pill).textContent = "點一下看路線介紹";
  pill.addEventListener("click", e => { e.stopPropagation(); openRoute(r.id); });
  pill.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openRoute(r.id); } });
});
function sizeRoutePills() {
  ROUTES.forEach(r => {
    let w = 260; try { w = r.pillText.getComputedTextLength() + 36 || 260; } catch (e) {}
    r.pillRect.setAttribute("x", r.label.x - w / 2); r.pillRect.setAttribute("y", r.label.y - 22); r.pillRect.setAttribute("width", w);
    // big hand on the bottom-right corner: fingertip on the pill, rest of the hand below it
    r.pillHand.setAttribute("x", r.label.x + w / 2 - 14); r.pillHand.setAttribute("y", r.label.y + 50);
  });
}
/* route picker: show only the walks you want (remembered per browser) */
let routeShow = new Set(ROUTES.map(r => r.id));
try { const v = JSON.parse(localStorage.getItem("routeShow") || "null"); if (Array.isArray(v) && v.length) routeShow = new Set(v.filter(id => ROUTES.some(r => r.id === id))); } catch (e) {}
const pick = document.getElementById("route-pick");
const pickAll = document.createElement("button"); pickAll.type = "button"; pickAll.className = "all"; pickAll.textContent = "全部"; pick.appendChild(pickAll);
ROUTES.forEach(r => {
  const b = document.createElement("button"); b.type = "button"; b.dataset.route = r.id;
  b.textContent = r.tag || r.name.replace("City Walk：", "");
  if (r.color) b.style.setProperty("--rc", `var(--route-${r.color})`);
  b.addEventListener("click", () => {
    // first tap while everything is shown = show only this walk; later taps add / remove
    if (routeShow.size === ROUTES.length) routeShow = new Set([r.id]);
    else if (routeShow.has(r.id)) { routeShow.delete(r.id); if (!routeShow.size) routeShow = new Set(ROUTES.map(x => x.id)); }
    else routeShow.add(r.id);
    saveShow(); applyRoute();
  });
  pick.appendChild(b);
});
pickAll.addEventListener("click", () => { routeShow = new Set(ROUTES.map(x => x.id)); saveShow(); applyRoute(); });
function saveShow() { try { localStorage.setItem("routeShow", JSON.stringify([...routeShow])); } catch (e) {} }
function shownRoutes() { return ROUTES.filter(r => routeShow.has(r.id)); }
function placePick() {
  // in fullscreen the fs-bar sits at the top of the map box, so the picker goes just below it
  const box = pick.closest(".mapbox"), bar = document.getElementById("fs-bar");
  const fs = box && box.classList.contains("fs") && bar && bar.offsetHeight;
  pick.style.top = fs ? (bar.offsetHeight + 6) + "px" : "";
}
if (window.MutationObserver && pick.closest(".mapbox")) new MutationObserver(placePick).observe(pick.closest(".mapbox"), { attributes: true, attributeFilter: ["class"] });
addEventListener("resize", placePick);
function applyRoute() {
  routeLayer.toggleAttribute("hidden", !routeOn);
  if (window.ROUTE_ON !== routeOn) { window.ROUTE_ON = routeOn; sizeTabs(); }
  pick.hidden = !routeOn; placePick();
  const allOn = routeShow.size === ROUTES.length;
  pickAll.setAttribute("aria-pressed", allOn);
  pick.querySelectorAll("button[data-route]").forEach(b => b.setAttribute("aria-pressed", !allOn && routeShow.has(b.dataset.route)));
  ROUTES.forEach(r => r.g.toggleAttribute("hidden", !routeShow.has(r.id)));
  document.getElementById("f-route").setAttribute("aria-pressed", routeOn);
  const card = document.getElementById("route-card");
  card.hidden = true;   // hint now lives on the route pills (hand icon)
  document.getElementById("route-card-name").textContent = "City Walk（" + ROUTES.length + " 條路線）";
  const ids = new Set(routeOn ? shownRoutes().flatMap(r => [...r.stops, ...(r.areas || [])]) : []);
  SPOTS.forEach(s => {
    s.g.classList.toggle("on-route", ids.has(s.id));
    s.g.classList.toggle("off-route", routeOn && !ids.has(s.id));
    if (s.areaEl) s.areaEl.classList.toggle("off-route", routeOn && !ids.has(s.id));
  });
  parkEl.classList.toggle("lit", ids.has("villaborghese"));
  const litAreas = new Set(routeOn ? shownRoutes().flatMap(r => r.areas || []) : []);
  SPOTS.forEach(s => { if (s.areaEl) s.areaEl.classList.toggle("lit", litAreas.has(s.id)); });
  EDGES.forEach(e => e.g.classList.toggle("off-route", routeOn && e.ids.some(id => !ids.has(id))));
  if (routeOn) sizeRoutePills();
}
document.getElementById("f-route").addEventListener("click", () => { routeOn = !routeOn; applyRoute(); });
function openRoute(id) {
  drawer.dataset.spot = ""; drawer.dataset.route = id;
  const r = ROUTES.find(x => x.id === id); if (!r) return;
  lastFocus = document.activeElement;
  SPOTS.forEach(x => x.g.classList.remove("active"));
  drawer.style.setProperty("--c", r.color ? `var(--route-${r.color})` : "var(--route)");
  if (r.color) drawer.style.setProperty("--route", `var(--route-${r.color})`); else drawer.style.removeProperty("--route");
  drawer.innerHTML = `
    <div class="d-top"><span class="cat">推薦散步路線</span><button class="close" id="d-close" aria-label="關閉">×</button></div>
    <h3 id="d-name">${esc(r.name)}</h3>
    <p class="latin">${esc(r.latin)}</p>
    <div class="rt-tabs" role="tablist"><button class="rt-tab" role="tab" data-tab="info" aria-selected="true">路線介紹</button>${r.food ? `<button class="rt-tab" role="tab" data-tab="food" aria-selected="false">🍴 吃什麼</button>` : ""}<button class="rt-tab" role="tab" data-tab="tips" aria-selected="false">💡 小提醒</button></div>
    <div class="rt-panel tips-panel" data-panel="tips" hidden>${list(r.tips)}</div>
    ${r.food ? `<div class="rt-panel" data-panel="food" hidden>
      <p class="food-intro">${esc(r.food.intro)}</p>
      <h4 class="food-h">山上與公園裡</h4>
      <ul class="food-list">${r.food.places.map(f => `<li class="food">
        <p class="food-where">${esc(f.where)}</p>
        <p class="food-name">${esc(f.name)}</p>
        <p class="food-kind">${esc(f.kind)}</p>
        <p>${esc(f.desc)}</p>
        <p class="food-hours">${esc(f.hours)}</p>
        <a class="gmap" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(f.q + " Roma")}&query_place_id=${f.pid}" target="_blank" rel="noopener"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5a4.5 4.5 0 0 0-4.5 4.5c0 3.4 4.5 8.5 4.5 8.5s4.5-5.1 4.5-8.5A4.5 4.5 0 0 0 8 1.5zm0 6.2a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4z" fill="currentColor"/></svg>Google 地圖 ↗</a>
      </li>`).join("")}</ul>
      <h4 class="food-h">為什麼更推薦下山再吃大餐</h4>
      ${list(r.food.why)}
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
  // zoom the map to this route (small screens)
  const xs = [], ys = [];
  r.pts.forEach(p => { xs.push(p[0]); ys.push(p[1] - 52); });
  r.stops.forEach(sid => { const s = SPOTS.find(x => x.id === sid); if (s && !s.g.classList.contains("off-route")) { const bb = s.g.getBBox(); xs.push(s.x, bb.x, bb.x + bb.width); ys.push(s.y, bb.y, bb.y + bb.height); } });
  mapView.fit(Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys));
  drawer.hidden = false; scrim.hidden = false;
  document.getElementById("d-close").addEventListener("click", closeSpot);
  drawer.querySelectorAll(".stop-link").forEach(b => b.addEventListener("click", () => openSpot(b.dataset.id)));
  bindTabs();
  document.getElementById("d-close").focus();
}

/* ---- Google Maps link ---- */
const GQ = {"vaticani": "Musei Vaticani", "sistina": "Cappella Sistina", "colosseo": "Colosseo", "massimo": "Palazzo Massimo alle Terme", "bocca": "Bocca della Verità", "esculapio": "Tempio di Esculapio Villa Borghese", "laterano": "Basilica di San Giovanni in Laterano", "medici": "Villa Medici", "pantheon": "Pantheon", "gianicolo": "Terrazza del Gianicolo", "trastevere": "Trastevere", "popolochurch": "Basilica di Santa Maria del Popolo", "maggiore": "Basilica di Santa Maria Maggiore", "traiano": "Mercati di Traiano", "hotel": "Hotel Nazionale Roma Piazza di Monte Citorio", "termini": "Stazione Roma Termini", "spagna": "Scalinata di Trinità dei Monti", "arapacis": "Museo dell'Ara Pacis", "gioacchino": "Chiesa di San Gioacchino in Prati", "pincio": "Terrazza del Pincio", "miracoli": "Chiesa Santa Maria dei Miracoli", "montesanto": "Basilica di Santa Maria in Montesanto", "monti": "Piazza della Madonna dei Monti", "vincoli": "Basilica di San Pietro in Vincoli", "acattolico": "Cimitero Acattolico", "mattatoio": "Mattatoio Testaccio", "ghetto": "Via del Portico d'Ottavia Roma", "rinascente": "Rinascente Roma Via del Tritone", "giubbonari": "Via dei Giubbonari Roma", "coronari": "Via dei Coronari Roma", "gioacchino": "Chiesa di San Gioacchino in Prati Roma", "minerva": "Basilica di Santa Maria sopra Minerva Roma", "doria": "Galleria Doria Pamphilj Roma", "barberini": "Palazzo Barberini Gallerie Nazionali Roma", "angeli": "Basilica di Santa Maria degli Angeli e dei Martiri Roma", "campidoglio": "Piazza del Campidoglio Roma", "agostino": "Basilica di Sant'Agostino Roma", "carlino": "San Carlo alle Quattro Fontane Roma", "andrea": "Sant'Andrea al Quirinale Roma", "gesu": "Chiesa del Gesù Roma", "smtrastevere": "Basilica di Santa Maria in Trastevere Roma"};
/* share a spot's Google Maps link: system share sheet if allowed, else copy, else show the link to copy by hand */
async function shareLink(btn) {
  const url = btn.dataset.url, name = btn.dataset.name, note = document.getElementById("d-share-note");
  const say = t => { note.textContent = t; clearTimeout(shareLink.t); shareLink.t = setTimeout(() => { note.textContent = ""; }, 2500); };
  try { if (navigator.share) { await navigator.share({ title: name, text: name + "（Google 地圖）", url }); return; } } catch (err) { if (err && err.name === "AbortError") return; }
  try { await navigator.clipboard.writeText(name + " " + url); say("已複製連結，可以貼到 LINE 或訊息裡"); return; } catch (err) {}
  note.textContent = "複製這個連結："; const inp = document.createElement("input"); inp.readOnly = true; inp.value = url; inp.setAttribute("aria-label", "Google 地圖連結");
  note.appendChild(inp); inp.focus(); inp.select();
}
/* anonymous error report: Google Form (no sign-in, no e-mail collected), prefilled with map + spot */
const REPORT_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfczsbVIwVeT78rpvKnk8CF1upTBqEKsf6viWWYu5iBn532Lg/viewform";
const REPORT_MAP = "羅馬";
const REPORT_BUILD = "2026-11-13";   // map version, so a report can be matched to what the reader saw
/* "來源" field: where the report came from, filled automatically so even an empty report says roughly what was wrong */
function reportSource(where) {
  const d = document.getElementById("drawer"), open = d && !d.hidden;
  const sp = open && d.dataset.spot ? SPOTS.find(x => x.id === d.dataset.spot) : null;
  const rt = open && d.dataset.route ? ROUTES.find(x => x.id === d.dataset.route) : null;
  const tab = open ? d.querySelector('.rt-tab[aria-selected="true"]') : null;
  const parts = [REPORT_MAP, where];
  if (sp) parts.push("景點：" + sp.name + "（" + sp.id + "）");
  if (rt) parts.push("路線：" + (rt.tag || rt.name) + "（" + rt.id + "）");
  if (tab) parts.push("分頁：" + tab.textContent.replace(/^[^\p{L}]+|[^\p{L}]+$/gu, "").trim());
  if (!sp && !rt) parts.push("沒有打開側邊內容");
  if (typeof routeOn !== "undefined" && routeOn) parts.push("City Walk 模式");
  if (window.NAME_ONLY) parts.push("簡潔模式");
  if (document.querySelector(".mapbox.fs")) parts.push("全螢幕");
  parts.push(innerWidth <= 640 ? "手機版" : "電腦版", "地圖版本 " + REPORT_BUILD);
  return parts.join("｜");
}
const reportUrl = (s, where) => REPORT_FORM + "?usp=pp_url&entry.772922063=" + encodeURIComponent(REPORT_MAP) + (s ? "&entry.2061406689=" + encodeURIComponent(s.name) : "") + "&entry.1913794735=" + encodeURIComponent(reportSource(where || "側邊內容"));
/* refresh the link at click time so 來源 reflects the current tab / mode */
document.addEventListener("click", e => {
  const a = e.target.closest && e.target.closest("a.icon-act.report, #foot-report");
  if (!a) return;
  const d = document.getElementById("drawer"), id = d && !d.hidden && d.dataset.spot;
  a.href = reportUrl(id ? SPOTS.find(x => x.id === id) : null, a.id === "foot-report" ? "頁尾" : "側邊內容");
}, true);
const gmapUrl = s => "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent((GQ[s.id] || s.latin.split(/ \/ | – /)[0]) + " Roma");

/* ---- Drawer ---- */
const drawer = document.getElementById("drawer"), scrim = document.getElementById("scrim");
let lastFocus = null;
const esc = t => String(t).replace(/[&<>"]/g, m => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;" }[m]));
function openExternal(url) {
  const a = document.createElement("a");
  a.href = url; a.target = "_blank"; a.rel = "noopener";
  document.body.appendChild(a); a.click(); a.remove();
}
const tipLinks = t => (t.links || []).map(l => `<a class="tip-map" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(l[1])}" target="_blank" rel="noopener">📍 ${esc(l[0])} ↗</a>`).join(" ");
const list = a => `<ul>${a.map(t => typeof t === "string" ? `<li>${esc(t)}</li>` : `<li>${esc(t.t)} ${tipLinks(t)}</li>`).join("")}</ul>`;
const STRIKE_IDS = ["termini"];   // train stations: link to strike lookup (user-requested 2026-11-17)
function openSpot(id) {
  drawer.dataset.spot = id; drawer.dataset.route = "";
  const s = SPOTS.find(x => x.id === id); if (!s) return;
  lastFocus = document.activeElement;
  SPOTS.forEach(x => x.g.classList.toggle("active", x.id === id));
  drawer.style.setProperty("--c", CAT[s.cat].color);
  drawer.style.removeProperty("--route");
  // 介紹 = what the place is; 💡 實用資訊 = everything for planning (hours, tickets, how to get there, reminders)
  const hasPrac = !!(STRIKE_IDS.includes(s.id) || s.warn || s.remind || s.hours || s.when || s.stay || s.fromHotel || s.price || s.site || s.pass || s.transport);
  drawer.innerHTML = `
    <div class="d-top"><span class="cat">${esc(CAT[s.cat].label)}</span><button class="close" id="d-close" aria-label="關閉">×</button></div>
    <h3 id="d-name">${esc(s.name)}</h3>
    <p class="latin">${esc(s.latin)}</p>
    <div class="d-actions">${s.cat !== "base" ? `<button class="visit-btn" id="d-visit" aria-pressed="${visited.has(s.id)}">${visited.has(s.id) ? "✓ 已去過（點一下取消）" : "標記為已去過"}</button>` : ""}<span class="d-icons"><a class="icon-act" href="${esc(gmapUrl(s))}" target="_blank" rel="noopener" aria-label="在 Google 地圖開啟" data-tip="Google 地圖" title="Google 地圖"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5a6.5 6.5 0 0 0-6.5 6.5c0 4.9 6.5 12.5 6.5 12.5s6.5-7.6 6.5-12.5A6.5 6.5 0 0 0 12 2.5zm0 9a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" fill="currentColor"/></svg></a><button class="icon-act" type="button" id="d-share" data-url="${esc(gmapUrl(s))}" data-name="${esc(s.name)}" aria-label="分享 Google 地圖連結" data-tip="分享" title="分享"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5.5" r="2.6" fill="currentColor"/><circle cx="6" cy="12" r="2.6" fill="currentColor"/><circle cx="18" cy="18.5" r="2.6" fill="currentColor"/><path d="M8.3 10.8 15.7 6.7M8.3 13.2l7.4 4.1" stroke="currentColor" stroke-width="2" fill="none"/></svg></button><a class="icon-act report" href="${esc(reportUrl(s))}" target="_blank" rel="noopener" aria-label="匿名回報這個景點的錯誤" data-tip="回報錯誤" title="回報錯誤"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 20.5h20L12 3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M12 9.5v5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="17.3" r="1.3" fill="currentColor"/></svg></a></span><span class="share-note" id="d-share-note" role="status" aria-live="polite"></span></div>
    ${s.stars ? `<p class="stars" aria-label="必去指數 ${s.stars} 顆星"><span>必去指數</span>${"★".repeat(s.stars)}<i>${"★".repeat(5 - s.stars)}</i></p>` : ""}
    ${hasPrac ? `<div class="rt-tabs" role="tablist"><button class="rt-tab" role="tab" data-tab="info" aria-selected="true">介紹</button><button class="rt-tab" role="tab" data-tab="tips" aria-selected="false">💡 實用資訊${s.warn ? '<span class="tab-alert" aria-label="有重要提醒">!</span>' : ""}</button></div>` : ""}
    ${hasPrac ? `<div class="rt-panel" data-panel="tips" hidden>
      ${s.warn ? `<div class="warn">⚠ ${esc(s.warn)}</div>` : ""}
      <dl>
      ${STRIKE_IDS.includes(s.id) ? `<div><dt>罷工查詢</dt><dd>義大利常有火車、公車罷工，出發前先查：<br><a class="site" href="https://www.theitalystrike.com/" target="_blank" rel="noopener">Italy Strike 罷工查詢 ↗</a><br><small>非官方整理，資料來自義大利交通部與交通業者公告；重要行程請再到官方網站確認</small><ul style="margin-top:8px"><li>罷工特別常見在<b>星期五</b>，其次是<b>星期一</b>，因為跟週末連在一起比較好動員。但這只是傾向，不是固定規則。</li><li>罷工時間的長度有慣例：<ul><li><b>鐵路</b>常是前一天 21:00 到當天 21:00，所以「週五罷工」可能從週四晚上就開始了。</li><li><b>地方交通</b>（羅馬 ATAC、威尼斯 ACTV 等）多是當天 24 小時或 4 小時，中間有保障時段。</li><li><b>航空</b>常是當天 24 小時，或某個時段 4～8 小時。</li></ul></li></ul></dd></div>` : ""}
      ${s.hours ? `<div><dt>${s.cat === "base" ? "服務資訊" : "營業時間"}</dt><dd>${list(s.hours)}</dd></div>` : ""}
      ${s.when ? `<div><dt>合適旅遊時段</dt><dd>${esc(s.when)}</dd></div>` : ""}
      ${s.stay ? `<div><dt>建議停留時間</dt><dd>${esc(s.stay)}</dd></div>` : ""}
      ${s.fromHotel ? `<div><dt>從飯店出發</dt><dd>${esc(s.fromHotel)}</dd></div>` : ""}
      ${s.transport ? `<div><dt>交通方式</dt><dd class="tr">${s.transport.map(([h, items]) => `<h4>${esc(h)}</h4>${list(items)}`).join("")}</dd></div>` : ""}
      ${s.price ? `<div><dt>票價</dt><dd>${esc(s.price)}</dd></div>` : ""}
      ${s.pass ? `<div><dt>聯票包含</dt><dd>${list(s.pass)}</dd></div>` : ""}
      ${s.site ? `<div><dt>官方網站</dt><dd><a class="site" href="${esc(s.site[1])}" target="_blank" rel="noopener">${esc(s.site[0])} ↗</a></dd></div>` : ""}
      ${s.remind ? `<div><dt>小提醒</dt><dd>${list(s.remind)}</dd></div>` : ""}
      </dl>
    </div>` : ""}
    <div class="rt-panel" data-panel="info">
    ${s.warn ? `<button class="warn-jump" type="button">⚠ 有開放或預約限制，點這裡看「實用資訊」</button>` : ""}
    <dl>
      <div><dt>特色</dt><dd>${esc(s.feature)}</dd></div>
      ${s.tips ? `<div><dt>看點</dt><dd>${list(s.tips)}</dd></div>` : ""}
      ${s.walk ? `<div><dt>看點</dt><dd>看點都串在 City Walk「${esc(((ROUTES.find(r => r.id === s.walk) || {}).name || "").replace(/^City Walk：/, ""))}」裡，照順序走一圈就全看到了。<br><button class="walk-link" type="button" data-route="${esc(s.walk)}">打開這條 City Walk →</button></dd></div>` : ""}
      ${s.howto ? `<div><dt>怎麼玩：一個下午到晚上</dt><dd><p class="howto-intro">${esc(s.howto.intro)}</p><ol class="howto">${s.howto.items.map(([h, x]) => `<li><b>${esc(h)}</b><br>${esc(x)}</li>`).join("")}</ol></dd></div>` : ""}
      ${!s.walk && routesOf(s.id).length ? `<div><dt>City Walk</dt><dd>${routesOf(s.id).map(r => `這裡在 City Walk「${esc(r.name.replace(/^City Walk：/, ""))}」路線上。<br><button class="walk-link" type="button" data-route="${esc(r.id)}">打開這條 City Walk →</button>`).join("<br>")}</dd></div>` : ""}
      ${s.links ? `<div><dt>相關連結</dt><dd><ul>${s.links.map(l => `<li><a class="site" href="${esc(l[1])}" target="_blank" rel="noopener">${esc(l[0])} ↗</a></li>`).join("")}</ul></dd></div>` : ""}
    </dl></div>`;
  drawer.hidden = false; scrim.hidden = false;
  document.getElementById("d-close").addEventListener("click", closeSpot);
  bindTabs();
  drawer.querySelectorAll(".walk-link").forEach(b => b.addEventListener("click", e => { const id = e.currentTarget.dataset.route; routeOn = true; if (!routeShow.has(id)) { routeShow.add(id); saveShow(); } applyRoute(); openRoute(id); }));
  document.getElementById("d-share")?.addEventListener("click", e => shareLink(e.currentTarget));
  document.getElementById("d-visit")?.addEventListener("click", () => {
    if (visited.has(s.id)) visited.delete(s.id); else visited.add(s.id);
    saveVisited(); applyVisited();
    if (visited.has(s.id) && !showDone) closeSpot(); else openSpot(s.id);
  });
  document.getElementById("d-close").focus();
}
const routesOf = id => ROUTES.filter(r => r.stops.includes(id) || (r.areas || []).includes(id));
function showTab(tab) {
  drawer.querySelectorAll(".rt-tab").forEach(x => x.setAttribute("aria-selected", x.dataset.tab === tab));
  drawer.querySelectorAll(".rt-panel").forEach(p => p.hidden = p.dataset.panel !== tab);
  drawer.scrollTop = 0;
}
function bindTabs() {
  drawer.querySelectorAll(".rt-tab").forEach(b => b.addEventListener("click", () => showTab(b.dataset.tab)));
  drawer.querySelector(".warn-jump")?.addEventListener("click", () => showTab("tips"));
}
function closeSpot() {
  drawer.hidden = true; scrim.hidden = true;
  SPOTS.forEach(x => x.g.classList.remove("active"));
  if (lastFocus && lastFocus.focus) lastFocus.focus();
}
scrim.addEventListener("click", closeSpot);
// small screens: one tap anywhere in the sheet (outside links/buttons) closes it
drawer.addEventListener("click", e => {
  if (!mapView.mq.matches) return;
  if (e.target.closest("a, button, input, select, textarea, summary, [role=button]")) return;
  if (window.getSelection && String(window.getSelection())) return;
  closeSpot();
});
document.addEventListener("keydown", e => { if (e.key === "Escape" && !drawer.hidden) closeSpot(); });
</script>
'''
S = 2.2
vbs = f"{vb[0]} {vb[1]} {vb[2]-vb[0]} {vb[3]-vb[1]}"
html = (html.replace("__DATA__", data_js).replace("__VB__", vbs).replace("__S__", str(S))
        .replace("__VBX__", str(vb[0])).replace("__VBY__", str(vb[1]))
        .replace("__VBW__", str(vb[2]-vb[0])).replace("__VBH__", str(vb[3]-vb[1])))
import faq
html = html.replace("<!--FAQ-->", faq.build(html, faq.QA_ROME), 1).replace("</style>", faq.CSS + "</style>", 1)
open("/home/claude/rome/羅馬地圖.html", "w").write(html)
print("ok", len(html))
