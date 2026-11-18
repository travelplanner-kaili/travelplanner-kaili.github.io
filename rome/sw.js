/* 羅馬地圖 offline helper
   - the map page: try the network first (so updates show up), fall back to the saved copy when offline
   - map tiles and fonts: keep what has been viewed, reuse it offline (no bulk pre-download)
   - walking routes: network only (the map falls back to straight-line estimates) */
const VERSION = "rome-v1";
const PAGE = VERSION + "-page", TILES = "rome-tiles", FONTS = "rome-fonts";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png"];
const MAX_TILES = 4000;

self.addEventListener("install", e => { e.waitUntil(caches.open(PAGE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith("rome-") && k.endsWith("-page") && k !== PAGE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

async function trimTiles() {
  const c = await caches.open(TILES), keys = await c.keys();
  for (let i = 0; i < keys.length - MAX_TILES; i++) await c.delete(keys[i]);
}

self.addEventListener("fetch", e => {
  const req = e.request; if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    // own files: always ask the server for the newest copy (no-cache), saved copy when offline
    e.respondWith(fetch(req, { cache: "no-cache" }).then(res => { if (res.ok) { const cp = res.clone(); caches.open(PAGE).then(c => c.put(req, cp)); } return res; })
      .catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match("./index.html"))));
    return;
  }
  const isTile = /tile\.openstreetmap\.org|arcgisonline\.com/.test(url.host);
  const isFont = /fonts\.(googleapis|gstatic)\.com/.test(url.host);
  if (isTile || isFont) {
    const name = isTile ? TILES : FONTS;
    e.respondWith(caches.open(name).then(c => c.match(req).then(hit => {
      const net = fetch(req).then(res => { if (res && (res.ok || res.type === "opaque")) { c.put(req, res.clone()); if (isTile) trimTiles(); } return res; }).catch(() => hit);
      return hit || net;
    })));
  }
  // everything else (walking routes, Google links): straight to the network
});
