import re, math, json, random
raw = open("/home/claude/lucca/index.html").read()
html = raw[raw.index("<title>"):raw.rindex("</body>")].rstrip() + "\n"

# ---- parse spots ----
spots = []
for m in re.finditer(r'\{ id:"(\w+)", cat:"(\w+)", x:(\d+), y:(\d+), lx:\d+, ly:\d+,\s*name:"([^"]+)"', html):
    spots.append(dict(id=m[1], cat=m[2], x=int(m[3]), y=int(m[4]), name=m[5]))
print(len(spots), "spots")
VB = (120, 130, 1680, 1420)

def tw(s, fs):
    w = 0
    for c in s:
        o = ord(c)
        if c == "–": w += .55*fs
        elif o > 0x2e80: w += fs
        elif c in "il.,:;'| ()": w += .32*fs
        elif c.isupper(): w += .66*fs
        else: w += .56*fs
    return w
def rbox(x, y, w, h, ang):
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    P = [(0, 4), (w, 4), (w, -h), (0, -h)]
    xs = [x + px*c - py*s_ for px, py in P]; ys = [y + px*s_ + py*c for px, py in P]
    return (min(xs), min(ys), max(xs), max(ys))
obstacles = [rbox(880, 640, tw("Via Fillungo", 19), 15, -82), rbox(340, 695, tw("Via San Paolino", 19), 15, 0),
             rbox(1200, 680, tw("Via Santa Croce", 19), 15, -1),
             (1600, 1150, 1645, 1230), (1370, 1335, 1640, 1372)]   # compass, scale bar
pins = [(s["x"], s["y"]) for s in spots]
def overlap(a, b, pad=0):
    return not (a[2]+pad <= b[0] or b[2]+pad <= a[0] or a[3]+pad <= b[1] or b[3]+pad <= a[1])
def seg_rect(p, q, r):
    n = max(2, int(math.dist(p, q)/5))
    for i in range(1, n):
        x = p[0]+(q[0]-p[0])*i/n; y = p[1]+(q[1]-p[1])*i/n
        if r[0]-3 <= x <= r[2]+3 and r[1]-3 <= y <= r[3]+3: return True
    return False
def seg_pt(p, q, c, rad):
    px, py = q[0]-p[0], q[1]-p[1]; L2 = px*px+py*py
    t = max(0, min(1, ((c[0]-p[0])*px+(c[1]-p[1])*py)/L2)) if L2 else 0
    return math.dist((p[0]+t*px, p[1]+t*py), c) < rad
def nearest(b, p): return (max(b[0], min(p[0], b[2])), max(b[1], min(p[1], b[3])))

# ---- edges: MST + hotel to nearest (skip near-collinear) ----
N = len(spots); D = lambda i, j: math.dist(pins[i], pins[j])   # 1 unit = 1 m
inT, edges = {0}, set()
while len(inT) < N:
    i, j = min(((i, j) for i in inT for j in range(N) if j not in inT), key=lambda e: D(*e))
    inT.add(j); edges.add(tuple(sorted((i, j))))
hi = next(i for i, s in enumerate(spots) if s["id"] == "hotel")
for j in sorted((j for j in range(N) if j != hi), key=lambda j: D(hi, j))[:4]:
    if any(k not in (hi, j) and D(hi, k)+D(k, j) < 1.1*D(hi, j) for k in range(N)): continue
    edges.add(tuple(sorted((hi, j))))
edges = sorted(edges, key=lambda e: D(*e))
segs = [(pins[i], pins[j]) for i, j in edges]
def walk(m):
    w = round(m*1.3/10)*10 if m*1.3 < 100 else round(m*1.3/50)*50
    return f"{w} m・{max(1, round(w/80))} 分" if w < 1000 else f"{w/1000:.1f} km・{round(w/80)} 分"

FE = 15
elabels, eboxes = [], []
for (i, j), (p, q) in zip(edges, segs):
    txt = walk(D(i, j)); W, H = tw(txt, FE)+14, 24
    ok = anc = None
    for off in [0, 15, -15, 28, -28, 42, -42, 58, -58, 75, -75]:
        for t in [.5, .42, .58, .34, .66, .26, .74, .18, .82]:
            dx, dy = q[0]-p[0], q[1]-p[1]; L = math.hypot(dx, dy) or 1
            cx, cy = p[0]+dx*t-dy/L*off, p[1]+dy*t+dx/L*off
            box = (cx-W/2, cy-H/2, cx+W/2, cy+H/2)
            if box[0] < VB[0]+6 or box[1] < VB[1]+6 or box[2] > VB[2]-6 or box[3] > VB[3]-6: continue
            if any(overlap(box, b, 5) for b in eboxes): continue
            if any(box[0]-14 < r[0] < box[2]+14 and box[1]-14 < r[1] < box[3]+14 for r in pins): continue
            if any(overlap(box, o, 3) for o in obstacles): continue
            ok, anc = box, (p[0]+dx*t, p[1]+dy*t); break
        if ok: break
    if ok: eboxes.append(ok)
    else: print("edge label skipped", spots[i]["id"], spots[j]["id"])
    elabels.append(dict(a=list(p), b=list(q), box=[round(v, 1) for v in ok] if ok else None,
                        anc=[round(v, 1) for v in anc] if ok else None, text=txt, ids=[spots[i]["id"], spots[j]["id"]]))

# ---- names-only label placement ----
FS = 19
for s in spots: s["sW"] = tw(s["name"], FS)+24; s["sH"] = 36
def place(order):
    global sb, sl
    sb, sl = [], []
    for s in order:
        best = None; p = (s["x"], s["y"])
        for r in range(12, 420, 5):
            for k in range(48):
                a = 2*math.pi*k/48
                cx, cy = p[0]+r*math.cos(a), p[1]+r*math.sin(a)
                box = (cx-s["sW"]/2, cy-s["sH"]/2, cx+s["sW"]/2, cy+s["sH"]/2)
                if box[0] < VB[0]+6 or box[1] < VB[1]+6 or box[2] > VB[2]-6 or box[3] > VB[3]-6: continue
                if any(overlap(box, b, 6) for b in sb): continue
                if any(overlap(box, b, 5) for b in eboxes): continue
                if any(overlap(box, o, 5) for o in obstacles): continue
                if any(box[0]-13 < q[0] < box[2]+13 and box[1]-13 < q[1] < box[3]+13 for q in pins): continue
                if any(seg_rect(a_, b_, (box[0]+4, box[1]+4, box[2]-4, box[3]-4)) for a_, b_ in segs): continue
                e = nearest(box, p)
                if any(seg_rect(p, e, b) for b in sb+eboxes): continue
                if any(seg_pt(p, e, q, 13) for q in pins if q != p): continue
                if any(seg_rect(L[0], L[1], box) for L in sl): continue
                ln = math.dist(p, e)
                if ln < 9: continue
                if best is None or ln < best[0]: best = (ln, box, e)
            if best and r > best[0]+70: break
        if not best: return s
        _, box, e = best
        s["slx"], s["sly"] = round(box[0], 1), round(box[1], 1)
        sb.append(box); sl.append((p, e))
    return None
random.seed(3); bestS = None
for trial in range(60):
    o = list(spots)
    if trial: random.shuffle(o)
    ok = False
    for _ in range(30):
        f = place(o)
        if f is None: ok = True; break
        o.remove(f); o.insert(0, f)
    if not ok: continue
    lens = [math.dist(a, b) for a, b in sl]
    sc = sum(l*l for l in lens) + 30*max(lens)**2
    if bestS is None or sc < bestS[0]: bestS = (sc, {s["id"]: [s["slx"], s["sly"]] for s in spots})
print("placed:", bestS is not None, "edges", len(elabels))
json.dump(dict(simple=bestS[1], edges=elabels), open("/home/claude/lucca/dist.json", "w"), ensure_ascii=False)
open("/home/claude/lucca/base.html", "w").write(html)
