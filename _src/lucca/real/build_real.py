import re
import json, re
SRC = '/home/claude/lucca/live/lucca.html'
h = open(SRC).read()
R = '/home/claude/lucca/real/'
C = json.load(open(R + 'coords.json'))
def cut(a, b, s=h, inc_b=False):
    i = s.index(a); j = s.index(b, i)
    return s[i:j + (len(b) if inc_b else 0)]

css = cut('<style>\n/* hidden must win', '</style>', inc_b=True)
head_html = cut('<div class="wrap">', '  <div class="mapbox">')
mapbox_rest = cut('    <div class="rad-card"', '  <div class="hint">')
faq = cut('  <section class="faq"', '</section>', inc_b=True)
tail_html = cut('<div class="scrim"', '<script>')

data_js = cut('const CAT = {', 'const NS = ')
data_js = data_js.replace('const TIER_REC = new Set(["giovanni", "ore", "piazzamichele", "campanile"]);', 'const TIER_REC = new Set(["giovanni", "ore", "piazzamichele", "campanile", "shopping"]);', 1) if 'const TIER_REC' in data_js else data_js
_f = 'feature:"全城散步與商業中心，串聯老字號甜點店（Taddeucci 等）、手工皮件與獨立精品工坊。"'
assert _f in data_js
data_js = data_js.replace(_f, _f[:-1] + '範圍大約是：聖保林街（Via San Paolino）→ 聖米迦勒廣場 → 菲盧戈街（Via Fillungo）→ 圓形競技場廣場。地圖上的綠色圈只是大致範圍，所以形狀有點怪，實際逛街就沿著這幾條路走。"', 1)
simple_js = cut('const SIMPLE = ', '/* ---- Wednesday hours')
days_js = cut('const DKEY = ', 'function applyDays()')
visited_links_js = cut('/* ---- Visited ---- */', '/* ---- Drawer ---- */')
visited_links_js = visited_links_js.replace('  EDGES.forEach(e => e.g.classList.toggle("hide-v", e.ids.some(hid)));\n', '')
visited_links_js = visited_links_js.replace('    if (s.areaEl) s.areaEl.classList.toggle("hide-v", hid(s.id));\n', '    if (s.areaEl) areaVis(s, hid(s.id) ? 0 : 1);\n')
visited_links_js = visited_links_js.replace('const gmapUrl = s => ', 'const gmapUrl = s => (s.custom || s.myHotel) ? (s.gurl || "https://www.google.com/maps/search/?api=1&query=" + s.ll[0].toFixed(6) + "," + s.ll[1].toFixed(6)) : ')
drawer_js = cut('/* ---- Drawer ---- */', '</script>')

css = css.replace('.mapbox svg {', '.mapbox > svg {').replace('.mapbox.fs svg {', '.mapbox.fs > svg {')
leaflet_css = open(R + 'node_modules/leaflet/dist/leaflet.css').read()
leaflet_js = open(R + 'node_modules/leaflet/dist/leaflet.js').read()
sortable_js = open(R + 'node_modules/sortablejs/Sortable.min.js').read()

ICON_CAL = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3.5 9.5h17M8 3v4M16 3v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M8 13.5h3M8 16.5h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'

# header: title + plan button (main bar and full-screen bar)
mapbox_rest = mapbox_rest.replace('<span class="p2p-dist" id="p2p-dist"></span>', '<span class="p2p-dist" id="p2p-dist"></span><a class="p2p-go" id="p2p-go" target="_blank" rel="noopener">用 Google 地圖導航 ↗</a>')
head_html = head_html.replace('<h1>盧卡古城景點地圖</h1>', '<h1>盧卡古城景點地圖</h1>\n      <p class="sub"><button type="button" class="plan-all tour-again">▶ 功能導覽</button><span class="sub-sep">・</span><button type="button" id="plan-all" class="plan-all">匯出整份地圖</button><span class="sub-sep">・</span><button type="button" class="plan-all imp-open">匯入地圖</button><span class="all-note" id="all-note" hidden></span></p>')
plan_btn = f'<button class="icon-btn plan-btn" type="button" aria-pressed="false" aria-label="我的行程：按日期排景點" data-tip="我的行程">{ICON_CAL}</button>'
head_html = head_html.replace('<span class="dot"></span>免費景點</button>', '<span class="dot"></span>免費景點</button><button class="chip" id="f-mine" data-cat="mine" aria-pressed="true" style="--c:#7B3C8C"><span class="dot"></span>私人景點</button>', 1)
assert 'f-mine' in head_html
head_html = head_html.replace('<span class="view-btns">', '<button type="button" class="plan-all plan-all-fs tour-again">▶ 功能導覽</button><button type="button" class="plan-all plan-all-fs">匯出整份地圖</button><button type="button" class="plan-all plan-all-fs imp-open">匯入地圖</button><span class="view-btns">', 1)
# 我的行程 = a small tab on the map (computer: left edge; phone: bottom-left 「▲ 我的行程」); the panel slides out from it
mapbox_rest, _n = re.subn(r'\n?\s*<button id="z-full".*?</button>', '', mapbox_rest, count=1, flags=re.S); assert _n == 1
mapbox_rest = mapbox_rest.replace('<div class="zoom">', '<button type="button" class="plan-tab plan-btn" aria-expanded="false" aria-controls="plan" aria-label="打開我的行程"><span class="pt-ar" aria-hidden="true"></span>我的行程</button>\n    <div class="zoom">', 1)
mapbox_rest = mapbox_rest.replace('<div class="zoom">', '<div class="zoom">\n      <button id="z-me" aria-label="我在哪（顯示我的位置）" title="我在哪" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="7" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3" fill="currentColor"/><path d="M12 1v4M12 19v4M1 12h4M19 12h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>', 1)
mapbox_rest = mapbox_rest.replace('<div class="zoom">', '''<aside class="plan" id="plan" hidden aria-label="我的行程">
      <div class="plan-head"><b>我的行程</b><button type="button" class="plan-tour" id="plan-tour">▶ 導覽</button><span class="plan-hbtns"><button class="plan-lv" id="plan-lv" type="button" aria-label="切換行程顯示的簡潔程度"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg><span id="plan-lv-t">全覽</span></button><button class="plan-lv plan-un-btn" id="plan-un" type="button" aria-pressed="false" title="列出還沒排進任何一天的景點">待選景點</button><button class="plan-x" id="plan-x" type="button" aria-label="收起行程">×</button></span></div>
      <div class="plan-days" id="plan-days" role="tablist"></div>
      <p class="plan-offnote">沒有選任何一天，地圖是原本的樣子；排好的行程都還在。點日期打開那天的行程，再點一次就關掉。</p>
      <div class="plan-paste" id="plan-paste" hidden>
        <label><span id="pp-lbl">貼上「匯出整份地圖」複製的連結</span> <textarea id="pp-text" rows="2" placeholder="貼在這裡"></textarea></label>
        <div class="pa-btns"><button type="button" class="pa-ok" id="pp-ok">加入</button><button type="button" id="pp-cancel">取消</button></div>
        <p class="pp-ver" id="pp-ver"></p>
      </div>
      <div class="plan-dayedit" id="plan-dayedit"></div>
      <div class="plan-daymemo" id="plan-daymemo"></div>
      <div class="plan-unlist" id="plan-unlist" hidden></div>
      <ol class="plan-list" id="plan-list"></ol>
      <p class="plan-empty" id="plan-empty">這天還沒有景點。點地圖上的景點，在介紹裡按「加入行程」。</p>
      <button type="button" class="plan-addbtn" id="plan-addbtn">＋ 地圖沒有的點</button>
      <div class="plan-add" id="plan-add" hidden>
        <label><span>名稱<span class="req">（必填）</span></span> <input id="pa-name" type="text" maxlength="40" placeholder="例如：午餐 Buca di Sant'Antonio"></label>
        <label>位置 <input id="pa-link" type="text" placeholder="Google 地圖網址，或 43.8429, 10.5027"></label>
        <div class="pa-loc"><span class="pa-where" id="pa-where">或</span><button type="button" id="pa-pick">點這裡去設定地圖</button></div>
        <label>備註 <input id="pa-note" type="text" maxlength="120" placeholder="想記的事"></label>
        <div class="pa-btns"><button type="button" id="pa-ok" class="pa-ok">確認</button><button type="button" id="pa-cancel" class="pa-del">取消</button></div>
      </div>
      <p class="plan-share-note" id="plan-share-note" hidden></p>
      <div class="plan-foot"><span id="plan-sum"></span><span class="plan-acts"><button type="button" id="plan-share" class="plan-copy">匯出本日行程</button><a id="plan-go" class="plan-copy" target="_blank" rel="noopener" hidden>Google 導航<span class="go-ar">↗</span></a><button type="button" id="plan-copy" class="plan-copy">轉文字</button></span></div>
    </aside>
    <div class="zoom">''', 1)

def _add_help(html):
    # a round ? button right after the 距離模式 icon (main row and full-screen bar): jumps to 使用方式 below the map
    def addq(m):
        return m.group(0) + '<button class="icon-btn help-btn" type="button" aria-label="使用說明" data-tip="使用說明"><span aria-hidden="true">?</span></button>'
    html, n = re.subn(r'<button class="icon-btn dist" id="(?:f-dist|fs-dist-btn)"[^>]*>.*?</button>', addq, html, flags=re.S)
    assert n == 2, n
    return html
hint = '''  <div class="hint">
    <span class="mobile-only">單指拖曳移動、雙指縮放，點景點看介紹；長按景點看附近範圍</span>
    <span>地圖拉很遠時只留景點點位，放大就會出現景點框</span>
    <span>底圖 © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> 貢獻者（電腦直接開檔時用 Esri 街道圖）</span>
    <span><a class="foot-report" id="foot-report" href="#" target="_blank" rel="noopener">⚠ 發現錯誤？匿名回報給作者</a></span>
  </div>
'''
plan_q = f'''<li class="faq-item"><p class="faq-q"><span class="n">Q17</span><span>可以排每天的行程嗎？</span></p><p class="faq-a">可以。點景點，在介紹裡按「加入行程」，選要排在哪一天。不想排行程就不用打開，地圖照常可以用。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q18</span><span>行程的日期怎麼設定？</span></p><p class="faq-a">日期、星期幾自己設定，營業時間只會顯示當天的訊息（但還是以官網為準）。天數可以直接拖曳換順序。要多排一天就按「＋」，或按「＋ 匯入本日行程」貼上別人匯出的行程。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q19</span><span>排好的行程在哪裡看？</span></p><p class="faq-a">點地圖左邊（手機在左下角）的「我的行程」，選一天就會列出那天的景點。地圖上用編號和虛線連起來，每段實際走巷子的距離和時間寫在行程清單裡。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q20</span><span>可以直接用 Google 地圖導航嗎？</span></p><p class="faq-a">可以。按「Google 導航 ↗」，這天的景點會依序帶進 Google 地圖的步行導航。想一段一段走，就按兩站中間括號裡的「實際路線 ↗」，只導航那一段。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q21</span><span>我的行程裡的景點跟日期可以換順序嗎？</span></p><p class="faq-a">可以，直接拖曳就好。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q23</span><span>可以把行程分享給朋友嗎？</span></p><p class="faq-a">可以。在「我的行程」按「分享本日行程」，會把目前打開的這一天做成一個連結。開啟另一個裝置的「我的行程」，選「＋ 匯入分享行程」，會把你的行程加成新的一天。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q24</span><span>可以把行程轉成文字傳給別人嗎？</span></p><p class="faq-a">可以，按「轉文字」會複製這天行程，直接貼就好。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q25</span><span>怎麼把整份地圖搬到另一台手機或電腦？</span></p><p class="faq-a"><button type="button" class="plan-all plan-all-faq">按這裡</button>複製整份地圖，再到另一台手機或電腦打開這份地圖，在「我的行程」按「＋ 匯入分享行程」貼上就好。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q26</span><span>怎麼快速找出還沒排進行程的景點？</span></p><p class="faq-a">按行程右上角的「待選景點」，會快速列出還沒被你排進任何一天的景點，按「＋ 加入」就排進目前選的那一天。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q27</span><span>別人能看到我的行程嗎？</span></p><p class="faq-a">自己設定的行程和景點，只會存在你自己的裝置裡，要用「匯出整份地圖」才能帶著走。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q28</span><span>可以看到我現在在哪裡嗎？</span></p><p class="faq-a">可以。按右下角最上面的定位按鈕，第一次瀏覽器會問能不能使用位置，選「允許」，地圖上就會出現藍點（淡藍圈是誤差範圍）。地圖移開後再按一次會回到藍點；藍點已經在畫面中間時再按一次就關掉。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q29</span><span>為什麼拉遠之後景點框不見了？</span></p><p class="faq-a">拉到看得到整個盧卡周邊時，景點框會全部疊在一起，所以只留景點點位。放大一點就會出現；框太擠時可以按 👁 簡潔模式只留名稱。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q30</span><span>地圖上沒有的地方（餐廳、店）可以自己加嗎？</span></p><p class="faq-a">可以。電腦在地圖空白處按右鍵、手機長按，就會在那個位置新增；也可以在「我的行程」按「＋ 地圖沒有的點」，貼上 Google 地圖的網址（或座標）自動抓位置，沒有網址就按「點這裡去設定地圖」。加好的景點是紫色的，點開可以編輯名稱、位置和備註，按「刪除景點」會先問一次，確定刪除後，景點和行程裡的它會一起刪掉。只想從某一天的行程拿掉，就在「我的行程」那一行按 ×，景點還會留在地圖上。只存在你自己這台手機或電腦。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q31</span><span>可以把街道底圖藏起來，畫面更乾淨嗎？</span></p><p class="faq-a">可以。按眼睛旁邊的圖層按鈕，底圖每按一次淡一點：淡一點 → 很淡 → 完全隱藏（只留城牆、主要道路、購物商圈和景點），再按一次恢復清楚。所有功能照常可以用，會記住你上次的選擇。沒有網路時地圖也是長這樣。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q32</span><span>可以像 App 一樣放在手機桌面嗎？</span></p><p class="faq-a">可以。iPhone 用 Safari 打開地圖，按下方分享按鈕 →「加入主畫面」；Android 用 Chrome 打開，按右上角「⋮」→「加到主畫面」。桌面會多一個「盧卡地圖」圖示，打開是全螢幕。這是最好的做法，方便從同一入口進去編輯本機設定。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q33</span><span>為什麼點開同一個地圖，看到的東西不一樣？</span></p><p class="faq-a">行程、自己加的點存在打開它的那個瀏覽器裡。就算是同一台裝置，從 LINE 點開和從 Chrome 打開也是兩份不同的資料。建議看上一題，把網頁加到手機桌面當捷徑，固定從同一個入口進去最不會搞混。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q34</span><span>沒有網路也能用嗎？</span></p><p class="faq-a">可以，但要先在有網路時打開過一次。景點、介紹、營業時間和你的行程會整份存在手機裡；街道底圖只存你看過的地方，出發前在有 Wi-Fi 時把要去的區域放大滑過一遍就好。</p></li><li class="faq-item"><p class="faq-q"><span class="n">Q35</span><span>沒有網路時怎麼導航？</span></p><p class="faq-a">沒網路時步行距離會改成直線估算。出發前在 Google 地圖 App 下載盧卡的離線地圖，按「Google 導航」一樣能用。</p></li></ol></section>'''
faq = faq.replace('</ol></section>', plan_q)
_a = '沒辦法直接改，但你可以看自己住在哪個景點附近，把那個景點當作你的飯店定位點。'
assert _a in faq
faq = faq.replace(_a, '可以自己加：在地圖上飯店的位置按右鍵（手機長按），或在「我的行程」按「＋ 地圖沒有的點」，名稱寫你的飯店。它會是紫色的點，也能排進行程當起點。')
faq = faq.replace('就是 Google 地圖連結。', '就是 Google 地圖連結。要從一個景點走到另一個，用距離模式選好起點和終點，卡片上有「用 Google 地圖導航」；排好的行程也可以整天或一段一段開 Google 導航。', 1)
faq = faq.replace('（直線距離 ×1.3 估算，實際路線以 Google 地圖為準）', '（選好終點後會沿著巷子畫出實際的步行路線和時間，也有按鈕直接開 Google 地圖導航）')
faq = faq.replace('地圖可以單指拖曳、雙指縮放，按右下角的 ⤢ 回到整張地圖。', '地圖可以單指拖曳、雙指縮放，可以一路放大到每條巷子；按右下角的 ⤢ 回到整個古城。')

extra_css = '''
<style>
/* ===== real-map version ===== */
.mapbox { isolation: isolate; }   /* keep Leaflet's high z-indexes inside the map, under the drawer */
#lmap { width: 100%; height: min(78vh, 880px); background: var(--bg); font: inherit; }
@media (max-width: 860px) { #lmap { height: 100%; } }
.mapbox.fs #lmap { flex: 1 1 auto; height: auto !important; min-height: 0; }
.leaflet-container { font-family: var(--f-body); }
.leaflet-control-attribution { font-size: 10px; }
.mapbox .zoom { z-index: 500; }
.rad-card, .p2p-card { z-index: 600; }
.lm-spot { width: 0 !important; height: 0 !important; overflow: visible; background: none; border: 0; }
.spot { position: absolute; left: 0; top: 0; width: 0; height: 0; cursor: pointer; outline: none; }
.spot > * { pointer-events: auto; }
.mapbox .spot svg.leader { position: absolute; left: 0; top: 0; overflow: visible; width: 1px !important; height: 1px !important; display: block; pointer-events: none; }
.spot .leader line { stroke: var(--c); stroke-width: 1.4; }
.spot .pin { position: absolute; width: 16px; height: 16px; left: -8px; top: -8px; border-radius: 50%; background: var(--pc, var(--c)); border: 2.5px solid #fff; box-shadow: 0 1px 3px rgba(0,0,0,.45); box-sizing: border-box; }
.spot.is-base .pin { border-radius: 3px; }
.spot .tab { position: absolute; white-space: nowrap; background: var(--paper); border: 1.6px solid var(--c); border-radius: 4px; padding: 3px 9px 4px; line-height: 1.35; box-shadow: 0 1px 6px var(--shadow); color: var(--ink); }
.spot:hover .tab, .spot.active .tab { background: var(--bg); }
.spot.active .tab { border-width: 3px; }
.spot .t-name { font: 700 14px var(--f-body); }
.spot .t-wed { font: 500 11.5px var(--f-body); font-variant-numeric: tabular-nums; }
.spot .t-price { font: 700 11.5px var(--f-body); color: var(--c); font-variant-numeric: tabular-nums; }
.spot .day-off { color: var(--paid); font-weight: 700; }
.spot.is-sup .tab { border-style: dashed; }
.spot.dim { opacity: .28; }
.spot.gone, .spot.hide-v { display: none; }
.spot.visited { opacity: .45; } .spot.visited .tab { border-style: dashed; }
.spot.rad-out { opacity: .13 !important; }
.spot.rad-center .tab { border-width: 3.5px; }
.spot.picked .tab { border-width: 3px; background: var(--bg); }
#lmap.names .t-more, #lmap.dist .t-more, .spot.slim1 .t-more { display: none; }
.spot.lbl-off .tab, .spot.lbl-off .leader { display: none; }
#lmap.lbl-none .tab, #lmap.lbl-none .leader { display: none; }
.spot .plan-no { display: none; position: absolute; left: -13px; top: -13px; width: 26px; height: 26px; border-radius: 50%; background: var(--route); color: #fff; font: 800 13px/26px var(--f-body); text-align: center; border: 2px solid var(--paper); box-shadow: 0 1px 4px rgba(0,0,0,.4); z-index: 2; }
#lmap.planning .spot.in-plan .plan-no { display: block; }
#lmap.planning .spot.in-plan .pin { visibility: hidden; }
/* 我的行程 open: spots not in the chosen day fade (still clickable, full again on hover / focus) */
#lmap.planning .spot:not(.in-plan) { opacity: .35; }
#lmap.planning .spot:not(.in-plan):hover, #lmap.planning .spot:not(.in-plan):focus-visible, #lmap.planning .spot.active { opacity: 1; }
.leaflet-pane path.area-band { stroke: none; fill: var(--open); fill-opacity: .28; cursor: pointer; }
.leaflet-pane path.area-dot { stroke: #fff; stroke-width: 2; fill: #3DAA5A; fill-opacity: 1; }
.leaflet-pane path.area-core { stroke: var(--open); stroke-opacity: .9; stroke-width: 2.5; stroke-dasharray: 10 7; stroke-linecap: round; stroke-linejoin: round; fill: none; }
.leaflet-pane path.area-poly { stroke: var(--open); fill: var(--open); fill-opacity: .13; stroke-width: 3; stroke-dasharray: 12 8; }
.leaflet-pane path.rad-circle { stroke: var(--paid); fill: var(--paid); fill-opacity: .07; stroke-width: 2.5; stroke-dasharray: 10 7; }
.leaflet-pane path.rad-ring { stroke: var(--paid); stroke-opacity: .35; fill: none; stroke-width: 1.5; stroke-dasharray: 4 6; }
.leaflet-pane path.p2p-line { stroke: var(--paid); stroke-width: 4; stroke-dasharray: 2 9; stroke-linecap: round; fill: none; }
.leaflet-pane path.edge-line { stroke: var(--ink); stroke-opacity: .6; stroke-width: 3; stroke-dasharray: 2 6; stroke-linecap: round; fill: none; }
.leaflet-pane path.street-band { stroke: var(--st-band, #8F8676); stroke-opacity: .38; stroke-linecap: round; stroke-linejoin: round; fill: none; }
/* when the street map is faded or hidden, the main streets must stay visible (stronger band, light in dark mode) */
#lmap.base-faded .leaflet-pane path.street-band { stroke-opacity: .7; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) #lmap { --st-band: #CFC4AE; } }
:root[data-theme="dark"] #lmap { --st-band: #CFC4AE; }
.street-name span { position: absolute; left: 0; top: 0; white-space: nowrap; font: 700 10px var(--f-body); font-size: clamp(8.5px, calc(10px * var(--ls, 1)), 11px); letter-spacing: .01em; color: var(--ink); -webkit-text-stroke: 2.5px var(--paper); paint-order: stroke fill; text-shadow: 0 1px 3px rgba(0,0,0,.25); pointer-events: none; }   /* like the Rome map: bold sans with a halo */
.street-name.off { display: none; }
.leaflet-pane path.wall-band { stroke: var(--wall-2); stroke-opacity: .35; stroke-linejoin: round; fill: var(--wall-2); fill-opacity: .06; }
.leaflet-pane path.wall-core { stroke: var(--wall); stroke-opacity: .9; stroke-width: 2.5; stroke-dasharray: 10 7; stroke-linecap: round; stroke-linejoin: round; fill: none; }
.leaflet-pane path.plan-line { stroke: var(--route); stroke-width: 4; stroke-dasharray: 10 7; stroke-linecap: round; fill: none; }
.mid-pill { width: 0 !important; height: 0 !important; background: none; border: 0; }
.mid-pill span { position: absolute; transform: translate(-50%, -50%); white-space: nowrap; font: 700 12.5px var(--f-body); padding: 2px 9px; border-radius: 999px; background: var(--paper); color: var(--ink); border: 1px solid var(--line); box-shadow: 0 1px 4px var(--shadow); font-variant-numeric: tabular-nums; }
.mid-pill.p2p span { background: var(--paid); color: var(--paper); border: 0; font-size: 14px; }
.mid-pill.leg span { background: var(--route); color: #fff; border: 0; font-size: 11.5px; }
:root { --route: #B4610E; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --route: #F0A55A; } }
:root[data-theme="dark"] { --route: #F0A55A; }
.icon-btn.plan-btn { border-color: var(--route); color: var(--route); }
.icon-btn.plan-btn[aria-pressed="true"] { background: var(--route); color: var(--paper); }
/* 我的行程 panel */
.plan { position: absolute; z-index: 700; left: 12px; top: 12px; width: min(340px, calc(100% - 80px)); max-height: calc(100% - 24px); display: flex; flex-direction: column; background: var(--paper); color: var(--ink); border: 2px solid var(--route); border-radius: 12px; box-shadow: 0 6px 20px var(--shadow); box-sizing: border-box; overflow: hidden; }
.mapbox.fs .plan { top: calc(var(--fsbar, 56px) + 10px); max-height: calc(100% - var(--fsbar, 56px) - 20px); }
@media (max-width: 640px) { .plan { z-index: 1001; left: 0; right: 0; top: auto !important; bottom: 0; width: auto; max-height: 48% !important; border-radius: 14px 14px 0 0; border-width: 2px 0 0; padding-bottom: env(safe-area-inset-bottom, 0px); } }
.plan-head { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px 4px; }
.plan-head b { font: 700 16px var(--f-display); color: var(--route); }
.plan-x { border: 0; background: none; font-size: 22px; line-height: 1; color: var(--muted); cursor: pointer; padding: 2px 6px; }
.plan-days { display: flex; gap: 6px; padding: 2px 12px 8px; border-bottom: 1px solid var(--line); flex-wrap: wrap; }
.plan-days button { font: 700 13px var(--f-body); padding: 4px 11px; border-radius: 999px; border: 1.5px solid var(--route); background: var(--paper); color: var(--route); cursor: pointer; }
.plan-days button[aria-selected="true"] { background: var(--route); color: var(--paper); }
.plan-days button .n { font-weight: 500; opacity: .8; margin-left: 3px; }
.plan-list { list-style: none; margin: 0; padding: 6px 8px; overflow-y: auto; flex: 1 1 auto; min-height: 0; }
.plan-list li { display: grid; grid-template-columns: auto auto 1fr auto auto auto; align-items: center; gap: 2px 6px; padding: 6px 4px; border-radius: 8px; }
.plan-list li.sortable-ghost { background: var(--bg); opacity: .6; }
.plan-list .p-drag { cursor: grab; color: var(--muted); font-size: 16px; padding: 0 2px; touch-action: none; user-select: none; }
.plan-list .p-no { width: 22px; height: 22px; border-radius: 50%; background: var(--route); color: #fff; font: 800 12px/22px var(--f-body); text-align: center; }
.plan-list .p-name { border: 0; background: none; text-align: left; font: 700 14px var(--f-body); color: var(--ink); cursor: pointer; padding: 0; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.plan-list input.p-time { font: 700 13px var(--f-body); font-variant-numeric: tabular-nums; text-align: center; width: 58px; border: 1px solid var(--line); border-radius: 6px; padding: 2px 4px; background: var(--paper); color: var(--ink); }
.plan-list .p-del { border: 0; background: none; color: var(--muted); font-size: 18px; cursor: pointer; padding: 0 4px; }
.plan-list .p-del.sure { font: 700 12px var(--f-body); color: var(--paper); background: var(--paid); border-radius: 999px; padding: 2px 8px; white-space: nowrap; }
.plan-list .p-note { grid-column: 3 / -1; font: 12.5px var(--f-body); border: 0; border-bottom: 1px dashed var(--line); background: none; color: var(--ink); padding: 2px 0; min-width: 0; }
.plan-list .p-leg { grid-column: 1 / -1; font-size: 12px; color: var(--route); padding-left: 34px; margin-top: 2px; }
.plan-list .p-leg-go { font-weight: 700; color: var(--route); text-decoration: underline; text-underline-offset: 2px; }
.plan-hbtns { display: inline-flex; align-items: center; gap: 4px; }
.plan-lv { font: 700 12.5px var(--f-body); border: 1.5px solid var(--route); color: var(--route); background: var(--paper); border-radius: 999px; padding: 2px 10px; cursor: pointer; }
.plan-lv { display: inline-flex; align-items: center; gap: 5px; }
.mapbox .plan-lv svg { width: 16px; height: 16px; display: block; }
.plan-list .p-time-txt { display: none; font: 700 12px var(--f-body); color: var(--route); font-variant-numeric: tabular-nums; }
/* 簡潔: no notes, tighter rows */
.plan.c1 .p-note, .plan.c2 .p-note { display: none; }
.plan.c1 .plan-list li { padding: 3px 4px; }
.plan-list .p-info { grid-column: 3 / -1; font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; min-width: 0; }
.plan.c1 .p-info, .plan.c2 .p-info { display: none; }
/* 最簡: one line of numbered stops, time in front when set */
.plan.c2 { width: min(320px, calc(100% - 80px)); }
.plan.c2 .plan-list { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 4px; padding: 8px 10px; }
.plan.c2 .plan-list li { display: inline-flex; align-items: center; gap: 4px; padding: 2px 0; }
.plan.c2 .p-drag, .plan.c2 .plan-list input, .plan.c2 .p-del, .plan.c2 .p-leg { display: none; }
.plan.c2 .p-time-txt:not(:empty) { display: inline; }
.plan.c2 .plan-list li:not(:last-child)::after { content: "→"; color: var(--route); font-weight: 700; margin-left: 2px; }
.plan.c2 .plan-list .p-name { font-size: 13.5px; }
.plan.c2 .plan-days button .n { display: none; }
.plan.c2 .plan-foot { padding-top: 4px; }
.plan-days .pd-add, .plan-days .pd-paste { border-style: dashed; padding: 4px 10px; }
.plan-dayedit { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px; padding: 6px 12px; font-size: 12.5px; color: var(--muted); border-bottom: 1px solid var(--line); }
.plan-dayedit label { display: inline-flex; align-items: center; gap: 4px; }
.plan-dayedit input, .plan-dayedit select { font: 700 13px var(--f-body); color: var(--ink); background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 2px 6px; }
.plan-dayedit input { width: 70px; }
.plan-dayedit .pd-del { margin-left: auto; border: 0; background: none; color: var(--paid); font: 700 12px var(--f-body); cursor: pointer; text-decoration: underline; }
.plan-list .p-info.closed { color: var(--paid); font-weight: 700; }
.plan.c2 .plan-dayedit { display: none; }
.plan-addbtn { margin: 4px 12px 6px; align-self: flex-start; font: 700 12.5px var(--f-body); border: 1.5px dashed var(--route); color: var(--route); background: var(--paper); border-radius: 999px; padding: 3px 12px; cursor: pointer; }
.plan.c2 .plan-addbtn { display: none; }
.plan-add { margin: 0 10px 8px; padding: 8px 10px; border: 1.5px solid var(--route); border-radius: 10px; display: flex; flex-direction: column; gap: 6px; font-size: 12.5px; color: var(--muted); }
.plan-add label { display: flex; flex-direction: column; gap: 2px; }
.plan-add input { font: 13.5px var(--f-body); color: var(--ink); background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 4px 6px; min-width: 0; }
.pa-loc { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 4px 8px; margin-top: -2px; }
.pa-loc button, .m-edit button.m-pick { font: 700 12px var(--f-body); border: 1.5px solid var(--route); color: var(--route); background: var(--paper); border-radius: 999px; padding: 2px 9px; cursor: pointer; }
.pa-where { margin: 0; font-weight: 700; color: var(--paid); }
.pa-btns .pa-del { border-color: var(--paid); color: var(--paid); }
.pa-where.ok { color: var(--open); }
.pa-btns { display: flex; flex-wrap: wrap; gap: 6px; }
.pa-btns button { font: 700 12.5px var(--f-body); border: 1.5px solid var(--route); color: var(--route); background: var(--paper); border-radius: 999px; padding: 3px 10px; cursor: pointer; }
.pa-btns .pa-ok { background: var(--route); color: var(--paper); }
#lmap.picking, #lmap.picking .leaflet-grab { cursor: crosshair; }
.leaflet-pane path.add-pin { stroke: #7B3C8C; stroke-width: 3; fill: #7B3C8C; fill-opacity: .35; }
.spot.is-mine .pin { border-radius: 50% 50% 50% 0; transform: rotate(-45deg); }
.d-mine { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; margin: -8px 0 14px; font-size: 13px; color: var(--muted); }
.d-mine button { border: 0; background: none; color: #7B3C8C; font: 700 13px var(--f-body); text-decoration: underline; cursor: pointer; padding: 0; }
.d-mine #d-delmine { color: var(--paid); }
.pa-loc { justify-content: flex-start !important; }
#z-me svg { width: 22px; height: 22px; }
#z-me[aria-pressed="true"] { color: #fff; background: #2B7BE4; border-color: #2B7BE4; }
#z-me.wait svg { animation: me-spin 1.2s linear infinite; }
@keyframes me-spin { to { transform: rotate(360deg); } }
.me-dot { background: #2B7BE4; border: 3px solid #fff; border-radius: 50%; box-shadow: 0 0 0 2px rgba(43,123,228,.35), 0 1px 4px rgba(0,0,0,.4); }
.leaflet-pane path.me-acc { stroke: #2B7BE4; stroke-opacity: .5; stroke-width: 1; fill: #2B7BE4; fill-opacity: .12; }
.base-btn { position: relative; }
.base-btn .base-slash { opacity: 0; }
.base-btn[data-lv="3"] .base-slash { opacity: 1; }
.base-btn[data-lv="1"] svg { opacity: .7; } .base-btn[data-lv="2"] svg { opacity: .45; }
.base-btn[aria-pressed="true"] { background: var(--paper) !important; color: var(--ink) !important; }
.base-btn[data-lv="3"] { background: var(--ink) !important; color: var(--paper) !important; }
.base-btn::before { content: ""; position: absolute; left: 50%; bottom: 3px; transform: translateX(-50%); width: 14px; height: 3px; border-radius: 2px; background: currentColor; opacity: 0; }
.base-btn[data-lv="1"]::before { opacity: .6; width: 14px; } .base-btn[data-lv="2"]::before { opacity: .6; width: 8px; }
#lmap.no-base { background: var(--bg); }
#lmap.no-base .leaflet-tile-pane { display: none; }
/* phone: the fullscreen bar on one slim row; the plan sheet scrolls as a whole so the day's spots are always there */
@media (max-width: 640px) {
  .mapbox.fs .fs-bar { gap: 5px; padding-top: calc(5px + env(safe-area-inset-top, 0px)); padding-bottom: 5px; }
  .mapbox.fs .fs-bar .icon-btn { width: 32px; height: 32px; }
  .mapbox.fs .fs-bar .icon-btn svg { width: 17px !important; height: 17px !important; }
  .mapbox.fs .fs-btn { padding: 4px 9px; font-size: 13px; }
  .mapbox.fs .fs-title { font-size: 14px; }
  .plan { overflow-y: auto; max-height: 58% !important; -webkit-overflow-scrolling: touch; }
  .plan > * { flex-shrink: 0; }
  .plan .plan-list { flex: none; overflow: visible; min-height: auto; }
  .plan-head { position: sticky; top: 0; z-index: 3; background: var(--paper); }
  .plan-foot { position: sticky; bottom: 0; z-index: 3; background: var(--paper); }
  .plan-days button { padding: 3px 9px; font-size: 12.5px; }
  .plan-head { padding: 6px 10px 2px; }
  .plan.c1, .plan.c2 { width: auto; }   /* the simpler levels must stay full width on phones too */
  .plan-head b, .plan-head button { white-space: nowrap; }
  .plan-days { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; }   /* days + ＋ + 匯入 on one row, swipe sideways when more */
  .plan-days::-webkit-scrollbar { display: none; }
  .plan-days button { flex: none; white-space: nowrap; }
}
.spot.pulse .plan-no, .spot.pulse .pin { animation: spot-pulse .7s ease-in-out 3; }
@keyframes spot-pulse { 0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(217,119,6,.6); } 50% { transform: scale(1.35); box-shadow: 0 0 0 10px rgba(217,119,6,0); } }
.upd-bar { position: fixed; left: 50%; top: calc(10px + env(safe-area-inset-top, 0px)); transform: translateX(-50%); z-index: 3000; display: flex; align-items: center; gap: 10px; max-width: min(94vw, 520px); background: var(--ink); color: var(--paper); padding: 8px 10px 8px 14px; border-radius: 999px; font: 600 13.5px var(--f-body); box-shadow: 0 6px 20px rgba(0,0,0,.3); }
.upd-bar button { border: 0; border-radius: 999px; padding: 5px 12px; font: 700 13px var(--f-body); cursor: pointer; background: var(--route); color: #fff; }
.upd-bar .upd-x { background: transparent; color: var(--paper); padding: 4px 6px; }
.upd-bar small { font-size: 11.5px; font-weight: 500; opacity: .85; }
.sub-sep { color: var(--muted); margin: 0 6px; }
.tour-again.plan-all-fs { margin-right: 8px; }
.tour-shield { position: fixed; inset: 0; z-index: 3999; background: transparent; }
.tour-hole { position: fixed; z-index: 4000; border-radius: 12px; box-shadow: 0 0 0 9999px rgba(15,13,11,.62); pointer-events: none; transition: all .25s ease; outline: 3px solid #F2A65A; }
.tour-card { position: fixed; z-index: 4001; box-sizing: border-box; width: min(320px, calc(100vw - 24px)); background: var(--paper); color: var(--ink); border-radius: 14px; padding: 14px 16px 12px; box-shadow: 0 12px 34px rgba(0,0,0,.35); font: 14.5px/1.6 var(--f-body); transition: top .25s ease, left .25s ease; }
.tour-fig { display: block; width: 100%; height: auto; margin: 6px 0 8px; }
.tour-fig .tf-bg { fill: #ECE8DD; stroke: var(--line); }
.tour-fig .tf-road { stroke: #fff; stroke-width: 9; fill: none; stroke-linecap: round; }
.tour-fig .tf-ring { fill: rgba(229,72,77,.07); stroke: #E5484D; stroke-width: 1.6; stroke-dasharray: 5 4; }
.tour-fig .tf-dot { stroke: #fff; stroke-width: 2.5; }
.tour-fig .tf-out { opacity: .35; }
.tour-fig .tf-hand { font-size: 24px; }
.tour-fig .tf-lbl { font: 700 13px var(--f-body); fill: #2A2724; }
.tour-fig .tf-sub { font-weight: 500; font-size: 11.5px; fill: #6E675D; }
.tour-fig .tf-ripple { fill: none; stroke: #A855F7; stroke-width: 2; opacity: .45; }
.tour-fig .tf-ripple2 { opacity: .2; }
.tour-fig .tf-chip { fill: #fff; stroke: var(--route); stroke-width: 1.5; stroke-dasharray: 4 3; }
.tour-fig .tf-chipt { fill: var(--route); font-size: 12px; }
.tour-card h3 { margin: 0 0 4px; font: 700 16px var(--f-display); color: var(--route); }
.tour-card p { margin: 0 0 12px; }
.tour-foot { display: flex; align-items: center; gap: 8px; }
.tour-dots { display: flex; gap: 4px; margin-right: auto; }
.tour-dots i { width: 6px; height: 6px; border-radius: 50%; background: var(--line); }
.tour-dots i.on { background: var(--route); }
.tour-card button { font: 700 13px var(--f-body); border-radius: 999px; padding: 5px 12px; cursor: pointer; border: 1.5px solid var(--route); background: var(--paper); color: var(--route); }
.tour-card .tour-next { background: var(--route); color: #fff; }
.tour-card .tour-skip { border: 0; color: var(--muted); padding: 5px 4px; }
.tour-card .tour-prev, .tour-card .tour-next { min-width: 40px; font-size: 16px; padding: 3px 12px; }
.tour-card .tour-next:not([aria-label="下一步"]) { font-size: 13px; }
/* fullscreen bar, ☰ 篩選 panel and the distance note sit above every map layer (Leaflet panes go up to ~1000) */
.mapbox.fs .fs-bar, .mapbox.fs .fs-panel { z-index: 1200; }
.mapbox.fs .fs-dist { z-index: 1150; }
#lmap { z-index: 0; }
.imp-pop { position: fixed; z-index: 1300; left: 50%; top: 18%; transform: translateX(-50%); width: min(380px, calc(100vw - 32px)); box-sizing: border-box; background: var(--paper); border: 2px solid var(--route); border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,.3); padding: 4px 0 6px; }
.imp-pop[hidden] { display: none; }
.imp-pop .plan-paste { margin: 6px 12px; border: 0; padding: 0; }
.add-pop { position: fixed; z-index: 1300; left: 16px; bottom: 16px; width: min(360px, calc(100vw - 32px)); max-height: calc(100vh - 32px); overflow-y: auto; box-sizing: border-box; background: var(--paper); border: 2px solid var(--route); border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,.3); }
.add-pop[hidden] { display: none; }
.add-pop-head { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px 0; }
.add-pop-head b { font: 700 16px var(--f-display); color: var(--route); }
.add-pop-x { border: 0; background: none; color: var(--muted); font-size: 22px; line-height: 1; cursor: pointer; padding: 2px 6px; }
.add-pop .plan-add { margin: 6px 0 0; border: 0; }
@media (max-width: 640px) { .add-pop { left: 0; right: 0; bottom: 0; width: auto; max-height: 70vh; border-radius: 14px 14px 0 0; border-width: 2px 0 0; padding-bottom: env(safe-area-inset-bottom, 0px); } }
.faq-tour { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; margin: 6px 0 12px; padding: 12px 14px; border: 1.5px solid var(--route); border-radius: 12px; background: var(--paper); }
.faq-tour span { color: var(--muted); font-size: 13.5px; flex: 1 1 260px; }
.faq-tour-btn { font: 700 15px var(--f-body); border: 0; border-radius: 999px; padding: 7px 16px; background: var(--route); color: #fff; cursor: pointer; }
.faq-more { margin: 0 0 14px; }
.faq-more summary { cursor: pointer; font-weight: 700; color: var(--route); padding: 6px 0; display: flex; align-items: center; gap: 10px; list-style: none; }
.faq-more summary::-webkit-details-marker { display: none; }
.faq-or { color: var(--muted); font-weight: 500; }
.faq-open { text-decoration: underline; text-underline-offset: 3px; }
.faq-open::after { content: " ▾"; } .faq-more[open] .faq-open::after { content: " ▴"; }
.faq-more[open] summary { margin-bottom: 4px; }
.plan-all-faq { font-size: inherit; margin-right: 2px; }
.faq-grp { font: 700 14px var(--f-body); color: var(--route); margin: 12px 0 0; padding-top: 8px; border-top: 1px solid var(--line); }
.faq-sub { font: 700 16px var(--f-display); margin: 14px 0 4px; }
.req { color: var(--paid); font-weight: 700; font-size: 12px; }
.plan-un-btn { font-size: 12.5px; }
#lmap.planning .spot.un-hi { opacity: 1; }
.plan-un-btn[aria-pressed="true"] { background: var(--route); color: var(--paper); border-color: var(--route); }
.plan-days .pd-paste { font-size: 12px; }
.plan-days button[data-k] { cursor: grab; touch-action: pan-x; }   /* 2026-11-27: the date row must swipe sideways on phones (pan-y blocked it) */
.plan-days .sortable-ghost { opacity: .4; }
.plan-paste { margin: 0 12px 8px; padding: 8px 10px; border: 1.5px dashed var(--route); border-radius: 8px; font-size: 12.5px; }
.plan-paste label { display: block; font-weight: 700; }
.plan-paste textarea { display: block; width: 100%; box-sizing: border-box; margin-top: 4px; font: 12px var(--f-body); color: var(--ink); background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 4px 6px; resize: vertical; }
.pp-ver { margin: 6px 0 0; color: var(--muted); font-size: 11.5px; }
.pp-ver.warn { color: var(--paid); font-weight: 700; }
.plan-unlist { padding: 4px 12px 8px; overflow-y: auto; }
.plan-unlist h4 { margin: 8px 0 4px; font-size: 12.5px; color: var(--muted); }
.plan-unlist .un-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; border-bottom: 1px solid var(--line); }
.plan-unlist .un-name { flex: 1; min-width: 0; text-align: left; border: 0; background: none; color: var(--ink); font: 700 13.5px var(--f-body); cursor: pointer; padding: 0; }
.plan-unlist .un-add { flex: none; font: 700 12px var(--f-body); border: 1.5px solid var(--route); color: var(--route); background: var(--paper); border-radius: 999px; padding: 2px 9px; cursor: pointer; }
.plan.un-mode .plan-list, .plan.un-mode .plan-empty, .plan.un-mode .plan-dayedit, .plan.un-mode .plan-addbtn, .plan.un-mode .plan-add, .plan.un-mode .plan-foot, .plan.un-mode .plan-share-note { display: none !important; }
.plan-all { border: 0; background: none; color: var(--route); font: 700 14px var(--f-body); text-decoration: underline; text-underline-offset: 3px; cursor: pointer; padding: 0; }
.plan-all-fs { display: none; }
.mapbox.fs .plan-all-fs { display: inline-block; font-size: 13px; margin: 2px 4px; }
.toast { position: fixed; left: 50%; bottom: calc(24px + env(safe-area-inset-bottom, 0px)); transform: translateX(-50%); z-index: 3000; max-width: min(92vw, 520px); background: var(--ink); color: var(--paper); padding: 10px 14px; border-radius: 10px; font: 600 13.5px/1.5 var(--f-body); box-shadow: 0 6px 20px rgba(0,0,0,.25); }
.all-note { display: block; margin-top: 4px; font-size: 13px; color: var(--open); font-weight: 700; }
.all-note textarea { display: block; width: 100%; max-width: 560px; box-sizing: border-box; margin-top: 4px; font: 12px var(--f-body); }
.share-ask .sa-list { margin: 8px 0 12px; padding-left: 1.2em; font-size: 13.5px; line-height: 1.6; }
.share-ask .sa-list li { margin: 2px 0; }
.share-ask .sa-list b { display: inline; font: 700 13.5px var(--f-body); color: var(--ink); margin: 0; }
.share-ask .sa-sum { margin: 4px 0 8px; color: var(--muted); font-size: 13px; }
.share-ask .sa-opt { border: 1px solid var(--line); border-radius: 10px; margin: 0 0 10px; padding: 6px 10px 8px; }
.share-ask .sa-opt legend { font-weight: 700; font-size: 13.5px; padding: 0 4px; }
.share-ask .sa-opt label { display: flex; align-items: center; gap: 8px; font-size: 14px; padding: 3px 0; cursor: pointer; }
.share-ask .sa-opt input { accent-color: var(--route); width: 17px; height: 17px; }
.share-ask .sa-warn { color: var(--paid); font-weight: 700; }
.share-ask .pa-btns { flex-wrap: wrap; }

.d-sure { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: -6px 0 14px; padding: 8px 10px; border: 1.5px solid var(--paid); border-radius: 8px; font-size: 13px; }
.d-sure button { font: 700 13px var(--f-body); border-radius: 999px; padding: 3px 12px; cursor: pointer; border: 1.5px solid var(--paid); background: var(--paper); color: var(--paid); }
.d-sure #d-delyes { background: var(--paid); color: var(--paper); }
.m-edit { display: flex; flex-direction: column; gap: 6px; margin: -6px 0 16px; padding: 10px; border: 1.5px solid #7B3C8C; border-radius: 10px; font-size: 12.5px; color: var(--muted); }
.m-edit label { display: flex; flex-direction: column; gap: 2px; }
.m-edit input, .m-edit textarea { font: 14px var(--f-body); color: var(--ink); background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 4px 6px; resize: vertical; }
.plan-share-note { margin: 0 12px 6px; font-size: 12.5px; color: var(--open); font-weight: 700; }
.plan-share-note .plan-txt { display: block; width: 100%; box-sizing: border-box; font: 12px var(--f-body); margin-top: 4px; }
.plan-share-note input { width: 100%; font: 12px var(--f-body); margin-top: 4px; }
.share-ask { position: fixed; inset: 0; z-index: 50; background: rgba(10,12,14,.45); display: grid; place-items: center; padding: 16px; }
.sa-card { width: min(420px, 100%); background: var(--paper); color: var(--ink); border: 2px solid var(--route); border-radius: 14px; padding: 18px 18px 14px; box-shadow: 0 10px 40px var(--shadow); }
.sa-card b { font: 700 18px var(--f-display); color: var(--route); }
.sa-card p { margin: 8px 0; } .sa-card .sa-sub { font-size: 13px; color: var(--muted); }
.plan-empty { margin: 10px 14px; font-size: 13.5px; color: var(--muted); }
.plan-foot { display: flex; flex-direction: column; align-items: stretch; gap: 6px; padding: 6px 12px 10px; border-top: 1px solid var(--line); font-size: 12.5px; color: var(--muted); }
.plan-copy { font: 700 12.5px var(--f-body); border: 1.5px solid var(--route); color: var(--route); background: var(--paper); border-radius: 999px; padding: 3px 10px; cursor: pointer; }
.p2p-card { pointer-events: auto !important; }
.p2p-go { align-self: flex-start; margin-top: 4px; font: 700 13px var(--f-body); color: var(--paid); background: var(--paper); border-radius: 999px; padding: 4px 12px; text-decoration: none; }
.plan-acts { display: flex; gap: 6px; }
.plan-acts > * { flex: 1 1 0; text-align: center; white-space: nowrap; min-width: 0; padding: 3px 4px; overflow: hidden; text-overflow: ellipsis; }
#plan-sum:empty { display: none; }
a.plan-copy { text-decoration: none; }
.go-ar { display: inline-block; margin-left: 2px; font-size: .9em; line-height: 1; }
.d-plan { display: flex; flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; align-items: center; gap: 6px; margin: -6px 0 16px; padding-bottom: 2px; font-size: 13px; color: var(--muted); }   /* 2026-11-27: one row that swipes sideways, like 我的行程 */
.d-plan::-webkit-scrollbar { display: none; }
.d-plan > * { flex: none; white-space: nowrap; }
.d-plan button { font: 700 13px var(--f-body); padding: 4px 10px; border-radius: 999px; border: 1.5px dashed var(--route); background: var(--paper); color: var(--route); cursor: pointer; }
.d-plan button[aria-pressed="true"] { background: var(--route); color: var(--paper); border-style: solid; }

/* 我的行程 tab (2026-11-18) */
.plan-tab { position: absolute; z-index: 700; left: 0; top: 50%; transform: translateY(-50%); writing-mode: vertical-rl; display: flex; align-items: center; gap: 6px; padding: 14px 7px; border: 0; border-radius: 0 10px 10px 0; background: var(--route); color: var(--paper); font: 700 14px var(--f-body); letter-spacing: .1em; cursor: pointer; box-shadow: 2px 2px 8px rgba(0,0,0,.25); }
.plan-tab .pt-ar::before { content: "▶"; font-size: 10px; }
.plan-tab:hover, .plan-tab:focus-visible { padding-right: 10px; outline: none; }
.plan-days .pd-off { border-style: dashed; color: var(--muted); }
.plan-days .pd-off[aria-selected="true"] { border-style: solid; color: inherit; }
.plan-offnote { display: none; margin: 6px 12px 10px; font-size: 13px; color: var(--muted); }
.plan.off .plan-offnote { display: block; }
.plan.off .plan-dayedit, .plan.off .plan-daymemo, .plan.off .plan-unlist, .plan.off .plan-list, .plan.off .plan-empty, .plan.off .plan-addbtn, .plan.off .plan-add, .plan.off .plan-foot, .plan.off .plan-share-note { display: none !important; }
@media (max-width: 640px) {
  .plan-tab { z-index: 1001; top: auto; bottom: 24px; left: 10px; transform: none; writing-mode: horizontal-tb; padding: 8px 14px; border-radius: 18px; letter-spacing: 0; font-size: 14px; }
  .plan-tab .pt-ar::before { content: "▲"; }
  .plan-tab:hover, .plan-tab:focus-visible { padding-right: 14px; }
}
.plan-tour { margin-right: auto; margin-left: 8px; border: 0; background: none; padding: 2px 4px; font: 700 12.5px var(--f-body); color: var(--route); text-decoration: underline; text-underline-offset: 3px; cursor: pointer; white-space: nowrap; }
.plan-head b, .plan-head button { white-space: nowrap; }
.plan-head { gap: 4px; }
.plan-hbtns { display: flex; align-items: center; gap: 4px; flex: none; }
@media (min-width: 641px) { .plan { width: min(372px, calc(100% - 80px)); } }
.plan-x { display: none !important; }
.plan-tab { z-index: 701; }
.plan-tab.open { transform: none; }
.plan-tab.open .pt-ar::before { content: "◀"; }
@media (max-width: 640px) {
  .plan-tab { z-index: 1002; bottom: 0; left: 12px; border-radius: 12px 12px 0 0; padding: 7px 14px 6px; box-shadow: 0 -2px 8px rgba(0,0,0,.2); }
  .plan-tab.open .pt-ar::before { content: "▼"; }
}
@media (max-width: 640px) { .leaflet-control-attribution { max-width: calc(100vw - 140px); font-size: 9px; line-height: 1.3; text-align: right; } }
@media (min-width: 641px) { .plan { left: 0; border-left-width: 0; border-radius: 0 12px 12px 0; } }
@media (min-width: 641px) { .plan-tab.open { left: min(372px, calc(100% - 80px)); top: 36px; } .mapbox.fs .plan-tab.open { top: calc(var(--fsbar, 56px) + 34px); } }
.plan.demo .plan-list::before { content: "示範：導覽結束後會自動清掉"; display: block; margin: 0 0 6px; padding: 3px 8px; border-radius: 6px; background: var(--route); color: var(--paper); font-size: 12px; font-weight: 700; width: fit-content; }
.faq-cnote { display: block; margin-top: 6px; font-size: 12.5px; color: var(--muted); line-height: 1.6; }
.hotel-set { margin-top: 6px; border: 1.5px solid var(--route); background: none; color: var(--route); border-radius: 999px; padding: 3px 12px; font: 700 13px var(--f-body); cursor: pointer; }
.hotel-hint { display: block; margin-top: 4px; font-size: 12px; color: var(--muted); }
.faq-gnote { margin: 4px 0 10px; font-size: 12.5px; line-height: 1.7; color: var(--muted); }
.faq-copyurl { border: 0; background: none; padding: 0; font: inherit; color: var(--route); text-decoration: underline; text-underline-offset: 3px; cursor: pointer; }
.faq-subnote { margin-left: 6px; font: 400 13px var(--f-body); color: var(--muted); }
@media (max-width: 640px) {
  .plan.big { max-height: calc(100% - 40px) !important; height: calc(100% - 40px); }
  .mapbox.fs .plan.big { max-height: calc(100% - var(--fsbar, 56px) - 40px) !important; height: calc(100% - var(--fsbar, 56px) - 40px); }
  .plan-tab.open .pt-ar::before { content: "▲"; }
  .plan-tab.open.big .pt-ar::before { content: "▼"; }
}
#lmap .plan-dim { filter: opacity(.35); }
.help-q { flex: none; width: 22px; height: 22px; border-radius: 50%; border: 1.5px solid var(--ink); background: var(--paper); color: var(--ink); font: 700 13px/1 var(--f-body); cursor: pointer; padding: 0; margin-left: auto; }
.help-q:hover, .help-q:focus-visible { background: var(--ink); color: var(--paper); outline: none; }
.faq-item.flash { animation: faqflash 2.4s ease; border-radius: 8px; }
@keyframes faqflash { 0%, 60% { background: color-mix(in srgb, var(--route) 22%, transparent); } 100% { background: transparent; } }
@media (max-width: 640px) { .p2p-card { bottom: 46px !important; } }
#dist-note { flex-wrap: nowrap; }
#dist-note > p { min-width: 0; flex: 1; }
.icon-btn.help-btn span { font: 700 17px/1 var(--f-body); }
.tour-hole2 { box-shadow: none; background: rgba(255,255,255,.12); }
.faq-trio { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0 24px; align-items: start; }
.faq-col { min-width: 0; }
.faq-col .faq-list { grid-template-columns: 1fr; }
.faq-col .faq-sub { min-height: 2.6em; display: flex; flex-wrap: wrap; align-items: baseline; }
@media (max-width: 860px) { .faq-trio { grid-template-columns: 1fr; } .faq-col .faq-sub { min-height: 0; } }
.tour-foot .tour-skip { white-space: nowrap; }
.tour-dots { flex-wrap: wrap; row-gap: 4px; }
.icon-btn.names-btn { position: relative; }
.icon-btn .lm-tag { display: none; position: absolute; right: -4px; bottom: -4px; min-width: 16px; height: 16px; padding: 0 2px; box-sizing: border-box; border-radius: 8px; background: var(--ink); color: var(--paper); font: 700 10px/16px var(--f-body); text-align: center; pointer-events: none; }
.icon-btn.names-btn[aria-pressed="true"] .lm-tag { background: var(--route); }
/* labels grow and shrink with the zoom, like the hand-drawn map (--ls is set at every zoom) */
.spot .tab { padding: calc(3px * var(--ls, 1)) calc(9px * var(--ls, 1)) calc(4px * var(--ls, 1)); border-radius: calc(4px * var(--ls, 1)); }
.spot .t-name { font-size: calc(14px * var(--ls, 1)); }
.spot .t-wed, .spot .t-price { font-size: calc(11.5px * var(--ls, 1)); }
.spot.mid .t-name, .spot.compact .t-name { font-size: calc(12.5px * var(--ls, 1)); }
.spot.mid .t-wed, .spot.mid .t-price { font-size: calc(10.5px * var(--ls, 1)); }
.spot.mid .tab, .spot.compact .tab { padding: calc(2px * var(--ls, 1)) calc(7px * var(--ls, 1)) calc(3px * var(--ls, 1)); }
/* 全覽／簡潔 on a city with the hand-drawn layout: sizes in map units (--k = px per unit), as the hand-drawn map */
#lmap.geo .spot .tab { padding: calc(var(--k) * 8px) calc(var(--k) * 13px) calc(var(--k) * 10px); border-radius: calc(var(--k) * 4px); line-height: 1.25; }
#lmap.geo .spot .t-name { font-size: calc(var(--k) * 28px); line-height: calc(var(--k) * 34px); }
#lmap.geo .spot .t-wed, #lmap.geo .spot .t-price { font-size: calc(var(--k) * 21px); line-height: calc(var(--k) * 30px); }
#lmap.geo .spot.mid .t-name { font-size: calc(var(--k) * 24px); line-height: calc(var(--k) * 30px); }
#lmap.geo .spot.mid .t-wed, #lmap.geo .spot.mid .t-price { font-size: calc(var(--k) * 18px); line-height: calc(var(--k) * 22px); }
#lmap.geo .spot.mid .tab { padding: calc(var(--k) * 6px) calc(var(--k) * 11px) calc(var(--k) * 8px); }
#lmap.geo .spot.slim1 .tab, #lmap.geo .spot.compact .tab { padding: calc(var(--k) * 5px) calc(var(--k) * 12px); }
#lmap.geo .spot.slim1 .t-name, #lmap.geo .spot.compact .t-name { font-size: calc(var(--k) * 28px); line-height: calc(var(--k) * 34px); }
#lmap.geo .spot .t-rush { font-size: calc(var(--k) * 15px); }
.leaflet-pane path.river-line { stroke: #2F7FC1; stroke-opacity: .5; stroke-linecap: round; stroke-linejoin: round; fill: none; }   /* 2026-11-20: as strong as the roads (購物街 .5 / .7), the old pale blue disappeared */
#lmap.base-faded .leaflet-pane path.river-line { stroke-opacity: .7; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .leaflet-pane path.river-line { stroke: #5AA2E0; } }
:root[data-theme="dark"] .leaflet-pane path.river-line { stroke: #5AA2E0; }
.river-name span { position: absolute; white-space: nowrap; transform: translate(0, -50%); font-family: var(--f-body); font-weight: 500; color: var(--free); opacity: .85; font-size: inherit; }
#lmap.geo .spot .pin { --ps: clamp(7px, calc(var(--k) * 24px), 16px); width: var(--ps); height: var(--ps); left: calc(var(--ps) / -2); top: calc(var(--ps) / -2); border-width: clamp(1.2px, calc(var(--k) * 4px), 2.5px); }
</style>'''

drawer_js = drawer_js.replace(
 '<span class="share-note" id="d-share-note" role="status" aria-live="polite"></span></div>',
 '<span class="share-note" id="d-share-note" role="status" aria-live="polite"></span></div>\n    <div class="d-plan"><span>加入行程：</span>${PDAYS.map(d => `<button type="button" class="plan-day" data-day="${d.k}" aria-pressed="${planHas(d.k, s.id)}">${planHas(d.k, s.id) ? "✓ " : "＋ "}${d.label}</button>`).join("")}</div>')
drawer_js = drawer_js.replace('<div><dt>特色</dt>', '<div><dt>${s.custom ? "備註" : "特色"}</dt>')
# 我的住宿 (hotel): change it here
HOTEL_BOX = ('${s.id === "hotel" ? `<div class="d-mine d-hotel"><span>${s.myHotel ? "這是你設定的住宿。" : "這是作者住的旅館（範例）。"}</span><button type="button" id="h-change">${s.myHotel ? "修改" : "改成我的住宿"}</button>${s.myHotel ? \'<button type="button" id="h-reset">改回範例</button>\' : ""}</div>'
  '<div class="m-edit" id="h-edit" hidden><label><span>旅館名稱<span class="req">（必填）</span></span> <input id="h-name" type="text" maxlength="40" placeholder="例如：Hotel Ilaria"></label><label>位置 <input id="h-link" type="text" placeholder="Google 地圖網址，或 43.8429, 10.5027"></label><div class="pa-loc"><span class="pa-where" id="h-where">或</span><button type="button" class="m-pick" id="h-pick">點這裡去設定地圖</button></div><label>備註 <input id="h-note" type="text" maxlength="120" placeholder="想記的事，例如 check-in 時間"></label><div class="pa-btns"><button type="button" class="pa-ok" id="h-save">確認</button><button type="button" id="h-cancel">取消</button></div></div>` : ""}')
drawer_js = drawer_js.replace('<span class="share-note" id="d-share-note" role="status" aria-live="polite"></span></div>\n    <div class="d-plan">', '<span class="share-note" id="d-share-note" role="status" aria-live="polite"></span></div>\n    ' + HOTEL_BOX + '\n    <div class="d-plan">', 1)
assert 'h-change' in drawer_js
# 從住宿出發 on the 實用資訊 tab of every spot (not hotel / station)
drawer_js = drawer_js.replace('const hasPrac = !!(', 'const fromH = hotelFromLine(s);\n  const hasPrac = !!(fromH || ', 1)
drawer_js = drawer_js.replace('${s.stay ? `<div><dt>建議停留時間</dt>', '${fromH}${s.stay ? `<div><dt>建議停留時間</dt>', 1)
assert 'hotelFromLine' in drawer_js and '${fromH}' in drawer_js
drawer_js = drawer_js.replace('</button>`).join("")}</div>', '</button>`).join("")}</div>${s.custom ? `<div class="d-mine"><span>這是你自己加的點。</span><button type="button" id="d-editmine">編輯</button><button type="button" id="d-delmine">刪除景點</button></div><div class="d-sure" id="d-sure" hidden><span>確定刪除這個景點？</span><button type="button" id="d-delyes">刪除（行程裡的景點會一起刪除）</button><button type="button" id="d-delno">取消</button></div><div class="m-edit" id="m-edit" hidden><label>名稱 <input id="me-name" type="text" maxlength="40"></label><label>位置：貼 Google 地圖網址或座標 <input id="me-link" type="text" placeholder="Google 地圖網址，或 43.8429, 10.5027"></label><div class="pa-loc"><span class="pa-where ok" id="me-where">✓ 位置不變</span><button type="button" class="m-pick" id="me-pick">在地圖上重新點位置</button></div><label>備註 <textarea id="me-note" rows="3" maxlength="300"></textarea></label><div class="pa-btns"><button type="button" class="pa-ok" id="me-save">確認</button><button type="button" id="me-cancel">取消</button></div></div>` : ""}', 1)
drawer_js = drawer_js.replace('  document.getElementById("d-close").focus();',
 '  if (s.custom) bindMineEdit(s);\n  bindHotel(s);\n  drawer.querySelectorAll(".plan-day").forEach(b => b.addEventListener("click", () => { planToggle(b.dataset.day, s.id); openSpot(s.id); }));\n  document.getElementById("d-close").focus({ preventScroll: true });')
assert 'planToggle' in drawer_js and 'PDAYS.map' in drawer_js

engine = open(R + 'engine.js').read()
engine = open(R + 'city_lucca.js').read() + engine
import datetime as _dt
MAP_UPDATED = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
engine = 'const MAP_UPDATED = "' + MAP_UPDATED + '";   // shown in the paste box; links carry it so an older map can warn\n' + engine
out = f'''<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="color-scheme" content="light dark">
<title>盧卡古城景點地圖（真地圖版）</title>
<link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="apple-touch-icon.png"><meta name="theme-color" content="#F4F1E8"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="盧卡地圖">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@600;700&family=Noto+Sans+TC:wght@400;500;700&family=Cormorant+Garamond:ital,wght@1,500;1,600&display=swap">
<style>{leaflet_css}</style>
{css}
{extra_css}
</head><body>
{head_html}  <div class="mapbox">
    <div id="lmap" role="application" aria-label="盧卡古城地圖"></div>
{mapbox_rest}{hint}{faq}
</div>

{tail_html}<script>{leaflet_js}</script>
<script>{sortable_js}</script>
<script>
{data_js}
const LL = {json.dumps(C["ll"])}, AREA_LL = {json.dumps(C["area"])};
SPOTS.forEach(s => {{ if (s.id === "shopping") s.area = AREA_LL; }});
{simple_js}
{days_js}
{engine}
{visited_links_js}
{drawer_js}
</script>
</body></html>
'''
_base_btn = '<button class="icon-btn base-btn" type="button" aria-pressed="false" aria-label="隱藏底圖：只留城牆、道路和景點" data-tip="隱藏底圖"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 8l10 5 10-5-10-5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="m2 13 10 5 10-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M3 21 21 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="base-slash"/></svg></button>'
out, _n = re.subn(r'(<button class="icon-btn names-btn".*?</button>)', lambda m: m.group(1) + _base_btn, out, flags=re.S)
assert _n == 2, _n
out = out.replace('</head>', '<style>' + '\n/* ===== 2026-11-20 ===== */\n/* 我的行程: distance pills only after tapping the dashed line */\n.leaflet-pane path.plan-hit { stroke: transparent; stroke-width: 24; fill: none; cursor: pointer; }\n#lmap:not(.legs-on) .mid-pill.leg { display: none; }\n#lmap.planning .spot.in-plan .plan-no { z-index: 4; }\n.plan-list .p-vis, .plan-daymemo .pd-done { flex: none; font: 700 12px var(--f-body); padding: 2px 9px; border-radius: 999px; border: 1.5px solid var(--muted); background: var(--paper); color: var(--muted); cursor: pointer; white-space: nowrap; line-height: 1.4; }\n.plan-list .p-vis[aria-pressed=\"true\"], .plan-daymemo .pd-done[aria-pressed=\"true\"] { background: var(--open); border-color: var(--open); color: var(--paper); border-style: solid; }\n.plan-list li.p-visited .p-name::after { content: none; }\n.plan.c2 .plan-list .p-vis { display: inline-block; font-size: 11px; padding: 1px 7px; }\n.mapbox .spot.lbl-off svg.leader, .mapbox #lmap.lbl-none .spot svg.leader { display: none; }   /* a hidden label leaves no stray line */\n.mapbox .mid-pill.leg.leg-hide { display: none; }\n#lmap.planning .spot.in-plan .plan-no { transform: scale(clamp(.72, var(--ls, 1), 1)); }\n.mapbox .mid-pill.leg span { padding: 1px 7px; }\n/* this day\'s note + 這天全部去過 */\n.plan-daymemo { display: flex; align-items: center; gap: 8px; padding: 6px 12px; border-bottom: 1px solid var(--line); }\n.plan-daymemo .pd-memo { flex: 1; min-width: 0; font: 700 13px var(--f-body); color: var(--ink); background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 4px 8px; }\n.plan-daymemo .pd-memo:not(:placeholder-shown) { border-color: var(--route); background: var(--warn-bg); }\n.plan-daymemo .pd-done { flex: none; font: 700 12px var(--f-body); padding: 3px 9px; border-radius: 999px; border: 1.5px solid var(--muted); background: var(--paper); color: var(--muted); cursor: pointer; white-space: nowrap; }\n.plan-daymemo .pd-done[aria-pressed="true"] { border-style: dashed; }\n.plan.un-mode .plan-daymemo { display: none !important; }\n.plan-list li.p-visited .p-name { opacity: .55; text-decoration: line-through; text-decoration-thickness: 1px; }\n/* 待選景點: 公休日 */\n.un-off { font-size: 11.5px; color: var(--muted); white-space: nowrap; margin-left: auto; }\n.un-off.today { color: var(--paid); font-weight: 700; }\n.un-off:not(:empty) + .un-add { margin-left: 6px; }\n/* phone: the top bar always fits, even on narrow phones or with bigger text */\n@media (max-width: 640px) {\n  .mapbox.fs .fs-bar { gap: clamp(2px, 1vw, 5px); padding-left: max(6px, env(safe-area-inset-left, 0px)); padding-right: max(6px, env(safe-area-inset-right, 0px)); }\n  .mapbox.fs .fs-bar .icon-btn { flex: 0 1 32px; width: auto; min-width: 24px; height: auto; aspect-ratio: 1; }\n  .mapbox.fs .fs-bar .icon-btn svg { width: 60% !important; height: auto !important; max-width: 17px; }\n  .mapbox.fs .fs-btn { flex: 0 1 auto; white-space: nowrap; }\n  .mapbox.fs .fs-title { flex: 1 1 0; }\n}\n' + '</style>\n</head>', 1)
out = out.replace('</body>', '<script>if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("sw.js").catch(() => {});</script>\n</body>', 1)
out = out.replace('class="faq-note">連結不定時更新到出發前，2027 年 2 月之後停止更新。', 'class="faq-note">最新更新：' + MAP_UPDATED, 1)
# FAQ: questions the 功能導覽 already covers fold away under one link; the rest stay open
EYE_IC = '<span class="ic "><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg></span>'
# user's own wording (2026-11-18); [[ref:…]] becomes the number of the question whose title contains …
FAQ_EDIT = {
  '地圖好亂，可以乾淨一點嗎？': (None, '可以，有三個方法：① 按右上角的 ' + EYE_IC + ' 眼睛切到「簡潔」，框裡只留名稱；眼睛有三種：自動（預設，放不下的框自動縮小）、全覽（每個框都完整）、簡潔。② 參考 [[ref:街道底圖]] 把底圖調淡或關掉。③ 參考 [[ref:可以刪除景點嗎]] 把不要的點隱藏。'),
  '我只在盧卡待一天，可以只看最重要的景點嗎？': ('我只在這裡待一天，可以只看最重要的景點嗎？', '可以。景點依重要性分三層：「主要景點」「推薦」「次要」，在篩選列依自己的需求開關。'),
  '去過的景點可以不要留在地圖上嗎？': ('可以刪除景點嗎？', '預設的圖資（主要景點、推薦、次要）不能刪除，只有自己新增的私人景點，能從它的介紹頁按「刪除景點」刪掉。如果不想看到預設的景點，可以：① 點景點，在介紹最上面按「標記為已去過」，它就會從地圖上隱藏；想再看到，從篩選選「顯示去過的景點」，點開它再按一次就回來了。② 用上方的篩選把整層（主要景點／推薦／次要）關掉。'),
  '這張地圖是你的，我可以客製成自己的嗎？': ('可以新增景點嗎？', '可以。電腦在地圖空白處按右鍵、手機長按，或在「我的行程」按「＋ 地圖沒有的點」，就能加成紫色的點，詳細看 [[ref:自己加嗎]]。'),
  '畫面怪怪的，字和底色都是白的？': ('畫面怪怪的，字和底色都是白的看不清楚？', '通常是手機瀏覽器的「網頁深色模式」把顏色改亂了。Chrome：右上角「⋮」→「設定」→「主題」，取消勾選「盡可能為網站套用深色主題」；Samsung 瀏覽器：在設定裡關掉深色模式。改完重新整理。'),
  '地圖上的飯店可以改成我的嗎？': (None, '可以。點地圖上的 Hotel Ilaria（黑色方塊），按「改成我的住宿」，填旅館名稱和位置就好；每個景點介紹裡「從住宿出發」的步行時間，也會改照你的旅館計算。想換回來，按「改回範例」。'),
  '我還是想用 Google 地圖導航耶？': (None, '可以，幾乎所有地圖功能都有設定直接連結 Google 地圖。'),
  '可以把行程分享給朋友嗎？': ('怎麼給別人（別的裝置）「有」我資料的地圖？', '先照 [[ref:「沒有」我資料的地圖]] 打開一份乾淨的地圖。再到有你資料的那份地圖，按上方的「匯出整份地圖」複製連結（手機在「☰ 篩選」裡），去想接受資料的舊地圖按「匯入地圖」貼上連結，你的景點、行程和設定就會帶過去。'),
  '怎麼把整份地圖搬到另一台手機或電腦？': (None, None),
  '地圖上沒有的地方（餐廳、店）可以自己加嗎？': ('地圖上沒有的地方可以自己加嗎？', '可以。地圖空白處電腦按右鍵、手機長按，會跳出新增的設定框；也可以在「我的行程」按「＋ 地圖沒有的點」。（請注意，這個紀錄只存在你自己這台手機或電腦）'),
}
def _faq_edit(out):
    for old, (nt, na) in FAQ_EDIT.items():
        m = re.search(r'(<span class="n">Q\d+</span><span>)' + re.escape(old) + r'(</span></p><p class="faq-a">).*?(</p>)', out, flags=re.S)
        assert m, old
        if na is None:   # delete the whole question
            li0 = out.rfind('<li class="faq-item">', 0, m.start()); li1 = out.index('</li>', m.end()) + 5
            out = out[:li0] + out[li1:]; continue
        out = out[:m.start()] + m.group(1) + (nt or old) + m.group(2) + na + m.group(3) + out[m.end():]
    return out
def _faq_refs(out):
    titles = re.findall(r'<span class="n">(Q\d+)</span><span>([^<]*)</span>', out)
    def r(m):
        hit = [n for n, t in titles if m.group(1) in t]
        assert hit, m.group(1)
        return hit[0]
    return re.sub(r'\[\[ref:([^\]]+)\]\]', r, out)
def _faq_fold(out):
    out = _faq_edit(out)
    i = out.index('<ol class="faq-list">'); j = out.index('</ol>', i)
    items = re.findall(r'<li class="faq-item">.*?</li>', out[i:j], flags=re.S)
    COVERED = ['怎麼看某個景點的介紹', '可以看某個地方周邊的景點', '可以知道到某個景點要走多遠', '可以乾淨一點嗎', '待一天', '我只想去免費的景點', '早上很早或晚上還能去哪裡', '只看那幾天的營業時間', '手機上地圖太小', '可以排每天的行程嗎', '排好的行程在哪裡看', '可以直接用 Google 地圖導航嗎', '可以看到我現在在哪裡', '地圖上沒有的地方可以自己加', '可以把街道底圖藏起來']
    # 分享與換裝置: principle first (map data updates itself; your own settings stay in this browser), then how to share
    items.append('<li class="faq-item"><p class="faq-q"><span class="n">Q0</span><span>地圖更新是什麼？</span></p><p class="faq-a">景點、介紹、營業時間這些圖資大家都一樣，如有改版會自動提醒更新，讓你的資訊永遠維持在最新版，[[ref:看不到我的景點跟行程]] 裡你自己的設定（景點、行程那些）不會被自動更新動到。</p></li>')
    items.append('<li class="faq-item"><p class="faq-q"><span class="n">Q0</span><span>為什麼其他人的地圖跟我不一樣，看不到我的景點跟行程？</span></p><p class="faq-a">請參考 [[ref:地圖更新是什麼]]，這份地圖的圖資是自動更新的，但 [[ref:可以新增景點嗎]]～[[ref:飯店可以改成我的]] 行程、自己加的景點、標記去過的景點、星期幾去、住宿，這些自己設定的資訊，只存在你現在打開這個網址的瀏覽器裡。換手機、換電腦，或同一台換個瀏覽器打開（例如從 LINE 點開），都看不到。</p></li>')
    items.append('<li class="faq-item"><p class="faq-q"><span class="n">Q0</span><span>怎麼給別人（別的裝置）「沒有」我資料的地圖？</span></p><p class="faq-a">點 <button type="button" class="faq-copyurl" data-url="https://travelplanner-kaili.github.io/lucca/">travelplanner-kaili.github.io/lucca</button> 直接幫你複製網址，傳給對方。</p></li>')
    items.append('<li class="faq-item"><p class="faq-q"><span class="n">Q0</span><span>可以只匯出某一天的行程嗎？</span></p><p class="faq-a">可以。在「我的行程」按「匯出本日行程」，會把目前打開的這一天做成一個連結。開啟另一個裝置的「我的行程」，選「＋ 匯入本日行程」，會把你的行程加成新的一天。用「匯入地圖」貼上整份地圖的連結時，也可以選「只匯入其中一天」。</p></li>')   # 2026-11-27: one-day share is back
    # 2026-11-27: the 我的行程 tour got 去過 and 這天的筆記; the Q&A says the same
    items.append('<li class="faq-item"><p class="faq-q"><span class="n">Q0</span><span>行程裡可以標記去過了嗎？</span></p><p class="faq-a">可以。每個景點右邊按「去過」，或按「這天全部去過」一次標好。跟景點介紹裡的「標記為已去過」是同一個，去過的景點會從地圖上隱藏。</p></li>')
    DROP = ['別人能看到我的行程嗎', '為什麼點開同一個地圖，看到的東西不一樣', '沒有網路也能用嗎', '沒有網路時怎麼導航', '為什麼拉遠之後景點框不見了']   # said in 為什麼其他人看不到我的行程
    items = [x for x in items if not any(k in x for k in DROP)]
    ttl0 = lambda x: re.search(r'<span class="n">Q\d+</span><span>([^<]*)', x).group(1)
    # 我的行程 has its own section (its own tour + folded text), in this order
    PLANQ = ['可以排每天的行程嗎', '排好的行程在哪裡看', '行程的日期怎麼設定', '換順序', '標記去過', '還沒排進行程', '轉成文字', '只匯出某一天']
    planq = []
    for k in PLANQ:
        for x in items:
            if k in ttl0(x) and x not in planq: planq.append(x)
    items = [x for x in items if x not in planq]
    cov = [x for x in items if any(k in x for k in COVERED)]
    rest = [x for x in items if x not in cov]
    CUSTQ = ['可以新增景點嗎', '可以刪除景點嗎', '飯店可以改成我的']
    custq = []
    for k in CUSTQ:
        for x in rest:
            if k in ttl0(x) and x not in custq: custq.append(x)
    rest = [x for x in rest if x not in custq]
    GROUPS = [
              ('分享與換裝置', ['地圖更新是什麼', '看不到我的景點跟行程', '「沒有」我資料的地圖', '「有」我資料的地圖', '把景點分享給朋友']),
              ('其他', ['像 App 一樣'])]
    CUST_NOTE = ('<p class="faq-gnote">※ 客製設定只會存在你製作的那一個頁面。換手機、換電腦，或同一台換個瀏覽器打開（例如從 LINE 點開），都看不到。相關討論請參考 [[ref:看不到我的景點跟行程]]、[[ref:「有」我資料的地圖]]。<br>※ 最好設一個捷徑在桌面，方便從同一入口進去編輯本機設定，相關討論請參考 [[ref:像 App 一樣]]。</p>')
    GNOTE = {}
    grouped, used = [], set()
    for g, keys in GROUPS:
        ttl = lambda x: re.search(r'<span class="n">Q\d+</span><span>([^<]*)', x).group(1)
        lst = []
        for k in keys:
            for x in rest:
                if k in ttl(x) and x not in used and x not in lst: lst.append(x)
        if g == '其他': lst = lst + [x for x in rest if x not in used and x not in lst]
        used.update(lst); grouped.append((g, lst))
    num = lambda lst, start: [re.sub(r'<span class="n">Q\d+</span>', '<span class="n">Q%d</span>' % (start + k), x, count=1) for k, x in enumerate(lst)]
    cov = num(cov, 1); planq = num(planq, len(cov) + 1); custq = num(custq, len(cov) + len(planq) + 1); n0 = len(cov) + len(planq) + len(custq) + 1; parts = []
    for g, lst in grouped:
        if not lst: continue
        parts.append('<h4 class="faq-grp">%s</h4>%s<ol class="faq-list">%s</ol>' % (g, GNOTE.get(g, ''), ''.join(num(lst, n0)))); n0 += len(lst)
    block = ('<div class="faq-trio"><section class="faq-col"><h3 class="faq-sub">基礎功能</h3>'
             '<details class="faq-more"><summary><button type="button" class="tour-again faq-tour-btn">▶ 快速導覽</button><span class="faq-or">或</span><span class="faq-open">點開看文字</span></summary><ol class="faq-list">%s</ol></details>'
             '</section><section class="faq-col"><h3 class="faq-sub">我的行程</h3>'
             '<details class="faq-more"><summary><button type="button" class="plan-tour-again faq-tour-btn">▶ 快速導覽</button><span class="faq-or">或</span><span class="faq-open">點開看文字</span></summary><ol class="faq-list">%s</ol></details>'
             '</section><section class="faq-col"><h3 class="faq-sub">客製你的地圖<small class="faq-subnote">（資料只會存在你製作的那一個頁面）</small></h3>'
             '<details class="faq-more"><summary><button type="button" class="custom-tour-again faq-tour-btn">▶ 快速導覽</button><span class="faq-or">或</span><span class="faq-open">點開看文字</span></summary>%s<ol class="faq-list">%s</ol></details>'
             '</section></div><h3 class="faq-sub">其他問題</h3>%s') % (''.join(cov), ''.join(planq), CUST_NOTE, ''.join(custq), ''.join(parts))
    return out[:i] + block + out[j + 5:]
out = _add_help(_faq_refs(_faq_fold(out)))
assert 'const REPORT_BUILD = "' in out
out = re.sub(r'const REPORT_BUILD = "[^"]*";', 'const REPORT_BUILD = "真地圖版 " + MAP_UPDATED;', out, count=1)
open(R + 'lucca-real.html', 'w').write(out)
open(R + 'version.json', 'w').write(json.dumps({'updated': MAP_UPDATED}))
print('ok', len(out))
