// TailorPro service worker: lets the app open with no internet.
// Bump CACHE_VERSION whenever you publish a new version of the app.
const CACHE_VERSION = "nyuzihouse-v8";

const CORE_FILES = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(CORE_FILES))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function fetchWithTimeout(request, ms) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("timeout")), ms);
    fetch(request).then(
      response => { clearTimeout(timer); resolve(response); },
      error => { clearTimeout(timer); reject(error); }
    );
  });
}

self.addEventListener("fetch", event => {
  const request = event.request;

  if (request.method !== "GET") return;

  const url = new URL(request.url);

  // The app page: use the internet when it's good (so updates arrive),
  // fall back to the saved copy when it's slow or offline.
  if (request.mode === "navigate") {
    event.respondWith(
      fetchWithTimeout(request, 15000)
        .then(response => {
          const copy = response.clone();
          caches.open(CACHE_VERSION).then(cache => cache.put("./index.html", copy));
          return response;
        })
        .catch(() => caches.match("./index.html").then(saved => saved || fetch(request)))
    );
    return;
  }

  // Icons, manifest and the splash font: saved copy first, refreshed in the background.
  const isOurs = url.origin === self.location.origin;
  const isFont = url.hostname.endsWith("googleapis.com") || url.hostname.endsWith("gstatic.com");

  if (isOurs || isFont) {
    event.respondWith(
      caches.match(request).then(saved => {
        const refresh = fetch(request)
          .then(response => {
            if (response && (response.ok || response.type === "opaque")) {
              const copy = response.clone();
              caches.open(CACHE_VERSION).then(cache => cache.put(request, copy));
            }
            return response;
          })
          .catch(() => saved);
        return saved || refresh;
      })
    );
  }
});
