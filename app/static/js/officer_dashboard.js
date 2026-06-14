// Officer Dashboard JavaScript - Complete Version

let currentEditDiseaseId = null;

document.addEventListener('DOMContentLoaded', function () {
    console.log("Officer Dashboard loaded");
    loadDashboardData();
    loadDiseases();
    loadFarmers();
    loadPredictions();

    // Search functionality
    const searchInput = document.getElementById('farmerSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function () {
            filterFarmers(this.value);
        });
    }

    // Disease filter
    const diseaseFilter = document.getElementById('diseaseFilter');
    if (diseaseFilter) {
        diseaseFilter.addEventListener('change', function () {
            filterPredictions(this.value);
        });
    }
});

function refreshDashboard() {
    showToast('Refreshing dashboard...', 'info');
    loadDashboardData();
    loadDiseases();
    loadFarmers();
    loadPredictions();
}

function loadDashboardData() {
    fetch('/api/officer/dashboard-data')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('totalFarmers').innerText = data.stats.total_farmers || 0;
                document.getElementById('totalPredictions').innerText = data.stats.total_predictions || 0;
                document.getElementById('diseasesDetected').innerText = data.stats.diseases_detected || 0;
                document.getElementById('activeFarmers').innerText = data.stats.active_farmers || 0;
            }
        })
        .catch(error => console.error("Error loading dashboard data:", error));
}

function loadDiseases() {
    fetch('/api/officer/diseases')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateDiseasesTable(data.diseases);
            }
        })
        .catch(error => console.error("Error loading diseases:", error));
}

function updateDiseasesTable(diseases) {
    const tbody = document.getElementById('diseasesTableBody');
    if (!tbody) return;

    if (!diseases || diseases.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No diseases found</td></tr>';
        return;
    }

    let html = '';
    diseases.forEach(disease => {
        html += '<tr>';
        html += '<td>' + escapeHtml(disease.disease_id) + '</td>';
        html += '<td><strong>' + escapeHtml(disease.disease_name_en || '-') + '</strong></td>';
        html += '<td>' + escapeHtml(disease.disease_name_sw || '-') + '</td>';
        html += '<td>' + escapeHtml(disease.scientific_name || '-') + '</td>';
        html += '<td class="action-buttons">';
        html += '<button class="btn btn-sm btn-info me-1" onclick="viewDiseaseDetails(' + disease.disease_id + ')" title="View Details"><i class="fas fa-eye me-1"></i>View</button>';
        html += '<button class="btn btn-sm btn-warning me-1" onclick="showEditDiseaseModal(' + disease.disease_id + ')" title="Edit Disease"><i class="fas fa-edit me-1"></i>Edit</button>';
        html += '<button class="btn btn-sm btn-danger" onclick="deleteDisease(' + disease.disease_id + ')" title="Delete Disease"><i class="fas fa-trash me-1"></i>Delete</button>';
        html += '</td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

function viewDiseaseDetails(diseaseId) {
    if (!diseaseId) {
        showToast('Invalid disease ID', 'danger');
        return;
    }

    showLoading(true);

    fetch('/api/officer/disease/' + diseaseId)
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showDiseaseDetailsModal(data.disease);
            } else {
                showToast(data.error || 'Error loading disease details', 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error loading disease details', 'danger');
        });
}

function showDiseaseDetailsModal(disease) {
    const modalBody = document.getElementById('diseaseDetailsModalBody');
    if (!modalBody) return;

    const html = `
        <div class="row">
            <div class="col-12 mb-3">
                <div class="card disease-detail-card">
                    <div class="card-header bg-light">
                        <strong><i class="fas fa-info-circle me-2"></i>Basic Information</strong>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-2">
                                <label class="fw-bold text-muted">Disease Name (English):</label>
                                <p class="mb-0">${escapeHtml(disease.disease_name_en || '-')}</p>
                            </div>
                            <div class="col-md-6 mb-2">
                                <label class="fw-bold text-muted">Disease Name (Swahili):</label>
                                <p class="mb-0">${escapeHtml(disease.disease_name_sw || '-')}</p>
                            </div>
                            <div class="col-12 mb-2">
                                <label class="fw-bold text-muted">Scientific Name:</label>
                                <p class="mb-0">${escapeHtml(disease.scientific_name || '-')}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 mb-3">
                <div class="card disease-detail-card">
                    <div class="card-header bg-light">
                        <strong><i class="fas fa-stethoscope me-2"></i>Description</strong>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-2">
                                <label class="fw-bold text-muted">English:</label>
                                <p class="mb-0">${escapeHtml(disease.description_en || '-')}</p>
                            </div>
                            <div class="col-md-6 mb-2">
                                <label class="fw-bold text-muted">Swahili:</label>
                                <p class="mb-0">${escapeHtml(disease.description_sw || '-')}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 mb-3">
                <div class="card disease-detail-card">
                    <div class="card-header bg-light">
                        <strong><i class="fas fa-head-side-medical me-2"></i>Symptoms</strong>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-2">
                                <label class="fw-bold text-muted">English:</label>
                                <p class="mb-0">${escapeHtml(disease.symptoms_en || '-')}</p>
                            </div>
                            <div class="col-md-6 mb-2">
                                <label class="fw-bold text-muted">Swahili:</label>
                                <p class="mb-0">${escapeHtml(disease.symptoms_sw || '-')}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 mb-3">
                <div class="card disease-detail-card">
                    <div class="card-header bg-light">
                        <strong><i class="fas fa-capsules me-2"></i>Treatment</strong>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-2">
                                <label class="fw-bold text-muted">English:</label>
                                <p class="mb-0">${escapeHtml(disease.treatment_en || '-')}</p>
                            </div>
                            <div class="col-md-6 mb-2">
                                <label class="fw-bold text-muted">Swahili:</label>
                                <p class="mb-0">${escapeHtml(disease.treatment_sw || '-')}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    modalBody.innerHTML = html;

    // Set up edit button
    const editBtn = document.getElementById('editDiseaseFromModalBtn');
    if (editBtn) {
        editBtn.onclick = function () {
            const modal = bootstrap.Modal.getInstance(document.getElementById('diseaseDetailsModal'));
            if (modal) modal.hide();
            showEditDiseaseModal(disease.disease_id);
        };
    }

    const modal = new bootstrap.Modal(document.getElementById('diseaseDetailsModal'));
    modal.show();
}

function showEditDiseaseModal(diseaseId) {
    if (!diseaseId) {
        showToast('Invalid disease ID', 'danger');
        return;
    }

    currentEditDiseaseId = diseaseId;
    showLoading(true);

    fetch('/api/officer/disease/' + diseaseId)
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showEditDiseaseForm(data.disease);
            } else {
                showToast(data.error || 'Error loading disease data', 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error loading disease data', 'danger');
        });
}

function showEditDiseaseForm(disease) {
    const existingModal = document.getElementById('editDiseaseModal');
    if (existingModal) existingModal.remove();

    const modalHtml = `
        <div class="modal fade" id="editDiseaseModal" tabindex="-1">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="fas fa-edit me-2"></i>Edit Disease: ${escapeHtml(disease.disease_name_en)}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editDiseaseForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Disease Name (English) *</label>
                                    <input type="text" id="edit_disease_name_en" class="form-control" value="${escapeHtml(disease.disease_name_en || '')}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Disease Name (Swahili)</label>
                                    <input type="text" id="edit_disease_name_sw" class="form-control" value="${escapeHtml(disease.disease_name_sw || '')}">
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Scientific Name</label>
                                    <input type="text" id="edit_scientific_name" class="form-control" value="${escapeHtml(disease.scientific_name || '')}">
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Description (English)</label>
                                    <textarea id="edit_description_en" class="form-control" rows="2">${escapeHtml(disease.description_en || '')}</textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Description (Swahili)</label>
                                    <textarea id="edit_description_sw" class="form-control" rows="2">${escapeHtml(disease.description_sw || '')}</textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Symptoms (English)</label>
                                    <textarea id="edit_symptoms_en" class="form-control" rows="2">${escapeHtml(disease.symptoms_en || '')}</textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Symptoms (Swahili)</label>
                                    <textarea id="edit_symptoms_sw" class="form-control" rows="2">${escapeHtml(disease.symptoms_sw || '')}</textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Treatment (English)</label>
                                    <textarea id="edit_treatment_en" class="form-control" rows="2">${escapeHtml(disease.treatment_en || '')}</textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Treatment (Swahili)</label>
                                    <textarea id="edit_treatment_sw" class="form-control" rows="2">${escapeHtml(disease.treatment_sw || '')}</textarea>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="updateDisease()">Save Changes</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modalElement = document.getElementById('editDiseaseModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    modalElement.addEventListener('hidden.bs.modal', function () {
        this.remove();
        currentEditDiseaseId = null;
    });
}

function updateDisease() {
    if (!currentEditDiseaseId) {
        showToast('No disease selected for editing', 'danger');
        return;
    }

    const diseaseData = {
        disease_name_en: document.getElementById('edit_disease_name_en').value,
        disease_name_sw: document.getElementById('edit_disease_name_sw').value,
        scientific_name: document.getElementById('edit_scientific_name').value,
        description_en: document.getElementById('edit_description_en').value,
        description_sw: document.getElementById('edit_description_sw').value,
        symptoms_en: document.getElementById('edit_symptoms_en').value,
        symptoms_sw: document.getElementById('edit_symptoms_sw').value,
        treatment_en: document.getElementById('edit_treatment_en').value,
        treatment_sw: document.getElementById('edit_treatment_sw').value
    };

    if (!diseaseData.disease_name_en) {
        showToast('Disease name (English) is required', 'warning');
        return;
    }

    showLoading(true);

    fetch('/api/officer/disease/' + currentEditDiseaseId + '/update', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(diseaseData)
    })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showToast(data.message || 'Disease updated successfully', 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('editDiseaseModal'));
                if (modal) modal.hide();
                setTimeout(() => loadDiseases(), 1000);
            } else {
                showToast(data.message || 'Error updating disease', 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error updating disease', 'danger');
        });
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

    fetch('/api/officer/disease/' + diseaseId + '/delete', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showToast(data.message || 'Disease deleted successfully', 'success');
                loadDiseases();
            } else {
                showToast(data.message || 'Error deleting disease', 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error deleting disease', 'danger');
        });
}

function showAddDiseaseModal() {
    const existingModal = document.getElementById('addDiseaseModal');
    if (existingModal) existingModal.remove();

    const modalHtml = `
        <div class="modal fade" id="addDiseaseModal" tabindex="-1">
            <div class="modal-dialog modal-lg modal-dialog-centered">
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
                                    <input type="text" id="add_disease_name_en" class="form-control" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Disease Name (Swahili)</label>
                                    <input type="text" id="add_disease_name_sw" class="form-control">
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Scientific Name</label>
                                    <input type="text" id="add_scientific_name" class="form-control">
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Description (English)</label>
                                    <textarea id="add_description_en" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Description (Swahili)</label>
                                    <textarea id="add_description_sw" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Symptoms (English)</label>
                                    <textarea id="add_symptoms_en" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Symptoms (Swahili)</label>
                                    <textarea id="add_symptoms_sw" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Treatment (English)</label>
                                    <textarea id="add_treatment_en" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="form-label">Treatment (Swahili)</label>
                                    <textarea id="add_treatment_sw" class="form-control" rows="2"></textarea>
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
    const modal = new bootstrap.Modal(document.getElementById('addDiseaseModal'));
    modal.show();
}

function addDisease() {
    const diseaseData = {
        disease_name_en: document.getElementById('add_disease_name_en').value,
        disease_name_sw: document.getElementById('add_disease_name_sw').value,
        scientific_name: document.getElementById('add_scientific_name').value,
        description_en: document.getElementById('add_description_en').value,
        description_sw: document.getElementById('add_description_sw').value,
        symptoms_en: document.getElementById('add_symptoms_en').value,
        symptoms_sw: document.getElementById('add_symptoms_sw').value,
        treatment_en: document.getElementById('add_treatment_en').value,
        treatment_sw: document.getElementById('add_treatment_sw').value
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
                loadDiseases();
            } else {
                showToast(data.message || 'Error adding disease', 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showToast('Network error adding disease', 'danger');
        });
}

function loadFarmers() {
    fetch('/api/officer/dashboard-data')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.recent_farmers) {
                updateFarmersTable(data.recent_farmers);
            }
        })
        .catch(error => console.error("Error loading farmers:", error));
}

function updateFarmersTable(farmers) {
    const tbody = document.getElementById('farmersTableBody');
    if (!tbody) return;

    if (!farmers || farmers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No farmers found</td></tr>';
        return;
    }

    let html = '';
    farmers.forEach(farmer => {
        html += '<tr>';
        html += '<td>' + escapeHtml(farmer.full_name || '-') + '</td>';
        html += '<td>' + escapeHtml(farmer.phone_number || '-') + '</td>';
        html += '<td>' + escapeHtml(farmer.email || '-') + '</td>';
        html += '<td>' + escapeHtml(farmer.location || '-') + '</td>';
        html += '<td>' + escapeHtml(farmer.district || '-') + '</td>';
        html += '<td>' + escapeHtml(farmer.region || '-') + '</td>';
        html += '<td>' + escapeHtml(farmer.created_at || '-') + '</td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

function filterFarmers(searchTerm) {
    const rows = document.querySelectorAll('#farmersTableBody tr');
    searchTerm = searchTerm.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

function loadPredictions() {
    fetch('/api/officer/dashboard-data')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.recent_predictions) {
                updatePredictionsTable(data.recent_predictions);
            }
        })
        .catch(error => console.error("Error loading predictions:", error));
}

function updatePredictionsTable(predictions) {
    const tbody = document.getElementById('predictionsTableBody');
    if (!tbody) return;

    if (!predictions || predictions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No predictions found</td></tr>';
        return;
    }

    let html = '';
    predictions.forEach(pred => {
        const confidence = pred.confidence_score ? parseFloat(pred.confidence_score).toFixed(1) + '%' : 'N/A';
        html += '<tr>';
        html += '<td>' + escapeHtml(pred.farmer_name || '-') + '</td>';
        html += '<td>' + escapeHtml(pred.farmer_phone || '-') + '</td>';
        html += '<td>' + escapeHtml(pred.location || '-') + '</td>';
        html += '<td><span class="badge bg-danger">' + escapeHtml(pred.disease_name || '-') + '</span></td>';
        html += '<td>' + confidence + '</td>';
        html += '<td>' + escapeHtml(pred.diagnosis_date || '-') + '</td>';
        html += '<td><button class="btn btn-sm btn-info" onclick="viewPredictionDetails(' + pred.id + ')">View Details</button></td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

function filterPredictions(diseaseName) {
    const rows = document.querySelectorAll('#predictionsTableBody tr');

    rows.forEach(row => {
        if (diseaseName === 'all') {
            row.style.display = '';
        } else {
            const diseaseCell = row.cells[3];
            const text = diseaseCell ? diseaseCell.textContent : '';
            row.style.display = text.includes(diseaseName) ? '' : 'none';
        }
    });
}

function viewPredictionDetails(predictionId) {
    showToast('Prediction details feature coming soon', 'info');
}

function exportFarmers() {
    showToast('Export CSV feature coming soon', 'info');
}

function exportPredictions() {
    showToast('Export CSV feature coming soon', 'info');
}

// Helper Functions
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
    const bgClass = type === 'success' ? 'bg-success' : (type === 'danger' ? 'bg-danger' : 'bg-info');

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="3000">
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

    toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
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

function scrollToFarmers() {
    document.getElementById('farmersSection').scrollIntoView({ behavior: 'smooth' });
}

function scrollToPredictions() {
    document.getElementById('predictionsSection').scrollIntoView({ behavior: 'smooth' });
}

// Make functions global
window.refreshDashboard = refreshDashboard;
window.viewDiseaseDetails = viewDiseaseDetails;
window.showEditDiseaseModal = showEditDiseaseModal;
window.deleteDisease = deleteDisease;
window.showAddDiseaseModal = showAddDiseaseModal;
window.addDisease = addDisease;
window.scrollToFarmers = scrollToFarmers;
window.scrollToPredictions = scrollToPredictions;
window.exportFarmers = exportFarmers;
window.exportPredictions = exportPredictions;
window.viewPredictionDetails = viewPredictionDetails;

console.log("Officer Dashboard JS loaded successfully");