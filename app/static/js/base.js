
function changeLanguage(lang) {
    const returnPath = window.location.pathname + window.location.search;
    window.location.href = `/change-language/${lang}?next=${encodeURIComponent(returnPath)}`;
}


document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.language-link').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const lang = this.getAttribute('data-lang');
            if (lang) {
                changeLanguage(lang);
            }
        });
    });

    const languageSelector = document.getElementById('languageSelector');
    if (languageSelector) {
        languageSelector.addEventListener('change', function () {
            changeLanguage(this.value);
        });
    }

    updateOfflineStatus();
});


function updateOfflineStatus() {
    const badge = document.getElementById('offlineBadge');
    if (badge) {
        badge.style.display = navigator.onLine ? 'none' : 'inline-block';
    }
}

window.addEventListener('online', updateOfflineStatus);
window.addEventListener('offline', updateOfflineStatus);


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
    document.querySelectorAll('.toast-notification').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${escapeHtml(message)}</span>
        <i class="fas fa-times close-toast" onclick="this.parentElement.remove()"></i>
    `;
    
    Object.assign(toast.style, {
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        zIndex: '9999',
        minWidth: '280px',
        maxWidth: '400px',
        background: 'white',
        borderRadius: '10px',
        padding: '15px 20px',
        boxShadow: '0 5px 20px rgba(0,0,0,0.15)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        borderLeft: `4px solid ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#17a2b8'}`,
        animation: 'slideInRight 0.3s ease'
    });

    document.body.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) toast.remove();
            }, 300);
        }
    }, 4000);
}

function showLoading(message = 'Processing...') {
    let overlay = document.querySelector('.loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 99999;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        `;
        overlay.innerHTML = `
            <div class="loading-spinner" style="text-align: center;">
                <div class="spinner-border text-success" style="width: 3rem; height: 3rem;" role="status"></div>
                <div class="mt-2 text-white">${escapeHtml(message)}</div>
            </div>
        `;
        document.body.appendChild(overlay);
    } else {
        const msgEl = overlay.querySelector('.mt-2');
        if (msgEl) msgEl.innerText = message;
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) overlay.style.display = 'none';
}



const baseStyleSheet = document.createElement('style');
baseStyleSheet.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    .toast-notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 280px;
        max-width: 400px;
        background: white;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideInRight 0.3s ease;
    }
    .toast-notification .close-toast {
        cursor: pointer;
        margin-left: auto;
        color: #999;
    }
    .toast-notification .close-toast:hover {
        color: #333;
    }
    .toast-notification.success { border-left: 4px solid #28a745; }
    .toast-notification.error { border-left: 4px solid #dc3545; }
    .toast-notification.warning { border-left: 4px solid #ffc107; }
    .toast-notification.info { border-left: 4px solid #17a2b8; }
    .toast-notification i:first-child {
        font-size: 20px;
    }
    .toast-notification.success i:first-child { color: #28a745; }
    .toast-notification.error i:first-child { color: #dc3545; }
    .toast-notification.warning i:first-child { color: #ffc107; }
    .toast-notification.info i:first-child { color: #17a2b8; }
`;
document.head.appendChild(baseStyleSheet);

console.log('🌽 Maize Disease Detection System base.js loaded');