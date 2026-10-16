const CACHE = 'tagesdoku-v79';
const SHELL = [
  './', './index.html', './manifest.webmanifest',
  './Tagesdokumentation_Ueberstunden_Rufdienst_ausfuellbar.pdf',
  './icon-192.png', './icon-512.png', './qrcode.js', './jsQR.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js'
];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c =>
    Promise.all(SHELL.map(u => c.add(new Request(u, {cache: 'reload'})).catch(() => null)))   // nicht die bis 10 min alte HTTP-Cache-Kopie
  ).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks =>
    Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  if (new URL(e.request.url).hostname === 'api.github.com') return;   // Online-Backup nie aus dem Cache
  const isPage = e.request.mode === 'navigate' || e.request.url.endsWith('/index.html') || e.request.url.endsWith('/app/');
  if (isPage) {
    /* Cache-first: Start sofort, auch offline. Frisch aus dem Netz nur, wenn die
       Seite es ausdruecklich verlangt (Update-Pruefung: cache 'reload'/'no-store')
       oder noch nichts im Cache liegt. Neue Versionen bringt sonst der neue SW
       (install laedt die Shell frisch). */
    const netz = () => fetch(e.request.url, {cache: 'no-cache', credentials: 'same-origin'}).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put('./index.html', copy)).catch(() => {}); }
      return res;
    });
    const frisch = e.request.cache === 'reload' || e.request.cache === 'no-store';
    e.respondWith(frisch
      ? netz().catch(() => caches.match('./index.html'))
      : caches.match('./index.html').then(hit => hit || netz()));
    return;
  }
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
      return res;
    }).catch(() => hit))
  );
});
