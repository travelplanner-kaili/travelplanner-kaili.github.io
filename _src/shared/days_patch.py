"""「我去的日子」for the Lucca / Venice single-file maps (Rome has its own copy in rome/build.py)."""
import json

CSS = """
/* 我去的日子 */
.chip-group.days { align-items: center; gap: 4px; }
.days-lbl { font: 700 12.5px var(--f-body); color: var(--muted); margin-right: 2px; white-space: nowrap; }
.chip.day { width: 30px; height: 30px; padding: 0; justify-content: center; border-radius: 50%; font: 700 14px var(--f-body); border-color: var(--ink); }
.chip.day[aria-pressed="true"] { background: var(--ink); color: var(--paper); opacity: 1; }
.chip.day[aria-pressed="false"] { opacity: .5; }
.spot .day-off { fill: var(--paid) !important; font-weight: 700; }
"""

def chips(default):
    b = "".join(f'<button class="chip day" type="button" data-day="{i}" aria-pressed="{"true" if i in default else "false"}" aria-label="星期{c}">{c}</button>' for i, c in enumerate("一二三四五六日"))
    return f'<span class="chip-group days" role="group" aria-label="星期幾去：景點框只顯示這幾天的營業時間"><span class="days-lbl">星期幾去</span>{b}</span>'

def js(key, week, prefix, nodim, hours_el, after):
    """hours_el: JS expression giving a spot's hours <text> (or null); after: JS run after a change (re-layout + filters)."""
    return f"""
/* ---- 我去的日子: pick weekdays (multi), labels show only those days' hours; spots closed on all of them fade ---- */
const DKEY = {json.dumps(key)}, DAYS = [...document.querySelectorAll(".chip.day")], DN = "一二三四五六日";
const WEEK = {json.dumps(week, ensure_ascii=False)}, WEEK_PREFIX = {json.dumps(prefix, ensure_ascii=False)}, WEEK_NODIM = new Set({json.dumps(sorted(nodim))});
try {{ const sv = JSON.parse(localStorage.getItem(DKEY) || "null"); if (Array.isArray(sv) && sv.length) DAYS.forEach(b => b.setAttribute("aria-pressed", sv.includes(+b.dataset.day) ? "true" : "false")); }} catch (e) {{}}
function dayRuns(ds) {{   // [0,1,2,4] → "週一至三、五"; [4,5] → "週五六"; [0,6] → "週一、日"
  if (ds.length === 7) return "每日";
  const runs = []; ds.forEach(d => {{ const r = runs[runs.length - 1]; if (r && d === r[1] + 1) r[1] = d; else runs.push([d, d]); }});
  return "週" + runs.map(r => r[1] - r[0] >= 2 ? DN[r[0]] + "至" + DN[r[1]] : DN.slice(r[0], r[1] + 1)).join("、");
}}
function weekLabel(id, sel) {{
  const wk = WEEK[id], groups = [];
  sel.forEach(d => {{ const v = wk[d]; const g = groups.find(x => x.v === v); if (g) g.days.push(d); else groups.push({{ v, days: [d] }}); }});
  const open = groups.filter(g => g.v), closed = groups.filter(g => !g.v).flatMap(g => g.days);
  if (!open.length) return null;
  const parts = open.map(g => ({{ d: g.days[0], t: dayRuns(g.days) + " " + g.v }}));
  if (closed.length) parts.push({{ d: closed[0], t: dayRuns(closed) + "休" }});
  return (WEEK_PREFIX[id] || "") + parts.sort((a, b) => a.d - b.d).map(x => x.t).join("｜");
}}
/* every day picked: one main time + the exceptions in brackets, e.g. 「09:00–19:00（週一休）」「收費 09:00–22:00（週一、五 11:30 起）」 */
const _tm = v => {{ const m = String(v).match(/^\d{{2}}:\d{{2}}–\d{{2}}:\d{{2}}(、\d{{2}}:\d{{2}}–\d{{2}}:\d{{2}})*$/); return m ? v.split("、").flatMap(x => x.split("–")) : null; }};
function exceptionText(main, v) {{
  if (!v) return "休";
  const a = _tm(main), b = _tm(v);
  const sp = t => (/^\d/.test(t) ? " " : "") + t;   // a space only before a time
  if (!a || !b || a.length !== b.length) return sp(v);
  const diff = a.map((x, i) => x !== b[i] ? i : -1).filter(i => i >= 0), last = a.length - 1;
  if (diff.length === 1 && diff[0] === 0) return " " + b[0] + " 起";
  if (diff.length === 1 && diff[0] === last) return "到 " + b[last];
  if (a.length === 4 && diff.every(i => i === 1 || i === 2)) return diff.length === 2 ? "午休 " + b[1] + "–" + b[2] : diff[0] === 1 ? " " + b[1] + " 起午休" : "午休到 " + b[2];
  return sp(v);
}}
function compactLabel(vals, prefix) {{   // vals: the 7 day values, Monday first
  const groups = [];
  vals.forEach((v, d) => {{ const g = groups.find(x => x.v === v); if (g) g.days.push(d); else groups.push({{ v, days: [d] }}); }});
  const open = groups.filter(g => g.v);
  if (!open.length) return null;
  const score = g => g.days.length * 2 + (_tm(g.v) ? 1 : 0);   // most days wins; on a tie prefer a real time
  const main = open.reduce((m, g) => score(g) > score(m) ? g : m, open[0]);
  const ex = groups.filter(g => g !== main).sort((x, y) => x.days[0] - y.days[0]);
  const merged = [];   // same note on several days → one entry (週六日時間不同)
  ex.forEach(g => {{ let t = exceptionText(main.v, g.v); if (t.length > 16) t = "時間不同"; const m = merged.find(x => x.t === t); if (m) m.days.push(...g.days); else merged.push({{ t, days: [...g.days] }}); }});
  return prefix + main.v + (merged.length ? "（" + merged.map(x => dayRuns(x.days.sort((p, q) => p - q)) + x.t).join("；") + "）" : "");
}}
function applyDays() {{
  let sel = DAYS.filter(pressed).map(b => +b.dataset.day);
  if (!sel.length) sel = [0, 1, 2, 3, 4, 5, 6];
  SPOTS.forEach(s => {{
    s.dayClosed = false;
    const t = WEEK[s.id] ? ({hours_el}) : null; if (!t) return;
    // reserve the box width the label had at first paint, so a longer line shrinks instead of widening the box
    if (s.dayOrig == null) s.dayOrig = t.textContent;
    if (!s.dayLim) {{ t.textContent = s.dayOrig; t.style.fontSize = ""; t.removeAttribute("textLength");
      try {{ const w = Math.max(...[...s.g.querySelectorAll("text")].map(x => x.getComputedTextLength())); if (w > 0) s.dayLim = w; }} catch (e) {{}} }}
    const lbl = sel.length === 7 ? compactLabel(WEEK[s.id], WEEK_PREFIX[s.id] || "") : weekLabel(s.id, sel), closed = lbl === null;
    s.dayClosed = closed && !WEEK_NODIM.has(s.id);
    t.textContent = closed ? "你選的日子休館" : lbl;
    t.classList.toggle("day-off", closed);
    t.style.fontSize = ""; t.removeAttribute("textLength"); t.removeAttribute("lengthAdjust");
    try {{
      const w = t.getComputedTextLength(), lim = s.dayLim || w;
      if (w > lim && w > 0) {{
        const k = Math.max(.7, lim / w); t.style.fontSize = (parseFloat(getComputedStyle(t).fontSize) * k) + "px";
        if (w * k > lim + 1) {{ t.setAttribute("textLength", lim); t.setAttribute("lengthAdjust", "spacingAndGlyphs"); }}
      }}
    }} catch (e) {{}}
  }});
}}
DAYS.forEach(b => b.addEventListener("click", () => {{
  b.setAttribute("aria-pressed", pressed(b) ? "false" : "true");
  try {{ localStorage.setItem(DKEY, JSON.stringify(DAYS.filter(pressed).map(x => +x.dataset.day))); }} catch (e) {{}}
  applyDays(); {after}
}}));
applyDays();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => {{ SPOTS.forEach(s => s.dayLim = 0); applyDays(); {after} }});
"""
