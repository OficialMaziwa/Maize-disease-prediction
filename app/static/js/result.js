function saveAsHTML() {
    const content = document.getElementById('report-content').cloneNode(true);
    const styles = document.querySelector('link[href*="bootstrap"]')?.href || 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css';

    const html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Maize Disease Report</title>
    <link href="${styles}" rel="stylesheet">
    <style>
        body { padding: 20px; background: white; }
        .save-options, .no-print, .btn, .alert-dismissible { display: none; }
        .card { box-shadow: none; border: 1px solid #ddd; }
        @media print { body { padding: 0; } }
    </style>
</head>
<body>
    <div class="container mt-4">
        ${content.outerHTML}
    </div>
</body>
</html>`;

    downloadFile(html, `maize_report_${formatDateForFilename()}.html`, 'text/html');
    showAlert(getTranslation('report_saved'));
}

function saveAsText() {
    const content = document.getElementById('report-content').innerText;
    downloadFile(content, `maize_report_${formatDateForFilename()}.txt`, 'text/plain');
    showAlert(getTranslation('report_saved'));
}

function copyToClipboard() {
    const content = document.getElementById('report-content').innerText;
    navigator.clipboard.writeText(content).then(() => {
        showAlert(getTranslation('report_copied'));
    }).catch(() => {
        showAlert('Failed to copy', 'danger');
    });
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type: type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
function formatDateForFilename() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}-${String(now.getMinutes()).padStart(2, '0')}-${String(now.getSeconds()).padStart(2, '0')}`;
}
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '250px';
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

function getTranslation(key) {
    const translations = {
        'report_saved': 'Report saved successfully!',
        'report_copied': 'Report copied to clipboard!'
    };
    return translations[key] || key;
}

function printReport() {
    const originalTitle = document.title;
    document.title = 'Maize Disease Diagnosis Report';
    window.print();
    document.title = originalTitle;
}

function shareReport() {
    const content = document.getElementById('report-content').innerText.substring(0, 1000);
    if (navigator.share) {
        navigator.share({
            title: 'Maize Disease Diagnosis Report',
            text: content,
        }).catch(() => { });
    } else {
        copyToClipboard();
        showAlert('Copied to clipboard. You can now paste to share.', 'info');
    }
}

document.addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveAsHTML();
    }
    if (e.ctrlKey && e.key === 'p') {
        e.preventDefault();
        window.print();
    }
});

console.log('Result page loaded - Report generation ready');