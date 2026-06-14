// farmers.js - Complete Farmers Management

let allFarmers = [];
let filteredFarmers = [];
let currentPage = 1;
const itemsPerPage = 15;

// Load farmers when page loads
document.addEventListener('DOMContentLoaded', function () {
    console.log("Farmers page loaded");
    loadFarmers();
    setupEventListeners();
});

function setupEventListeners() {
    // Search filter
    document.getElementById('searchFarmers').addEventListener('keyup', function () {
        currentPage = 1;
        filterFarmers();
    });

    // Status filter
    document.getElementById('statusFilter').addEventListener('change', function () {
        currentPage = 1;
        filterFarmers();
    });

    // Region filter
    document.getElementById('regionFilter').addEventListener('change', function () {
        currentPage = 1;
        filterFarmers();
        updateDistrictFilter();
    });

    // Date filters
    document.getElementById('dateFrom').addEventListener('change', function () {
        currentPage = 1;
        filterFarmers();
    });

    document.getElementById('dateTo').addEventListener('change', function () {
        currentPage = 1;
        filterFarmers();
    });
}

function loadFarmers() {
    showLoading(true);

    fetch('/api/officer/farmers?limit=500')
        .then(response => response.json())
        .then(data => {
            showLoading(false);

            if (data.success) {
                allFarmers = data.farmers || [];
                console.log(`Loaded ${allFarmers.length} farmers`);

                updateStatistics();
                updateRegionFilter();
                filterFarmers();
            } else {
                console.error("Error loading farmers:", data.error);
                showToast("Error loading farmers data", "danger");
            }
        })
        .catch(error => {
            showLoading(false);
            console.error("Fetch error:", error);
            showToast("Error connecting to server", "danger");
        });
}

function updateStatistics() {
    const total = allFarmers.length;
    const active = allFarmers.filter(f => f.is_active === 1 || f.is_active === true).length;
    const inactive = total - active;

    document.getElementById('totalFarmers').textContent = total;
    document.getElementById('activeFarmers').textContent = active;
    document.getElementById('inactiveFarmers').textContent = inactive;
}

function updateRegionFilter() {
    const regions = [...new Set(allFarmers.map(f => f.region).filter(r => r))];
    const regionSelect = document.getElementById('regionFilter');

    let html = '<option value="all">All Regions</option>';
    regions.forEach(region => {
        html += `<option value="${region}">${region}</option>`;
    });
    regionSelect.innerHTML = html;
}

function updateDistrictFilter() {
    const selectedRegion = document.getElementById('regionFilter').value;
    let districts = [];

    if (selectedRegion === 'all') {
        districts = [...new Set(allFarmers.map(f => f.district).filter(d => d))];
    } else {
        districts = [...new Set(allFarmers.filter(f => f.region === selectedRegion).map(f => f.district).filter(d => d))];
    }

    const districtSelect = document.getElementById('districtFilter');
    let html = '<option value="all">All Districts</option>';
    districts.forEach(district => {
        html += `<option value="${district}">${district}</option>`;
    });
    districtSelect.innerHTML = html;
}

function filterFarmers() {
    const searchTerm = document.getElementById('searchFarmers').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const regionFilter = document.getElementById('regionFilter').value;
    const districtFilter = document.getElementById('districtFilter').value;
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;

    filteredFarmers = allFarmers.filter(farmer => {
        // Search filter
        if (searchTerm) {
            const matches = (farmer.full_name && farmer.full_name.toLowerCase().includes(searchTerm)) ||
                (farmer.phone_number && farmer.phone_number.toLowerCase().includes(searchTerm)) ||
                (farmer.location && farmer.location.toLowerCase().includes(searchTerm)) ||
                (farmer.email && farmer.email.toLowerCase().includes(searchTerm));
            if (!matches) return false;
        }

        // Status filter
        if (statusFilter !== 'all') {
            const isActive = (farmer.is_active === 1 || farmer.is_active === true);
            if (statusFilter === 'active' && !isActive) return false;
            if (statusFilter === 'inactive' && isActive) return false;
        }

        // Region filter
        if (regionFilter !== 'all' && farmer.region !== regionFilter) return false;

        // District filter
        if (districtFilter !== 'all' && farmer.district !== districtFilter) return false;

        // Date filters
        if (dateFrom && farmer.created_at && farmer.created_at < dateFrom) return false;
        if (dateTo && farmer.created_at && farmer.created_at > dateTo) return false;

        return true;
    });

    displayFarmers();
}

function displayFarmers() {
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageFarmers = filteredFarmers.slice(start, end);
    const totalPages = Math.ceil(filteredFarmers.length / itemsPerPage);

    // Update showing info
    document.getElementById('showingStart').textContent = filteredFarmers.length === 0 ? 0 : start + 1;
    document.getElementById('showingEnd').textContent = Math.min(end, filteredFarmers.length);
    document.getElementById('totalCount').textContent = filteredFarmers.length;

    // Update table
    const tbody = document.getElementById('farmersTableBody');

    if (pageFarmers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center py-5">
                    <i class="fas fa-database fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No farmers found matching your criteria</p>
                </td>
            </tr>
        `;
    } else {
        let html = '';
        pageFarmers.forEach((farmer, index) => {
            const statusClass = (farmer.is_active === 1 || farmer.is_active === true) ? 'status-active' : 'status-inactive';
            const statusText = (farmer.is_active === 1 || farmer.is_active === true) ? 'Active' : 'Inactive';

            html += `
                <tr onclick="showFarmerDetails(${farmer.user_id})">
                    <td>${start + index + 1}</td>
                    <td><strong>${escapeHtml(farmer.full_name || 'N/A')}</strong></td>
                    <td>${escapeHtml(farmer.phone_number || 'N/A')}</td>
                    <td>${escapeHtml(farmer.email || 'N/A')}</td>
                    <td>${escapeHtml(farmer.location || '-')}</td>
                    <td>${escapeHtml(farmer.district || '-')}</td>
                    <td><span class="badge bg-info">${escapeHtml(farmer.region || '-')}</span></td>
                    <td>${farmer.created_at || '-'}</td>
                    <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn btn-sm btn-info" onclick="event.stopPropagation(); showFarmerDetails(${farmer.user_id})" title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showFarmerDiagnoses(${farmer.user_id}, '${escapeHtml(farmer.full_name)}')" title="View Diagnoses">
                                <i class="fas fa-chart-line"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    }

    // Update pagination
    updatePagination(totalPages);
}

function updatePagination(totalPages) {
    let paginationHtml = `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage('prev')">
                <i class="fas fa-chevron-left"></i>
            </a>
        </li>
    `;

    // Show page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        paginationHtml += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(1)">1</a></li>`;
        if (startPage > 2) paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
    }

    for (let i = startPage; i <= endPage; i++) {
        paginationHtml += `
            <li class="page-item ${currentPage === i ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        paginationHtml += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${totalPages})">${totalPages}</a></li>`;
    }

    paginationHtml += `
        <li class="page-item ${currentPage === totalPages || totalPages === 0 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage('next')">
                <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    `;

    document.getElementById('pagination').innerHTML = paginationHtml;
}

function changePage(direction) {
    const totalPages = Math.ceil(filteredFarmers.length / itemsPerPage);

    if (direction === 'prev' && currentPage > 1) {
        currentPage--;
    } else if (direction === 'next' && currentPage < totalPages) {
        currentPage++;
    } else if (typeof direction === 'number') {
        currentPage = direction;
    }

    displayFarmers();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showFarmerDetails(farmerId) {
    const farmer = allFarmers.find(f => f.user_id === farmerId);
    if (!farmer) {
        showToast("Farmer not found", "danger");
        return;
    }

    const modalBody = document.getElementById('farmerDetailsBody');
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header bg-success text-white">
                        <i class="fas fa-user me-2"></i>Personal Information
                    </div>
                    <div class="card-body">
                        <p><strong>Full Name:</strong> ${escapeHtml(farmer.full_name)}</p>
                        <p><strong>Phone Number:</strong> ${escapeHtml(farmer.phone_number)}</p>
                        <p><strong>Email:</strong> ${escapeHtml(farmer.email || 'Not provided')}</p>
                        <p><strong>Status:</strong> <span class="badge ${farmer.is_active ? 'bg-success' : 'bg-danger'}">${farmer.is_active ? 'Active' : 'Inactive'}</span></p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header bg-info text-white">
                        <i class="fas fa-map-marker-alt me-2"></i>Location Information
                    </div>
                    <div class="card-body">
                        <p><strong>Location:</strong> ${escapeHtml(farmer.location || '-')}</p>
                        <p><strong>District:</strong> ${escapeHtml(farmer.district || '-')}</p>
                        <p><strong>Region:</strong> ${escapeHtml(farmer.region || '-')}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <i class="fas fa-clock me-2"></i>Account Information
                    </div>
                    <div class="card-body">
                        <p><strong>Registered Date:</strong> ${farmer.created_at || '-'}</p>
                        <p><strong>User ID:</strong> ${farmer.user_id}</p>
                        <p><strong>Role:</strong> Farmer</p>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Store current farmer ID for diagnose button
    window.currentFarmerId = farmerId;
    window.currentFarmerName = farmer.full_name;

    const modal = new bootstrap.Modal(document.getElementById('farmerDetailsModal'));
    modal.show();
}

function viewFarmerDiagnoses() {
    const farmerId = window.currentFarmerId;
    const farmerName = window.currentFarmerName;
    showFarmerDiagnoses(farmerId, farmerName);
}

function showFarmerDiagnoses(farmerId, farmerName) {
    showLoading(true);

    fetch(`/api/officer/farmer-diagnoses/${farmerId}`)
        .then(response => response.json())
        .then(data => {
            showLoading(false);

            const modalBody = document.getElementById('farmerDiagnosesBody');

            if (data.success && data.diagnoses && data.diagnoses.length > 0) {
                let html = `
                    <h5 class="mb-3">Diagnoses History for: ${escapeHtml(farmerName)}</h5>
                    <div class="table-responsive">
                        <table class="table table-bordered table-hover">
                            <thead class="bg-info text-white">
                                <tr>
                                    <th>#</th>
                                    <th>Disease</th>
                                    <th>Confidence</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

                data.diagnoses.forEach((diag, index) => {
                    const badgeClass = diag.disease_name === 'Healthy' ? 'bg-success' : 'bg-warning';
                    html += `
                        <tr>
                            <td>${index + 1}</td>
                            <td><span class="badge ${badgeClass}">${escapeHtml(diag.disease_name)}</span></td>
                            <td>${diag.confidence_score}%</td>
                            <td>${diag.diagnosis_date}</td>
                        </tr>
                    `;
                });

                html += `
                            </tbody>
                        </table>
                    </div>
                `;
                modalBody.innerHTML = html;
            } else {
                modalBody.innerHTML = `
                    <div class="text-center py-5">
                        <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
                        <p>No diagnoses found for this farmer</p>
                    </div>
                `;
            }

            const modal = new bootstrap.Modal(document.getElementById('farmerDiagnosesModal'));
            modal.show();
        })
        .catch(error => {
            showLoading(false);
            console.error("Error:", error);
            showToast("Error loading diagnoses", "danger");
        });
}

function refreshFarmers() {
    loadFarmers();
    showToast("Farmers data refreshed!", "success");
}

function exportFarmersCSV() {
    window.open('/api/officer/export-farmers', '_blank');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading(show) {
    let loader = document.getElementById('globalLoader');
    if (!loader && show) {
        loader = document.createElement('div');
        loader.id = 'globalLoader';
        loader.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:99999;display:flex;justify-content:center;align-items:center;';
        loader.innerHTML = '<div class="spinner-border text-light" style="width:3rem;height:3rem;"></div>';
        document.body.appendChild(loader);
    } else if (loader && !show) {
        loader.remove();
    }
}

function showToast(message, type) {
    console.log(message);
    alert(message);
}