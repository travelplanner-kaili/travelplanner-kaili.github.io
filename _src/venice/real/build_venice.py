"""Venice real-map version (2026-11-27): the Lucca real map (lucca-real.html, freshly built) is the template, like Rome;
Venice's data comes from the hand-drawn venice.html, the info card is Rome's (links, 小提醒, transport), plus venice_extra.js
(water-bus stops, traghetto crossings, 購物).
Coordinates: real ones from OpenStreetMap (Nominatim, looked up 2026-11-27 through her desktop browser) in coords_raw.json;
places it could not find (water-bus stops, traghetti, the Ghetto) use the hand-drawn spot through a least-squares affine
(most drawn spots are within ~50 m). The Grand Canal is OSM's centre line (canal.json): she finds her way by the canals."""
import json, re, math, subprocess, datetime as dt
from urllib.parse import urlparse
import numpy as np

LR = '/home/claude/lucca/real/'
VR = '/home/claude/venice/'
OUT = VR + 'real/'
RH = open('/home/claude/rome/羅馬地圖.html').read()          # Rome's hand-drawn page: its drawer is reused
subprocess.run(['python3', LR + 'build_real.py'], check=True, cwd=LR, capture_output=True)
T = open(LR + 'lucca-real.html').read()
H = open(VR + 'venice.html').read()
C = json.load(open(OUT + 'coords_raw.json'))
CANAL = json.load(open(OUT + 'canal.json'))

i = H.index('const ALL = ') + len('const ALL = '); ALL = json.loads(H[i:H.index(';\n', i)])
WEEK = json.loads(H[H.index('const WEEK = ') + 13:H.index(', WEEK_PREFIX', H.index('const WEEK = '))])
VAPL = {v['id']: v for v in json.loads(H[H.index('const VAP_LABELS = ') + 19:H.index(';\n', H.index('const VAP_LABELS = '))])}
SHOPL = {v['id']: v for v in json.loads(H[H.index('const SHOP_LABELS = ') + 20:H.index(';\n', H.index('const SHOP_LABELS = '))])}
SHOP_PATHS = re.findall(r'<path class="st-band" d="([^"]+)"', H)   # same order as the shop entries
SHOP_IDS = [a['id'] for a in ALL if a['cat'] == 'shop']
assert len(SHOP_PATHS) == len(SHOP_IDS) == 5
A = {a['id']: a for a in ALL}

# ---- privacy (2026-11-27, she asked not to expose where she is): the public map shows 2/12–2/15, and her real arrival
# (train, seat, time), departure and 【這趟旅程】 notes are taken out. Museum free days are said generally (每月第一個週日).
def _sub(id, field, old, new):
    a = A[id]; v = a[field]
    if isinstance(v, list):
        hit = [k for k, x in enumerate(v) if old in x]; assert hit, (id, field, old)
        for k in hit: v[k] = v[k].replace(old, new)
        a[field] = [x for x in v if x.strip()]
    else:
        assert old in v, (id, field, old); a[field] = v.replace(old, new)
PRIV = [
  ('sanmarco', 'when', '；週五 14:55 才到站，當天來不及', ''),
  ('rialto', 'remind', '，2/5 下午才抵達、週日休市，只能排在週六（2/6）早上', ''),
  ('mercato', 'when', '只能排週六（2/6）08:00～10:00：週五下午才抵達、週日休市，11:00 後攤販開始收攤。', '週二至週六 08:00～10:00 最熱鬧，11:00 後攤販開始收攤。'),
  ('frari', 'when', '週五下午從火車站走往市區時也順路', '從火車站走往市區時也順路'),
  ('ghetto', 'remind', '2/5（五）14:55 到站後可以直接從這區開始：', ''),
  ('tr_ferrovia', 'when', '只有週六（2/6）上午能搭：週五 14:55 到站時已收班、週日停駛。', '只有週一至週六上午能搭，下午和週日停駛。'),
  ('tr_carbon', 'when', '只能排週六上午：週五下午才到、14:00 收，週日不開。', '週一至週六上午，14:00 收班，週日不開。'),
  ('piazza', 'remind', '2/5～2/7 正逢 2027 威尼斯嘉年華（官方日期 1/23～2/9），週末是人潮最高峰', '2027 威尼斯嘉年華官方日期 1/23～2/9，週末是人潮最高峰'),
  ('accademia', 'when', '或週五下午抵達後（開到 19:15）；2/7（週日）是當月第一個週日免費入場', '或平日傍晚（開到 19:15）；每月第一個週日免費入場'),
  ('accademia', 'price', '2/7 是二月第一個週日，', '每月第一個週日'),
  ('accademia', 'remind', '2/7（週日）看完', '第一個週日看完'),
  ('accademia', 'remind', '2/7（週日）免費日人潮多', '第一個週日免費日人潮多'),
  ('accademia', 'remind', '，或週五傍晚抵達後去（開到 19:15）', '，或平日傍晚去（開到 19:15）'),
  ('accademia', 'pl', '€15（2/7 免費）', '€15（首週日免費）'),
  ('correr', 'remind', '2/7（第一個週日）', '每月第一個週日'),
  ('correr', 'pl', '2/7 考古館免費', '首週日考古館免費'),
  ('zattere', 'remind', '2/7（日）建議接在學院美術館後面', '第一個週日建議接在學院美術館後面'),
  ('grimani', 'when', '2/7（週日）免費日上午', '每月第一個週日（免費）上午'),
  ('grimani', 'price', '2/7 是當月第一個週日，', '每月第一個週日'),
  ('grimani', 'remind', '2/7 免費是依往年', '第一個週日免費是依往年'),
  ('grimani', 'pl', '2/7 免費', '首週日免費'),
  ('oriente', 'when', '2/7 下午', '每月第一個週日下午（免費）'),
  ('oriente', 'price', '2/7 國立部分免費', '每月第一個週日國立部分免費'),
  ('oriente', 'pl', '2/7 免費', '首週日免費'),
  ('station', 'feature', '我們 2/5（週五）從佛羅倫斯搭 Italo 8910，12:39 開、14:55 抵達這裡（6 車 9 號位）。', ''),
  ('station', 'remind', '抵達：2/5（五）14:55，Italo 8910（佛羅倫斯 S.M.N. 12:39 開）。', ''),
  ('station', 'remind', '週五下午抵達後還來得及', '下午抵達後還來得及'),
  ('station', 'remind', '離開時 2/8 一早出發，要先確認', '一早離開的話，要先確認'),
]
for x in PRIV: _sub(*x)
for id in ('tr_dogana', 'tr_giglio', 'v_ferrovia'):
    A[id]['remind'] = [x for x in A[id]['remind'] if not x.startswith('【這趟旅程】')]
for a in ALL: a.pop('rows', None)   # the hand-drawn label rows (not used on the real map)
_left = re.findall(r'2/[5-8](?!\d)|14:55|Italo|號位|這趟旅程', json.dumps(ALL, ensure_ascii=False)); assert not _left, _left

# drawn x,y → lat,lng (least squares on well-known landmarks)
CORE = ['sanmarco', 'ducale', 'piazza', 'campanile', 'sospiri', 'rialto', 'accademia', 'salute', 'guggenheim', 'sangiorgio', 'frari', 'sanrocco',
        'fenice', 'bovolo', 'mercato', 'pontacc', 'dogana', 'acquaalta', 'zanipolo', 'miracoli', 'correr', 'cadoro', 'grimani', 'oriente',
        'scalzi', 'costituzione', 'station', 'proma']
M = np.linalg.lstsq(np.array([[A[k]['x'], A[k]['y'], 1] for k in CORE]), np.array([C[k] for k in CORE]), rcond=None)[0]
def aff(x, y): v = np.array([x, y, 1]) @ M; return [round(float(v[0]), 6), round(float(v[1]), 6)]
KM = [111320, 111320 * math.cos(math.radians(45.435))]
def dist(p, q): return math.hypot((p[0] - q[0]) * KM[0], (p[1] - q[1]) * KM[1])
_p0, _p1 = aff(0, 0), aff(1000, 0); UNIT_M = dist(_p0, _p1) / 1000

LL = {}
for a in ALL:
    LL[a['id']] = C[a['id']] if a['id'] in C else aff(a['x'], a['y'])

def lab_of(a):
    # the drawn label corner; when the real spot is far from where it was drawn (> 60 m), move the label with it
    pin = aff(a['x'], a['y']); off = [LL[a['id']][0] - pin[0], LL[a['id']][1] - pin[1]] if dist(pin, LL[a['id']]) > 60 else [0, 0]
    lab = {}
    for key, (x, y) in {'l': ('lx', 'ly'), 'u': ('ux', 'uy'), 'n': ('nx', 'ny')}.items():
        if a.get(x) is not None: p = aff(a[x], a[y]); lab[key] = [round(p[0] + off[0], 6), round(p[1] + off[1], 6)]
    return lab

DROP = {'x', 'y', 'lx', 'ly', 'ux', 'uy', 'nx', 'ny', 'rows', 'H', 'Hs', 'hl', 'pl', 'fromBase', 'gq', 'cross', 'pass_', 'site'}
spots, GQ = [], {}
for a in ALL:
    t = {k: v for k, v in a.items() if k not in DROP}
    if a.get('pass_'): t['pass'] = a['pass_']
    if a.get('site'): t['site'] = [urlparse(a['site']).netloc.replace('www.', ''), a['site']]
    if a.get('pl'): t['sPrice'] = a['pl']
    if a.get('hl') and a['id'] not in WEEK: t['sHours'] = a['hl']
    if a['cat'] == 'shop': t.update(cat='open', tier='購物', shop=True, shopStreet=True, cold=True)
    if a['cat'] == 'vap': t['tier'] = None
    lab = lab_of(a)
    if lab: t['lab'] = lab
    if a.get('gq'): GQ[a['id']] = a['gq'] + ', Venezia'
    spots.append(t)
# default lodging = an EXAMPLE spot near Piazza San Marco, not hers (2026-11-27: she stays at a B&B — the address is her room,
# too dangerous on a public map). People set their own with 改成我的住宿 (kept only in their browser).
spots.append(dict(id='hotel', cat='base', name='範例住宿（聖馬可廣場）', latin='範例位置', mapName='HOTEL', sPrice='範例住宿',
                  feature='這是範例位置，方便看各景點從市中心走過去要多久。點「改成我的住宿」換成你自己的住宿，只會存在你自己的瀏覽器。'))
LL['hotel'] = [45.43430, 12.33810]; GQ['hotel'] = 'Piazza San Marco, Venezia'
# 購物: a placeholder shop until she sends the real ones (2026-11-27)
spots.append(dict(id='s_test', cat='open', tier='購物', shop=True, compact=True, name='test', latin='Test shop（暫放）',
                  feature='測試用的暫放店家，之後會換成真的店。', sHours='10:00–19:30', sTime='逛街', sPrice='免費逛',
                  hours=['測試資料'], price='免費逛', tips=['這是暫放的測試店家。'], when='逛街時順路', stay='約 15 分鐘'))
LL['s_test'] = [45.43745, 12.33660]   # Salizada Pio X, near Rialto

# water-bus stops (yellow V) and traghetto crossings
VAP = [dict(id=a['id'], ll=LL[a['id']], name=VAPL[a['id']]['name'], lines=VAPL[a['id']]['lines']) for a in ALL if a['cat'] == 'vap']
FERRY = []
for a in ALL:
    if a.get('cross'):
        x1, y1, x2, y2 = a['cross']; d = [LL[a['id']][0] - aff(a['x'], a['y'])[0], LL[a['id']][1] - aff(a['x'], a['y'])[1]]
        FERRY.append([[p[0] + d[0], p[1] + d[1]] for p in (aff(x1, y1), aff(x2, y2))])

# shopping streets: pink, name in Chinese + the Italian on the street signs; clicking opens the street's card
shop_streets = []
for sid, d in zip(SHOP_IDS, SHOP_PATHS):
    pts = [aff(float(x), float(y)) for x, y in re.findall(r'([\d.]+) ([\d.]+)', d)]
    shop_streets.append(dict(id=sid, name=SHOPL[sid]['name'] + ' ' + SHOPL[sid]['orig'], pts=pts, at=0.5, cls='shop-street', minZoom=16.25))

days = [dict(k='0212', date='2/12', wd=4), dict(k='0213', date='2/13', wd=5), dict(k='0214', date='2/14', wd=6), dict(k='0215', date='2/15', wd=0)]   # shown one week later than her real stay (privacy, 2026-11-27)
CITY = {
  'key': 'venice', 'name': '威尼斯', 'title': '威尼斯', 'center': [45.4365, 12.3330], 'farKm': 15,
  'bounds': [[45.4255, 12.3150], [45.4470, 12.3530]], 'homeSpot': 'rialto', 'homeZoom': 15.5,
  'unitM': round(UNIT_M, 4), 'river': CANAL, 'riverLabel': dict(ll=[45.43615, 12.33140], text='大運河 Canal Grande'),
  'wall': None, 'streets': shop_streets, 'days': days,
  'tourSpots': ['piazza', 'rialto', 'accademia', 'salute', 'sanmarco'], 'hideSpot': 'bovolo',
  'demo': [dict(id='sanmarco', time='09:30', note='先上官網預約時段'), dict(id='ducale', time='11:00', note=''), dict(id='rialto', time='14:00', note='')],
}
city_js = 'const CITY = ' + json.dumps(CITY, ensure_ascii=False) + ';\n'
city_js += '''CITY.tourExtra = [
  { sel: ".icon-btn.shop-btn", t: "購物", x: "地圖上粉紅色的路是購物街，點路名看介紹；按這顆會再加上店家（粉紅色實心框）。" }
];
'''

CAT = '''const CAT = {
  paid: { label: "需購票／有營業時限", color: "var(--paid)" },
  free: { label: "免費景點", color: "var(--free)" },
  open: { label: "全天無時限", color: "var(--open)" },
  base: { label: "住宿與交通", color: "var(--ink)" },
  vap: { label: "水上巴士站", color: "var(--vap)" }
};'''
data = ('<script>\n' + CAT + '\nconst SPOTS = ' + json.dumps(spots, ensure_ascii=False) + ';\nconst LL = ' + json.dumps(LL)
        + ';\nconst VAP = ' + json.dumps(VAP, ensure_ascii=False) + ', FERRY_CROSS = ' + json.dumps(FERRY) + ';\n')

out = T
# Lucca-only pieces of the template
# (the hand-drawn Venice uses Lucca's label sizes, 19 / 14.5, so <style id="geo-city"> stays)
out = re.sub(r'<style id="lucca-only">.*?</style>\n?', '', out, count=1, flags=re.S)
out, _n = re.subn(r'<button class="icon-btn shop-btn lucca-only"', '<button class="icon-btn shop-btn"', out); assert _n == 2   # Venice keeps the 購物 buttons
# ---- data, days, city ----
i = out.index('<script>\nconst CAT = {'); j = out.index('const DKEY = ', i)
out = out[:i] + data + out[j:]
out = out.replace('const DKEY = "trip-days-lucca"', 'const DKEY = "trip-days-venice"', 1)
out, n = re.subn(r'const WEEK = \{.*?\}, WEEK_PREFIX = \{.*?\}, WEEK_NODIM = new Set\(\[.*?\]\);',
                 lambda m: 'const WEEK = ' + json.dumps(WEEK, ensure_ascii=False) + ', WEEK_PREFIX = {}, WEEK_NODIM = new Set([]);', out, count=1, flags=re.S)
assert n == 1
out, n = re.subn(r'const CITY = \{.*?\n\};\n', lambda m: city_js, out, count=1, flags=re.S); assert n == 1
out, n = re.subn(r'CITY\.unitM = [\d.]+;\n', '', out, count=1); assert n == 1
out = out.replace('const VKEY = "trip-visited-lucca"', 'const VKEY = "trip-visited-venice"', 1)
out, n = re.subn(r'const GQ = [^\n]*', lambda m: 'const GQ = ' + json.dumps(GQ, ensure_ascii=False) + ';', out, count=1); assert n == 1
out = out.replace('const REPORT_MAP = "盧卡";', 'const REPORT_MAP = "威尼斯";', 1)
# 星期幾去: Venice days are Fri–Sun (spec 2026-11-15)
out = re.sub(r'(<button class="chip day" type="button" data-day="(\d)" aria-pressed=")(true|false)',
             lambda m: m.group(1) + ('true' if m.group(2) in '456' else 'false'), out)
# 水上巴士站 chip after 冷門時段
out, n = re.subn(r'(<button class="chip cold" id="f-cold"[^>]*>.*?</button>)',
                 lambda m: m.group(1) + '<button class="chip vap-chip" type="button" aria-pressed="true" style="--c:var(--vap)" data-tip="地圖上的小黃點：水上巴士站"><span class="dot"></span>水上巴士站</button>', out, count=1, flags=re.S)
assert n == 1

# ---- drawer: Rome's, with the same real-map patches ----
dj = RH[RH.index('/* ---- Drawer ---- */'):RH.index('</script>', RH.index('/* ---- Drawer ---- */'))]
dj = re.sub(r'\n\s*\$\{s\.fromHotel \? `<div><dt>從飯店出發</dt>.*?: ""\}', '', dj, count=1)
dj = dj.replace('|| s.fromHotel ', '')
dj, _n = re.subn(r'const STRIKE_IDS = \[[^\]]*\];', 'const STRIKE_IDS = ["station", "proma"];', dj, count=1); assert _n == 1
src = open(LR + 'build_real.py').read()
a = src.index('drawer_js = drawer_js.replace(\n'); b = src.index("assert 'planToggle' in drawer_js and 'PDAYS.map' in drawer_js")
ns = {'drawer_js': dj}; exec(src[a:b], ns); dj = ns['drawer_js']
for k in ('planToggle', 'h-change', 'hotelFromLine', 'bindMineEdit', 'bindHotel'): assert k in dj, k
dj = dj.replace('例如：Hotel Ilaria', '例如：你的旅館或民宿名稱')
dj, _n = re.subn(r'\n\s*\$\{s\.stars \? `<p class="stars".*?</p>` : ""\}', '', dj, count=1); assert _n == 1
i = out.index('/* ---- Drawer ---- */'); j = out.index('</script>', i)
out = out[:i] + dj + '\n' + open(OUT + 'venice_extra.js').read() + out[j:]

# ---- page text ----
rep = [
  ('<title>盧卡古城景點地圖（真地圖版）</title>', '<title>威尼斯景點地圖（真地圖版）</title>'),
  ('<h1>盧卡古城景點地圖</h1>', '<h1>威尼斯景點地圖</h1>'),
  ('aria-label="盧卡古城地圖"', 'aria-label="威尼斯地圖"'),
  ('content="盧卡地圖"', 'content="威尼斯地圖"'),
  ('travelplanner-kaili.github.io/lucca/', 'travelplanner-kaili.github.io/venice/'),
  ('travelplanner-kaili.github.io/lucca', 'travelplanner-kaili.github.io/venice'),
  ('「盧卡地圖」圖示', '「威尼斯地圖」圖示'),
  ('Hotel Ilaria', '範例住宿'),
  ('43.8429, 10.5027', '45.4375, 12.3360'),
  ('最後只留城牆、道路和景點', '最後只留運河和景點'),
  ('（只留城牆、主要道路、購物商圈和景點）', '（只留大運河、購物街和景點）'),
  ('只留城牆、道路和景點', '只留運河和景點'),
  ('隱藏底圖：只留城牆、道路和景點', '隱藏底圖：只留運河和景點'),
  ('回到整個古城', '回到整張地圖'),
  ('「星期幾去」（預設是週三）', '「星期幾去」（預設是週五六日）'),
  ('盧卡古城', '威尼斯'),
]
for x, y in rep: out = out.replace(x, y)
for x, y in [('這是作者住的旅館（範例）。', '這是範例位置。'), ('" 是作者住的旅館。', '" 是範例位置。'),
             ('這是作者住的旅館，換成你的旅館', '這是範例位置，換成你的住宿')]:
    assert x in out, x; out = out.replace(x, y)
out = re.sub(r'<div class="eyebrow">[^<]*</div>', '<div class="eyebrow">Venezia · Veneto</div>', out, count=1)
# the location note (build_real.py) also under the drawer's forms (住宿, 自己加的點), which come from this city's own drawer
_lh = re.search(r'<small class="loc-help">.*?</small>', out).group(0)
out, _n = re.subn(r'(placeholder="Google 地圖網址，或 [\d.]+, [\d.]+"></label>)(?!<small class="loc-help">)', lambda m: m.group(1) + _lh, out)
assert out.count('<small class="loc-help">') == 3, out.count('<small class="loc-help">')

# ---- FAQ: Venice's 購物 and 水上巴士 questions join the basics (like Rome) ----
def faq_item(title):
    return re.search(r'<li class="faq-item"><p class="faq-q"><span class="n">Q\d+</span><span>' + re.escape(title) + r'</span>.*?</li>', H, flags=re.S).group(0)
shop_q = faq_item('想逛街買東西要去哪裡？'); vap_q = faq_item('地圖上黃色的 V 是什麼？').replace('地圖上黃色的 V 是什麼？', '地圖上的小黃點是什麼？')
assert '地圖上橘色的路' in shop_q; shop_q = shop_q.replace('地圖上橘色的路', '地圖上粉紅色的路')
assert '藍綠色小船則是' in vap_q; vap_q = vap_q.replace('藍綠色小船則是', '藍綠色的點和大運河上的短線則是')
fi = out.index('<section class="faq"'); fj = out.index('</ol></section>\n</div>', fi) + len('</ol></section>')
faq = out[fi:fj]
num2title = dict(re.findall(r'<span class="n">(Q\d+)</span><span>([^<]*)</span>', faq))
def to_ref(m):
    body = re.sub(r'Q\d+', lambda q: '[[ref:%s]]' % num2title[q.group(0)] if q.group(0) in num2title else q.group(0), m.group(2))
    return m.group(1) + body + m.group(3)
faq = re.sub(r'(<p class="faq-a">)(.*?)(</p>)', to_ref, faq, flags=re.S)
faq = re.sub(r'(<p class="faq-gnote">)(.*?)(</p>)', to_ref, faq, flags=re.S)
anchor = re.search(r'<li class="faq-item"><p class="faq-q"><span class="n">Q\d+</span><span>手機上地圖太小？</span>', faq); assert anchor
faq = faq[:anchor.start()] + shop_q + vap_q + faq[anchor.start():]
k = [0]
def rn(m): k[0] += 1; return '<span class="n">Q%d</span>' % k[0]
faq = re.sub(r'<span class="n">Q\d+</span>', rn, faq)
title2num = {t: n for n, t in re.findall(r'<span class="n">(Q\d+)</span><span>([^<]*)</span>', faq)}
faq = re.sub(r'\[\[ref:([^\]]+)\]\]', lambda m: title2num[m.group(1)], faq)
out = out[:fi] + faq + out[fj:]

# ---- styles: Venice colours, canal, water bus, ferries, shops (Rome's 購物 look) ----
css = '''<style>
/* ===== Venice ===== */
:root { --shop-street: #C8457F; --ferry: #0E7C86; --vap: #E2B007; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --shop-street: #F08CBA; --ferry: #3FB6C0; --vap: #F2C230; } }
:root[data-theme="dark"] { --shop-street: #F08CBA; --ferry: #3FB6C0; --vap: #F2C230; }
.icon-btn.shop-btn { border-color: var(--shop-street); color: var(--shop-street); }
.icon-btn.shop-btn[aria-pressed="true"] { background: var(--shop-street); color: var(--paper); }
.ic.ic-shop { border-color: var(--shop-street); color: var(--shop-street); }
.spot.shopbox .tab { background: var(--c); }
.spot.shopbox .tab .t-name, .spot.shopbox .tab .t-more { color: var(--paper); }
.leaflet-pane path.street-band.shop-street { stroke: var(--shop-street); stroke-opacity: .5; cursor: pointer; }
#lmap.base-faded .leaflet-pane path.street-band.shop-street { stroke-opacity: .7; }
.street-name.shop-street span { color: var(--shop-street); cursor: pointer; pointer-events: auto; }
.street-name.shop-street span:hover { text-decoration: underline; }
/* the Grand Canal stays clear (she finds her way by the canals): same strength as the Tiber rule */
.leaflet-pane path.ferry-line { stroke: var(--ferry); stroke-width: 3; stroke-dasharray: 5 4; stroke-linecap: round; fill: none; }
.vap-mark .v { position: absolute; left: -12px; top: -12px; width: 24px; height: 24px; border-radius: 50%; cursor: pointer; font-size: 0; }   /* tap area */
.vap-mark .v::after { content: ""; position: absolute; left: 7px; top: 7px; width: 10px; height: 10px; border-radius: 50%; background: var(--vap); }   /* 2026-11-27: a small solid yellow dot (the V circles were too loud) */
.vap-mark .vl { position: absolute; left: 9px; top: -8px; white-space: nowrap; font: 700 11px var(--f-body); color: var(--ink); text-shadow: 0 0 3px var(--paper), 0 0 3px var(--paper), 0 0 2px var(--paper); cursor: pointer; }
.vap-mark .vl b { color: #8A6A00; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .vap-mark .vl b { color: var(--vap); } }
:root[data-theme="dark"] .vap-mark .vl b { color: var(--vap); }
#lmap.vap-small .vap-mark .vl { display: none; }
#lmap.dist .vap-mark, #lmap.planning .vap-mark { opacity: .45; }
.chip.vap-chip .dot { background: var(--vap); }
.tip-map { white-space: nowrap; }
dd.tr h4 { margin: 8px 0 4px; font-size: 13px; }
</style>
'''
out = out.replace('</head>', css + '</head>', 1)
MAP_UPDATED = re.search(r'const MAP_UPDATED = "([^"]+)"', out).group(1)
open(OUT + 'venice-real.html', 'w').write(out)
open(OUT + 'version.json', 'w').write(json.dumps({'updated': MAP_UPDATED}))
print('ok', len(out), 'spots', len(spots), 'vap', len(VAP), 'ferries', len(FERRY), 'unitM', round(UNIT_M, 3))
