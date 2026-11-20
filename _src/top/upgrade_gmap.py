import json
VISIT = '''    ${s.cat !== "base" ? `<button class="visit-btn" id="d-visit" aria-pressed="${visited.has(s.id)}">${visited.has(s.id) ? "✓ 已去過（點一下取消）" : "標記為已去過"}</button>` : ""}'''
NEW = '''    <div class="d-actions">${s.cat !== "base" ? `<button class="visit-btn" id="d-visit" aria-pressed="${visited.has(s.id)}">${visited.has(s.id) ? "✓ 已去過（點一下取消）" : "標記為已去過"}</button>` : ""}<a class="gmap" href="${esc(gmapUrl(s))}" target="_blank" rel="noopener"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5a4.5 4.5 0 0 0-4.5 4.5c0 3.4 4.5 8.5 4.5 8.5s4.5-5.1 4.5-8.5A4.5 4.5 0 0 0 8 1.5zm0 6.2a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4z" fill="currentColor"/></svg>Google 地圖 ↗</a></div>'''
CSS_ANCHOR = '.visit-btn[aria-pressed="true"]'
CSS = '''.d-actions { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 16px; }
.d-actions .visit-btn { margin: 0; }
.gmap { display: inline-flex; align-items: center; gap: 6px; padding: 7px 16px; border-radius: 999px; border: 1.5px solid var(--free); color: var(--free); background: var(--paper); font: 700 14px var(--f-body); text-decoration: none; }
.gmap svg { width: 15px; height: 15px; }
.gmap:hover { background: var(--bg); }
.gmap:focus-visible { outline: 2px solid var(--free); outline-offset: 2px; }
'''
def JS(city, overrides):
    return ('/* ---- Google Maps link ---- */\nconst GQ = ' + json.dumps(overrides, ensure_ascii=False) + ';\n'
            'const gmapUrl = s => "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent((GQ[s.id] || s.latin.split(/ \\/ | – /)[0]) + " ' + city + '");\n\n/* ---- Drawer ---- */')
ROME = {"vaticani": "Musei Vaticani", "sistina": "Cappella Sistina", "colosseo": "Colosseo", "massimo": "Palazzo Massimo alle Terme",
        "bocca": "Bocca della Verità", "esculapio": "Tempio di Esculapio Villa Borghese", "laterano": "Basilica di San Giovanni in Laterano",
        "medici": "Villa Medici", "pantheon": "Pantheon", "gianicolo": "Terrazza del Gianicolo", "trastevere": "Trastevere",
        "popolochurch": "Basilica di Santa Maria del Popolo", "maggiore": "Basilica di Santa Maria Maggiore", "traiano": "Mercati di Traiano",
        "hotel": "Hotel Nazionale Roma Piazza di Monte Citorio", "termini": "Stazione Roma Termini", "spagna": "Scalinata di Trinità dei Monti",
        "arapacis": "Museo dell'Ara Pacis", "gioacchino": "Chiesa di San Gioacchino in Prati", "pincio": "Terrazza del Pincio"}
LUCCA = {"duomo": "Cattedrale di San Martino", "giovanni": "Chiesa dei Santi Giovanni e Reparata", "hotel": "Hotel Ilaria Via del Fosso",
         "station": "Stazione di Lucca", "shopping": "Via Fillungo", "campanile": "Campanile Cattedrale di San Martino",
         "museo": "Museo della Cattedrale"}

# Rome build.py
p = "/home/claude/rome/build.py"; s = open(p).read()
for a, c in [(VISIT, NEW), (CSS_ANCHOR, CSS + CSS_ANCHOR), ("/* ---- Drawer ---- */", JS("Roma", ROME))]:
    assert s.count(a) == 1, ("rome", a[:40], s.count(a)); s = s.replace(a, c, 1)
open(p, "w").write(s)
# Lucca patch.py: add rep() calls before the final write
p = "/home/claude/lucca/patch.py"; s = open(p).read()
anchor = 'open("/home/claude/lucca/盧卡地圖範本.html", "w").write(h)'
extra = "GMAP_PAIRS = " + repr([(VISIT, NEW), (CSS_ANCHOR, CSS + CSS_ANCHOR), ("/* ---- Drawer ---- */", JS("Lucca", LUCCA))]) + "\nfor a, c in GMAP_PAIRS: rep(a, c)\n"
open(p, "w").write(s.replace(anchor, extra + anchor))
print("ok")
