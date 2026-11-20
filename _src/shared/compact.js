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
