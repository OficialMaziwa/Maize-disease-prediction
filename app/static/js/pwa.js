// PWA (Progressive Web App) Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(function (registration) {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(function (err) {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// Handle online/offline status
window.addEventListener('online', function () {
    const offlineBadge = document.getElementById('offlineBadge');
    if (offlineBadge) {
        offlineBadge.style.display = 'none';
    }
    if (typeof showToast === 'function') {
        showToast('You are back online!', 'success');
    }
});

window.addEventListener('offline', function () {
    const offlineBadge = document.getElementById('offlineBadge');
    if (offlineBadge) {
        offlineBadge.style.display = 'inline-block';
    }
    if (typeof showToast === 'function') {
        showToast('You are offline. Some features may be limited.', 'warning');
    }
});

// Check if online initially
if (!navigator.onLine) {
    const offlineBadge = document.getElementById('offlineBadge');
    if (offlineBadge) {
        offlineBadge.style.display = 'inline-block';
    }
}