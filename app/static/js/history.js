// Prediction History JavaScript
class PredictionHistory {
    constructor() {
        this.currentUserId = null;
        this.init();
    }

    init() {
        this.loadHistory();
        this.setupEventListeners();
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/farmer/predictions');
            const data = await response.json();

            console.log('API Response:', data);

            if (data.success) {
                this.displayHistory(data.predictions || []);
                this.updateStats({
                    total: data.total || 0,
                    avg_confidence: data.avg_confidence || 0,
                    offline_count: data.offline_count || 0
                });
            } else {
                this.showError(data.error || 'Failed to load history');
            }
        } catch (error) {
            console.error('Error loading history:', error);
            this.showError(getTranslation('error_loading_history'));
        }
    }

    displayHistory(predictions) {
        const container = document.getElementById('historyList');
        if (!container) return;

        if (!predictions || predictions.length === 0) {
            container.innerHTML = this.getEmptyStateHTML();
            return;
        }

        console.log('Displaying predictions count:', predictions.length);

        container.innerHTML = '';
        predictions.forEach(item => {
            const historyItem = this.createHistoryItem(item);
            if (historyItem) {
                container.appendChild(historyItem);
            }
        });
    }

    createHistoryItem(item) {
        const div = document.createElement('div');
        div.className = 'history-item';

        // Try multiple possible ID field names
        let predictionId = item.prediction_id || item.id || item.diagnosis_id || item.predictionId;

        // If still no ID, log error and skip this item
        if (!predictionId) {
            console.error('No ID found in item. Available keys:', Object.keys(item));
            console.log('Problematic item:', item);
            return null; // Skip this item
        }

        div.setAttribute('data-id', predictionId);

        const confidence = parseFloat(item.confidence_score) || 0;
        let confidenceClass = 'confidence-low';
        if (confidence >= 70) confidenceClass = 'confidence-high';
        else if (confidence >= 40) confidenceClass = 'confidence-medium';

        let diagnosisDate = item.diagnosis_date || new Date().toISOString();
        try {
            diagnosisDate = new Date(diagnosisDate).toLocaleString();
        } catch (e) {
            diagnosisDate = diagnosisDate;
        }

        const isSynced = item.is_synced === 1 || item.is_synced === '1' || item.is_synced === true;
        const mode = item.mode || 'online';

        div.innerHTML = `
            <div class="row align-items-center">
                <div class="col-auto">
                    <div class="disease-icon">
                        <i class="fas fa-leaf text-success"></i>
                    </div>
                </div>
                <div class="col">
                    <div class="disease-name">
                        <i class="fas fa-microscope"></i> ${escapeHtml(item.disease_name || 'Unknown')}
                    </div>
                    <div class="d-flex flex-wrap align-items-center gap-2 mt-2">
                        <span class="confidence-badge ${confidenceClass}">
                            <i class="fas fa-percent"></i> ${confidence}% ${getTranslation('confidence')}
                        </span>
                        <span class="date-info">
                            <i class="fas fa-calendar-alt"></i> ${diagnosisDate}
                        </span>
                        <span class="mode-badge ${mode === 'online' ? 'mode-online' : 'mode-offline'}">
                            <i class="fas fa-${mode === 'online' ? 'wifi' : 'plug'}"></i> 
                            ${mode === 'online' ? getTranslation('online') : getTranslation('offline')}
                        </span>
                        <span class="mode-badge ${isSynced ? 'mode-online' : 'mode-offline'}">
                            <i class="fas fa-${isSynced ? 'check-circle' : 'clock'}"></i>
                            ${isSynced ? getTranslation('synced') : getTranslation('pending_sync')}
                        </span>
                    </div>
                </div>
                <div class="col-auto">
                    <button class="btn-delete" onclick="historyManager.deletePrediction(${predictionId})" title="${getTranslation('delete')}">
                        <i class="fas fa-trash-alt fa-lg"></i>
                    </button>
                </div>
            </div>
        `;

        return div;
    }

    updateStats(stats) {
        if (stats) {
            const totalElem = document.getElementById('totalPredictions');
            if (totalElem) totalElem.innerText = stats.total || 0;

            const avgElem = document.getElementById('avgConfidence');
            if (avgElem) avgElem.innerText = `${stats.avg_confidence || 0}%`;

            const offlineElem = document.getElementById('offlinePredictions');
            if (offlineElem) offlineElem.innerText = stats.offline_count || 0;

            const syncBtn = document.getElementById('syncOfflineBtn');
            if (syncBtn) {
                if (stats.offline_count > 0) {
                    syncBtn.style.display = 'inline-block';
                } else {
                    syncBtn.style.display = 'none';
                }
            }
        }
    }

    async deletePrediction(id) {
        console.log('Delete called with ID:', id);

        if (!id || id === 'undefined' || id === null || isNaN(id)) {
            this.showToast('Invalid prediction ID', 'error');
            return;
        }

        if (!confirm(getTranslation('confirm_delete'))) return;

        // Show loading state on button
        const deleteBtn = event?.target?.closest('.btn-delete');
        if (deleteBtn) {
            const originalHtml = deleteBtn.innerHTML;
            deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            deleteBtn.disabled = true;
        }

        try {
            const response = await fetch(`/api/farmer/predictions/delete/${id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });

            console.log('Response status:', response.status);

            if (response.status === 404) {
                this.showToast('Delete endpoint not found', 'error');
                return;
            }

            const data = await response.json();
            console.log('Response data:', data);

            if (data.success) {
                this.showToast('Prediction deleted successfully', 'success');
                await this.loadHistory(); // Reload history
            } else {
                this.showToast(data.error || 'Failed to delete', 'error');
            }
        } catch (error) {
            console.error('Error deleting prediction:', error);
            this.showToast('Error deleting prediction: ' + error.message, 'error');
        } finally {
            if (deleteBtn) {
                deleteBtn.innerHTML = '<i class="fas fa-trash-alt fa-lg"></i>';
                deleteBtn.disabled = false;
            }
        }
    }

    async clearAllHistory() {
        if (!confirm(getTranslation('confirm_clear_all'))) return;

        const clearBtn = document.getElementById('clearHistoryBtn');
        if (clearBtn) {
            clearBtn.disabled = true;
            clearBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Clearing...';
        }

        try {
            const response = await fetch('/api/farmer/predictions/clear-all', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (data.success) {
                this.showToast(data.message || 'All history cleared', 'success');
                await this.loadHistory();
            } else {
                this.showToast(data.error || 'Failed to clear history', 'error');
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            this.showToast('Error clearing history', 'error');
        } finally {
            if (clearBtn) {
                clearBtn.disabled = false;
                clearBtn.innerHTML = '<i class="fas fa-trash-alt"></i> ' + getTranslation('clear_history');
            }
        }
    }

    async syncOfflinePredictions() {
        const syncBtn = document.getElementById('syncOfflineBtn');
        if (syncBtn) {
            syncBtn.disabled = true;
            syncBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Syncing...';
        }

        try {
            const response = await fetch('/api/farmer/predictions/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (data.success) {
                this.showToast(`Synced ${data.synced_count} predictions`, 'success');
                await this.loadHistory();
            } else {
                this.showToast(data.error || 'Sync failed', 'error');
            }
        } catch (error) {
            console.error('Error syncing:', error);
            this.showToast('Error syncing predictions', 'error');
        } finally {
            if (syncBtn) {
                syncBtn.disabled = false;
                syncBtn.innerHTML = '<i class="fas fa-sync-alt"></i> ' + getTranslation('sync_now');
            }
        }
    }

    getEmptyStateHTML() {
        return `
            <div class="empty-state">
                <i class="fas fa-history fa-3x mb-3"></i>
                <h4>${getTranslation('no_history')}</h4>
                <p class="text-muted">${getTranslation('no_history_message')}</p>
                <a href="/predict" class="btn btn-success mt-3">
                    <i class="fas fa-microscope me-2"></i>${getTranslation('make_prediction')}
                </a>
            </div>
        `;
    }

    showError(message) {
        const container = document.getElementById('historyList');
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle text-danger fa-3x mb-3"></i>
                    <h4 class="text-danger">Error</h4>
                    <p class="text-muted">${escapeHtml(message)}</p>
                    <button class="btn btn-primary mt-3" onclick="location.reload()">
                        <i class="fas fa-sync-alt me-2"></i>Retry
                    </button>
                </div>
            `;
        }
    }

    showToast(message, type) {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.custom-toast');
        existingToasts.forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `custom-toast alert alert-${type === 'success' ? 'success' : 'danger'} fade show`;
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        toast.style.minWidth = '280px';
        toast.style.backgroundColor = type === 'success' ? '#d4edda' : '#f8d7da';
        toast.style.color = type === 'success' ? '#155724' : '#721c24';
        toast.style.border = type === 'success' ? '1px solid #c3e6cb' : '1px solid #f5c6cb';
        toast.style.borderRadius = '8px';
        toast.style.padding = '12px 20px';
        toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        toast.style.fontSize = '14px';
        toast.style.fontWeight = '500';
        toast.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                    ${escapeHtml(message)}
                </div>
                <button type="button" class="btn-close" style="background: none; border: none; font-size: 20px; cursor: pointer; margin-left: 15px; opacity: 0.7;">&times;</button>
            </div>
        `;
        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast && toast.remove) toast.remove();
        }, 3000);

        // Close button functionality
        const closeBtn = toast.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.onclick = () => toast.remove();
        }
    }

    setupEventListeners() {
        const clearBtn = document.getElementById('clearHistoryBtn');
        if (clearBtn) {
            clearBtn.removeEventListener('click', this.clearAllHistory);
            clearBtn.addEventListener('click', () => this.clearAllHistory());
        }

        const syncBtn = document.getElementById('syncOfflineBtn');
        if (syncBtn) {
            syncBtn.removeEventListener('click', this.syncOfflinePredictions);
            syncBtn.addEventListener('click', () => this.syncOfflinePredictions());
        }
    }
}

// Helper functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Get translation function
function getTranslation(key) {
    if (window.historyTranslations && window.historyTranslations[key]) {
        return window.historyTranslations[key];
    }
    // Default translations
    const defaults = {
        'confidence': 'Confidence',
        'online': 'Online',
        'offline': 'Offline',
        'synced': 'Synced',
        'pending_sync': 'Pending Sync',
        'delete': 'Delete',
        'no_history': 'No History Found',
        'no_history_message': 'You haven\'t made any predictions yet.',
        'make_prediction': 'Make a Prediction',
        'loading_history': 'Loading history...',
        'error_loading_history': 'Error loading history',
        'confirm_delete': 'Are you sure you want to delete this prediction?',
        'confirm_clear_all': 'Are you sure you want to clear all prediction history? This cannot be undone.',
        'sync_now': 'Sync Now',
        'clear_history': 'Clear History'
    };
    return defaults[key] || key;
}

// Initialize history manager
let historyManager;

document.addEventListener('DOMContentLoaded', function () {
    // Check if already initialized
    if (!historyManager) {
        historyManager = new PredictionHistory();
    }
});

// Export for debugging (optional)
window.historyManager = historyManager;