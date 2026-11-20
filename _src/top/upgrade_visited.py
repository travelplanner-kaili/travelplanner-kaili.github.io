CSS = '''.chip.done { border-style: dashed; border-color: var(--open); }
.chip.done[aria-pressed="false"] { opacity: 1; }
.chip.done[aria-pressed="true"] { background: var(--open); color: var(--paper); border-style: solid; }
.visit-btn { display: inline-flex; align-items: center; gap: 6px; margin: 0 0 16px; padding: 7px 16px; border-radius: 999px; border: 1.5px solid var(--open); background: var(--paper); color: var(--open); font: 700 14px var(--f-body); cursor: pointer; }
.visit-btn[aria-pressed="true"] { background: var(--open); color: var(--paper); }
.visit-btn:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }
.spot.visited { opacity: .45; }
.spot.visited .tab { stroke-dasharray: 5 4; }
.spot.hide-v, .area.hide-v, .edge.hide-v { display: none; }
.chip.sup .dot {'''
CHIP = '''<button class="chip done" id="f-done" hidden aria-pressed="false" title="去過的景點記在這台裝置的瀏覽器裡">顯示去過的景點（<span id="done-n">0</span>）</button>
      <button class="chip sup" id="f-sup"'''
def JS(key): return '''/* ---- Visited ---- */
const VKEY = "%s";
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

/* ---- Drawer ---- */''' % key
LATIN_OLD = '<p class="latin">${esc(s.latin)}</p>'
LATIN_NEW = LATIN_OLD + '''
    ${s.cat !== "base" ? `<button class="visit-btn" id="d-visit" aria-pressed="${visited.has(s.id)}">${visited.has(s.id) ? "✓ 已去過（點一下取消）" : "標記為已去過"}</button>` : ""}'''
CLOSE_OLD = 'document.getElementById("d-close").addEventListener("click", closeSpot);'
CLOSE_NEW = CLOSE_OLD + '''
  document.getElementById("d-visit")?.addEventListener("click", () => {
    if (visited.has(s.id)) visited.delete(s.id); else visited.add(s.id);
    saveVisited(); applyVisited();
    if (visited.has(s.id) && !showDone) closeSpot(); else openSpot(s.id);
  });'''
PAIRS = lambda key: [(".chip.sup .dot {", CSS), ('<button class="chip sup" id="f-sup"', CHIP),
                     ("/* ---- Drawer ---- */", JS(key)), (LATIN_OLD, LATIN_NEW), (CLOSE_OLD, CLOSE_NEW)]

# Rome: edit the template inside build.py directly
p = "/home/claude/rome/build.py"; s = open(p).read()
for a, c in PAIRS("trip-visited-rome"):
    assert s.count(a) == 1, ("rome", a[:50], s.count(a)); s = s.replace(a, c)
open(p, "w").write(s)

# Lucca: append rep() calls to patch.py so they run after the earlier patches
p = "/home/claude/lucca/patch.py"; s = open(p).read()
anchor = 'open("/home/claude/lucca/盧卡地圖範本.html", "w").write(h)'
assert s.count(anchor) == 1
extra = "VISITED_PAIRS = " + repr(PAIRS("trip-visited-lucca") + [('document.querySelectorAll(".chip:not(.dist)")', 'document.querySelectorAll(".chip:not(.dist):not(.done)")')]) + "\nfor a, c in VISITED_PAIRS: rep(a, c)\n"
open(p, "w").write(s.replace(anchor, extra + anchor))
print("ok")
