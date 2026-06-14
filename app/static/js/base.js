// ==================== BASE JAVASCRIPT ====================
// Language switching with session and localStorage
function changeLanguage(lang) {
    localStorage.setItem('preferred_language', lang);

    fetch(`/change-language/${lang}?next=${window.location.pathname}`)
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                window.location.reload();
            }
        })
        .catch(() => {
            window.location.href = `/change-language/${lang}?next=${window.location.pathname}`;
        });
}

// Add event listeners to language links
document.querySelectorAll('.language-link').forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault();
        changeLanguage(this.getAttribute('data-lang'));
    });
});

// Load saved language from localStorage
document.addEventListener('DOMContentLoaded', function () {
    const savedLang = localStorage.getItem('preferred_language');
    const currentLang = document.querySelector('html').getAttribute('lang') || 'en';

    if (savedLang && savedLang !== currentLang) {
        changeLanguage(savedLang);
    }
});

// Online/Offline detection
function updateOfflineStatus() {
    const badge = document.getElementById('offlineBadge');
    if (badge) {
        badge.style.display = navigator.onLine ? 'none' : 'inline-block';
    }
}

window.addEventListener('online', updateOfflineStatus);
window.addEventListener('offline', updateOfflineStatus);
document.addEventListener('DOMContentLoaded', updateOfflineStatus);

// Utility Functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed bottom-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function showLoading(message = 'Processing...') {
    let overlay = document.querySelector('.loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `<div class="loading-spinner"><div class="spinner-border text-primary"></div><div class="mt-2">${message}</div></div>`;
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('.mt-2').innerText = message;
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

console.log('🌽 Maize Disease Detection System base.js loaded');