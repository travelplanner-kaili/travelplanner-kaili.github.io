# 宣傳短片（2026-11-27 第一支：羅馬地圖介紹片，30 秒直式 1080×1920）
- rec.js：用 Playwright 開羅馬真地圖（手機 432×768 ×2.5），真的操作並逐格截圖。頁面動畫放慢 SLOW 倍（CSS 用 Animation.setPlaybackRate、地圖移動用自己的 H.fly），時間再除回來，所以畫面順。
  `SLOW=6 NODE_PATH=/opt/npm-tools/node_modules node rec.js full/f ./seq_full.js`（在 /home/claude/video 跑）
- 底圖：容器連不到 OSM 圖磚。做法是用她電腦 Claude App 的內建瀏覽器（在她網站頁面上 fetch tile.openstreetmap.org）抓圖塊、打包成 rome_tiles.json 下載，她拖到桌面後 stage 進來，解到 /home/claude/video/tiles/z/x/y.png（其實是 jpeg）。rec.js 用 page.route 從這裡供應；缺的圖塊列在 need.json。片尾要寫「地圖資料 © OpenStreetMap 貢獻者」。
- 頁面用 http://rome.test/ 假網址開（route 回應本機檔案），這樣引擎走 OSM 圖層，不是 file:// 的 Esri。
- seq_full.js：腳本（開場 → 點特雷維噴泉 → 實用資訊 → City Walk 貝尼尼之路 → 加 3 個景點進 1/26 → 打開我的行程）。H.mark() 記時間點給字幕對齊。
- make.py：字幕卡（Noto Sans CJK TC Black，橘框白底）和逐格 → 30fps 影片；final.py：五段字幕 + 片尾卡（網址、免費使用），concat 輸出。
- 她的意見：要有地圖底圖（淡淡的，底圖濃淡「淡一點」lv1）。配樂她發文時用 IG／臉書內建音樂庫加。
