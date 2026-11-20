# Lucca: same tiers / filters as Rome (主要・推薦 on by default, 次要 off; 需購票・免費・冷門時段). Applied to the built HTML.
import re
TIER_JS = '''
/* ---- tiers (same rules as the Rome map) ---- */
const TIER_MAIN = new Set(["duomo", "guinigi", "mura", "anfiteatro", "michele", "frediano"]);
const TIER_REC = new Set(["giovanni", "ore", "piazzamichele", "campanile"]);
SPOTS.forEach(s => {
  if (s.cat === "base") return;
  s.tier = TIER_MAIN.has(s.id) ? "主要" : TIER_REC.has(s.id) ? "推薦" : "次要";
  s.sup = s.tier === "次要";
  // 冷門時段: visitable before 09:00 or after 19:00 (any listed time outside 09–19, or open all day)
  const txt = (s.hours || []).join(" ");
  const ts = [...txt.matchAll(/(\\d{1,2}):(\\d{2})/g)].map(m => +m[1] * 60 + +m[2]);
  s.cold = /全天|24 ?小時/.test(txt) || ts.some(t => t < 540 || t > 1140);
});
'''
CHIPS = '''      <span class="chip-group" role="group" aria-label="景點層級"><button class="chip tier" data-tier="主要" aria-pressed="true" style="--c:var(--ink)"><span class="dot"></span>主要景點</button><button class="chip tier" data-tier="推薦" aria-pressed="true" style="--c:var(--ink)"><span class="dot"></span>推薦</button><button class="chip tier sup" id="f-sup" data-tier="次要" aria-pressed="false" style="--c:var(--muted)"><span class="dot"></span>次要</button></span>
      <span class="chip-group" role="group" aria-label="景點類型"><button class="chip" id="f-paid" data-cat="paid" aria-pressed="true" style="--c:var(--paid)"><span class="dot"></span>需購票景點</button><button class="chip" id="f-free" data-cat="free" aria-pressed="true" style="--c:var(--free)"><span class="dot"></span>免費景點</button><button class="chip cold" id="f-cold" aria-pressed="false" style="--c:var(--ink)" data-tip="只看早上 9 點前或晚上 7 點後還能去的景點" title="只看早上 9 點前或晚上 7 點後還能去的景點"><span class="dot"></span>冷門時段（9 點前或晚上 7 點後）</button></span>
'''
CSS = '''
.chip-group { display: inline-flex; flex-wrap: wrap; gap: 6px; padding-right: 8px; margin-right: 2px; border-right: 1px solid var(--line, rgba(0,0,0,.12)); }
.chip-group:last-of-type { border-right: 0; }
.chip.tier[data-tier="推薦"] .dot { background: none; border: 2.5px solid var(--c); width: 7px; height: 7px; }
.chip[data-cat="free"] .dot { background: linear-gradient(90deg, var(--free) 50%, var(--open) 50%); }
.chip.cold .dot { background: linear-gradient(90deg, var(--c) 50%, transparent 50%); border: 1.5px solid var(--c); width: 8px; height: 8px; }
.item.gone { display: none; }
.spot.dim { opacity: .28; pointer-events: auto; }   /* faded by a filter, but still clickable */
'''
FILTER_JS = '''/* ---- Filters: tier (主要／推薦／次要) hides, type (需購票／免費) and 冷門時段 dim ---- */
const pressed = el => el.getAttribute("aria-pressed") === "true";
function applySup() {
  const tiers = new Set([...document.querySelectorAll(".chip[data-tier]")].filter(pressed).map(c => c.dataset.tier));
  const cats = new Set([...document.querySelectorAll(".chip[data-cat]")].filter(pressed).map(c => c.dataset.cat));
  if (!cats.size) ["paid", "free"].forEach(c => cats.add(c));   // nothing picked = no type filter
  if (cats.has("free")) cats.add("open");   // 免費 covers the free squares and walls too
  const cold = pressed(document.getElementById("f-cold"));
  SPOTS.forEach(s => {
    const gone = !!s.tier && !tiers.has(s.tier), dim = s.cat !== "base" && (!cats.has(s.cat) || (cold && !s.cold));
    s.g.classList.toggle("gone", gone); s.g.classList.toggle("dim", dim);
    const it = document.getElementById("item-" + s.id); if (it) it.classList.toggle("gone", gone || dim);
  });
  document.querySelectorAll(".group").forEach(g => g.hidden = ![...g.querySelectorAll(".item")].some(i => !i.classList.contains("gone")));
  syncArea(); syncEdges();
}
document.querySelectorAll(".chip[data-tier], .chip[data-cat], #f-cold").forEach(ch => ch.addEventListener("click", () => {
  ch.setAttribute("aria-pressed", pressed(ch) ? "false" : "true"); applySup();
}));
applySup();
'''
def tiers(h):
    old = re.search(r'      <button class="chip" id="f-paid".*?\n      <button class="chip" id="f-free".*?\n      <button class="chip" id="f-open".*?\n', h).group(0)
    h = h.replace(old, CHIPS, 1)
    h, n = re.subn(r'      <button class="chip sup" id="f-sup"[^\n]*\n', '', h, count=1); assert n == 1
    h = h.replace(".chip.sup .dot {", CSS + ".chip.sup .dot {", 1)
    old = re.search(r'/\* ---- Filters ---- \*/\n.*?\napplySup\(\);\n', h, re.S).group(0)
    h = h.replace(old, FILTER_JS, 1)
    # tiers must exist before the spots are drawn
    i = h.index("const SPOTS = ["); j = h.index("\n];", i) + 3
    h = h[:j] + TIER_JS + h[j:]
    # map labels: drop the grey 適合 line (still in the side panel); keep the element hidden for the time-mode code
    a = '    t2 = el("text", { class: "t-time t-more", x: s.lx + 12, y: s.ly + 67 }, g); t2.textContent = "適合 " + s.sTime;'
    assert a in h; h = h.replace(a, '    t2 = el("text", { class: "t-time t-more", x: s.lx + 12, y: s.ly + 67, style: "display:none" }, g);', 1)
    a = 'y: s.ly + (allDay ? 47 : 88) }, g); t3.textContent = s.sPrice;\n  s.H = allDay ? 58 : 99;'
    assert a in h, "t3"; h = h.replace(a, 'y: s.ly + (allDay ? 47 : 67) }, g); t3.textContent = s.sPrice;\n  s.H = allDay ? 58 : 78;', 1)
    h = h.replace('s.texts = [t1, tw, t2, t3].filter(Boolean); s.timeText = t2;', 's.texts = [t1, tw, t3].filter(Boolean); s.timeText = t2 || { textContent: "" };', 1)
    assert "TIER_MAIN" in h and 'id="f-cold"' in h and "function applySup" in h
    return h
