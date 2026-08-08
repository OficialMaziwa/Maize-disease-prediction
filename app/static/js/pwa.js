
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

if (!navigator.onLine) {
    const offlineBadge = document.getElementById('offlineBadge');
    if (offlineBadge) {
        offlineBadge.style.display = 'inline-block';
    }
}