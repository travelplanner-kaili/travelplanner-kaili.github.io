import re, sys
NOTE_P2P = "先點起點，會顯示它到相鄰景點的距離；再點終點，就畫出兩點之間的距離與步行時間。點空白處重新選。"
NOTE_ALL = "顯示所有相鄰景點之間的步行距離與時間。"
TAIL = "步行距離以直線距離 ×1.3 估算，步速每分鐘 80 公尺；實際路線請以 Google 地圖導航為準。"

def upgrade(path, svgvar, m_per_unit, fs, H):
    s = open(path).read()
    css = (".dist-bar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin: 0 0 10px; font-size: 13.5px; background: var(--paper); border: 1px solid var(--line); border-left: 3px solid var(--ink); padding: 8px 12px; border-radius: 4px; }\n"
           ".dist-bar p { margin: 0; flex: 1 1 320px; min-width: 0; }\n"
           ".seg { display: inline-flex; border: 1.5px solid var(--ink); border-radius: 999px; overflow: hidden; flex: none; }\n"
           ".seg-btn { font: 700 13px var(--f-body); padding: 5px 14px; background: var(--paper); color: var(--ink); border: 0; cursor: pointer; }\n"
           ".seg-btn[aria-pressed=\"true\"] { background: var(--ink); color: var(--paper); }\n"
           ".seg-btn:focus-visible { outline: 2px solid var(--free); outline-offset: -3px; }\n"
           f".p2p-line {{ stroke: var(--paid); stroke-width: {4 if fs > 18 else 3}; stroke-dasharray: 2 8; stroke-linecap: round; fill: none; }}\n"
           ".p2p-pill { fill: var(--paid); }\n"
           f".p2p-text {{ font: 700 {fs}px var(--f-body); fill: var(--paper); font-variant-numeric: tabular-nums; }}")
    s, n1 = re.subn(r"^\.dist-note \{[^\n]*\}$", lambda m: css, s, flags=re.M)
    bar = ('<div class="dist-bar" id="dist-note" hidden>'
           '<div class="seg" role="group" aria-label="距離顯示方式">'
           '<button class="seg-btn" data-sub="p2p" aria-pressed="true">點到點</button>'
           '<button class="seg-btn" data-sub="all" aria-pressed="false">全部顯示</button></div>'
           f'<p id="dist-text">{NOTE_P2P}{TAIL}</p></div>')
    s, n2 = re.subn(r'<p class="dist-note" id="dist-note" hidden>.*?</p>', lambda m: bar, s)
    js = f'''let picked = null, pairEnd = null, sub = "p2p";
const M_PER_UNIT = {m_per_unit};
const NOTES = {{ p2p: "{NOTE_P2P}", all: "{NOTE_ALL}" }}, NOTE_TAIL = "{TAIL}";
const p2pLine = el("g", {{}}); {svgvar}.insertBefore(p2pLine, document.getElementById("spots"));
const p2pLabel = el("g", {{}}, {svgvar});
function walkText(units) {{
  const m = units * M_PER_UNIT * 1.3;
  const w = m < 100 ? Math.round(m / 10) * 10 : Math.round(m / 50) * 50;
  return (w < 1000 ? w + " m" : (w / 1000).toFixed(1) + " km") + "・" + Math.max(1, Math.round(w / 80)) + " 分";
}}
function renderDist() {{
  SPOTS.forEach(s => s.g.classList.toggle("picked", sub === "p2p" && (s.id === picked || s.id === pairEnd)));
  EDGES.forEach(e => e.g.classList.toggle("on", sub === "all" || (!!picked && !pairEnd && e.ids.includes(picked))));
  p2pLine.replaceChildren(); p2pLabel.replaceChildren();
  if (sub !== "p2p" || !picked || !pairEnd) return;
  const a = SPOTS.find(s => s.id === picked), b = SPOTS.find(s => s.id === pairEnd);
  el("line", {{ class: "p2p-line", x1: a.x, y1: a.y, x2: b.x, y2: b.y }}, p2pLine);
  const cx = (a.x + b.x) / 2, cy = (a.y + b.y) / 2;
  const pill = el("rect", {{ class: "p2p-pill" }}, p2pLabel);
  const t = el("text", {{ class: "p2p-text", x: cx, y: cy + {round(fs * 0.36, 1)}, "text-anchor": "middle" }}, p2pLabel);
  t.textContent = a.name + " → " + b.name + "　" + walkText(Math.hypot(b.x - a.x, b.y - a.y));
  let w = 300; try {{ w = t.getComputedTextLength() + {round(fs * 1.2)}; }} catch (e) {{}}
  pill.setAttribute("x", cx - w / 2); pill.setAttribute("y", cy - {H} / 2);
  pill.setAttribute("width", w); pill.setAttribute("height", {H}); pill.setAttribute("rx", {H} / 2);
}}
function pickSpot(id) {{
  if (id === null) {{ picked = pairEnd = null; }}
  else if (sub !== "p2p") return;
  else if (!picked || pairEnd) {{ picked = id; pairEnd = null; }}
  else if (id === picked) {{ picked = null; }}
  else {{ pairEnd = id; }}
  renderDist();
}}
document.querySelectorAll(".seg-btn").forEach(b => b.addEventListener("click", () => {{
  sub = b.dataset.sub;
  document.querySelectorAll(".seg-btn").forEach(x => x.setAttribute("aria-pressed", x === b));
  document.getElementById("dist-text").textContent = NOTES[sub] + NOTE_TAIL;
  pickSpot(null);
}}));
'''
    s, n3 = re.subn(r"let picked = null;\nfunction pickSpot\(id\) \{.*?\n\}\n", lambda m: js, s, flags=re.S)
    old = f'{svgvar}.addEventListener("click", () => {{ if (distMode && picked) pickSpot(null); }});'
    n4 = s.count(old)
    s = s.replace(old, f'{svgvar}.addEventListener("click", () => {{ if (distMode && sub === "p2p" && picked) pickSpot(null); }});')
    print(path, n1, n2, n3, n4)
    assert n1 == n2 == n3 == n4 == 1
    open(path, "w").write(s)

upgrade("/home/claude/rome/build.py", "svg", 2.2, 22, 38)
upgrade("/home/claude/lucca/patch.py", "mapSvg", 1, 16, 28)
