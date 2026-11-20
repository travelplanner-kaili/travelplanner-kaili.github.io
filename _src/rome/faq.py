"""使用方式 Q&A shown under the map. Icons reuse the map's own button drawings so they match."""
import re

def _svg(html, key):
    i = html.find(key)
    if i < 0: return ""
    j = html.find("<svg", i); e = html.find("</svg>", j) + 6
    return html[j:e]

QA = [
 ("怎麼看某個景點的介紹？",
  "點地圖上的景點框，旁邊會打開介紹：「介紹」寫景點有什麼好看，「💡 實用資訊」有營業時間、票價、休館和預約提醒、怎麼排時間。比較重要的路會特別標出來，橘色的路也可以點，裡面會介紹那條路可以幹嘛。"),
 ("可以看某個地方周邊的景點嗎？",
  "電腦版在景點上按兩下，會顯示方圓 100 公尺內的景點；再按兩下，再擴大 100 公尺。手機、平板等小螢幕改成長按景點、再長按一次擴大。點一下地圖空白處就會關掉。"),
 ("可以知道到某個景點要走多遠嗎？",
  "按右上角的 {dist} 距離模式，先點起點、再點終點，就會顯示兩個景點間的距離和步行時間，省掉在 Google 地圖上一個個輸入的時間。（直線距離 ×1.3 估算，實際路線以 Google 地圖為準）"),
 ("地圖好亂，可以乾淨一點嗎？",
  "可以。按右上角的 {eye} 簡潔模式，框裡就只留名稱。需要快速看票價和營業時間時，再按一次 {eye} 就會把完整資訊開回來。"),
 ("我只去羅馬兩天，可以只看最重要的景點嗎？",
  "可以。景點依重要性分三層：「主要景點」「推薦」「次要」，在篩選列（手機在上方的「☰ 篩選」裡）點選要顯示哪幾層，依自己的需求開關。"),
 ("我只想去免費的景點？",
  "可以。篩選列只留「免費景點」、把「需購票景點」關掉，要買票的景點就會變淡（還是可以點開看）。"),
 ("義大利景點開放時間很短，早上很早或晚上還能去哪裡？",
  "篩選列選「冷門時段」，會突顯早上 9 點前或晚上 7 點後還能去的景點。"),
 ("有推薦的散步路線嗎？",
  "按右上角的 {walk} City Walk，可以只挑想看的路線，例如貝尼尼之路、卡拉瓦喬之路、米開朗基羅之路、科爾索購物之路。點路線或路線旁的距離膠囊，會打開路線介紹和沿途吃什麼。"),
 ("想逛街買東西要去哪裡？",
  "地圖上橘色的路就是可以購物的路，點路名可以看介紹。按右上角的 {shop} 購物，還會加上店家（綠色實心框）。（我不愛購物所以放得不多，有時間會慢慢新增）"),
 ("去過的景點可以不要留在地圖上嗎？",
  "可以。點景點，在介紹最上面按「標記為已去過」，那個景點就會從地圖上消失。想再看到時，篩選列會出現「顯示去過的景點」，按下去就會回到地圖上。（這個紀錄只存在你自己這台手機或電腦）"),
 ("這張地圖是你的，我可以客製成自己的嗎？",
  "可以。用上面的「去過」功能，把自己不要的點關掉，這張地圖就變成你的囉。（一樣只存在你自己這台手機或電腦）"),
 ("地圖上的 HOTEL 可以改成我的嗎？",
  "沒辦法直接改，但你可以看自己住在哪個景點附近，把那個景點當作你的飯店定位點。"),
 ("手機上地圖太小？",
  "按 {full} 全螢幕（手機一打開就是全螢幕）。地圖可以單指拖曳、雙指縮放，按右下角的 ⤢ 回到整張地圖。"),
 ("我還是想用 Google 地圖導航耶？",
  "可以。打開景點介紹，上方的 {pin} 就是 Google 地圖連結。"),
 ("可以把景點分享給朋友嗎？",
  "可以。在景點介紹上方點 {share} 分享。"),
 ("發現資料有錯怎麼辦？",
  "點景點介紹裡的 {warn} 回報，或頁面最下方的「⚠ 發現錯誤？匿名回報給作者」，不用留下任何個人資料。"),
 ("畫面怪怪的，字和底色都是白的？",
  "通常是手機瀏覽器的「網頁深色模式」把顏色改亂了。Chrome：右上角「⋮」→「設定」→「主題」，取消勾選「盡可能為網站套用深色主題」；Samsung 瀏覽器：在設定裡關掉深色模式。改完重新整理。"),
]

PIN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5a6.5 6.5 0 0 0-6.5 6.5c0 4.9 6.5 12.5 6.5 12.5s6.5-7.6 6.5-12.5A6.5 6.5 0 0 0 12 2.5zm0 9a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" fill="currentColor"/></svg>'
SHARE = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5.5" r="2.6" fill="currentColor"/><circle cx="6" cy="12" r="2.6" fill="currentColor"/><circle cx="18" cy="18.5" r="2.6" fill="currentColor"/><path d="M8.3 10.8 15.7 6.7M8.3 13.2l7.4 4.1" stroke="currentColor" stroke-width="2" fill="none"/></svg>'
WARN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 20.5h20L12 3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M12 9.5v5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="17.3" r="1.3" fill="currentColor"/></svg>'

CSS = """
/* 使用方式 Q&A under the map */
.faq { margin-top: 28px; border-top: 1px solid var(--line); padding-top: 18px; }
.faq-head { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 4px 16px; margin-bottom: 12px; }
.faq h2 { font-family: var(--f-display); font-size: 22px; margin: 0; }
.faq-note { font-size: 13px; color: var(--muted); margin: 0; }
.faq-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap: 10px 24px; margin: 0; padding: 0; list-style: none; }
.faq-item { min-width: 0; padding: 10px 0; border-bottom: 1px dashed var(--line); }
.faq-q { font-weight: 700; margin: 0 0 3px; display: flex; gap: 8px; }
.faq-q .n { flex: none; color: var(--paid); font-variant-numeric: tabular-nums; }
.faq-a { margin: 0; color: var(--ink); font-size: 14.5px; line-height: 1.75; padding-left: 2.4em; }
.ic { display: inline-grid; place-items: center; width: 24px; height: 24px; border-radius: 50%; border: 1.5px solid var(--ink); color: var(--ink); background: var(--paper); vertical-align: -6px; margin: 0 2px; }
.ic svg { width: 14px !important; height: 14px !important; display: block; }
.ic.ic-walk { border-color: var(--route); color: var(--route); }
.ic.ic-shop { border-color: var(--open); color: var(--open); }
.ic.ic-act { border-color: var(--free); color: var(--free); }
.ic.ic-warn { border-color: var(--paid); color: var(--paid); }
"""

def build(html, qa=None, note="連結不定時更新到出發前，2027 年 2 月之後停止更新。"):
    qa = qa or QA
    icons = {
        "eye": ("", _svg(html, 'class="icon-btn names-btn"')),
        "dist": ("", _svg(html, 'id="f-dist"')),
        "walk": ("ic-walk", _svg(html, 'id="f-route"')),
        "shop": ("ic-shop", _svg(html, 'id="f-shop"')),
        "full": ("", _svg(html, 'id="fs-open"')),
        "pin": ("ic-act", PIN), "share": ("ic-act", SHARE), "warn": ("ic-warn", WARN),
    }
    def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    def fill(t):
        t = esc(t)
        return re.sub(r"\{(\w+)\}", lambda m: f'<span class="ic {icons[m.group(1)][0]}">{icons[m.group(1)][1]}</span>', t)
    items = "".join(f'<li class="faq-item"><p class="faq-q"><span class="n">Q{i}</span><span>{esc(q)}</span></p><p class="faq-a">{fill(a)}</p></li>' for i, (q, a) in enumerate(qa, 1))
    return f'<section class="faq" id="faq" aria-labelledby="faq-h"><div class="faq-head"><h2 id="faq-h">使用方式</h2><p class="faq-note">{esc(note)}</p></div><ol class="faq-list">{items}</ol></section>'


# 盧卡：no City Walk / shopping buttons
QA_LUCCA = [QA[0][0:1] + ("點地圖上的景點框，旁邊會打開介紹：「介紹」寫景點有什麼好看，「💡 實用資訊」有營業時間、票價、午休和聯票提醒、怎麼排時間。",)] + [QA[1], QA[2], QA[3],
 ("我只在盧卡待一天，可以只看最重要的景點嗎？", QA[4][1]), QA[5], QA[6]] + QA[9:11] + [
 ("地圖上的飯店可以改成我的嗎？", QA[11][1])] + QA[12:]

# 威尼斯：no City Walk / shopping / hotel; orange streets are shopping streets
QA_VENICE = [
 ("怎麼看某個景點的介紹？", "點地圖上的景點框，旁邊會打開介紹：「介紹」寫景點有什麼好看，「💡 實用資訊」有營業時間、票價、預約、休館和嘉年華注意事項。橘色的路是購物街，點路名也會介紹那條路可以逛什麼。"),
 QA[1],
 ("可以知道到某個景點要走多遠嗎？", "按右上角的 {dist} 距離模式，先點起點、再點終點，就會顯示兩個景點間的距離和步行時間。（直線距離 ×1.3 估算；威尼斯巷子彎來彎去，過大運河要走橋或搭船，實際以 Google 地圖為準）"),
 QA[3],
 ("我只在威尼斯待兩天，可以只看最重要的景點嗎？", QA[4][1]),
 QA[5], QA[6],
 ("想逛街買東西要去哪裡？", "地圖上橘色的路就是購物街，點路名可以看介紹。"),
 QA[9], QA[10],
] + QA[12:]

DAYS_Q = ("我只有某幾天會去，可以只看那幾天的營業時間嗎？",
  "可以。篩選列的「星期幾去」點選星期幾（可以複選，例如只選二、四），景點框裡就只顯示那幾天的營業時間，有休館的會寫「週一休」；你選的日子全部都休館的景點會變淡，框裡寫「你選的日子休館」。選擇會記在你自己的手機或電腦。（節日、特殊活動這類臨時休館不會算進來，請看景點的實用資訊）")
QA_ROME = QA[:7] + [DAYS_Q] + QA[7:]

QA_LUCCA = QA_LUCCA[:7] + [(DAYS_Q[0], DAYS_Q[1].replace("篩選列的「星期幾去」", "篩選列的「星期幾去」（預設是週三）"))] + QA_LUCCA[7:]
QA_VENICE = QA_VENICE[:7] + [(DAYS_Q[0], DAYS_Q[1].replace("篩選列的「星期幾去」", "篩選列的「星期幾去」（預設是週五六日）"))] + QA_VENICE[7:]
