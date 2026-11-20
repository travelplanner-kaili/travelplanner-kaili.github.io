"""Python twin of compactLabel() in the map's JS: all-week label = main time + exceptions in brackets."""
import re
DN = "一二三四五六日"
_T = re.compile(r"^\d{2}:\d{2}–\d{2}:\d{2}(、\d{2}:\d{2}–\d{2}:\d{2})*$")

def _tm(v):
    return [t for x in v.split("、") for t in x.split("–")] if v and _T.match(v) else None

def day_runs(ds):
    if len(ds) == 7: return "每日"
    runs = []
    for d in ds:
        if runs and d == runs[-1][1] + 1: runs[-1][1] = d
        else: runs.append([d, d])
    return "週" + "、".join(DN[a] + "至" + DN[b] if b - a >= 2 else DN[a:b + 1] for a, b in runs)

def _exc(main, v):
    if not v: return "休"
    sp = lambda t: (" " if t[:1].isdigit() else "") + t
    a, b = _tm(main), _tm(v)
    if not a or not b or len(a) != len(b): return sp(v)
    diff = [i for i in range(len(a)) if a[i] != b[i]]; last = len(a) - 1
    if diff == [0]: return " " + b[0] + " 起"
    if diff == [last]: return "到 " + b[last]
    if len(a) == 4 and all(i in (1, 2) for i in diff):
        return "午休 " + b[1] + "–" + b[2] if len(diff) == 2 else (" " + b[1] + " 起午休" if diff[0] == 1 else "午休到 " + b[2])
    return sp(v)

def compact(vals, prefix=""):
    groups = []
    for d, v in enumerate(vals):
        g = next((x for x in groups if x["v"] == v), None)
        if g: g["days"].append(d)
        else: groups.append({"v": v, "days": [d]})
    opened = [g for g in groups if g["v"]]
    if not opened: return None
    score = lambda g: len(g["days"]) * 2 + (1 if _tm(g["v"]) else 0)
    main = opened[0]
    for g in opened:
        if score(g) > score(main): main = g
    merged = []
    for g in sorted([g for g in groups if g is not main], key=lambda g: g["days"][0]):
        t = _exc(main["v"], g["v"])
        if len(t) > 16: t = "時間不同"
        m = next((x for x in merged if x["t"] == t), None)
        if m: m["days"] += g["days"]
        else: merged.append({"t": t, "days": list(g["days"])})
    return prefix + main["v"] + ("（" + "；".join(day_runs(sorted(x["days"])) + x["t"] for x in merged) + "）" if merged else "")
