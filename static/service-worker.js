const CACHE_NAME = "unit-converter-v2";
const urlsToCache = [
	"/",
	"/static/css/output.css",
	"/static/favicon.ico",
	"https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Lexend:wght@400;600;700&display=swap",
	"https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js",
	"https://cdn.jsdelivr.net/npm/chart.js",
];

// Install service worker
self.addEventListener("install", (event) => {
	event.waitUntil(
		caches.open(CACHE_NAME).then((cache) => {
			console.log("Opened cache");
			return cache.addAll(urlsToCache);
		})
	);
});

// Fetch events - handle only GET, cache same-origin API GETs
self.addEventListener("fetch", (event) => {
	const req = event.request;

	// Only handle GET requests
	if (req.method !== "GET") {
		return;
	}

	event.respondWith(
		caches.match(req).then((response) => {
			if (response) {
				return response;
			}

			const fetchRequest = req.clone();

			return fetch(fetchRequest)
				.then((networkResponse) => {
					// Check if valid response
					if (
						!networkResponse ||
						networkResponse.status !== 200 ||
						networkResponse.type !== "basic"
					) {
						return networkResponse;
					}

					// Cache same-origin GET API responses
					try {
						const url = new URL(fetchRequest.url);
						const sameOrigin = url.origin === self.location.origin;
						if (sameOrigin && url.pathname.startsWith("/api/")) {
							const responseToCache = networkResponse.clone();
							caches.open(CACHE_NAME).then((cache) => {
								cache.put(fetchRequest, responseToCache);
							});
						}
					} catch (e) {}

					return networkResponse;
				})
				.catch(() => {
					// Fallback to app shell for navigation
					if (req.mode === "navigate") {
						return caches.match("/");
					}
					return caches.match(req);
				});
		})
	);
});

// Activate service worker
self.addEventListener("activate", (event) => {
	const cacheWhitelist = [CACHE_NAME];

	event.waitUntil(
		caches.keys().then((cacheNames) => {
			return Promise.all(
				cacheNames.map((cacheName) => {
					if (cacheWhitelist.indexOf(cacheName) === -1) {
						return caches.delete(cacheName);
					}
				})
			);
		})
	);
});
