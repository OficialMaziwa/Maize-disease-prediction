
const userId = window.location.pathname.split('/').pop();
let currentUserData = null;

function loadUserData() {
    fetch(`/admin/user/${userId}`)
        .then(response => response.json())
        .then(user => {
            if (user.error) {
                document.querySelector('.profile-info-card').innerHTML = `
                    <div class="alert alert-danger text-center">
                        <i class="fas fa-exclamation-triangle me-2"></i> ${user.error}
                    </div>`;
                return;
            }

            currentUserData = user;
            renderUserInfo(user);
            loadUserStatistics(user.user_id);
            loadUserActivity(user.user_id);
            loadNotificationCount(user.user_id);
        })
        .catch(error => {
            console.error('Error:', error);
            document.querySelector('.profile-info-card').innerHTML = `
                <div class="alert alert-danger text-center">
                    <i class="fas fa-exclamation-triangle me-2"></i> Failed to load user data
                </div>`;
        });
}

function renderUserInfo(user) {
    const avatarUrl = user.profile_picture
        ? `/static/profile_photos/${user.profile_picture}`
        : `https://ui-avatars.com/api/?background=667eea&color=fff&name=${encodeURIComponent(user.full_name || user.phone_number)}`;
    document.getElementById('profileAvatar').src = avatarUrl;

    const statusClass = user.is_active ? 'status-active' : 'status-inactive';
    const statusText = user.is_active ? 'Active' : 'Inactive';
    const approvedClass = user.is_approved ? 'status-approved' : (user.rejection_reason ? 'status-rejected' : 'status-pending');
    const approvedText = user.is_approved ? 'Approved' : (user.rejection_reason ? 'Rejected' : 'Pending');

    document.getElementById('personalInfo').innerHTML = `
        <div class="info-item">
            <div class="info-label">Full Name</div>
            <div class="info-value"><strong>${escapeHtml(user.full_name) || '-'}</strong></div>
        </div>
        <div class="info-item">
            <div class="info-label">Phone Number</div>
            <div class="info-value">${escapeHtml(user.phone_number) || '-'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Email</div>
            <div class="info-value">${escapeHtml(user.email) || '-'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Role</div>
            <div class="info-value">
                <span class="badge bg-${user.role === 'admin' ? 'danger' : (user.role === 'extension_officer' ? 'info' : 'success')}">
                    ${user.role ? user.role.replace('_', ' ').toUpperCase() : '-'}
                </span>
            </div>
        </div>
    `;

    document.getElementById('accountInfo').innerHTML = `
        <div class="info-item">
            <div class="info-label">User ID</div>
            <div class="info-value">#${user.user_id}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Status</div>
            <div class="info-value"><span class="status-badge ${statusClass}">${statusText}</span></div>
        </div>
        <div class="info-item">
            <div class="info-label">Approval Status</div>
            <div class="info-value"><span class="status-badge ${approvedClass}">${approvedText}</span></div>
        </div>
        <div class="info-item">
            <div class="info-label">Language Preference</div>
            <div class="info-value">${user.language_preference || 'English'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Registered On</div>
            <div class="info-value">${user.created_at ? formatDate(user.created_at) : '-'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Last Login</div>
            <div class="info-value">${user.last_login ? formatDate(user.last_login) : 'Never'}</div>
        </div>
        ${user.approved_at ? `
        <div class="info-item">
            <div class="info-label">Approved On</div>
            <div class="info-value">${formatDate(user.approved_at)}</div>
        </div>` : ''}
        ${user.rejection_reason ? `
        <div class="info-item">
            <div class="info-label">Rejection Reason</div>
            <div class="info-value text-danger">${escapeHtml(user.rejection_reason)}</div>
        </div>` : ''}
    `;

    document.getElementById('locationInfo').innerHTML = `
        <div class="info-item">
            <div class="info-label">Location</div>
            <div class="info-value">${escapeHtml(user.location) || 'Not specified'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">District</div>
            <div class="info-value">${escapeHtml(user.district) || 'Not specified'}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Region</div>
            <div class="info-value">${escapeHtml(user.region) || 'Not specified'}</div>
        </div>
    `;

    const toggleBtn = document.getElementById('statusToggleBtn');
    if (toggleBtn) {
        toggleBtn.innerHTML = user.is_active ?
            '<i class="fas fa-ban me-2"></i> Deactivate User' :
            '<i class="fas fa-check-circle me-2"></i> Activate User';
    }

    if (user.created_at) {
        const created = new Date(user.created_at);
        const now = new Date();
        const days = Math.floor((now - created) / (1000 * 60 * 60 * 24));
        document.getElementById('activeDays').innerText = days;
    }
}

function loadUserStatistics(userId) {
    fetch(`/api/user/statistics?user_id=${userId}`)
        .then(response => response.json())
        .then(stats => {
            document.getElementById('totalDiagnoses').innerText = stats.total_predictions || 0;
            document.getElementById('accuracyRate').innerText = (stats.success_rate || 85) + '%';
        })
        .catch(error => console.error('Stats error:', error));
}

function loadUserActivity(userId) {
    fetch(`/api/user/activity?user_id=${userId}`)
        .then(response => response.json())
        .then(activities => {
            const container = document.getElementById('activityList');
            if (!activities || activities.length === 0) {
                container.innerHTML = '<div class="text-center py-3 text-muted"><i class="fas fa-inbox fa-2x mb-2 d-block"></i><p>No activity yet</p></div>';
                return;
            }

            container.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <div class="activity-icon" style="background: ${activity.color || '#e9ecef'}">
                        <i class="fas ${activity.icon || 'fa-leaf'}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${escapeHtml(activity.title)}</div>
                        <div class="activity-date">${activity.date}</div>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Activity error:', error);
            document.getElementById('activityList').innerHTML = '<div class="text-center py-3 text-muted">Unable to load activity</div>';
        });
}

function loadNotificationCount(userId) {
    fetch(`/api/notifications/count?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('notificationsCount').innerText = data.count || 0;
        })
        .catch(error => console.error('Notif count error:', error));
}

function toggleUserStatus() {
    if (!currentUserData) return;

    const action = currentUserData.is_active ? 'deactivate' : 'activate';
    if (confirm(`Are you sure you want to ${action} this user?`)) {
        fetch(`/admin/user/${userId}/toggle-status`, { method: 'POST' })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showAlert(result.message, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showAlert('Error: ' + result.message, 'danger');
                }
            })
            .catch(error => showAlert('Error: ' + error, 'danger'));
    }
}

function editUser() {
    if (!currentUserData) return;

    document.getElementById('editFullName').value = currentUserData.full_name || '';
    document.getElementById('editEmail').value = currentUserData.email || '';
    document.getElementById('editPhone').value = currentUserData.phone_number || '';
    document.getElementById('editRole').value = currentUserData.role || 'farmer';
    document.getElementById('editLocation').value = currentUserData.location || '';
    document.getElementById('editDistrict').value = currentUserData.district || '';
    document.getElementById('editRegion').value = currentUserData.region || '';

    new bootstrap.Modal(document.getElementById('editUserModal')).show();
}

function saveUserChanges() {
    const data = {
        full_name: document.getElementById('editFullName').value,
        email: document.getElementById('editEmail').value,
        role: document.getElementById('editRole').value,
        location: document.getElementById('editLocation').value,
        district: document.getElementById('editDistrict').value,
        region: document.getElementById('editRegion').value
    };

    fetch(`/admin/user/${userId}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
                showAlert('User updated successfully!', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showAlert('Error: ' + result.message, 'danger');
            }
        })
        .catch(error => showAlert('Error: ' + error, 'danger'));
}

function deleteUser() {
    if (confirm('⚠️ WARNING: This action cannot be undone!\n\nAre you sure you want to permanently delete this user?')) {
        const confirmation = prompt('Type "DELETE" to confirm:');
        if (confirmation === 'DELETE') {
            fetch(`/admin/user/${userId}/delete`, { method: 'DELETE' })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        showAlert('User deleted successfully!', 'success');
                        setTimeout(() => {
                            window.location.href = '/admin';
                        }, 1500);
                    } else {
                        showAlert('Error: ' + result.message, 'danger');
                    }
                })
                .catch(error => showAlert('Error: ' + error, 'danger'));
        }
    }
}

function sendNotification() {
    new bootstrap.Modal(document.getElementById('notificationModal')).show();
}

function sendManualNotification() {
    const data = {
        user_id: parseInt(userId),
        title_en: document.getElementById('notifTitleEn').value,
        title_sw: document.getElementById('notifTitleSw').value || document.getElementById('notifTitleEn').value,
        message_en: document.getElementById('notifMessageEn').value,
        message_sw: document.getElementById('notifMessageSw').value || document.getElementById('notifMessageEn').value,
        type: document.getElementById('notifType').value
    };

    if (!data.title_en || !data.message_en) {
        showAlert('Please enter title and message', 'danger');
        return;
    }

    fetch('/admin/send-notification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                bootstrap.Modal.getInstance(document.getElementById('notificationModal')).hide();
                showAlert('Notification sent successfully!', 'success');
                loadNotificationCount(userId);
                document.getElementById('notificationForm').reset();
            } else {
                showAlert('Error: ' + result.message, 'danger');
            }
        })
        .catch(error => showAlert('Error: ' + error, 'danger'));
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.style.textAlign = 'center';
    alertDiv.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);

    setTimeout(() => {
        if (alertDiv && alertDiv.remove) {
            alertDiv.remove();
        }
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function () {
    loadUserData();
});

console.log('User details page loaded');