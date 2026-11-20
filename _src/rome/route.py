# City Walk routes for the Rome map (used by build.py)
import math
S = 2.2
LON0, LAT0 = 12.4475, 41.9205
KX = 111320 * math.cos(math.radians(41.9)) / S
KY = 110950 / S
def proj(lat, lon): return [round((lon - LON0) * KX, 1), round((LAT0 - lat) * KY, 1)]

WAY = [(41.9142103, 12.4921442), (41.91380, 12.49000), (41.9135972, 12.4871019), (41.91450, 12.48450),
       (41.9149545, 12.4827624), (41.91380, 12.48100), (41.91230, 12.47930), (41.9111207, 12.4779391),
       (41.91130, 12.47720), (41.91100, 12.47690), (41.9110163, 12.4762093), (41.9114632, 12.4762433)]
def geom(way):
    pts = [proj(*p) for p in way]
    length_m = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) * S
    return pts, f"{length_m/1000:.1f}", round(length_m / 70 / 5) * 5   # relaxed pace ~70 m/min
pts, km, mins = geom(WAY)

ROUTES = [dict(
  id="borghese-walk", name="City Walk：博爾蓋賽・蘋丘之路（博爾蓋賽美術館 → 人民廣場）", tag="博爾蓋賽・蘋丘之路",
  latin="Villa Borghese · Pincio · Piazza del Popolo",
  stops=["borghese", "esculapio", "pincio", "popolo", "miracoli", "montesanto", "popolochurch"],
  areas=["villaborghese"],   # parks the walk passes through: lit up with the route
  pts=pts,
  summary=f"這段路線前 80% 都在博爾蓋賽別墅公園裡，本質上就是一趟從公園最東端走到最西端的純綠地步行：從東側角落的博爾蓋賽美術館出發，橫穿公園到西側懸崖邊的 蘋丘平台，再順著之字形石階走下人民廣場。全長約 {km} 公里，邊走邊看約 {mins} 分鐘（不含參觀）。",
  plan=["13:00 博爾蓋賽美術館（預約 13:00 場次，參觀 2 小時）",
        "15:00 出館，沿林蔭大道往西散步，經過 Piazza di Siena 橢圓草地",
        "15:30 湖畔醫神神殿：坐下來歇腳，想划船可以在這裡租",
        "16:30 蘋丘平台：俯瞰人民廣場、等夕陽（1 月底日落約 17:15）",
        "17:20 走之字形階梯下到人民廣場",
        "17:30 人民聖母教堂看卡拉瓦喬（開到 18:00；週日 16:30–18:00）"],
  stopsText=[["博爾蓋賽美術館", "起點，在公園最東邊的角落。看完展覽步出美術館門口，腳下已經是公園的碎石林蔭大道；門票只含館內，公園免費。"],
             ["醫神神殿（湖畔）", "中段：沿公園主步道（Viale dei Pupazzi／Viale del Lago）往西走，兩側是大片草坪、高聳的義大利傘松與石雕噴泉；途中經過公園中心的湖畔小神廟，可以在湖邊看水鴨野禽、稍作歇息。"],
             ["蘋丘平台", "高潮：平台仍在公園西側邊緣的圍牆內，是緊鄰山丘懸崖的高空觀景露台。人民廣場就在正下方，往前遠眺是整座羅馬城與聖彼得大教堂的圓頂。"],
             ["人民廣場", "終點：看完夕陽或市景，順著平台兩側蜿蜒的之字形景觀石階（Scalinata del Pincio）一路往下，踏上石磚平地的那一刻才真正離開公園，走進人民廣場。"],
             ["奇蹟聖母堂", "廣場南側「雙子教堂」的西側那座（面向南方的右手邊）。每天開，下午 16:00 後可入內；2026 年中有整修暫停開放的回報，去之前先確認。"],
             ["蒙特桑托聖母堂", "雙子教堂的東側那座，又叫藝術家教堂。平日只在 17:30–19:30 開，傍晚下山剛好；週日中午 12:00 有藝術家彌撒。兩座外觀對稱、內部完全不同，可以兩邊都進去比較。"],
             ["人民聖母教堂", "廣場北側城門旁，卡拉瓦喬兩幅真跡與拉斐爾設計的基吉小堂。"]],
  why=["完全隔絕車潮：從美術館出來到看見人民廣場之前，全程都是純步行綠地，沒有紅綠燈和車水馬龍，走起來非常安靜舒服。",
       "全程下坡或平路：美術館和平台都在山丘高處，橫穿公園時是在台地上走平路，最後順著階梯下山，完全不用吃力爬坡。"],
  start="美術館在平奇歐山丘延伸出來的高台上，從市區走過去是上坡（從飯店約 2.4 公里）。建議從飯店搭公車或計程車直接到美術館門口，省下爬坡的體力。",
  end="走完在人民廣場，可以沿科爾索大道（Via del Corso）一路往南逛回飯店，約 1.2 公里、15～20 分鐘；或從北側城門外的地鐵 A 線 Flaminio 站搭車。",
  food=dict(
    intro="山上和公園裡都有東西吃，從隨買隨吃的輕食點心，到坐下來看風景的景觀餐廳都有。不過強烈建議在山上簡單吃點輕食墊墊胃就好，大餐留到走下山、到人民廣場再吃，體驗會好很多。",
    places=[
      dict(name="ViVi - Galleria Borghese", where="起點・博爾蓋賽美術館地下室", kind="健康輕食咖啡館・€10–20",
           hours="週一休；週二至六 09:00–18:30，週日 09:00–19:00（Google 地圖資料）",
           desc="美術館地下室附設的咖啡館，提供有機輕食與飲品。就算沒有買票進展廳，也能從側邊下樓上洗手間或點杯咖啡歇腳。",
           q="ViVi Galleria Borghese", pid="ChIJI4tuCTFhLxMRE7QzUDXJwn4"),
      dict(name="Casina del Lago", where="中段・湖畔醫神神殿旁", kind="咖啡吧・€1–10",
           hours="每日 08:00–17:30（Google 地圖資料）",
           desc="在公園正中心的湖畔，綠意環繞的戶外休閒小店。觀光區定位鮮明，餐點以簡單果腹為主，Google 評價普通，當作喝咖啡、上洗手間的歇腳點就好。",
           q="Casina del Lago Villa Borghese", pid="ChIJb5wObLdhLxMRui249WGdOCw"),
      dict(name="Casina Valadier", where="高潮・蘋丘平台後方", kind="景觀餐廳與酒吧・中高價位",
           hours="Google 地圖目前把它標為婚宴、活動場地，去之前先確認當天有沒有對外營業",
           desc="平奇歐平台後方的新古典主義莊園，露台可以俯瞰羅馬全景。適合吃精緻義大利料理，或黃昏時來一杯開胃酒（Aperitivo）。想在室內吃正餐通常要提前預約，服裝也要整齊。",
           q="Casina Valadier", pid="ChIJHVzf4f5gLxMRM1GL6ClUDVM")],
    why=["公園裡大多是觀光客輕食亭（Chiosco）：平奇歐平台步道兩側有幾輛小餐車賣熱狗、夾心麵包和飲料，價格偏貴，多是微波或冷食，口味普通。",
         "下山後選擇爆棚：走下之字形階梯進到人民廣場周邊，特別是 Via di Ripetta、Via del Corso 兩側的小巷，有很多道地的羅馬小酒館（Trattoria）、手工義大利麵館、薄脆披薩店和老牌冰淇淋店。",
         "最舒服的節奏：看完展覽在美術館地下室或湖邊喝杯咖啡、吃個可頌提神，一路散步穿過公園，在平台看完夕陽再輕鬆走下山，剛好在市區吃熱騰騰的道地晚餐。"]),
  tips=__import__("notes").GONGYUE + ["如果搶到的是早上 09:00 場次，也可以走同一條路線，只是看不到 Pincio 的夕陽，而且人民聖母教堂中午 12:00 就關門。",
        "週一美術館休館，這條路線要避開週一。",
        "蒙特桑托聖母堂（藝術家教堂）平日 17:30 後才開、週六不開；如果是週日（旅程中是 1/31），改成中午 11:30 前到人民廣場，參加 12:00 的藝術家彌撒。"]
)]


# ---- Route 2: ancient core -> Monti lanes ----
WAY2 = [(41.8902102, 12.4922309), (41.8898, 12.4906), (41.8890, 12.4893), (41.8886559, 12.4875481),   # Colosseo -> Arch -> Palatino
        (41.8905, 12.4870), (41.8920906, 12.4864378), (41.8927, 12.4871), (41.8936, 12.4888),           # down to the Forum, out to Via dei Fori Imperiali
        (41.8948378, 12.4910085),                                                                      # Piazza della Madonna dei Monti (lunch)
        (41.8949, 12.4920), (41.8942, 12.4922), (41.8937984, 12.4931498),                               # Via Leonina -> Via Cavour -> Borgia steps -> San Pietro in Vincoli
        (41.8942, 12.4922), (41.8947, 12.4912), (41.8956, 12.4906), (41.8963, 12.4902),                 # back down, Via dei Serpenti north
        (41.8967, 12.4925), (41.8972, 12.4949), (41.8983274, 12.495782), (41.8972, 12.4949),            # Via Panisperna -> Santa Pudenziana and back
        (41.8960, 12.4940), (41.8949, 12.4929),                                                         # Via Urbana -> Via Leonina
        (41.8948378, 12.4910085)]                                                                      # back to the fountain
_p2, km2, mins2 = geom(WAY2)
from marks import MONTI_CHAIN
_marks2 = [dict(n=m[0], name=m[1], q=m[2], x=round(proj(m[3], m[4])[0] + m[5][0], 1), y=round(proj(m[3], m[4])[1] + m[5][1], 1)) for m in MONTI_CHAIN]
ROUTES.append(dict(
  id="monti-walk", name="City Walk：古羅馬・蒙蒂之路（古羅馬核心 → 蒙蒂區巷弄）", tag="古羅馬・蒙蒂之路",
  latin="Colosseo · Palatino · Foro Romano · Monti",
  stops=["colosseo", "palatino", "foro", "vincoli", "monti", "pudenziana"],
  areas=["monti"],
  marks=_marks2,
  chainTitle="蒙蒂區散步順序（①～⑨ 對應地圖上的編號）",
  chain=__import__("notes").MONTI_CHAIN_TIPS,
  way=WAY2,
  summary=f"上午用同一張聯票走完古羅馬競技場、帕拉丁山和古羅馬廣場，從廣場北側出口出來，過帝國議事廣場大道就走進 Monti。中午在巷弄吃飯，下午爬博吉亞階梯看聖伯多祿鎖鏈堂的《摩西像》，再沿四條石磚老街逛選品店和古著小店，最後回到噴泉廣場喝杯開胃酒。全長約 {km2} 公里，純步行約 {mins2} 分鐘（不含參觀）；古蹟區內的路線是示意。",
  stopsText=[["羅馬競技場", "起點：預約 08:30 開門第一場，人最少。看完從君士坦丁凱旋門旁往帕拉丁山走。"],
             ["帕拉丁山", "古羅馬皇宮所在的山丘，在遺址間散步，從山上俯瞰古羅馬廣場。"],
             ["古羅馬廣場", "從帕拉丁山往下走進廣場，沿聖道（Via Sacra）看神殿與元老院遺跡，再從北側出口出來（出去就不能再進），過帝國議事廣場大道沿 Via della Madonna dei Monti 走進 Monti 吃午餐。"],
             ["聖伯多祿鎖鏈堂", "午休後 15:00 開門。從噴泉廣場沿 Via Leonina 走到 Via Cavour，穿過拱門爬上博吉亞階梯（Scalinata dei Borgia），就到教堂，看米開朗基羅的《摩西像》和聖伯多祿的鐵鎖鏈。"],
             ["蒙蒂區", "終點：走下階梯回到 Monti，從 Piazza della Madonna dei Monti 沿 Via dei Serpenti 往北、右轉 Via Panisperna、再沿 Via Urbana 繞回噴泉廣場，沿路是獨立選品店、古著小店、復古咖啡館與餐酒館；傍晚在噴泉旁喝杯開胃酒收尾。"],
             ["聖普切恩齊亞納大殿", "Via Urbana 東北端的老教堂，有羅馬最古老的 4 世紀馬賽克。只開上午，下午經過只能看外觀；想進去可以另外排一個上午。"]],
  why=["一張聯票走完古羅馬三大遺跡，出口直接接進 Monti，不用回頭走擠滿觀光客的主幹道。",
       "上午看兩千年前的帝國，下午逛生活巷弄，一動一靜；Monti 沒有拉客的觀光餐廳，吃飯、喝咖啡都舒服。"],
  flowTitle="競技場＋蒙蒂區的半日動線",
  flow=["古羅馬重頭戲：參觀古羅馬競技場與古羅馬廣場／帕拉丁山，這時正好就在 Monti 腳下。",
        "轉進蒙蒂山丘：順著階梯走進蒙蒂區，直接參觀聖伯多祿鎖鏈堂，欣賞米開朗基羅的《摩西像》。",
        "暮色老街漫步：順著 Via Urbana 和 Via del Boschetto 逛選品店、看常春藤老建築，在噴泉廣場旁稍作歇息。",
        "用餐或打道回府：在 Monti 的小酒館吃晚餐，吃完順路散步看競技場與帝國議事廣場的打燈夜景回飯店。"],
  plan=["08:30 羅馬競技場（預約開門第一場，約 1.5 小時）",
        "10:00 從君士坦丁凱旋門旁上帕拉丁山（約 1.5 小時）",
        "11:30 往下走進古羅馬廣場（約 1 小時）",
        "12:30 從北側出口出來，走進 Monti 吃午餐",
        "15:00 爬博吉亞階梯到聖伯多祿鎖鏈堂看《摩西像》（約 30 分鐘）",
        "15:40 逛 Via dei Serpenti → Via Panisperna → Via Urbana 的選品店與古著小店",
        "17:30 回到 Piazza della Madonna dei Monti，噴泉旁喝杯開胃酒",
        "19:30 在 Monti 的小酒館吃晚餐",
        "21:00 散步看競技場與帝國議事廣場的打燈夜景，走回飯店"],
  start="從飯店走到古羅馬競技場約 2.2 公里、25～30 分鐘（經威尼斯廣場、沿帝國議事廣場大道一路往東），也可以搭計程車；地鐵 B 線 Colosseo 站出站就到。",
  end="從 Monti 走回飯店約 1.7 公里、20～25 分鐘（經帝國議事廣場大道、威尼斯廣場），可以順便看夜晚打燈的帝國議事廣場；地鐵 B 線 Cavour 站就在博吉亞階梯旁。",
  tips=["聯票：競技場要預約入場時段；帕拉丁山和古羅馬廣場在 24 小時內各入場一次（詳見羅馬競技場的實用資訊）。",
        "古蹟區冬季 16:30 關門，路面是碎石和古道，要穿好走的鞋、帶水。",
        "聖伯多祿鎖鏈堂 12:20–15:00 午休，週日上午 09:00 才開；進教堂要遮住肩膀和膝蓋。",
        "Monti 往南沿 Via dei Serpenti 走到底，約 5 分鐘就回到競技場，兩邊可以隨時接上。"],
))

# ---- Route 3: Via del Corso shopping walk (user-requested 2026-11-11) ----
WAY3 = [(41.9110163, 12.4762093), (41.9097, 12.4769), (41.9053, 12.4786), (41.9012, 12.4802),   # Piazza del Popolo -> Largo Goldoni -> Largo Chigi
        (41.9027487, 12.4845887),                                                              # Via del Tritone -> Rinascente
        (41.9016, 12.4840), (41.9009325, 12.483313),                                           # down to the Trevi Fountain
        (41.8997, 12.4809),                                                                    # Via delle Muratte back to the Corso
        (41.8963, 12.4821), (41.8957663, 12.4825739)]                                          # south to Piazza Venezia
_L3 = lambda *qs: [[q, q + " Roma"] for q in qs]
ROUTES.append(dict(
  id="corso-walk", name="City Walk：科爾索購物之路", tag="科爾索購物之路",
  latin="Via del Corso · Rinascente · Fontana di Trevi · Piazza Venezia",
  stops=["popolo", "rinascente", "trevi", "venezia"],
  avoid=["miracoli", "montesanto", "popolochurch", "pincio", "spagna", "hotel", "colonna", "ignazio", "arapacis", "medici", "pantheon", "navona", "luigi", "doria", "barberini", "minerva", "vittoria", "rinascente"],   # the Corso runs through the busiest part of the map
  way=WAY3,
  summary="Via del Corso 是羅馬市中心最長、最熱鬧的購物主軸，北起人民廣場、南到威尼斯廣場，一條直線不會迷路，是挑選大眾品牌與義大利連鎖服飾折扣的大本營。中途在 Largo Chigi 轉進 Via del Tritone 逛文藝復興百貨，再走 3 分鐘到特雷維噴泉，最後回到 Corso 一路往南走到威尼斯廣場。",
  stopsText=[["人民廣場", "起點：廣場南側雙子教堂中間那條筆直的大街就是 Via del Corso，順著往南走。"],
             ["文藝復興百貨", "中途：在科隆納廣場旁的 Largo Chigi 左轉進 Via del Tritone，走 3 分鐘就到。精品、羊絨、皮件集中在這裡，地下室看古羅馬處女水道遺址，頂樓喝咖啡歇腳。"],
             ["特雷維噴泉", "從百貨往南下坡 3 分鐘就到，傍晚噴泉打燈很美。"],
             ["威尼斯廣場", "終點：沿 Via delle Muratte 回到 Corso 繼續往南，大街盡頭的白色大理石建築就是維托里亞諾紀念堂。"]],
  chainTitle="沿路逛什麼",
  chain=[dict(t="義大利本土高實用性品牌：羊絨專門店 Falconeri、經典羊毛內搭 Intimissimi，還有 Massimo Dutti、Geox，以及各家快時尚品牌旗艦店。",
              links=[["Falconeri", "Falconeri Via del Corso Roma"], ["Intimissimi", "Intimissimi Via del Corso Roma"],
                     ["Massimo Dutti", "Massimo Dutti Via del Corso Roma"], ["Geox", "Geox Via del Corso Roma"]]),
         dict(t="Largo Goldoni 路口往東看，是精品街 Via dei Condotti，盡頭就是西班牙階梯；想看一線精品可以繞過去再走回來。",
              links=_L3("Via dei Condotti")),
         dict(t="科隆納廣場（Piazza Colonna）上有馬可・奧里略圓柱，旁邊就是你的飯店，可以先回去放戰利品。",
              links=[["馬可・奧里略圓柱", "Colonna di Marco Aurelio Roma"]])],
  why=["一條直線走到底，不會迷路；沿路串起人民廣場、科隆納廣場、特雷維噴泉、威尼斯廣場。",
       "大眾品牌、百貨精品一次逛完；中途經過飯店，買太多可以先回去放。"],
  plan=["14:00 人民廣場出發，沿 Via del Corso 往南",
        "14:20 Largo Goldoni 路口：想看精品就往東繞 Via dei Condotti 到西班牙階梯",
        "14:30 逛 Corso 兩側的 Falconeri、Intimissimi、Massimo Dutti、Geox 等品牌（約 1.5 小時）",
        "16:00 科隆納廣場看馬可・奧里略圓柱，順路回飯店放東西",
        "16:20 Largo Chigi 轉進 Via del Tritone，逛文藝復興百貨、看地下室水道遺址、頂樓喝咖啡（約 1 小時）",
        "17:30 走 3 分鐘到特雷維噴泉看傍晚打燈",
        "18:00 沿 Via delle Muratte 回到 Corso，往南走到威尼斯廣場看紀念堂夜景"],
  start="從飯店走到人民廣場約 1.2 公里、15～20 分鐘；也可以接在「博爾蓋賽・蘋丘之路」之後直接逛。",
  end="從威尼斯廣場走回飯店約 700 公尺、10 分鐘。",
  tips=["一月初開始冬季折扣季（saldi），約六週；一月底進入深折階段，正是撿便宜的時候。",
        "非歐盟旅客同一天同一家店消費滿 €70.01 可以退稅，記得帶護照；文藝復興百貨可以全館累積、集中辦理。",
        "週末下午 Corso 人潮非常擠，人行道又窄，注意隨身財物、包包背在前面。",
        "多數店家 10:00 開門，週日也大多有營業。"],
))

# ---- Route 4: Bernini trail (user-supplied stop list, 2026-11-11) ----
WAY4 = [(41.9142, 12.4922), (41.9097, 12.4893), (41.9065, 12.4900), (41.9055, 12.4925), (41.9046, 12.4943),   # Borghese -> Porta Pinciana -> Via Veneto -> S. Maria della Vittoria
        (41.9040, 12.4905), (41.9036, 12.4885), (41.9027, 12.4846), (41.9009325, 12.483313),                   # Via Barberini -> Piazza Barberini (Triton) -> Via del Tritone -> Trevi
        (41.8997, 12.4809), (41.8988, 12.4795), (41.8980312, 12.4777993),                                      # Via delle Muratte -> Piazza di Pietra -> Minerva
        (41.8986, 12.4769), (41.8992, 12.4745), (41.8992, 12.4731),                                            # Pantheon -> Piazza Navona
        (41.9004, 12.4702), (41.9007, 12.4675), (41.9014, 12.4664), (41.9031, 12.4663),                        # Via dei Coronari -> Ponte Sant'Angelo -> Castel Sant'Angelo
        (41.9022, 12.4600), (41.9022, 12.4573), (41.9022, 12.4539)]                                            # Via della Conciliazione -> St Peter's Square -> Basilica
ROUTES.append(dict(
  id="bernini-walk", name="City Walk：貝尼尼之路", color="bernini", tag="貝尼尼之路",
  latin="Galleria Borghese · S. Maria della Vittoria · Piazza della Minerva · Piazza Navona · San Pietro",
  stops=["borghese", "vittoria", "minerva", "navona", "sanpietro"],
  avoid=["villaborghese", "pincio", "medici", "spagna", "trevi", "hotel", "colonna", "ignazio", "pantheon", "luigi", "castello", "vaticani"],
  way=WAY4,
  summary="跟著巴洛克雕塑大師貝尼尼（Gian Lorenzo Bernini，1598–1680）走過羅馬：從青年時期登峰造極的大理石雕像，到巴洛克戲劇張力的最高傑作，再到改變羅馬面貌的廣場噴泉，最後走進他後半生擔任教廷總建築師的舞台——聖彼得大教堂。全程約 5 公里，可以分兩天走，或中段搭計程車。",
  stopsText=[["博爾蓋賽美術館", "Ⅰ 青年時期技藝登峰造極的殿堂，集中欣賞他最震撼的早期大理石雕塑：《埃涅阿斯、安喀塞斯與阿斯卡尼俄斯》（1618–1619）、《劫掠普洛塞庇娜》（1621–1622）、《大衛》（1623–1624）、《阿波羅與達芙妮》（1622–1625）。須事先預約。"],
             ["勝利之后聖母堂", "Ⅱ 柯爾納羅小堂（Cornaro Chapel）裡的《聖德蕾莎的狂喜》（1647–1652），巴洛克戲劇張力與宗教神秘主義結合的最高傑作。"],
             ["神廟遺址聖母堂", "Ⅲ 門外的密涅瓦廣場（Piazza della Minerva），萬神殿後方的小廣場上，矗立著貝尼尼設計、象徵堅定智慧的小象馱著古埃及方尖碑：《小象方尖碑》（Pulcino della Minerva，1667）。"],
             ["納沃納廣場", "Ⅳ 羅馬巴洛克公共空間的靈魂：中央的《四河噴泉》（Fontana dei Fiumi，1648–1651），四尊巨像象徵四大洲的四條大河——多瑙河、尼羅河、恆河、拉普拉塔河。"],
             ["聖彼得大教堂", "Ⅴ 貝尼尼後半生擔任教廷總建築師與雕塑家的核心舞台：聖彼得廣場柱廊（1656–1667）、青銅華蓋（聖體傘，1624–1633）、聖伯多祿寶座（Cathedra Petri，1657–1666）、聖朗基努斯像（1629–1638）、亞歷山大七世墓（1671–1678）。"]],
  chainTitle="沿路順看的貝尼尼",
  chain=[dict(t="巴貝里尼廣場的《海神噴泉》（Fontana del Tritone，1642–1643），從勝利之后聖母堂往下走就會經過；廣場角落還有小小的《蜜蜂噴泉》。",
              links=[["海神噴泉", "Fontana del Tritone Roma"], ["蜜蜂噴泉", "Fontana delle Api Roma"]]),
         dict(t="勝利之后聖母堂附近還有貝尼尼自認最滿意的小教堂——奎里納爾聖安德肋堂（Sant'Andrea al Quirinale）；往北 2 分鐘就是他的死對頭波洛米尼的四泉聖嘉祿堂，兩座一起看最過癮。",
              links=[["奎里納爾聖安德肋堂", "Sant'Andrea al Quirinale Roma"], ["四泉聖嘉祿堂", "San Carlo alle Quattro Fontane Roma"]]),
         dict(t="納沃納廣場南端的《摩爾人噴泉》，中央的摩爾人雕像也是貝尼尼設計。",
              links=[["摩爾人噴泉", "Fontana del Moro Roma"]]),
         dict(t="往梵蒂岡途中過聖天使橋，橋上十尊手持耶穌受難刑具的天使像，是貝尼尼設計、由工作室完成的（1669–1671）。",
              links=[["聖天使橋", "Ponte Sant'Angelo Roma"]])],
  why=["一次看懂貝尼尼從青年到晚年的代表作，從美術館、教堂、廣場一路看到聖彼得大教堂。",
       "沿路會經過特雷維噴泉、萬神殿、聖天使城堡，觀光順路。"],
  plan=["09:00 博爾蓋賽美術館（預約時段，參觀 2 小時）",
        "11:15 步行約 20 分鐘到勝利之后聖母堂（12:00 午休前到）",
        "11:45 往下走經過巴貝里尼廣場的海神噴泉，沿 Via del Tritone 到特雷維噴泉一帶吃午餐",
        "14:00 密涅瓦廣場看小象方尖碑（順便進神廟遺址聖母堂、看隔壁萬神殿）",
        "14:45 納沃納廣場看四河噴泉、摩爾人噴泉",
        "15:30 走 Via dei Coronari、過聖天使橋看天使像",
        "16:15 沿協和大道到聖彼得廣場，進聖彼得大教堂看華蓋、寶座、朗基努斯像、亞歷山大七世墓（冬季關門時間請先查官網）"],
  start="從飯店到博爾蓋賽美術館約 2 公里，步行約 30 分鐘，或搭計程車約 10 分鐘。",
  end="從聖彼得大教堂回飯店約 3 公里，可搭計程車或 64 號公車。",
  tips=["博爾蓋賽美術館一定要事先預約，週一休館。",
        "勝利之后聖母堂中午 12:00–16:00 關門，上午要趕在 12:00 前到；趕不上就下午 16:00 後再去。",
        "全程約 5 公里，走不完可以分兩天：第一天博爾蓋賽＋勝利之后聖母堂，第二天密涅瓦廣場 → 納沃納廣場 → 聖彼得大教堂。",
        "聖彼得大教堂入口要安檢排隊，週三上午教宗接見時可能關閉；穿著要遮肩膀和膝蓋。"],
))

# ---- Route 5: Caravaggio trail (stop list from a Xiaohongshu video comment, 2026-11-12) ----
WAY5 = [(41.9113, 12.4762), (41.9107, 12.4762), (41.9075, 12.4757), (41.9040, 12.4752), (41.9020, 12.4745), (41.9008444, 12.4742631),   # S. Maria del Popolo -> Via di Ripetta -> Sant'Agostino
        (41.8996104, 12.4747406), (41.8990, 12.4760), (41.8986, 12.4769), (41.8988, 12.4795), (41.8979782, 12.4815742),   # San Luigi -> Pantheon -> Piazza di S. Ignazio -> Doria Pamphilj
        (41.8997, 12.4809), (41.9009325, 12.483313), (41.9027, 12.4846), (41.9036, 12.4885), (41.903358, 12.489826),       # Corso -> Trevi -> Via del Tritone -> Piazza Barberini -> Palazzo Barberini
        (41.9036, 12.4885), (41.9065, 12.4900), (41.9097, 12.4893), (41.9142103, 12.4921442)]                              # Via Veneto -> Porta Pinciana -> Galleria Borghese
ROUTES.append(dict(
  id="caravaggio-walk", name="City Walk：卡拉瓦喬之路", color="cara", tag="卡拉瓦喬之路",
  latin="S. Maria del Popolo · Sant'Agostino · San Luigi dei Francesi · Galleria Doria Pamphilj · Palazzo Barberini · Galleria Borghese",
  stops=["popolochurch", "agostino", "luigi", "doria", "barberini", "borghese"],
  avoid=[],
  way=WAY5,
  summary="在羅馬追光，尋找卡拉瓦喬（Caravaggio，1571–1610）：一天看遍 6 個地點、近 20 幅真跡。上午先看三座免費教堂（人民聖母教堂、聖奧斯定聖殿、聖王路易堂），再看兩座貴族宮殿美術館，最後在博爾蓋賽美術館收尾。順序由北往南、再往東北繞回，不走回頭路。",
  stopsText=[["人民聖母教堂", "Ⅰ 主祭壇左側的切拉西禮拜堂（Cerasi Chapel）：《聖保羅皈依》《聖彼得受難》，免費。"],
             ["聖奧斯定聖殿", "Ⅱ 進門左手邊第一間禮拜堂：《朝聖者聖母》（洛雷托聖母），朝聖者沾滿泥土的腳底曾引發爭議，免費。"],
             ["聖王路易堂", "Ⅲ 孔塔雷利禮拜堂：《聖馬太蒙召》《聖馬太與天使》《聖馬太殉教》，免費。"],
             ["多利亞潘菲利美術館", "Ⅳ 《逃往埃及途中的休息》《懺悔的抹大拉》《施洗者聖約翰》。週三休館。"],
             ["巴貝里尼宮", "Ⅴ 《朱迪斯斬首赫羅弗尼斯》《那喀索斯》《施洗者聖約翰（荒野）》。週一休館。"],
             ["博爾蓋賽美術館", "Ⅵ 《捧果籃的男孩》、聖母像（《馬夫的聖母》）、《施洗者聖約翰》《書寫的聖哲羅姆》《大衛與歌利亞頭顱》。須事先預約，週一休館。"]],
  chainTitle="還想多看卡拉瓦喬",
  chain=[dict(t="卡比托利歐博物館有《女占卜師》《施洗者聖約翰》。",
              links=[["卡比托利歐博物館", "Musei Capitolini Roma"]]),
         dict(t="梵蒂岡博物館的繪畫館（Pinacoteca）有《基督下葬》，參觀梵蒂岡那天別錯過。",
              links=[["梵蒂岡繪畫館", "Pinacoteca Vaticana"]])],
  why=["卡拉瓦喬在羅馬的代表作一次看齊，從教堂原地到貴族收藏都有。",
       "四個點由西往東北一路串起，中途經過萬神殿、特雷維噴泉。"],
  plan=["08:30 人民聖母教堂看切拉西禮拜堂（12:00 前要看完）",
        "09:00 沿 Via di Ripetta 往南走約 15 分鐘到聖奧斯定聖殿看《朝聖者聖母》",
        "09:40 往南 2 分鐘到聖王路易堂看聖馬太三部曲（09:30 開門）",
        "10:30 步行約 8 分鐘到多利亞潘菲利美術館（週五至週日 10:00 才開）",
        "12:30 特雷維噴泉一帶吃午餐",
        "14:00 巴貝里尼宮（約 1.5 小時）",
        "15:45 沿 Via Veneto 往北走約 20 分鐘到博爾蓋賽美術館",
        "17:00 博爾蓋賽美術館預約時段（2 小時）"],
  start="從飯店走到人民廣場約 1.2 公里、15～20 分鐘。",
  end="從博爾蓋賽美術館回飯店約 2 公里，步行約 30 分鐘或搭計程車。",
  tips=["休館日不同，排日子要小心：多利亞潘菲利週三休，巴貝里尼宮和博爾蓋賽週一休，所以適合週二、週四到週日。",
        "博爾蓋賽美術館一定要事先預約時段。",
        "三座教堂都有午休：人民聖母教堂 12:00、聖奧斯定聖殿 12:30 關門，聖王路易堂約 12:45–14:30 午休、週日上午 11:30 才開，所以教堂都排在上午。",
        "卡拉瓦喬的畫多半很暗，教堂裡的禮拜堂要投幣開燈才看得清楚，準備幾枚 €1 硬幣。"],
))

# ---- Route 6: Michelangelo trail, east to west (user-supplied plan, 2026-11-12) ----
WAY6 = [(41.9032171, 12.4969794), (41.9020, 12.4955), (41.9005, 12.4925), (41.8985, 12.4925), (41.8955, 12.4930), (41.8937984, 12.4931498),   # S. Maria degli Angeli -> Via Nazionale -> Monti -> S. Pietro in Vincoli
        (41.8955, 12.4930), (41.8935, 12.4885), (41.8950, 12.4850), (41.8940, 12.4822), (41.8931725, 12.4827909),                          # Via Cavour -> Via dei Fori Imperiali -> Cordonata -> Campidoglio
        (41.8940, 12.4822), (41.8945, 12.4815), (41.8963, 12.4797), (41.8980312, 12.4777993),                                             # Aracoeli -> Via del Gesù -> Minerva
        (41.8986, 12.4769), (41.9000, 12.4728), (41.9005, 12.4702), (41.9007, 12.4675), (41.9014, 12.4664), (41.9031, 12.4663),             # Pantheon -> Navona (north) -> Via dei Coronari -> Ponte Sant'Angelo
        (41.9022, 12.4600), (41.9022, 12.4573), (41.9021667, 12.4539367)]                                                                  # Via della Conciliazione -> St Peter's
ROUTES.append(dict(
  id="michel-walk", name="City Walk：米開朗基羅之路", color="michel", tag="米開朗基羅之路",
  latin="S. Maria degli Angeli · S. Pietro in Vincoli · Campidoglio · S. Maria sopra Minerva · San Pietro",
  stops=["angeli", "vincoli", "campidoglio", "minerva", "sanpietro"],
  avoid=["termini", "monti", "colosseo", "foro", "venezia", "pantheon", "ignazio", "navona", "luigi", "castello", "vaticani", "doria", "hotel"],
  way=WAY6,
  summary="由東向西筆直橫貫羅馬市中心的米開朗基羅主題散步。前段是免排隊的市區街景與教堂，最後跨過台伯河走進梵蒂岡。只想輕鬆散步的話，可以在第 4 站神廟遺址聖母堂（萬神殿旁）直接結束喝咖啡；體力充沛、想看大師頂級巨作，再沿聖天使橋走進梵蒂岡。",
  stopsText=[["天使與殉教者聖母大殿", "Ⅰ 共和廣場：米開朗基羅 86 歲接下的晚期建築，把古羅馬戴克里先浴場改建成教堂，保留八根花崗岩巨柱和十字拱頂；地上有 18 世紀的黃銅子午線日晷。"],
             ["聖伯多祿鎖鏈堂", "Ⅱ 蒙蒂區山丘：儒略二世陵墓的核心雕像《摩西像》，大理石長鬚的垂墜感、繃緊的手臂青筋和威嚴憤怒的神韻極具張力。免費，中午 12:20–15:00 午休。"],
             ["卡比托利歐山", "Ⅲ 古羅馬中心：米開朗基羅的都市規劃經典，Cordonata 緩坡石階、十二角星芒地坪的梯形廣場；元老宮後方有免費懸崖觀景台俯瞰古羅馬廣場。"],
             ["神廟遺址聖母堂", "Ⅳ 萬神殿旁：主祭壇左側是米開朗基羅 1521 年完成的《背負十字架的基督》，門外還有貝尼尼的小象方尖碑。——市區漫步分水嶺，不去梵蒂岡的話在這裡結束喝咖啡。"],
             ["聖彼得大教堂", "Ⅴ【自由選配尾站】往西穿過納沃納廣場北側、過聖天使橋，沿協和大道約 20 分鐘到聖彼得廣場。右側第一小堂的《聖殤》是大師 24 歲的成名作，也是他唯一親筆簽名的雕塑；中央的雙層大圓頂是他生前最後的建築設計。"]],
  why=["一條直線由東往西走，不走回頭路；從大師晚年的建築一路看到青年成名作。",
       "前四站都免費、免排隊；最後一站可以自由決定要不要去。"],
  plan=["08:30 天使與殉教者聖母大殿（共和廣場）",
        "09:15 沿 Via Nazionale 往下走約 15 分鐘到聖伯多祿鎖鏈堂看《摩西像》（12:20 午休前到）",
        "10:15 沿 Via Cavour、帝國議事廣場大道走到卡比托利歐山，上懸崖觀景台看古羅馬廣場",
        "11:15 往北走約 10 分鐘到神廟遺址聖母堂看《背負十字架的基督》，順看萬神殿",
        "12:00 午餐、喝咖啡（不去梵蒂岡就在這裡結束）",
        "13:30 經納沃納廣場北側、科羅納里街，過聖天使橋",
        "14:15 聖彼得大教堂看《聖殤》與大圓頂（冬季關門時間請先查官網）"],
  start="天使與殉教者聖母大殿離特米尼車站步行約 5 分鐘，從飯店走過去約 1.5 公里、20 分鐘，或搭地鐵 A 線到 Repubblica 站。",
  end="在萬神殿旁結束的話，走回飯店只要 5 分鐘；從聖彼得大教堂回飯店約 3 公里，可搭計程車或 64 號公車。",
  tips=["全程約 5 公里，在第 4 站結束的話約 3 公里。",
        "聖伯多祿鎖鏈堂中午 12:20–15:00 關門，要排在上午或 15:30 之後。",
        "週末的神廟遺址聖母堂 13:00–14:00 午休。",
        "聖彼得大教堂入口要安檢排隊，週三上午教宗接見時可能關閉；所有教堂都要遮住肩膀和膝蓋。"],
))

# distance pill: midpoint of the path by length, nudged off the line
def _label(pts, text, stops, wide=False, avoid=(), pills=True):
    # try segment midpoints on both sides; keep clear of the route stops' labels and pins
    import json
    spots = {s["id"]: s for s in json.load(open("/home/claude/rome/data.json"))["spots"]}
    _bx = lambda z: (z.get("ux", z["lx"]), z.get("uy", z["ly"]))   # City Walk mode shows the full layout (ux/uy)
    boxes = [(_bx(spots[i])[0], _bx(spots[i])[1], _bx(spots[i])[0] + spots[i]["W"], _bx(spots[i])[1] + spots[i]["H"]) for i in list(stops) + [a for a in avoid if a in spots]]
    pins = [(spots[i]["x"], spots[i]["y"]) for i in list(stops) + [a for a in avoid if a in spots]]
    W, H = sum(24 if ord(c) > 0x2e80 else 13 for c in text) + 36 + 40, 44   # 24px bold pill text + padding + hand icon
    if pills: boxes += _PILLS   # other routes' distance pills
    best = None
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; L = math.dist(a, b)
        if L < 40: continue
        for t in ((0.5, 0.35, 0.65, 0.2, 0.8) + ((0.1, 0.3, 0.45, 0.55, 0.7, 0.9) if wide else ())):
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
            for side in ((1, -1, 1.8, -1.8, 2.6, -2.6, 3.4, -3.4) + ((4.2, -4.2, 5, -5, 6, -6, 7, -7) if wide else ())):
                cx, cy = x + nx * 46 * side, y + ny * 46 * side
                box = (cx - W / 2, cy - H / 2, cx + W / 2, cy + H / 2)
                if any(not (box[2] + 12 <= q[0] or q[2] + 12 <= box[0] or box[3] + 12 <= q[1] or q[3] + 12 <= box[1]) for q in boxes): continue
                if any(box[0] - 20 < p[0] < box[2] + 20 and box[1] - 20 < p[1] < box[3] + 20 for p in pins): continue
                score = abs(t - 0.5) + abs(side) * 0.2
                if best is None or score < best[0]: best = (score, cx, cy)
    if best is None and not wide: return _label(pts, text, stops, True, avoid)
    if best is None and pills: return _label(pts, text, stops, True, avoid, False)   # then allow touching another pill
    if best is None and avoid: return _label(pts, text, stops, True, (), False)       # last resort: only keep clear of this route's own stops
    _PILLS.append((best[1] - W / 2, best[2] - H / 2, best[1] + W / 2, best[2] + H / 2))
    return dict(x=round(best[1], 1), y=round(best[2], 1), text=text)
_PILLS = []
_ALLSTOPS = [i for r in ROUTES for i in r["stops"] + r.get("areas", [])]
for r in ROUTES:
    _p, _km, _mins = geom(r.pop("way")) if "way" in r else (r["pts"], km, mins)
    r["pts"] = _p
    # in City Walk mode every route's stops are labelled, so keep each pill clear of all of them
    r["label"] = _label(r["pts"], (f"【{r['tag']}】" if r.get("tag") else "") + f"{_km} km・步行約 {_mins} 分", r["stops"] + r.get("areas", []), avoid=(r.pop("avoid", ()), _ALLSTOPS)[1])   # in City Walk mode only route stops are shown, so only those matter
