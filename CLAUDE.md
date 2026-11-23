# 義大利旅遊地圖 — 給下一個 Claude 的交接

使用者（travelplanner-kaili）用繁體中文溝通，自稱「電腦白痴」：技術步驟要一步一步、用白話講，不要丟指令給她跑。
她做 2027 義大利自助旅行的互動景點地圖，會公開分享連結（Threads）。出發前持續更新，2027 年 2 月後停止。

- 行程：羅馬 1/26–2/3（Hotel Nazionale Roma）→ 盧卡 2/3–2/5（Hotel Ilaria）→ 威尼斯 2/5–2/8。
- 網站：https://travelplanner-kaili.github.io/ （本 repo，GitHub Pages，main 分支一推就上線，約 1 分鐘）
  - `lucca/`、`rome/`：已上線的真地圖版（Leaflet 真街道底圖 + 全部功能）。
  - `index.html`：地圖目錄頁。威尼斯還沒做真地圖版（目錄上是「準備中」）。
- claude.ai Project「旅遊地圖」放了同樣的成品和規格書：`claude/盧卡真地圖版.html`、`claude/羅馬真地圖版.html`、
  `claude/旅遊地圖製作規格.md`（＝ `_src/spec.md`），還有舊的手繪版。

## 為什麼這樣做 → 看 git log 和規格書
- `git log` 每個 commit 都寫了原因（使用者決定了什麼、為什麼）。改東西前先 `git log -p -- <檔案>` 看來龍去脈。
- `_src/spec.md` 是規則書：每條規則都標日期，很多是使用者逐字定稿的文字（Q&A、導覽文字），不要自己改寫。
- 新規則：寫進 `_src/spec.md`，同步上傳 Project 的 `claude/旅遊地圖製作規格.md`（先 project_read 再 project_write）。

## 原始碼（`_src/`，網站不會公開它）
- 開工：把 repo clone 到 `/home/claude/travelplanner-kaili.github.io`，跑 `_src/setup.sh`
  （腳本用 `/home/claude/lucca`、`/home/claude/rome` 這種絕對路徑，setup 會建好連結、npm install）。
- `_src/lucca/real/engine.js`：所有城市共用的真地圖引擎；城市差異只放在 CITY 設定
  （盧卡：`city_lucca.js`；羅馬：`build_rome.py` 裡的 CITY）。
- `_src/lucca/real/build_real.py`：手繪盧卡頁 `_src/lucca/live/lucca.html` → `lucca-real.html`。
- `_src/rome/real/build_rome.py`：以剛建好的盧卡真地圖當模板，換成羅馬資料 + `rome_extra.js`（City Walk、購物、搶票）。
- 手繪版產生器：`_src/rome/gen.py`→`data.json`、`build.py`→`羅馬地圖.html`；盧卡 `luc.py`/`patch.py`；威尼斯只有成品 html。
- 測試：`_src/*/real/tests/*.js`（Playwright，`node 檔名`）。容器連不到圖磚和步行路線服務，畫面上底圖會是空白，屬正常。

## 每次改完的固定流程（使用者習慣）
1. 改 `_src/`，跑 build，用 Playwright 在電腦（1280）和手機（390）寬度都測，截圖自己看。
2. `_src/deploy.sh rome|lucca|all` 複製成品 → `git commit`（訊息寫原因）→ `git -c push.negotiate=true push origin main`，用 `gh run watch` 等上線。
3. 上傳 Project：`claude/羅馬真地圖版.html` / `claude/盧卡真地圖版.html`（成品）、`claude/旅遊地圖製作規格.md`（規格）。
4. 如果連得到她的電腦（remote-devices 工具），把成品存到桌面 `C:\Users\alily\OneDrive\桌面\盧卡真地圖版.html` / `羅馬真地圖版.html`，用 md5 核對。
5. 回報：做了什麼、哪裡要她自己看。網站更新要 1～2 分鐘，叫她看地圖下方「最新更新」時間。

## 目前狀態（2026-11-20 交接時）
- 羅馬：已上線最新版（13:05）。最後三個改動在等她確認：
  1. 眼睛三種模式：自動／全覽／簡潔（按鈕右下角小標「自」「全」「簡」）。
  2. 自動模式框依縮放變大小、推薦框小一號、太擠的只顯示名字。
  3. 全覽／簡潔改回手繪地圖的排法（框在手繪位置、跟地圖等比例縮放），並畫出台伯河。
- 羅馬 2026-11-20 下午：照她的 12 點回饋改完上線（規格書最後一節「2026-11-20 使用者回饋」）。她說：先只做羅馬和規格書，羅馬改完再做盧卡、威尼斯。
  shared 的 engine.js / build_real.py 已含這些改動；盧卡套用時要一起帶上（City Walk 加入行程、購物街粉紅色是羅馬專屬，盧卡沒有）。
- 盧卡：網站上還是 2026-11-18 的版本。`engine.js` 已含上面的改動，但盧卡要等她確認羅馬後才套用：
  - 盧卡的全覽／簡潔要用手繪盧卡的框位置（`live/lucca.html` 的 SPOTS 有 x,y,lx,ly 等，`coords.json` 有座標轉換）→ 做成 `s.lab` 和 `CITY.unitM`，跟 `build_rome.py` 一樣。
  - 盧卡沒有河；城牆照舊。
  - 套用後重測、部署、更新 Project 檔和桌面檔。
- 威尼斯：還沒做真地圖版。做法同羅馬：寫 `_src/venice/real/build_venice.py`，以盧卡真地圖為模板。
  她在威尼斯靠運河認路，運河要一直清楚（手機深色模式也要）；街名一律附當地原文。
- 她請我們記得：真地圖上線後提醒她檢查匯入時的「你的地圖更新時間」提示，再決定留不留。

## 羅馬藝術觀脈絡頁（2026-11-22 上線：`rome-art/`）
- 內容就是 `rome-art/rome_art.md`：網頁打開時直接讀這份檔案（讀不到才用內嵌的備份）。她會自己在 GitHub 網頁上改這份檔案，不經過 Claude。
  所以改內容一律改 `rome-art/rome_art.md`；之後若改版面，先把網站上最新的 rome_art.md 複製回 `_src/rome-art/`，再跑 `_src/rome-art/build.py`（會覆寫 rome-art/ 裡兩個檔）。
- 檔案格式：`## 段落標題 @時代色`（@pre＝脈絡圖最上面的 Q0 問答、@intro＝問答頁前言）、`### Q5-3-1 | 題目`（編號決定縮排）、`> 簡答`（可多行）、`#### 小標`、`- ` 條列、`1. ` 編號、`* ` 縮排小項、`:: ` 灰框、`|` 表格、一行 `=== 深究` 之後收進可展開的「深究」。
- 寫法（2026-11-23 她定）：簡答＝一句小結論；詳答＝條列；深究才寫敘述。遊客耐心有限，不要贅詞和形容。
- 版面與脈絡圖表格的文字在 `_src/rome-art/content.js`（ERAS）、`template.html`、`app.js`。她的內容多半是自己貼上逐字稿，照貼；有史實疑慮在回覆裡講，不在網頁上標。
- 她不喜歡硬套的比喻；問答要一題接一題往下推，不要突然冒出新概念。

## 她明確不要的東西（別再提）
點底圖上的 POI、行程時間自動檢查、廁所／超市、日落時間、預約待辦（用備註）、換底圖來源、立體剪紙地標（真地圖不放）。
