"""Rome real-map version: the Lucca real map (lucca-real.html, freshly built) is the template;
Rome's data, drawer, City Walk and shopping replace the Lucca-only parts."""
import json, re, subprocess, datetime as dt
import numpy as np

LR = '/home/claude/lucca/real/'
RR = '/home/claude/rome/'
OUT = RR + 'real/'
subprocess.run(['python3', LR + 'build_real.py'], check=True, cwd=LR, capture_output=True)
T = open(LR + 'lucca-real.html').read()
H = open(RR + '羅馬地圖.html').read()
D = json.load(open(RR + 'data.json'))

def jcut(name, nxt):
    i = H.index('const %s = ' % name) + len('const %s = ' % name); j = H.index(';\nconst %s' % nxt, i)
    return json.loads(H[i:j])
SPOTS = jcut('SPOTS', 'ROUTES'); ROUTES = jcut('ROUTES', 'EDGES')
BASEJ = H[H.index('const BASE = ') + 13:H.index(';\n', H.index('const BASE = '))]
BASE = json.loads(BASEJ)

# svg x,y → lat,lng (the drawn map is an exact affine of the real one)
X = np.array([[s['x'], s['y'], 1] for s in D['spots']]); Y = np.array([[s['lat'], s['lon']] for s in D['spots']])
A = np.linalg.lstsq(X, Y, rcond=None)[0]
def ll(p): v = np.array([p[0], p[1], 1]) @ A; return [round(float(v[0]), 6), round(float(v[1]), 6)]
DD = {s['id']: s for s in D['spots']}

LL = {s['id']: [DD[s['id']]['lat'], DD[s['id']]['lon']] for s in SPOTS}
WEEK, WPRE, NODIM, KEEP = {}, {}, [], []
DROP = {'x', 'y', 'lx', 'ly', 'slx', 'sly', 'ux', 'uy', 'nx', 'ny', 'W', 'mapLines', 'fromHotel', 'week'}
spots = []
for s in SPOTS:
    w = s.get('week')
    if w:
        WEEK[s['id']] = w['d']
        if w.get('p'): WPRE[s['id']] = w['p']
        if w.get('nodim'): NODIM.append(s['id'])
        if w.get('keep'): KEEP.append(s['id'])
    t = {k: v for k, v in s.items() if k not in DROP}
    # the hand-drawn map's label spots (top-left corners) for 全覽／簡潔: l = default, u = with 次要 / City Walk, n = 簡潔, sl = name-only, sh = 購物
    lab = {}
    for key, (a, b) in {'l': ('lx', 'ly'), 'u': ('ux', 'uy'), 'n': ('nx', 'ny'), 'sl': ('slx', 'sly'), 'sh': ('shx', 'shy')}.items():
        if s.get(a) is not None and s.get(b) is not None: lab[key] = ll((s[a], s[b]))
    if lab: t['lab'] = lab
    ap = DD[s['id']].get('areaPts')
    if ap: t['area'] = [ll(p) for p in ap]
    spots.append(t)

routes = []
for r in ROUTES:
    t = {k: v for k, v in r.items() if k not in ('pts', 'marks', 'label')}
    t['ll'] = [ll(p) for p in r['pts']]
    t['marks'] = [dict(n=m['n'], name=m['name'], q=m['q'], ll=ll((m['x'], m['y']))) for m in r.get('marks', [])]
    t['pill'] = ll((r['label']['x'], r['label']['y'])); t['pillText'] = r['label']['text']
    routes.append(t)

names = {l['id']: l['name'] for l in BASE.get('shopStreetLabels', [])}
shop_streets = [dict(id=st['id'], name=names.get(st['id'], ''), pts=[ll(p) for p in st['d']], at=0.5, cls='shop-street', minZoom=16.25)
                for st in BASE.get('shopStreets', [])]

CAT = H[H.index('const CAT = {'):H.index('\nconst SPOTS = ')]
GQ = H[H.index('const GQ = '):H.index('\n', H.index('const GQ = '))]

lats = [v[0] for v in LL.values()]; lngs = [v[1] for v in LL.values()]
days = [dict(k='0126', date='1/26', wd=1), dict(k='0127', date='1/27', wd=2), dict(k='0128', date='1/28', wd=3), dict(k='0129', date='1/29', wd=4),
        dict(k='0130', date='1/30', wd=5), dict(k='0131', date='1/31', wd=6), dict(k='0201', date='2/1', wd=0), dict(k='0202', date='2/2', wd=1), dict(k='0203', date='2/3', wd=2)]
import math
_p0, _p1 = ll((0, 0)), ll((1000, 0))
UNIT_M = math.hypot((_p1[0] - _p0[0]) * 111320, (_p1[1] - _p0[1]) * 111320 * math.cos(math.radians(_p0[0]))) / 1000
TIBER = [ll(p) for p in BASE['tiber']]; RIVER_LBL = dict(ll=ll((BASE['river']['x'], BASE['river']['y'])), text=BASE['river']['text'])
CITY = {
  'key': 'rome', 'name': '羅馬', 'title': '羅馬', 'center': [41.8986, 12.4823], 'farKm': 30,
  'bounds': [[41.889, 12.462], [41.910, 12.500]], 'homeSpot': 'pantheon', 'homeZoom': 15.25,
  'unitM': round(UNIT_M, 4), 'river': TIBER, 'riverLabel': RIVER_LBL,
  'wall': None, 'streets': shop_streets, 'days': days,
  'tourSpots': ['pantheon', 'trevi', 'navona', 'spagna', 'colosseo'], 'hideSpot': 'trevi',
  'demo': [dict(id='colosseo', time='08:30', note='先上官網買票'), dict(id='foro', time='11:00', note=''), dict(id='palatino', time='13:00', note='')],
}
city_js = 'const CITY = ' + json.dumps(CITY, ensure_ascii=False) + ';\n'
city_js += '''CITY.unWalk = true;   // 待選景點 lists the City Walks (rome_extra.js); the 我的行程 tour says so
CITY.tourExtra = [
  { sel: ".icon-btn.route", t: "City Walk", x: "推薦的散步路線，沿著真的街道畫出來；點路線或距離膠囊看路線介紹、沿途吃什麼。" },
  { sel: ".icon-btn.shop-btn", t: "購物", x: "地圖上粉紅色的路是購物街，點路名看介紹；按這顆會再加上店家（綠色實心框）。" }
];
'''

data = ('<script>\n' + CAT + '\nconst SPOTS = ' + json.dumps(spots, ensure_ascii=False) + ';\nconst ROUTES = ' + json.dumps(routes, ensure_ascii=False)
        + ';\nconst LL = ' + json.dumps(LL) + ';\nconst WEEK_KEEP = new Set(' + json.dumps(KEEP) + ');\n')

out = re.sub(r'<style id="geo-city">.*?</style>\n?', '', T, count=1, flags=re.S)   # Lucca's label sizes, not Rome's
# ---- data, days table, city ----
i = out.index('<script>\nconst CAT = {'); j = out.index('const DKEY = ', i)
out = out[:i] + data + out[j:]
out = out.replace('const DKEY = "trip-days-lucca"', 'const DKEY = "trip-days-rome"', 1)
out, n = re.subn(r'const WEEK = \{.*?\}, WEEK_PREFIX = \{.*?\}, WEEK_NODIM = new Set\(\[.*?\]\);',
                 lambda m: 'const WEEK = ' + json.dumps(WEEK, ensure_ascii=False) + ', WEEK_PREFIX = ' + json.dumps(WPRE, ensure_ascii=False) + ', WEEK_NODIM = new Set(' + json.dumps(NODIM) + ');', out, count=1, flags=re.S)
assert n == 1
out, n = re.subn(r'const CITY = \{.*?\n\};\n', lambda m: city_js, out, count=1, flags=re.S); assert n == 1
out, n = re.subn(r'CITY\.unitM = [\d.]+;\n', '', out, count=1); assert n == 1   # Lucca's scale line from the template
out = out.replace('const VKEY = "trip-visited-lucca"', 'const VKEY = "trip-visited-rome"', 1)
out, n = re.subn(r'const GQ = [^\n]*', lambda m: GQ, out, count=1); assert n == 1
out = out.replace('const REPORT_MAP = "盧卡";', 'const REPORT_MAP = "羅馬";', 1)

# ---- drawer: Rome's (City Walk links, links, transport…) with the same real-map patches as Lucca ----
dj = H[H.index('/* ---- Drawer ---- */'):H.index('</script>', H.index('/* ---- Drawer ---- */'))]
dj = re.sub(r'\n\s*\$\{s\.fromHotel \? `<div><dt>從飯店出發</dt>.*?: ""\}', '', dj, count=1)
dj = dj.replace('|| s.fromHotel ', '')
assert 'fromHotel' not in dj
src = open(LR + 'build_real.py').read()
a = src.index('drawer_js = drawer_js.replace(\n'); b = src.index("assert 'planToggle' in drawer_js and 'PDAYS.map' in drawer_js")
ns = {'drawer_js': dj}
exec(src[a:b], ns)
dj = ns['drawer_js']
for k in ('planToggle', 'h-change', 'hotelFromLine', 'bindMineEdit', 'bindHotel'): assert k in dj, k
dj = dj.replace('例如：Hotel Ilaria', '例如：Hotel Nazionale Roma')
# 2026-11-27: she asked to drop 必去指數 from the spot drawer (the stars on the map labels stay)
dj, _n = re.subn(r'\n\s*\$\{s\.stars \? `<p class="stars".*?</p>` : ""\}', '', dj, count=1); assert _n == 1 and '必去指數' not in dj
i = T.index('/* ---- Drawer ---- */'); i = out.index('/* ---- Drawer ---- */'); j = out.index('</script>', i)
extra_js = open(OUT + 'rome_extra.js').read()
out = out[:i] + dj + '\n' + extra_js + out[j:]

# ---- page text ----
rep = [
  ('<title>盧卡古城景點地圖（真地圖版）</title>', '<title>羅馬景點地圖（真地圖版）</title>'),
  ('<h1>盧卡古城景點地圖</h1>', '<h1>羅馬景點地圖</h1>'),
  ('aria-label="盧卡古城地圖"', 'aria-label="羅馬地圖"'),
  ('content="盧卡地圖"', 'content="羅馬地圖"'),
  ('travelplanner-kaili.github.io/lucca/', 'travelplanner-kaili.github.io/rome/'),
  ('travelplanner-kaili.github.io/lucca', 'travelplanner-kaili.github.io/rome'),
  ('「盧卡地圖」圖示', '「羅馬地圖」圖示'),
  ('Hotel Ilaria', 'Hotel Nazionale'),
  ('43.8429, 10.5027', '41.9009, 12.4779'),
  ('最後只留城牆、道路和景點', '最後只留景點和路線'),
  ('（只留城牆、主要道路、購物商圈和景點）', '（只留景點、購物街和路線）'),
  ('只留城牆、道路和景點', '只留景點和路線'),
  ('隱藏底圖：只留城牆、道路和景點', '隱藏底圖：只留景點和路線'),
  ('回到整個古城', '回到整張地圖'),
  ('「星期幾去」（預設是週三）', '「星期幾去」'),
]
for a, b in rep: out = out.replace(a, b)
out = re.sub(r'<div class="eyebrow">[^<]*</div>', '<div class="eyebrow">Roma · Lazio</div>', out, count=1)

# ---- City Walk + 購物 buttons (after 距離模式, before ?) and the route picker ----
ic = lambda cls: re.search(r'<button class="icon-btn %s"[^>]*>.*?</button>' % cls, H, flags=re.S).group(0)
walk_btn = re.sub(r' id="f-route"', '', ic('route')); shop_btn = re.sub(r' id="f-shop"', '', ic('shop-btn'))
out, n = re.subn(r'(<button class="icon-btn dist" id="(f-dist|fs-dist-btn)"[^>]*>.*?</button>)',
                 lambda m: m.group(1) + walk_btn.replace('class="icon-btn route"', 'class="icon-btn route"' + (' id="f-route"' if m.group(2) == 'f-dist' else ' id="fs-route-btn"'))
                 + shop_btn.replace('class="icon-btn shop-btn"', 'class="icon-btn shop-btn"' + (' id="f-shop"' if m.group(2) == 'f-dist' else ' id="fs-shop-btn"')), out, flags=re.S)
assert n == 2, n
out = out.replace('    <div class="rad-card"', '    <div class="route-pick" id="route-pick" role="group" aria-label="選擇要顯示的 City Walk" hidden></div>\n    <div class="rad-card"', 1)

# ---- FAQ: Rome's City Walk and 購物 questions join the basics ----
def faq_item(title):
    m = re.search(r'<li class="faq-item"><p class="faq-q"><span class="n">Q\d+</span><span>' + re.escape(title) + r'</span>.*?</li>', H, flags=re.S)
    return m.group(0)
walk_q = faq_item('有推薦的散步路線嗎？'); shop_q = faq_item('想逛街買東西要去哪裡？')
# 2026-11-20: shopping streets are pink on the real map (orange was mixed up with 我的行程 and City Walk)
assert '地圖上橘色的路' in shop_q; shop_q = shop_q.replace('地圖上橘色的路', '地圖上粉紅色的路')
fi = out.index('<section class="faq"'); fj = out.index('</ol></section>\n</div>', fi) + len('</ol></section>')
faq = out[fi:fj]
# 待選景點 also lists the City Walks in Rome (2026-11-27, same as the 我的行程 tour)
_a = '按「＋ 加入」就排進目前選的那一天。'
assert faq.count(_a) == 1; faq = faq.replace(_a, _a + '最下面還有 City Walk，可以整條路線一次加進來。')
# answers point to other questions by number: turn those into the question's title first, renumber, then put numbers back
num2title = dict(re.findall(r'<span class="n">(Q\d+)</span><span>([^<]*)</span>', faq))
def to_ref(m):
    body = re.sub(r'Q\d+', lambda q: '[[ref:%s]]' % num2title[q.group(0)] if q.group(0) in num2title else q.group(0), m.group(2))
    return m.group(1) + body + m.group(3)
faq = re.sub(r'(<p class="faq-a">)(.*?)(</p>)', to_ref, faq, flags=re.S)
faq = re.sub(r'(<p class="faq-gnote">)(.*?)(</p>)', to_ref, faq, flags=re.S)
anchor = re.search(r'<li class="faq-item"><p class="faq-q"><span class="n">Q\d+</span><span>手機上地圖太小？</span>', faq)
assert anchor
faq = faq[:anchor.start()] + walk_q + shop_q + faq[anchor.start():]
k = [0]
def rn(m): k[0] += 1; return '<span class="n">Q%d</span>' % k[0]
faq = re.sub(r'<span class="n">Q\d+</span>', rn, faq)
title2num = {t: n for n, t in re.findall(r'<span class="n">(Q\d+)</span><span>([^<]*)</span>', faq)}
faq = re.sub(r'\[\[ref:([^\]]+)\]\]', lambda m: title2num[m.group(1)], faq)
out = out[:fi] + faq + out[fj:]

# ---- styles ----
css = '''<style>
/* ===== Rome: City Walk, 購物 ===== */
:root { --route-bernini: #1F6FB5; --route-cara: #7B3C8C; --route-michel: #0E7C72;  --shop-street: #C8457F; --walk: #C62828; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --route-bernini: #6FB0EE; --route-cara: #C891DA; --route-michel: #5CCABD; --shop-street: #F08CBA; --walk: #FF6B6B; } }
:root[data-theme="dark"] { --route-bernini: #6FB0EE; --route-cara: #C891DA; --route-michel: #5CCABD; --shop-street: #F08CBA; --walk: #FF6B6B; }
.icon-btn.route { border-color: var(--walk); color: var(--walk); }
.icon-btn.route[aria-pressed="true"] { background: var(--walk); color: var(--paper); }
.icon-btn.shop-btn { border-color: var(--open); color: var(--open); }
.icon-btn.shop-btn[aria-pressed="true"] { background: var(--open); color: var(--paper); }
.ic.ic-walk { border-color: var(--walk); color: var(--walk); }
.ic.ic-shop { border-color: var(--open); color: var(--open); }
.route-pick { position: absolute; left: max(10px, env(safe-area-inset-left, 0px)); top: 10px; z-index: 720; max-width: calc(100% - 80px); display: flex; flex-wrap: wrap; gap: 6px; }
.route-pick button { --rc: var(--walk); font: 700 13px var(--f-body); padding: 5px 11px; border-radius: 999px; border: 2px solid var(--rc); background: var(--paper); color: var(--rc); cursor: pointer; }
.route-pick button[aria-pressed="true"] { background: var(--rc); color: var(--paper); }
.route-pick button.all { --rc: var(--ink); }
.mapbox.fs .route-pick { top: calc(var(--fsbar, 56px) + 6px); }
/* computer: with 我的行程 open, the walk chips sit to the right of the panel (and its tab) instead of over it */
@media (min-width: 641px) { .mapbox:has(.plan:not([hidden])) .route-pick { left: calc(min(372px, 100% - 80px) + 48px); max-width: calc(100% - min(372px, 100% - 80px) - 120px); } }
@media (max-width: 640px) { .route-pick { top: 6px; left: 6px; right: 6px; max-width: none; gap: 4px; flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; padding-bottom: 2px; } .route-pick::-webkit-scrollbar { display: none; } .route-pick button { flex: none; } }
.leaflet-pane path.route-line { stroke: var(--rc, var(--walk)); stroke-width: 3.5; stroke-dasharray: 8 6; stroke-linecap: round; stroke-linejoin: round; fill: none; }
.leaflet-pane path.route-hit { stroke: transparent; stroke-width: 26; fill: none; cursor: pointer; }
.route-end span { position: absolute; left: -13px; top: -13px; width: 26px; height: 26px; border-radius: 50%; background: var(--rc, var(--walk)); color: var(--paper); border: 2.5px solid var(--paper); font: 700 13px/21px var(--f-body); text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.3); }
.route-mark span { position: absolute; left: -12px; top: -12px; width: 24px; height: 24px; border-radius: 50%; background: var(--paper); color: var(--rc, var(--walk)); border: 2.5px solid var(--rc, var(--walk)); font: 700 12px/19px var(--f-body); text-align: center; cursor: pointer; }
.route-mark span:hover { background: var(--rc, var(--walk)); color: var(--paper); }
.route-pill span { position: absolute; transform: translate(-50%, -50%); white-space: nowrap; background: var(--rc, var(--walk)); color: var(--paper); border: 2px solid var(--paper); border-radius: 999px; padding: 4px 12px; font: 700 13px var(--f-body); cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,.25); }
.route-pill span::after { content: "👆"; position: absolute; right: -16px; bottom: -22px; font-size: 24px; pointer-events: none; filter: drop-shadow(0 1px 1px rgba(0,0,0,.35)); }
.spot.off-route { display: none !important; }
#lmap .off-route-area { display: none; }
.leaflet-pane path.street-band.shop-street { stroke: var(--shop-street); stroke-opacity: .5; cursor: pointer; }
#lmap.base-faded .leaflet-pane path.street-band.shop-street { stroke-opacity: .7; }
.street-name.shop-street span { color: var(--shop-street); cursor: pointer; pointer-events: auto; }
.street-name.shop-street span:hover { text-decoration: underline; }
.spot.rush .tab { border-width: 3px; }
.spot .t-rush { display: inline-block; margin-left: 4px; padding: 0 5px; border-radius: 4px; background: var(--paid); color: var(--paper); font: 700 calc(10.5px * var(--ls, 1))/1.5 var(--f-body); vertical-align: 1px; }
.spot.shopbox .tab { background: var(--c); }
.spot.shopbox .tab .t-name, .spot.shopbox .tab .t-more { color: var(--paper); }
ol.stops { margin: 0; padding-left: 1.3em; }
.food-intro { margin: 0 0 18px; line-height: 1.7; }
.food-h { font-size: 13px; letter-spacing: .06em; color: var(--muted); margin: 0 0 10px; }
.food-list { list-style: none; margin: 0 0 22px; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.food { border: 1px solid var(--line); border-left: 4px solid var(--walk); border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }
.food p { margin: 0; line-height: 1.6; }
.food-where { font-size: 12px; font-weight: 700; color: var(--walk); letter-spacing: .04em; }
.food-name { font: 700 17px var(--f-body); }
.food-kind, .food-hours { font-size: 13px; color: var(--muted); }
.stop-link { font: 700 15px var(--f-body); color: var(--walk); background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; }
.walk-link { margin-top: 10px; font: 700 15px var(--f-body); padding: 8px 14px; border-radius: 999px; border: 2px solid var(--walk); background: none; color: var(--walk); cursor: pointer; }
.walk-link:hover { background: var(--walk); color: var(--paper); }
.howto-intro { margin: 0 0 8px; line-height: 1.7; }
.howto { margin: 0; padding-left: 1.3em; display: flex; flex-direction: column; gap: 8px; line-height: 1.65; }
.stars { margin: -8px 0 16px; color: var(--paid); font-size: 17px; letter-spacing: .12em; display: flex; align-items: center; gap: 10px; }
.stars span { font-size: 12px; font-weight: 700; letter-spacing: .1em; color: var(--muted); }
.stars i { font-style: normal; color: var(--line); }
.tip-map { white-space: nowrap; }
dd.tr h4 { margin: 8px 0 4px; font-size: 13px; }
</style>
'''
out = out.replace('</head>', css + '</head>', 1)
MAP_UPDATED = re.search(r'const MAP_UPDATED = "([^"]+)"', out).group(1)
open(OUT + 'rome-real.html', 'w').write(out)
open(OUT + 'version.json', 'w').write(json.dumps({'updated': MAP_UPDATED}))
print('ok', len(out), 'routes', len(routes), 'shop streets', len(shop_streets))
