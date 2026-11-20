import json, math, sys
sys.path.insert(0, "/home/claude/rome")
from spots import SPOTS
from notes import UPDATES, NEW, APPEND_TIPS, APPEND_LINKS, WEEK, WEEK_PREFIX, WEEK_NODIM
from weeklabel import compact
for s in SPOTS:
    s.update(UPDATES.get(s["id"], {}))
SPOTS[-2:-2] = NEW   # keep hotel/station last
for s in SPOTS:
    if s["id"] in APPEND_TIPS: s["tips"] = list(s.get("tips") or []) + APPEND_TIPS[s["id"]]
    if s["id"] in APPEND_LINKS: s["links"] = list(s.get("links") or []) + APPEND_LINKS[s["id"]]
    if s["id"] in WEEK: s["week"] = {"d": WEEK[s["id"]], "p": WEEK_PREFIX.get(s["id"], ""), "nodim": s["id"] in WEEK_NODIM, "keep": s["id"] in ("colonna",)}
    if s["id"] in WEEK and s["id"] not in ("colonna",) and s.get("sHours"):
        s["sHours"] = compact(WEEK[s["id"]], WEEK_PREFIX.get(s["id"], ""))   # map label = main time + exceptions, layout plans for its width
        if len(s["sHours"]) > 24 and "（" in s["sHours"]:   # long: exceptions go on a second line so the box stays narrow
            s["sHours"], _x = s["sHours"].split("（", 1); s["sHours2"] = "（" + _x

S = 2.2                     # meters per SVG unit
LON0, LAT0 = 12.4475, 41.9205
KX = 111320 * math.cos(math.radians(41.9)) / S
KY = 110950 / S
def proj(lat, lon):
    return ((lon - LON0) * KX, (LAT0 - lat) * KY)
def dist_m(a, b):
    (x1, y1), (x2, y2) = proj(*a), proj(*b)
    return math.hypot(x2 - x1, y2 - y1) * S

FN, FL = 28, 21             # font sizes: name / other lines
def tw(s, fs):
    w = 0
    for c in s:
        o = ord(c)
        if c in "–": w += 0.55 * fs
        elif o > 0x2e80: w += fs
        elif c in "il.,:;'| ()": w += 0.32 * fs
        elif c.isupper(): w += 0.66 * fs
        else: w += 0.56 * fs
    return w

# ---- tiers (user list 2026-11-13): 主要 + 推薦 shown by default, everything else is 次要 (the old 附加景點) ----
TIER_MAIN = {"colosseo", "foro", "palatino", "pantheon", "vaticani", "sistina", "sanpietro", "borghese", "trevi",
             "navona", "spagna", "castello", "popolo", "pincio", "venezia"}
TIER_REC = {"vincoli", "campidoglio", "ignazio", "luigi", "carlino", "monti",
            "popolochurch", "miracoli", "montesanto", "campo", "giubbonari", "colonna", "gioacchino", "agostino", "minerva", "smtrastevere", "vittoria", "gesu", "trastevere", "coronari", "ghetto", "bocca"}
RUSH = {"borghese", "vaticani", "sistina", "colosseo", "foro", "palatino"}   # tickets sell out: book the moment they open
for s in SPOTS:
    if s.get("cat") == "base": continue
    s["tier"] = "主要" if s["id"] in TIER_MAIN else "推薦" if s["id"] in TIER_REC else "次要"
    s["sup"] = s["tier"] == "次要"
    if s["id"] in RUSH: s["rush"] = True
COMPACT = {"minerva", "doria", "barberini", "rinascente", "giubbonari", "agostino"}   # 附加景點 squeezed into the centre
for s in SPOTS:
    s["x"], s["y"] = [round(v, 1) for v in proj(s["lat"], s["lon"])]
    allday = s["cat"] in ("open", "base")
    if s["cat"] == "open": s["sPrice"] = "免費"
    # map label lines: name, hours (not for all-day places), mass, price (left out when free); no stars on the map
    free = s["sPrice"].startswith("免費") or s["cat"] == "open"
    nm = s.get("mapName", s["name"])
    small = [] if s.get("mapName") else ([] if allday else [s["sHours"]] + ([s["sHours2"]] if s.get("sHours2") else [])) + (["彌撒 " + s["sMass"]] if s.get("sMass") else []) + ([] if free else [s["sPrice"]])
    s["mapLines"] = small
    s["W"] = max([tw(nm, FN)] + [tw(t, FL) for t in small]) + 26
    s["H"] = 50 if not small else 68 + 30 * (len(small) - 1) + 14
    if s.get("tier") == "推薦" and not allday:   # 推薦: same lines, smaller type (name 24px, lines 18px)
        s["mid"] = True
        s["W"] = max([tw(nm, 24)] + [tw(t, 18) for t in small]) + 22
        s["H"] = 44 if not small else 55 + 22 * (len(small) - 1) + 11
    if s.get("sup"):   # 次要: name-only labels
        s["compact"] = True
        s["W"] = tw(nm, 26) + 24; s["H"] = 44
    if "area" in s:
        s["areaPts"] = [[round(v, 1) for v in proj(a, b)] for a, b in s.pop("area")]

# hotel / station distances
H = next(s for s in SPOTS if s["id"] == "hotel")
T = next(s for s in SPOTS if s["id"] == "termini")
def d(a, b): return dist_m((a["lat"], a["lon"]), (b["lat"], b["lon"]))
def near(id_): return next(s for s in SPOTS if s["id"] == id_)
fmt = lambda m: f"{round(m/10)*10:.0f} 公尺" if m < 1000 else f"{m/1000:.1f} 公里"
H["feature"] = H["feature"].replace("DIST",
  f"直線距離：萬神殿約 {fmt(d(H, near('pantheon')))}、特雷維噴泉約 {fmt(d(H, near('trevi')))}、"
  f"西班牙階梯約 {fmt(d(H, near('spagna')))}、羅馬競技場約 {fmt(d(H, near('colosseo')))}、特米尼車站約 {fmt(d(H, T))}。")
T["feature"] = T["feature"].replace("DIST", f"距飯店直線約 {fmt(d(H, T))}，計程車約 10～15 分鐘，或搭 85 號公車（見下方交通方式）。")
for s in SPOTS:
    if s["cat"] != "base" and "fromHotel" not in s:
        m = d(H, s); s["fromHotel"] = f"直線約 {fmt(m)}" + (f"，步行約 {round(m*1.3/80/5)*5} 分鐘" if m < 3000 else "")
print("colo->cara", round(d(near("colosseo"), near("caracalla"))), "hotel->cara", round(d(H, near("caracalla"))))

# ---------- base geometry ----------
TIBER = [(41.9230,12.4668),(41.9180,12.4690),(41.9140,12.4705),(41.9100,12.4724),(41.9065,12.4741),
         (41.9040,12.4728),(41.9024,12.4705),(41.9016,12.4668),(41.9005,12.4648),(41.8985,12.4634),
         (41.8955,12.4657),(41.8925,12.4705),(41.8913,12.4740),(41.8905,12.4770),(41.8893,12.4793),
         (41.8862,12.4795),(41.8830,12.4778),(41.8805,12.4742),(41.8780,12.4718),(41.8760,12.4700),(41.8735,12.4690)]
STREETS = [
 ("Via del Corso", [(41.9105,12.4766),(41.9030,12.4795),(41.8980,12.4815),(41.8962,12.4822)]),
 ("Via dei Fori Imperiali", [(41.8955,12.4835),(41.8935,12.4860),(41.8912,12.4900)]),
 ("Via Nazionale", [(41.8968,12.4858),(41.8990,12.4900),(41.9010,12.4935),(41.9027,12.4960)]),
 ("Via Cavour", [(41.8993,12.4985),(41.8960,12.4940),(41.8935,12.4892)]),
 ("Via della Conciliazione", [(41.9022,12.4583),(41.9022,12.4650)]),
 ("Corso Vittorio Emanuele II", [(41.9005,12.4653),(41.8988,12.4700),(41.8962,12.4745),(41.8958,12.4770)]),
 ("Via del Babuino", [(41.9105,12.4770),(41.9062,12.4818)]),
 ("Via dei Coronari", [(41.90040,12.47270),(41.90049,12.47018),(41.90065,12.46880),(41.90072,12.46760)]),
 ("Via dei Giubbonari", [(41.8954,12.4723),(41.8947,12.4733),(41.8943,12.4742),(41.8940,12.4750)]),
]
PARK = [(41.9112,12.4771),(41.9150,12.4772),(41.9182,12.4830),(41.9178,12.4935),(41.9135,12.4955),(41.9090,12.4890),(41.9093,12.4815)]
VATICAN = [(41.9070,12.4475),(41.9075,12.4535),(41.9045,12.4565),(41.9020,12.4575),(41.9005,12.4560),(41.8995,12.4500),(41.9025,12.4462)]

P = lambda pts: [[round(v, 1) for v in proj(a, b)] for a, b in pts]
tiber, park, vat = P(TIBER), P(PARK), P(VATICAN)

def rbox(x, y, w, h, ang):
    # bbox of text rotated about (x,y) baseline-left
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    pts = [(0, 4), (w, 4), (w, -h), (0, -h)]
    xs = [x + px*c - py*s_ for px, py in pts]; ys = [y + px*s_ + py*c for px, py in pts]
    return (min(xs), min(ys), max(xs), max(ys))

# 通俗中文街名 (user-requested 2026-11-15): shown before the Italian name; streets without a widely used Chinese name keep the Italian only
from streetzh import STREET_ZH
zh = lambda n: f"{STREET_ZH[n]} {n}" if n in STREET_ZH else n
SOFT_OBS = []   # street labels squeezed in by the fallback: hidden in the slim (names / distance) modes
HL_STREETS = {"Via dei Giubbonari", "Via dei Coronari"}   # streets the user asked to mark: drawn in the accent colour
from notes import SHOP_STREETS, SHOP_NEW as _SN
SHOP_NAMES = {nm for _, _, nm in SHOP_STREETS if nm}
street_out, obstacles = [], []
# 立體地標: the drawing stands on the pin, so street names and labels keep clear of it like any other obstacle
ICON_BOX = {"colosseo": (-46, -72, 52, 10), "pantheon": (-28, -54, 32, 7), "trevi": (-38, -56, 42, 9), "spagna": (-32, -71, 36, 7)}   # drawing extent around the pin (scale: colosseo 1.3, pantheon 0.85, trevi/spagna 1.0)
ICON_OBS = [(z["x"] + ICON_BOX[z["id"]][0], z["y"] + ICON_BOX[z["id"]][1], z["x"] + ICON_BOX[z["id"]][2], z["y"] + ICON_BOX[z["id"]][3]) for z in SPOTS if z["id"] in ICON_BOX]
obstacles += ICON_OBS
_hit_icon = lambda bb: any(not (bb[2] + 6 <= b[0] or b[2] + 6 <= bb[0] or bb[3] + 6 <= b[1] or b[3] + 6 <= bb[1]) for b in ICON_OBS)
def _street_label(name, pts, label, last):
    pp = P(pts)
    if name in SHOP_NAMES:   # labelled below as a shopping street
        street_out.append(dict(d=pp, name="", tx=0, ty=0, rot=0, hl=name in HL_STREETS, soft=False)); return True
    # label on the longest segment
    best = max(range(len(pp)-1), key=lambda i: math.dist(pp[i], pp[i+1]))
    (x1, y1), (x2, y2) = pp[best], pp[best+1]
    if x2 < x1: (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    L = math.dist((x1, y1), (x2, y2)); w = tw(label, 23)
    nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
    allpins = [proj(s["lat"], s["lon"]) for s in SPOTS]
    cands = []
    for t in [i/20 for i in range(21)]:
        if L*(1-t) < w*0.9: continue
        for side in (10, -26):
            bx, by = x1 + (x2-x1)*t - nx*side, y1 + (y2-y1)*t - ny*side
            bb = rbox(bx, by, w, 22, ang)
            clear = min([math.dist(((bb[0]+bb[2])/2,(bb[1]+bb[3])/2), q) for q in allpins])
            if not _hit_icon(bb) and not any(bb[0]-30 < q[0] < bb[2]+30 and bb[1]-30 < q[1] < bb[3]+30 for q in allpins):
                cands.append((-clear, bx, by))   # as far from the spots as the street allows
    soft = False
    if not cands:
        soft = name not in HL_STREETS
        # crowded or short street: centre the label on the whole street, letting it run past the ends
        (x1, y1), (x2, y2) = pp[0], pp[-1]
        if x2 < x1: (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1)); L = math.dist((x1, y1), (x2, y2))
        nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        for side in (-26, 10, -44, 28, -62, 46):
            for sh in (0, 20, -20, 40, -40, 60, -60):
                bx = (x1 + x2) / 2 - ux * (w / 2 - sh) - nx * side
                by = (y1 + y2) / 2 - uy * (w / 2 - sh) - ny * side
                bb = rbox(bx, by, w, 22, ang)
                if not _hit_icon(bb) and not any(bb[0]-12 < q[0] < bb[2]+12 and bb[1]-12 < q[1] < bb[3]+12 for q in allpins):
                    cands.append((abs(side) + abs(sh), bx, by))
    if not cands:
        for side in (-26, 10, -44, 28, -62, 46, -80, 64):
            for sh in (0, 20, -20, 40, -40, 60, -60, 90, -90):
                bx = (x1 + x2) / 2 - ux * (w / 2 - sh) - nx * side
                by = (y1 + y2) / 2 - uy * (w / 2 - sh) - ny * side
                bb = rbox(bx, by, w, 22, ang)
                if not _hit_icon(bb) and not any(bb[0] < q[0] < bb[2] and bb[1] < q[1] < bb[3] for q in allpins):
                    cands.append((abs(side) + abs(sh) + 100, bx, by))
    if cands:
        _, tx, ty = min(cands)
    else:
        if not last: return False
        print("street label dropped:", name); street_out.append(dict(d=pp, name="", tx=0, ty=0, rot=0)); return True
    street_out.append(dict(d=pp, name=label, tx=round(tx,1), ty=round(ty,1), rot=round(ang,1), hl=name in HL_STREETS, soft=soft))
    obstacles.append(rbox(tx, ty, w, 22, ang))
    if soft: SOFT_OBS.append(obstacles[-1])
    return True
for name, pts in STREETS:
    _vs = [zh(name)] + ([STREET_ZH[name]] if name in STREET_ZH else [])   # bilingual first; Chinese only if that does not fit
    for _i, _v in enumerate(_vs):
        if _street_label(name, pts, _v, _i == len(_vs) - 1): break
_ov = lambda a, b, pad=0: not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])
_allpins = [proj(z["lat"], z["lon"]) for z in SPOTS + _SN]
shop_street_labels = []
for sid, pts, nm in sorted(SHOP_STREETS, key=lambda t: -len(t[2])):
    if not nm: continue
    pp = [proj(a, b) for a, b in pts]
    best = None
    for si in range(len(pp) - 1):
        (x1, y1), (x2, y2) = pp[si], pp[si + 1]
        if x2 < x1: (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1)); L = math.dist((x1, y1), (x2, y2))
        w = tw(zh(nm), 21); ux, uy = (x2 - x1) / L, (y2 - y1) / L
        nx_, ny_ = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
        for t in [i / 10 for i in range(-20, 31)]:
            for side in (7, -7, 20, -20, 34, -34, 48, -48, 64, -64, 80, -80):
                bx = x1 + (x2 - x1) * t - ux * w / 2 - nx_ * side
                by = y1 + (y2 - y1) * t - uy * w / 2 - ny_ * side
                bb = rbox(bx, by, w, 18, ang)
                hit = sum(1 for b in obstacles if _ov(bb, b, 4)) * 10 + sum(1 for q in _allpins if bb[0] - 10 < q[0] < bb[2] + 10 and bb[1] - 10 < q[1] < bb[3] + 10) * 4
                sc = hit * 1000 + max(0, abs(t - 0.5) - 0.5) * 300 + abs(t - 0.5) * 30 + abs(side) * 2
                if best is None or sc < best[0]: best = (sc, bx, by, ang, bb)
    _, bx, by, ang, bb = best
    obstacles.append(bb)   # spot labels keep clear of the shopping street names
    shop_street_labels.append(dict(id=sid, name=zh(nm), x=round(bx, 1), y=round(by, 1), rot=round(ang, 1)))
vx = min(p[0] for p in vat) - 22; vy = sum(p[1] for p in vat) / len(vat)
vat_lbl = dict(x=round(vx,1), y=round(vy,1))
obstacles.append((vx - 22, vy - 70, vx + 8, vy + 70))
river_lbl = dict(x=proj(41.8975,12.4600)[0], y=proj(41.8975,12.4600)[1], text="台伯河 Tevere")
obstacles.append((river_lbl["x"]-4, river_lbl["y"]-20, river_lbl["x"]+tw("台伯河 Tevere",19)+4, river_lbl["y"]+6))
from marks import MONTI_CHAIN
for _m in MONTI_CHAIN:
    _x, _y = proj(_m[3], _m[4]); _x += _m[5][0]; _y += _m[5][1]
    obstacles.append((_x - 18, _y - 18, _x + 18, _y + 18))
# spots whose label must sit below the pin and keep off a neighbourhood area (so the area stays readable)
BELOW = {"vincoli": "monti"}

# ---------- label placement ----------
xs = [s["x"] for s in SPOTS]; ys = [s["y"] for s in SPOTS]
VB = [min(xs) - 330, min(ys) - 250, max(xs) + 330, max(ys) + 220]
pins = [(s["x"], s["y"]) for s in SPOTS]

def overlap(a, b, pad=0):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])
def seg_rect(p, q, r):
    # sample along the segment
    n = max(2, int(math.dist(p, q) / 6))
    for i in range(1, n):
        x = p[0] + (q[0]-p[0]) * i / n; y = p[1] + (q[1]-p[1]) * i / n
        if r[0] - 4 <= x <= r[2] + 4 and r[1] - 4 <= y <= r[3] + 4: return True
    return False
def seg_pt(p, q, c, rad):
    px, py = q[0]-p[0], q[1]-p[1]; L2 = px*px + py*py
    t = max(0, min(1, ((c[0]-p[0])*px + (c[1]-p[1])*py) / L2)) if L2 else 0
    return math.dist((p[0]+t*px, p[1]+t*py), c) < rad
def nearest(box, p):
    return (max(box[0], min(p[0], box[2])), max(box[1], min(p[1], box[3])))

order = sorted(SPOTS, key=lambda s: -sum(1 for t in SPOTS if math.dist((s["x"],s["y"]),(t["x"],t["y"])) < 450))
def place(order):
    global placed_boxes, placed_leaders
    placed_boxes, placed_leaders = list(FIX_B), list(FIX_L)
    for s in order:
        best = None
        p = (s["x"], s["y"])
        for r in range(20, 900, 10):
            for k in range(48):
                a = 2*math.pi*k/48
                cx, cy = p[0] + r*math.cos(a), p[1] + r*math.sin(a)
                box = (cx - s["W"]/2, cy - s["H"]/2, cx + s["W"]/2, cy + s["H"]/2)
                if box[0] < VB[0]+8 or box[1] < VB[1]+8 or box[2] > VB[2]-8 or box[3] > VB[3]-8: continue
                if any(overlap(box, b, 6 if RELAX else 16) for b in placed_boxes): continue
                if any(overlap(box, o, 6) for o in obstacles): continue
                if s["id"] in BELOW:
                    if box[1] < p[1]: continue
                    _ar = next(z for z in SPOTS if z["id"] == BELOW[s["id"]]).get("areaPts")
                    if _ar and overlap(box, (min(q[0] for q in _ar), min(q[1] for q in _ar), max(q[0] for q in _ar), max(q[1] for q in _ar)), 8): continue
                PM = 12 if RELAX else 24
                if any(box[0]-PM < q[0] < box[2]+PM and box[1]-PM < q[1] < box[3]+PM for q in pins): continue
                e = nearest(box, p)
                if any(seg_rect(p, e, b) for b in placed_boxes): continue
                if any(seg_pt(p, e, q, 16) for q in pins if q != p): continue
                if not RELAX and any(seg_rect(L[0], L[1], box) for L in placed_leaders): continue
                if any(seg_rect(p, e, o) for o in obstacles): continue
                ln = math.dist(p, e)
                if ln < 22: continue
                if best is None or ln < best[0]: best = (ln, box, e)
            if best and r > best[0] + 120: break
        if not best:
            return s
        _, box, e = best
        s["lx"], s["ly"] = round(box[0], 1), round(box[1], 1)
        placed_boxes.append(box); placed_leaders.append(((s["x"], s["y"]), e))
    
    return None
import random
def run(order):
    global LAST_FAIL
    for attempt in range(40):
        fail = place(order)
        if fail is None: return True
        LAST_FAIL = fail['id']
        order.remove(fail); order.insert(0, fail)
    return False
import os
TRIALS = int(os.environ.get('TRIALS', '30'))
RELAX = False
random.seed(7)
FIX_B, FIX_L = [], []
base_order = list(order)
def search(subset, trials):
    best = None
    for trial in range(trials):
        o = list(subset)
        if trial: random.shuffle(o)
        if not run(o): continue
        lens = [math.dist(L[0], L[1]) for L in placed_leaders[len(FIX_L):]]
        score = sum(l*l for l in lens) + 30*max(lens)**2
        if best is None or score < best[0]:
            best = (score, {s["id"]: (s["lx"], s["ly"]) for s in subset}, list(placed_boxes), list(placed_leaders), max(lens))
    return best
def place_greedy(subset, obs, trials, size=lambda z: (z["W"], z["H"]), gap=6, pre_boxes=(), pre_leads=()):
    """Greedy ring search: each label as close to its own pin as possible. Boxes never overlap each other, other pins or
    obstacles; a leader never crosses a label and a label never sits on a leader. Best of `trials` random orders."""
    P_ = [(z["x"], z["y"]) for z in subset]
    def once(order):
        boxes, leads, pos = list(pre_boxes), list(pre_leads), {}
        for z in order:
            p = (z["x"], z["y"]); W_, H_ = size(z); best = None
            for strict in (True, False):   # nothing fits: let the leader cross labels as a last resort
                if best: break
                for r in range(18, 1100, 8):
                    for k in range(40):
                        a = 2 * math.pi * k / 40
                        cx, cy = p[0] + r * math.cos(a), p[1] + r * math.sin(a)
                        box = (cx - W_ / 2, cy - H_ / 2, cx + W_ / 2, cy + H_ / 2)
                        if box[0] < VB[0] + 8 or box[1] < VB[1] + 8 or box[2] > VB[2] - 8 or box[3] > VB[3] - 8: continue
                        if any(overlap(box, b, gap) for b in boxes): continue
                        if any(overlap(box, o, 3) for o in obs): continue
                        if any(box[0] - 9 < q[0] < box[2] + 9 and box[1] - 9 < q[1] < box[3] + 9 for q in P_): continue
                        e = nearest(box, p)
                        if strict and any(seg_rect(p, e, b) for b in boxes): continue
                        if strict and any(seg_rect(L[0], L[1], box) for L in leads): continue
                        ln = math.dist(p, e)
                        if best is None or ln < best[0]: best = (ln, box, e)
                    if best and r > best[0] + 40: break
            if not best: return None
            boxes.append(best[1]); leads.append((p, best[2])); pos[z["id"]] = (round(best[1][0], 1), round(best[1][1], 1))
        return pos, boxes
    dens = lambda z: -sum(1 for q in P_ if math.dist((z["x"], z["y"]), q) < 350)
    best = None
    for t in range(trials):
        o = sorted(subset, key=lambda z: (z.get("cat") != "base", dens(z)))
        if t: random.shuffle(o); o.sort(key=lambda z: z.get("cat") != "base")   # hotel/station first, next to their pins
        r_ = once(o)
        if not r_: continue
        pos = r_[0]
        sc = 0; mx = 0
        for z in subset:
            W_, H_ = size(z); bx, by = pos[z["id"]]
            l = math.dist((z["x"], z["y"]), nearest((bx, by, bx + W_, by + H_), (z["x"], z["y"]))); sc += l * l; mx = max(mx, l)
        sc += 20 * mx * mx
        if best is None or sc < best[0]: best = (sc, pos, mx)
    return best

# all spots together (two-phase left 附加景點 like 圖拉真市集 boxed in)
import hashlib
_key = hashlib.md5(json.dumps([[[s["id"], s["x"], s["y"], round(s["W"]), s["H"]] for s in SPOTS], [[round(v) for v in o] for o in obstacles]]).encode()).hexdigest()   # obstacles too: a new street label must re-run placement
_cache = "/home/claude/rome/.place_cache.json"
try: _c = json.load(open(_cache))
except Exception: _c = {}
if _c.get("key") == _key:
    b1 = (0, {k: tuple(v) for k, v in _c["pos"].items()}, [], [], _c["maxlen"]); print("normal layout from cache")
else:
    _g = place_greedy(list(SPOTS), obstacles, TRIALS)   # greedy: every label as close to its pin as possible
    b1 = (0, _g[1], [], [], _g[2]) if _g else None
    if b1: json.dump({"key": _key, "pos": b1[1], "maxlen": b1[4]}, open(_cache, "w"))
if b1 is None:
    # crowded centre (e.g. Pantheon / Minerva / Sant'Ignazio): retry with relaxed spacing before giving up
    print("normal layout: relaxing spacing (last fail", LAST_FAIL, ")"); RELAX = True
    b1 = search(list(base_order), TRIALS)
    if b1: json.dump({"key": _key, "pos": b1[1], "maxlen": b1[4]}, open(_cache, "w"))
    RELAX = False
if b1 is None: print("FAIL", LAST_FAIL); raise SystemExit
b2 = (0, {}, [], [], 0)
print("max leader", round(b1[4]))
pos = {**b1[1], **b2[1]}
for s in SPOTS: s["lx"], s["ly"] = pos[s["id"]]
# that full layout (附加景點 included) is used when 附加景點 or City Walk is on: keep it as ux/uy
for s in SPOTS: s["ux"], s["uy"] = s["lx"], s["ly"]
# default view hides 附加景點, so give the main spots their own roomier layout without them

MAIN = [s for s in SPOTS if not s.get("sup")]
pins = [(s["x"], s["y"]) for s in MAIN]
_mkey = hashlib.md5((_key + "|main").encode()).hexdigest()
_mcache = "/home/claude/rome/.place_cache_main.json"
try: _mc = json.load(open(_mcache))
except Exception: _mc = {}
if _mc.get("key") == _mkey:
    bm = (0, {k: tuple(v) for k, v in _mc["pos"].items()}); print("main-only layout from cache")
else:
    # pins sit so close together around the Pantheon that the strict spacing pushes labels far away;
    # the relaxed spacing still keeps labels apart but lets them sit next to their own pins
    bm = place_greedy(MAIN, obstacles, TRIALS)
    if bm: json.dump({"key": _mkey, "pos": bm[1], "maxlen": bm[2]}, open(_mcache, "w")); print("main-only max leader", round(bm[2]))
if bm:
    for s in MAIN: s["lx"], s["ly"] = bm[1][s["id"]]
else: print("main-only layout failed; default view uses the full layout")
pins = [(s["x"], s["y"]) for s in SPOTS]

# ================= 簡潔模式: name-only labels for every spot, as close to the pins as possible (nx/ny) =================
_nsize = lambda z: (tw(z.get("mapName", z["name"]), 26) + 24, 44 if z["cat"] != "base" or z.get("mapName") else 70)
_nkey = hashlib.md5((_key + "|names|" + json.dumps([[z["id"], round(_nsize(z)[0])] for z in SPOTS])).encode()).hexdigest()
_ncache = "/home/claude/rome/.place_cache_names.json"
try: _nc = json.load(open(_ncache))
except Exception: _nc = {}
if _nc.get("key") == _nkey: bn = (0, {k: tuple(v) for k, v in _nc["pos"].items()}); print("names layout from cache")
else:
    bn = place_greedy(SPOTS, [o for o in obstacles if o not in SOFT_OBS], TRIALS, _nsize)
    if bn: json.dump({"key": _nkey, "pos": bn[1]}, open(_ncache, "w")); print("names max leader", round(bn[2]))
    else: print("names layout FAIL")
if bn:
    for z in SPOTS: z["nx"], z["ny"] = bn[1][z["id"]]

# ================= 距離模式：names only + walking distance between spots =================
FS = 26
def walk(m):
    w = round(m * 1.3 / 50) * 50          # straight line x1.3 ≈ walking route
    mins = max(1, round(w / 80))          # 80 m per minute
    dist = f"{w} m" if w < 1000 else f"{w/1000:.1f} km"
    return f"{dist}・{mins} 分", w
N = len(SPOTS)
D2 = lambda i, j: dist_m((SPOTS[i]["lat"], SPOTS[i]["lon"]), (SPOTS[j]["lat"], SPOTS[j]["lon"]))
# minimum spanning tree (Prim)
def mst(nodes):
    nodes = list(nodes); inT, out = {nodes[0]}, set()
    while len(inT) < len(nodes):
        i, j = min(((i, j) for i in inT for j in nodes if j not in inT), key=lambda e: D2(*e))
        inT.add(j); out.add(tuple(sorted((i, j))))
    return out
# all spots, plus main spots only (so the network still connects when 附加景點 are hidden)
edges = mst(range(N)) | mst([i for i in range(N) if not SPOTS[i].get("sup")])
hi = next(i for i, s in enumerate(SPOTS) if s["id"] == "hotel")
for j in sorted((j for j in range(N) if j != hi), key=lambda j: D2(hi, j))[:4]:
    if any(k not in (hi, j) and D2(hi, k) + D2(k, j) < 1.1 * D2(hi, j) for k in range(N)): continue
    edges.add(tuple(sorted((hi, j))))
edges = sorted(edges, key=lambda e: D2(*e))
segs = [((SPOTS[i]["x"], SPOTS[i]["y"]), (SPOTS[j]["x"], SPOTS[j]["y"])) for i, j in edges]

elabels, eboxes = [], []
for (i, j), (p, q) in zip(edges, segs):
    txt, w = walk(D2(i, j))
    W, Hh = tw(txt, 19) + 18, 30
    ok = None
    if D2(i, j) * 1.3 < 160: elabels.append(dict(a=[round(v,1) for v in p], b=[round(v,1) for v in q], box=None, anc=None, text=txt, ids=[SPOTS[i]["id"], SPOTS[j]["id"]])); continue  # very short hops: line only, keeps crowded squares readable
    for off in [0, 18, -18, 34, -34, 52, -52, 72, -72, 95, -95]:
        for t in [0.5, 0.42, 0.58, 0.34, 0.66, 0.26, 0.74, 0.18, 0.82]:
            dx, dy = q[0]-p[0], q[1]-p[1]; L = math.hypot(dx, dy) or 1
            cx, cy = p[0] + dx*t - dy/L*off, p[1] + dy*t + dx/L*off
            box = (cx - W/2, cy - Hh/2, cx + W/2, cy + Hh/2)
            if any(overlap(box, b, 6) for b in eboxes): continue
            if any(box[0]-16 < r[0] < box[2]+16 and box[1]-16 < r[1] < box[3]+16 for r in pins): continue
            if any(overlap(box, o, 4) for o in obstacles): continue
            ok = box; anc = (p[0] + dx*t, p[1] + dy*t); break
        if ok: break
    if not ok:
        print("edge label skipped", SPOTS[i]["id"], SPOTS[j]["id"]); ok = None
    eboxes.append(ok) if ok else None
    elabels.append(dict(a=[round(v,1) for v in p], b=[round(v,1) for v in q],
                        box=[round(v,1) for v in ok] if ok else None, anc=[round(v,1) for v in anc] if ok else None, text=txt, ids=[SPOTS[i]["id"], SPOTS[j]["id"]]))

for s in SPOTS:
    s["sW"] = tw(s["name"], FS) + 24; s["sH"] = 44
    if s.get("stars"): s["sW"] += 10 + s["stars"] * 19
def place_simple(order):
    global sb, sl
    sb, sl = list(FIX_SB), list(FIX_SL)
    for s in order:
      p = (s["x"], s["y"])
      for relax in (False, True):   # crowded spot: second pass lets the leader pass closer to other pins / edge lines
        best = None
        for r in range(14, 500, 6):
              for k in range(48):
                  a = 2*math.pi*k/48
                  cx, cy = p[0] + r*math.cos(a), p[1] + r*math.sin(a)
                  box = (cx - s["sW"]/2, cy - s["sH"]/2, cx + s["sW"]/2, cy + s["sH"]/2)
                  if box[0] < VB[0]+8 or box[1] < VB[1]+8 or box[2] > VB[2]-8 or box[3] > VB[3]-8: continue
                  if any(overlap(box, b, 8) for b in sb): continue
                  if any(overlap(box, b, 6) for b in eboxes): continue
                  if any(overlap(box, o, 6) for o in obstacles): continue
                  if any(box[0]-14 < q[0] < box[2]+14 and box[1]-14 < q[1] < box[3]+14 for q in pins): continue
                  if not (RS or relax) and any(seg_rect(a_, b_, (box[0]+4, box[1]+4, box[2]-4, box[3]-4)) for a_, b_ in segs): continue
                  e = nearest(box, p)
                  if any(seg_rect(p, e, b) for b in sb + ([] if relax else eboxes)): continue
                  if any(seg_pt(p, e, q, 8 if relax else 14) for q in pins if q != p): continue
                  if any(seg_rect(L[0], L[1], box) for L in sl): continue
                  ln = math.dist(p, e)
                  if ln < 10: continue
                  if best is None or ln < best[0]: best = (ln, box, e)
              if best and r > best[0] + 80: break
        if best: break
      if not best: return s
      _, box, e = best
      s["slx"], s["sly"] = round(box[0], 1), round(box[1], 1)
      sb.append(box); sl.append((p, e))
    return None
FIX_SB, FIX_SL = [], []
RS = False
SFAIL = {}
def search_s(subset, trials):
    best = None
    for trial in range(trials):
        o = list(subset)
        if trial: random.shuffle(o)
        ok = False
        for attempt in range(60):
            f = place_simple(o)
            if f is None: ok = True; break
            SFAIL[f["id"]] = SFAIL.get(f["id"], 0) + 1
            o.remove(f); o.insert(0, f)
        if not ok: continue
        lens = [math.dist(a, b) for a, b in sl[len(FIX_SL):]]
        sc = sum(l*l for l in lens) + 30*max(lens)**2
        if best is None or sc < best[0]:
            best = (sc, {s["id"]: (s["slx"], s["sly"]) for s in subset}, list(sb), list(sl))
    return best
RS = False
for _o in SOFT_OBS: obstacles.remove(_o)
_kkey = hashlib.md5((_key + "|simple|" + json.dumps(sorted(elabels_key))).encode()).hexdigest() if "elabels_key" in dir() else hashlib.md5((_key + "|simple").encode()).hexdigest()
_kcache = "/home/claude/rome/.place_cache_simple.json"
try: _kc = json.load(open(_kcache))
except Exception: _kc = {}
if _kc.get("key") == _kkey:
    s1 = (0, {k: tuple(v) for k, v in _kc["pos"].items()}, [], []); print("simple layout from cache")
else:
    s1 = search_s(list(base_order), max(10, TRIALS // 2))
    if s1 is None:
        print("simple mode: relaxing edge-line rule"); RS = True
        s1 = search_s(list(base_order), max(10, TRIALS // 2))
    if s1: json.dump({"key": _kkey, "pos": s1[1]}, open(_kcache, "w"))
s2 = (0, {}, [], [])
print("simple fails:", sorted(SFAIL.items(), key=lambda x: -x[1])[:6]); print("simple mode placed:", s1 is not None, "edges", len(elabels))
spos = {**s1[1], **s2[1]}
for s in SPOTS: s["slx"], s["sly"] = spos[s["id"]]

# ================= 購物 view: shopping spots only, name-only labels, their own layout (shx/shy) =================
from notes import SHOP_NEW, SHOP_IDS
for z in SHOP_NEW:
    z["x"], z["y"] = [round(v, 1) for v in proj(z["lat"], z["lon"])]
    z["shop"] = True; z["tier"] = "購物"; z["compact"] = True
    z["W"] = tw(z["name"], 26) + 24; z["H"] = 44
    m = d(H, z); z["fromHotel"] = f"直線約 {fmt(m)}" + (f"，步行約 {round(m*1.3/80/5)*5} 分鐘" if m < 3000 else "")
SHOPS = [z for z in SPOTS if z["id"] in SHOP_IDS] + SHOP_NEW
_save = {z["id"]: (z.get("lx"), z.get("ly"), z["W"], z["H"]) for z in SPOTS}
for z in SHOPS:
    z["shop"] = True
    if z["cat"] != "base" or z.get("mapName"): z["W"] = tw(z.get("mapName", z["name"]), 26) + 24; z["H"] = 44
STREET_IDS = {i for i, _, nm in SHOP_STREETS if nm}   # shopping streets: drawn as street names, not boxes, in the 購物 view
SHOPS_ALL = SHOPS
# the default boxes (主要＋推薦) stay up in the 購物 view: shop boxes are placed around them
MAIN_IDS = {z["id"] for z in MAIN}
SHOPS = [z for z in SHOPS if z["id"] not in STREET_IDS and z["id"] not in MAIN_IDS]
_mb = [(_save[i][0], _save[i][1], _save[i][0] + _save[i][2], _save[i][1] + _save[i][3]) for i in MAIN_IDS]
_ml = [((z["x"], z["y"]), nearest((_save[z["id"]][0], _save[z["id"]][1], _save[z["id"]][0] + _save[z["id"]][2], _save[z["id"]][1] + _save[z["id"]][3]), (z["x"], z["y"]))) for z in MAIN]
_mp = [(z["x"] - 9, z["y"] - 9, z["x"] + 9, z["y"] + 9) for z in MAIN]
pins = [(z["x"], z["y"]) for z in SHOPS]
_skey = hashlib.md5((_key + "|shop2|" + json.dumps([[z["id"], z["x"], z["y"], round(z["W"])] for z in SHOPS]) + json.dumps(_mb)).encode()).hexdigest()
_scache = "/home/claude/rome/.place_cache_shop.json"
try: _sc = json.load(open(_scache))
except Exception: _sc = {}
if _sc.get("key") == _skey: bsh = (0, {k: tuple(v) for k, v in _sc["pos"].items()}); print("shop layout from cache")
else:
    bsh = place_greedy(SHOPS, [o for o in obstacles if o not in SOFT_OBS] + _mp, 40, pre_boxes=_mb, pre_leads=_ml)
    if bsh: json.dump({"key": _skey, "pos": bsh[1]}, open(_scache, "w")); print("shop max leader", round(bsh[2]))
    else: print("SHOP layout FAIL")
for z in SHOPS: z["shx"], z["shy"] = bsh[1][z["id"]]
SHOPS = SHOPS_ALL
for z in SPOTS:
    if z["id"] in STREET_IDS: z["shopStreet"] = True
    lx, ly, W_, H_ = _save[z["id"]]; z["lx"], z["ly"], z["W"], z["H"] = lx, ly, W_, H_
for z in SHOP_NEW:
    if z["id"] in STREET_IDS: z["shx"], z["shy"], z["shopStreet"] = z["x"], z["y"], True
    for a, b in (("lx", "shx"), ("ly", "shy"), ("ux", "shx"), ("uy", "shy"), ("slx", "shx"), ("sly", "shy"), ("nx", "shx"), ("ny", "shy")): z[a] = z[b]
SPOTS[-2:-2] = SHOP_NEW
pins = [(z["x"], z["y"]) for z in SPOTS]

shop_streets = [dict(id=i, d=[[round(v, 1) for v in proj(a, b)] for a, b in pts]) for i, pts, _nm in SHOP_STREETS]
out = dict(shopStreets=shop_streets, shopStreetLabels=shop_street_labels, edges=elabels, vatlbl=vat_lbl, spots=SPOTS, streets=street_out, tiber=tiber, park=park, vat=vat, river=river_lbl, vb=[round(v) for v in VB],
           scale=round(500 / S, 1))
json.dump(out, open("/home/claude/rome/data.json", "w"), ensure_ascii=False)
print("VB", VB)
