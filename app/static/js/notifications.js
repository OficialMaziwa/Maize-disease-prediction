
let notificationsList = [];
let currentPage = 1;
let totalNotifications = 0;

document.addEventListener('DOMContentLoaded', function () {
    loadNotifications();
    loadUnreadCount();
});

async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications?limit=50');
        const data = await response.json();

        console.log('Notifications response:', data);

        if (data.success) {
            notificationsList = Array.isArray(data.notifications) ? data.notifications : [];
            totalNotifications = notificationsList.length;

            displayNotifications(notificationsList);
            updateNotificationBadge(data.unread_count || 0);
        } else {
            console.error('Failed to load notifications:', data.error);
            displayNotifications([]);
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        displayNotifications([]);
    }
}

async function loadUnreadCount() {
    try {
        const response = await fetch('/api/notifications/unread-count');
        const data = await response.json();

        if (data.success) {
            updateNotificationBadge(data.unread_count || 0);
        }
    } catch (error) {
        console.error('Error loading unread count:', error);
    }
}

function displayNotifications(notifications) {
    const container = document.getElementById('notificationList');
    if (!container) return;

    if (!notifications || notifications.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-bell-slash fa-2x mb-2 d-block"></i>
                <p>No notifications yet</p>
            </div>
        `;
        return;
    }

    let html = '';
    notifications.forEach(notification => {
        const isRead = notification.is_read ? 'read' : 'unread';
        const icon = getNotificationIcon(notification.notification_type);

        html += `
            <div class="notification-item ${isRead}" data-id="${notification.id}">
                <div class="notification-icon">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-title">${escapeHtml(notification.title || 'Notification')}</div>
                    <div class="notification-message">${escapeHtml(notification.message || '').substring(0, 100)}</div>
                    <div class="notification-time">${notification.created_at || 'Just now'}</div>
                </div>
                ${!notification.is_read ? '<div class="notification-badge"></div>' : ''}
            </div>
        `;
    });

    container.innerHTML = html;

    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', () => {
            const id = item.dataset.id;
            if (id) {
                markAsRead(id);
            }
        });
    });
}

function getNotificationIcon(type) {
    switch (type) {
        case 'ACCOUNT_APPROVAL':
            return 'fa-check-circle';
        case 'PREDICTION_RESULT':
            return 'fa-microscope';
        case 'SYSTEM_ALERT':
            return 'fa-exclamation-triangle';
        default:
            return 'fa-bell';
    }
}

async function markAsRead(notificationId) {
    try {
        const response = await fetch(`/api/notifications/${notificationId}/read`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            loadNotifications();
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

async function markAllAsRead() {
    try {
        const response = await fetch('/api/notifications/mark-all-read', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            loadNotifications();
        }
    } catch (error) {
        console.error('Error marking all as read:', error);
        showToast('Failed to mark all as read', 'danger');
    }
}

function updateNotificationBadge(count) {
    const badge = document.getElementById('notificationBadge');
    const dropdown = document.getElementById('notificationDropdown');

    if (badge) {
        if (count > 0) {
            badge.style.display = 'inline-block';
            badge.textContent = count > 99 ? '99+' : count;
        } else {
            badge.style.display = 'none';
        }
    }

    if (dropdown) {
        const header = dropdown.querySelector('.dropdown-header');
        if (header) {
            header.innerHTML = `
                <i class="fas fa-bell me-2"></i>
                Notifications ${count > 0 ? `<span class="badge bg-danger ms-2">${count}</span>` : ''}
                <button class="btn btn-sm btn-link float-end" onclick="markAllAsRead()">
                    <i class="fas fa-check-double"></i> Mark all read
                </button>
            `;
        }
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '250px';
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

setInterval(() => {
    if (document.querySelector('.notification-dropdown')?.classList.contains('show')) {
        loadNotifications();
    }
    loadUnreadCount();
}, 30000);

window.markAllAsRead = markAllAsRead;