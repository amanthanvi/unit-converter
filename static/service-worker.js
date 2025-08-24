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
		caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
	);
});

// Fetch events: do NOT cache dynamic API responses
self.addEventListener("fetch", (event) => {
	const url = event.request.url;
	if (url.includes("/api/")) {
		// Always network for API (including /api/v1); no caching
		event.respondWith(fetch(event.request));
		return;
	}

	event.respondWith(
		caches.match(event.request).then((response) => {
			return response || fetch(event.request);
		})
	);
});

// Activate service worker
self.addEventListener("activate", (event) => {
	const cacheWhitelist = [CACHE_NAME];
	event.waitUntil(
		caches.keys().then((names) =>
			Promise.all(
				names.map((name) => {
					if (!cacheWhitelist.includes(name)) {
						return caches.delete(name);
					}
				})
			)
		)
	);
});
