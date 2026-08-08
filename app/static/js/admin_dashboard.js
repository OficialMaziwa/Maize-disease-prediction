
document.addEventListener('DOMContentLoaded', function () {
    console.log("Admin Dashboard loaded");
    loadData();

    // Initialize Bootstrap tabs if needed
    var triggerTabList = [].slice.call(document.querySelectorAll('#adminTabs a'));
    triggerTabList.forEach(function (triggerEl) {
        var tabTrigger = new bootstrap.Tab(triggerEl);
        triggerEl.addEventListener('click', function (event) {
            event.preventDefault();
            tabTrigger.show();
        });
    });
});

function loadData() {
    // Load users
    fetch('/api/admin/maziwa-list')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Users loaded:", data.users.length);
                updateUserTables(data.users);
            }
        })
        .catch(error => console.error("Error loading users:", error));

    // Load diseases
    fetch('/api/officer/diseases')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Diseases loaded:", data.diseases.length);
                updateDiseaseTable(data.diseases);
            }
        })
        .catch(error => console.error("Error loading diseases:", error));

    // Load stats
    loadStats();
}

function loadStats() {
    fetch('/api/admin/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Check if elements exist before setting
                var el = document.getElementById('totalUsers');
                if (el) el.innerText = data.total_users || 0;
                el = document.getElementById('totalFarmers');
                if (el) el.innerText = data.total_farmers || 0;
                el = document.getElementById('totalOfficers');
                if (el) el.innerText = data.total_officers || 0;
                el = document.getElementById('totalPredictions');
                if (el) el.innerText = data.total_predictions || 0;

                var pendingSpan = document.getElementById('pendingOfficers');
                if (pendingSpan) pendingSpan.innerText = data.pending_officers || 0;
            }
        })
        .catch(error => console.error("Error loading stats:", error));
}

function updateUserTables(users) {
    const farmers = users.filter(u => u.role === 'farmer');
    const officers = users.filter(u => u.role === 'extension_officer');
    const admins = users.filter(u => u.role === 'admin');
    const pending = users.filter(u => u.role === 'extension_officer' && !u.is_approved);

    updateFarmersTable(farmers);
    updateOfficersTable(officers);
    updateAdminsTable(admins);
    updatePendingTable(pending);

    var el = document.getElementById('totalUsers');
    if (el) el.textContent = users.length;

    el = document.getElementById('totalFarmers');
    if (el) el.textContent = farmers.length;

    el = document.getElementById('totalOfficers');
    if (el) el.textContent = officers.length;

    el = document.getElementById('totalAdmins');
    if (el) el.textContent = admins.length;

    el = document.getElementById('pendingCount');
    if (el) el.textContent = pending.length;

    el = document.getElementById('farmersCount');
    if (el) el.textContent = farmers.length;

    el = document.getElementById('officersCount');
    if (el) el.textContent = officers.length;

    el = document.getElementById('adminsCount');
    if (el) el.textContent = admins.length;
}

function updateFarmersTable(farmers) {
    const tbody = document.getElementById('farmersTableBody');
    if (!tbody) return;

    if (!farmers || farmers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No farmers found</td></tr>';
        return;
    }

    let html = '';
    farmers.forEach(farmer => {
        html += '<tr data-user-id="' + farmer.user_id + '">';
        html += '<td>' + escapeHtml(farmer.user_id) + '</td>';
        html += '<td><strong>' + escapeHtml(farmer.full_name) + '</strong></td>';
        html += '<td>' + escapeHtml(farmer.phone_number) + '</td>';
        html += '<td>' + escapeHtml(farmer.email || '-') + '</td>';
        html += '<td>' + escapeHtml(farmer.location || '-') + '</td>';
        html += '<td>' + escapeHtml(farmer.district || '-') + '</td>';
        html += '<td>' + escapeHtml(farmer.region || '-') + '</td>';
        html += '<td><span class="badge bg-success">Active</span></td>';
        html += '<td class="action-buttons">';
        html += '<button class="btn btn-sm btn-info me-1" onclick="viewUser(\'' + farmer.user_id + '\')" title="View"><i class="fas fa-eye"></i></button>';
        html += '<button class="btn btn-sm btn-warning me-1" onclick="editUser(\'' + farmer.user_id + '\')" title="Edit"><i class="fas fa-edit"></i></button>';
        html += '<button class="btn btn-sm btn-danger" onclick="deleteUser(\'' + farmer.user_id + '\')" title="Delete"><i class="fas fa-trash"></i></button>';
        html += '</td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

function updateOfficersTable(officers) {
    const tbody = document.getElementById('officersTableBody');
    if (!tbody) return;

    if (!officers || officers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No officers found</td></tr>';
        return;
    }

    let html = '';
    officers.forEach(officer => {
        const statusBadge = officer.is_active ? 'bg-success' : 'bg-danger';
        const statusText = officer.is_active ? 'Active' : 'Inactive';
        const approvedBadge = officer.is_approved ? 'bg-success' : 'bg-warning';
        const approvedText = officer.is_approved ? 'Approved' : 'Pending';

        html += '<tr data-user-id="' + officer.user_id + '">';
        html += '<td>' + escapeHtml(officer.user_id) + '</td>';
        html += '<td><strong>' + escapeHtml(officer.full_name) + '</strong></td>';
        html += '<td>' + escapeHtml(officer.phone_number) + '</td>';
        html += '<td>' + escapeHtml(officer.email || '-') + '</td>';
        html += '<td>' + escapeHtml(officer.region || '-') + '</td>';
        html += '<td><span class="badge ' + statusBadge + '">' + statusText + '</span></td>';
        html += '<td><span class="badge ' + approvedBadge + '">' + approvedText + '</span></td>';
        html += '<td class="action-buttons">';
        html += '<button class="btn btn-sm btn-info me-1" onclick="viewUser(\'' + officer.user_id + '\')" title="View"><i class="fas fa-eye"></i></button>';
        html += '<button class="btn btn-sm btn-warning me-1" onclick="editUser(\'' + officer.user_id + '\')" title="Edit"><i class="fas fa-edit"></i></button>';
        if (!officer.is_approved) {
            html += '<button class="btn btn-sm btn-success me-1" onclick="approveOfficer(\'' + officer.user_id + '\')" title="Approve"><i class="fas fa-check"></i></button>';
        }
        html += '<button class="btn btn-sm btn-danger" onclick="deleteUser(\'' + officer.user_id + '\')" title="Delete"><i class="fas fa-trash"></i></button>';
        html += '</td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

function updateAdminsTable(admins) {
    const tbody = document.getElementById('adminsTableBody');
    if (!tbody) return;

    if (!admins || admins.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No admins found</td></tr>';
        return;
    }

    let html = '';
    admins.forEach(admin => {
        const statusBadge = admin.is_active ? 'bg-success' : 'bg-danger';
        const statusText = admin.is_active ? 'Active' : 'Inactive';

        html += '<tr data-user-id="' + admin.user_id + '">';
        html += '<td>' + escapeHtml(admin.user_id) + '</td>';
        html += '<td><strong>' + escapeHtml(admin.full_name) + '</strong></td>';
        html += '<td>' + escapeHtml(admin.phone_number) + '</td>';
        html += '<td>' + escapeHtml(admin.email || '-') + '</td>';
        html += '<td><span class="badge bg-info">' + escapeHtml(admin.role) + '</span></td>';
        html += '<td><span class="badge ' + statusBadge + '">' + statusText + '</span></td>';
        html += '<td class="action-buttons">';
        html += '<button class="btn btn-sm btn-info me-1" onclick="viewUser(\'' + admin.user_id + '\')" title="View"><i class="fas fa-eye"></i></button>';
        html += '<button class="btn btn-sm btn-warning me-1" onclick="editUser(\'' + admin.user_id + '\')" title="Edit"><i class="fas fa-edit"></i></button>';
        if (admin.user_id != window.currentUserId) {
            html += '<button class="btn btn-sm btn-danger" onclick="deleteUser(\'' + admin.user_id + '\')" title="Delete"><i class="fas fa-trash"></i></button>';
        }
        html += '</td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

function updatePendingTable(pending) {
    const tbody = document.getElementById('pending-officers-tbody');
    if (!tbody) return;

    if (!pending || pending.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No pending officers</td></tr>';
        return;
    }

    let html = '';
    pending.forEach(officer => {
        html += '<tr id="officer-row-' + officer.user_id + '">';
        html += '<td>' + escapeHtml(officer.user_id || '-') + '</td>';
        html += '<td><strong>' + escapeHtml(officer.full_name || '-') + '</strong></td>';
        html += '<td>' + escapeHtml(officer.phone_number || '-') + '</td>';
        html += '<td>' + escapeHtml(officer.email || '-') + '</td>';
        html += '<td>' + escapeHtml(officer.region || '-') + '</td>';
        html += '<td>' + (officer.created_at ? officer.created_at.substring(0, 10) : '-') + '</td>';
        html += '<td class="action-buttons">';
        html += '<button class="btn btn-sm btn-success me-1" onclick="approveOfficer(\'' + officer.user_id + '\')" title="Approve"><i class="fas fa-check me-1"></i>Approve</button>';
        html += '<button class="btn btn-sm btn-danger me-1" onclick="showRejectModal(\'' + officer.user_id + '\', \'' + escapeHtml(officer.full_name) + '\')" title="Reject"><i class="fas fa-times me-1"></i>Reject</button>';
        html += '<button class="btn btn-sm btn-info" onclick="viewUser(\'' + officer.user_id + '\')" title="View"><i class="fas fa-eye"></i></button>';
        html += '</td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

function updateDiseaseTable(diseases) {
    const tbody = document.getElementById('diseasesTableBody');
    if (!tbody) return;

    if (!diseases || diseases.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No diseases found</td></tr>';
        return;
    }

    let html = '';
    diseases.forEach(disease => {
        html += '<tr data-disease-id="' + disease.disease_id + '">';
        html += '<td>' + escapeHtml(disease.disease_id) + '</td>';
        html += '<td><strong>' + escapeHtml(disease.disease_name_en || '-') + '</strong></td>';
        html += '<td>' + escapeHtml(disease.disease_name_sw || '-') + '</td>';
        html += '<td>' + escapeHtml(disease.scientific_name || '-') + '</td>';
        html += '<td class="action-buttons">';
        html += '<button class="btn btn-sm btn-info me-1" onclick="viewDisease(' + disease.disease_id + ')" title="View"><i class="fas fa-eye me-1"></i>View</button>';
        html += '<button class="btn btn-sm btn-warning me-1" onclick="editDisease(' + disease.disease_id + ')" title="Edit"><i class="fas fa-edit me-1"></i>Edit</button>';
        html += '<button class="btn btn-sm btn-danger" onclick="deleteDisease(' + disease.disease_id + ')" title="Delete"><i class="fas fa-trash me-1"></i>Delete</button>';
        html += '</td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}


// USER CRUD FUNCTIONS

function viewUser(userId) {
    if (!userId) {
        showToast('Invalid user ID', 'danger');
        return;
    }
    window.location.href = '/admin/user/' + userId + '/view';
}

function editUser(userId) {
    if (!userId) {
        showToast('Invalid user ID', 'danger');
        return;
    }
    window.location.href = '/admin/user/' + userId + '/edit';
}

function deleteUser(userId) {
    if (!userId) {
        showToast('Invalid user ID', 'danger');
        return;
    }

    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
    }

    showLoading(true);

    fetch('/admin/user/' + userId + '/delete', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showToast('User deleted successfully', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast('Error: ' + (data.message || 'Unknown error'), 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error: ' + error.message, 'danger');
        });
}


// ADD USER FUNCTIONS

function showAddFarmerModal() {
    window.location.href = '/admin/farmer/add';
}

function showAddOfficerModal() {
    window.location.href = '/admin/officer/add';
}

function showAddAdminModal() {
    window.location.href = '/admin/admin/add';
}

function showEditUserModal(userId) {
    editUser(userId);
}


// OFFICER APPROVAL FUNCTIONS
function approveOfficer(userId) {
    if (!userId) {
        showToast('Invalid officer ID', 'danger');
        return;
    }

    if (!confirm('Are you sure you want to approve this extension officer? They will receive email notification.')) {
        return;
    }

    showLoading(true);

    fetch('/admin/officer/' + userId + '/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showToast(data.message || 'Officer approved successfully', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast('Error: ' + (data.message || 'Unknown error'), 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error: ' + error.message, 'danger');
        });
}

function showRejectModal(userId, officerName) {
    if (!userId) {
        showToast('Invalid officer ID', 'danger');
        return;
    }

    // Remove existing modal
    const existingModal = document.getElementById('rejectModal');
    if (existingModal) existingModal.remove();

    const modalHtml = `
        <div class="modal fade" id="rejectModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-times-circle me-2"></i>Reject Officer: ${escapeHtml(officerName)}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Are you sure you want to reject <strong>${escapeHtml(officerName)}</strong>'s application?</p>
                        <div class="mb-3">
                            <label class="form-label">Reason for rejection:</label>
                            <textarea id="rejectionReason" class="form-control" rows="3" placeholder="Please provide a reason..."></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" onclick="rejectOfficer('${userId}')">Confirm Rejection</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modalElement = document.getElementById('rejectModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    modalElement.addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

function rejectOfficer(userId) {
    const reason = document.getElementById('rejectionReason') ?
        document.getElementById('rejectionReason').value :
        'No specific reason provided';

    if (!reason.trim()) {
        showToast('Please provide a reason for rejection', 'warning');
        return;
    }

    showLoading(true);

    fetch('/admin/officer/' + userId + '/reject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: reason })
    })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showToast(data.message || 'Officer rejected', 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('rejectModal'));
                if (modal) modal.hide();
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast('Error: ' + (data.message || 'Unknown error'), 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error: ' + error.message, 'danger');
        });
}


// DISEASE CRUD FUNCTIONS

function viewDisease(diseaseId) {
    if (!diseaseId) {
        showToast('Invalid disease ID', 'danger');
        return;
    }
    window.location.href = '/admin/disease/' + diseaseId + '/view';
}

function editDisease(diseaseId) {
    if (!diseaseId) {
        showToast('Invalid disease ID', 'danger');
        return;
    }
    window.location.href = '/admin/disease/' + diseaseId + '/edit';
}

function deleteDisease(diseaseId) {
    if (!diseaseId) {
        showToast('Invalid disease ID', 'danger');
        return;
    }

    if (!confirm('Are you sure you want to delete this disease? This action cannot be undone.')) {
        return;
    }

    showLoading(true);

    fetch('/admin/disease/' + diseaseId + '/delete', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showToast(data.message || 'Disease deleted successfully', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast('Error: ' + (data.message || 'Unknown error'), 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error: ' + error.message, 'danger');
        });
}

// ADD DISEASE FUNCTION
function showAddDiseaseModal() {
    const existingModal = document.getElementById('addDiseaseModal');
    if (existingModal) existingModal.remove();

    const modalHtml = `
        <div class="modal fade" id="addDiseaseModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-plus-circle me-2"></i>Add New Disease
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addDiseaseForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Disease Name (English) *</label>
                                    <input type="text" id="disease_name_en" class="form-control" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Disease Name (Swahili)</label>
                                    <input type="text" id="disease_name_sw" class="form-control">
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Scientific Name</label>
                                    <input type="text" id="scientific_name" class="form-control">
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Description (English)</label>
                                    <textarea id="description_en" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Description (Swahili)</label>
                                    <textarea id="description_sw" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Symptoms (English)</label>
                                    <textarea id="symptoms_en" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Symptoms (Swahili)</label>
                                    <textarea id="symptoms_sw" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Treatment (English)</label>
                                    <textarea id="treatment_en" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Treatment (Swahili)</label>
                                    <textarea id="treatment_sw" class="form-control" rows="2"></textarea>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="addDisease()">Add Disease</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modalElement = document.getElementById('addDiseaseModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    modalElement.addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

function addDisease() {
    const diseaseData = {
        disease_name_en: document.getElementById('disease_name_en').value,
        disease_name_sw: document.getElementById('disease_name_sw').value,
        scientific_name: document.getElementById('scientific_name').value,
        description_en: document.getElementById('description_en').value,
        description_sw: document.getElementById('description_sw').value,
        symptoms_en: document.getElementById('symptoms_en').value,
        symptoms_sw: document.getElementById('symptoms_sw').value,
        treatment_en: document.getElementById('treatment_en').value,
        treatment_sw: document.getElementById('treatment_sw').value
    };

    if (!diseaseData.disease_name_en) {
        showToast('Disease name (English) is required', 'warning');
        return;
    }

    showLoading(true);

    fetch('/api/officer/disease/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(diseaseData)
    })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showToast(data.message || 'Disease added successfully', 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('addDiseaseModal'));
                if (modal) modal.hide();
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast('Error: ' + (data.message || 'Unknown error'), 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error: ' + error.message, 'danger');
        });
}


// HELPER FUNCTIONS


function refreshAllData() {
    showToast('Refreshing data...', 'info');
    location.reload();
}

function generateReport(type) {
    showToast('Report generation for ' + type + ' coming soon', 'info');
}

function showLoading(show) {
    let overlay = document.getElementById('loadingOverlay');

    if (show) {
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;display:flex;justify-content:center;align-items:center';
            overlay.innerHTML = '<div class="spinner-border text-light" style="width:3rem;height:3rem" role="status"><span class="visually-hidden">Loading...</span></div>';
            document.body.appendChild(overlay);
        }
    } else {
        if (overlay) overlay.remove();
    }
}

function showToast(message, type = 'success') {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9998';
        document.body.appendChild(toastContainer);
    }

    const toastId = 'toast_' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : (type === 'danger' ? 'bg-danger' : (type === 'warning' ? 'bg-warning' : 'bg-info'));
    const textColor = type === 'warning' ? 'text-dark' : 'text-white';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} ${textColor} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="3000">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Store current user ID from session
window.currentUserId = document.querySelector('[data-user-id]') ?
    document.querySelector('[data-user-id]').getAttribute('data-user-id') : null;

// Make all functions global
window.viewUser = viewUser;
window.editUser = editUser;
window.deleteUser = deleteUser;
window.approveOfficer = approveOfficer;
window.showRejectModal = showRejectModal;
window.rejectOfficer = rejectOfficer;
window.viewDisease = viewDisease;
window.editDisease = editDisease;
window.deleteDisease = deleteDisease;
window.showAddDiseaseModal = showAddDiseaseModal;
window.addDisease = addDisease;
window.refreshAllData = refreshAllData;
window.generateReport = generateReport;
window.showAddFarmerModal = showAddFarmerModal;
window.showAddOfficerModal = showAddOfficerModal;
window.showAddAdminModal = showAddAdminModal;
window.showEditUserModal = showEditUserModal;

console.log("Admin dashboard JS loaded successfully");