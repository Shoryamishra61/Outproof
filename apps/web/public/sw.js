// Cache the setup shell only. This does not provide offline outing compilation.
const cacheName = 'ground-rule-setup-v1';
self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(cacheName).then((cache) => cache.addAll(['/', '/icon.svg', '/manifest.webmanifest'])));
});
self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key.startsWith('ground-rule-setup-') && key !== cacheName).map((key) => caches.delete(key)))));
});
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin || new URL(event.request.url).pathname.startsWith('/v1/')) return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request).then((cached) => cached || Response.error())));
});
