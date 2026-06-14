// Service Worker for Maize Disease Detection System
const CACHE_NAME = 'maize-detection-v1';
const STATIC_CACHE = 'maize-static-v1';
const DYNAMIC_CACHE = 'maize-dynamic-v1';

// Files to cache on install
const urlsToCache = [
    '/',
    '/static/css/base.css',
    '/static/js/base.js',
    '/static/js/notifications.js',
    '/offline'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static assets');
                return cache.addAll(urlsToCache);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache then network
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached response if found
                if (response) {
                    return response;
                }
                // Otherwise fetch from network
                return fetch(event.request)
                    .then(fetchResponse => {
                        // Don't cache non-GET requests or external URLs
                        if (event.request.method !== 'GET' || !event.request.url.startsWith(self.location.origin)) {
                            return fetchResponse;
                        }
                        // Cache the fetched response
                        return caches.open(DYNAMIC_CACHE)
                            .then(cache => {
                                cache.put(event.request, fetchResponse.clone());
                                return fetchResponse;
                            });
                    })
                    .catch(() => {
                        // If offline and fetch fails, return offline page
                        if (event.request.mode === 'navigate') {
                            return caches.match('/offline');
                        }
                    });
            })
    );
});