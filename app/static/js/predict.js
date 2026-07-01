// Predict Page JavaScript - With Language Support

let currentImageData = null;
let stream = null;
let cameraMode = 'environment'; // default: back camera

// Initialize camera when camera tab is shown
document.addEventListener('DOMContentLoaded', function () {
    // Get current language from HTML
    const langSelector = document.getElementById('languageSelector');
    if (langSelector) {
        currentLang = langSelector.value;
    }

    // File upload handling
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const rejectMessage = document.getElementById('rejectMessage');
    const rejectText = document.getElementById('rejectText');

    // File input change
    fileInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
            processImageFile(file, previewImg, imagePreview, uploadArea, rejectMessage, rejectText);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#28a745';
        uploadArea.style.background = '#f0fff4';
    });

    uploadArea.addEventListener('dragleave', function (e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#dee2e6';
        uploadArea.style.background = '';
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#dee2e6';
        uploadArea.style.background = '';

        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            processImageFile(file, previewImg, imagePreview, uploadArea, rejectMessage, rejectText);
            fileInput.files = e.dataTransfer.files;
        }
    });

    uploadArea.addEventListener('click', function () {
        fileInput.click();
    });

    // Initialize camera tab
    const cameraTab = document.getElementById('camera-tab');
    if (cameraTab) {
        cameraTab.addEventListener('shown.bs.tab', function () {
            initCamera(cameraMode);
        });
    }

    const uploadTab = document.getElementById('upload-tab');
    if (uploadTab) {
        uploadTab.addEventListener('shown.bs.tab', function () {
            stopCamera();
        });
    }
});

// Set camera mode (front/back)
function setCameraMode(mode) {
    cameraMode = mode;
    // Update button styles
    document.getElementById('backCameraBtn').className = 'btn btn-sm btn-outline-primary' + (mode === 'environment' ? ' active' : '');
    document.getElementById('frontCameraBtn').className = 'btn btn-sm btn-outline-secondary' + (mode === 'user' ? ' active' : '');
    // Reinitialize camera with new mode
    if (document.getElementById('camera-tab').classList.contains('active')) {
        initCamera(mode);
    }
}

// Process image file - UPLOAD MARA MOJA
function processImageFile(file, previewImg, imagePreview, uploadArea, rejectMessage, rejectText) {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        rejectText.textContent = 'Please upload a valid image file (JPEG, PNG, or WEBP)';
        rejectMessage.style.display = 'flex';
        return;
    }

    // Validate file size (max 50MB for mobile)
    if (file.size > 50 * 1024 * 1024) {
        rejectText.textContent = 'File too large. Maximum size is 50MB';
        rejectMessage.style.display = 'flex';
        return;
    }

    rejectMessage.style.display = 'none';

    const reader = new FileReader();
    reader.onload = function (e) {
        previewImg.src = e.target.result;
        imagePreview.style.display = 'block';
        uploadArea.style.display = 'none';

        // Store image data for prediction
        currentImageData = e.target.result;

        // ANALYZE IMMEDIATELY - NO SECOND UPLOAD
        analyzeImage(currentImageData);
    };
    reader.readAsDataURL(file);
}

// Initialize camera
async function initCamera(mode) {
    const video = document.getElementById('video');
    const cameraPreview = document.getElementById('cameraPreview');
    const cameraRejectMessage = document.getElementById('cameraRejectMessage');

    try {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: { exact: mode } }
        });
        video.srcObject = stream;
        video.style.display = 'block';
        cameraPreview.style.display = 'none';
        cameraRejectMessage.style.display = 'none';

        // Setup capture button
        const captureBtn = document.getElementById('captureBtn');
        captureBtn.style.display = 'flex';
        captureBtn.onclick = capturePhoto;
    } catch (err) {
        console.error('Camera error:', err);
        // Fallback: try any camera
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.style.display = 'block';
            cameraRejectMessage.style.display = 'none';
            const captureBtn = document.getElementById('captureBtn');
            captureBtn.style.display = 'flex';
            captureBtn.onclick = capturePhoto;
        } catch (err2) {
            const cameraRejectText = document.getElementById('cameraRejectText');
            cameraRejectText.textContent = 'Unable to access camera. Please check permissions.';
            cameraRejectMessage.style.display = 'flex';
        }
    }
}

// Capture photo from camera
function capturePhoto() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const cameraPreview = document.getElementById('cameraPreview');
    const cameraPreviewImg = document.getElementById('cameraPreviewImg');
    const cameraContainer = document.querySelector('.camera-container');
    const captureBtn = document.getElementById('captureBtn');

    if (video && canvas) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Get image data
        const imageData = canvas.toDataURL('image/jpeg', 0.9);
        cameraPreviewImg.src = imageData;
        cameraPreview.style.display = 'block';
        cameraContainer.style.display = 'none';
        captureBtn.style.display = 'none';

        // Store for prediction
        currentImageData = imageData;

        // Stop camera stream
        stopCamera();

        // ANALYZE IMMEDIATELY - NO SECOND UPLOAD
        analyzeImage(currentImageData);
    }
}

// Stop camera
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

// Reset upload
function resetUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const fileInput = document.getElementById('fileInput');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');

    uploadArea.style.display = 'block';
    imagePreview.style.display = 'none';
    fileInput.value = '';
    currentImageData = null;
    results.style.display = 'none';
    loading.style.display = 'none';
}

// Reset camera
function resetCamera() {
    const cameraPreview = document.getElementById('cameraPreview');
    const cameraContainer = document.querySelector('.camera-container');
    const captureBtn = document.getElementById('captureBtn');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');

    cameraPreview.style.display = 'none';
    cameraContainer.style.display = 'block';
    captureBtn.style.display = 'flex';
    currentImageData = null;
    results.style.display = 'none';
    loading.style.display = 'none';

    // Reinitialize camera
    initCamera(cameraMode);
}

// Reset all
function resetAll() {
    resetUpload();
    resetCamera();

    // Also reset the active tab to upload
    const uploadTab = document.getElementById('upload-tab');
    if (uploadTab) {
        const bsTab = new bootstrap.Tab(uploadTab);
        bsTab.show();
    }
}

// Analyze image - UPLOAD MARA MOJA - REDIRECT TO RESULT PAGE
function analyzeImage(imageData) {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');

    // Show loading, hide results
    loading.style.display = 'block';
    results.style.display = 'none';

    // Get current language from selector
    const langSelector = document.getElementById('languageSelector');
    const currentLang = langSelector ? langSelector.value : 'en';

    // Prepare request
    fetch('/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image: imageData,
            language: currentLang
        })
    })
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';

            if (data.success) {
                // Redirect to result page with data
                const params = new URLSearchParams({
                    disease: data.disease,
                    confidence: data.confidence,
                    description: data.description,
                    symptoms: data.symptoms,
                    treatment: data.treatment,
                    organic: JSON.stringify(data.organic_treatment),
                    chemical: JSON.stringify(data.chemical_treatment),
                    cultural: JSON.stringify(data.cultural_practices),
                    action: JSON.stringify(data.action_plan)
                });
                window.location.href = `/result?${params.toString()}`;
            } else {
                showToast(data.error || 'Prediction failed. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loading.style.display = 'none';
            showToast('Error connecting to server. Please try again.', 'error');
        });
}

// Display results (kept for backward compatibility)
function displayResults(data) {
    // Disease name and confidence
    document.getElementById('diseaseName').innerHTML = `<span class="badge bg-success fs-4">${data.disease}</span>`;

    const confidence = Math.round(data.confidence);
    document.getElementById('confidenceBar').style.width = `${confidence}%`;
    document.getElementById('confidenceText').innerHTML = `${confidence}%`;

    // Set confidence bar color
    const confidenceBar = document.getElementById('confidenceBar');
    if (confidence >= 70) {
        confidenceBar.className = 'progress-bar bg-success';
    } else if (confidence >= 50) {
        confidenceBar.className = 'progress-bar bg-warning';
    } else {
        confidenceBar.className = 'progress-bar bg-danger';
    }

    // Description
    document.getElementById('description').innerHTML = data.description || 'No description available.';

    // Symptoms - convert newlines to HTML
    const symptoms = data.symptoms || 'No symptoms information available.';
    document.getElementById('symptoms').innerHTML = symptoms.replace(/\n/g, '<br>');

    // Organic treatment list
    const organicList = document.getElementById('organicList');
    organicList.innerHTML = '';
    if (data.organic_treatment && data.organic_treatment.length) {
        data.organic_treatment.forEach(item => {
            const li = document.createElement('li');
            li.className = 'mb-2';
            li.innerHTML = item;
            organicList.appendChild(li);
        });
    } else {
        organicList.innerHTML = '<li class="text-muted">No organic treatment information available.</li>';
    }

    // Chemical treatment list
    const chemicalList = document.getElementById('chemicalList');
    chemicalList.innerHTML = '';
    if (data.chemical_treatment && data.chemical_treatment.length) {
        data.chemical_treatment.forEach(item => {
            const li = document.createElement('li');
            li.className = 'mb-2';
            li.innerHTML = item;
            chemicalList.appendChild(li);
        });
    } else {
        chemicalList.innerHTML = '<li class="text-muted">No chemical treatment information available.</li>';
    }

    // Cultural practices list
    const culturalList = document.getElementById('culturalList');
    culturalList.innerHTML = '';
    if (data.cultural_practices && data.cultural_practices.length) {
        data.cultural_practices.forEach(item => {
            const li = document.createElement('li');
            li.className = 'mb-2';
            li.innerHTML = item;
            culturalList.appendChild(li);
        });
    } else {
        culturalList.innerHTML = '<li class="text-muted">No cultural practices information available.</li>';
    }

    // Action plan list
    const actionPlan = document.getElementById('actionPlan');
    actionPlan.innerHTML = '';
    if (data.action_plan && data.action_plan.length) {
        data.action_plan.forEach(item => {
            const li = document.createElement('li');
            li.className = 'mb-2';
            li.innerHTML = item;
            actionPlan.appendChild(li);
        });
    } else {
        actionPlan.innerHTML = '<li class="text-muted">No action plan available.</li>';
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;

    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-check-circle';
    if (type === 'error') icon = 'fa-exclamation-circle';

    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <div class="message">${escapeHtml(message)}</div>
        <i class="fas fa-times close-toast"></i>
    `;

    document.body.appendChild(toast);

    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '280px';
    toast.style.background = 'white';
    toast.style.borderRadius = '10px';
    toast.style.padding = '15px 20px';
    toast.style.boxShadow = '0 5px 20px rgba(0,0,0,0.15)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.gap = '12px';
    toast.style.borderLeft = `4px solid ${type === 'success' ? '#28a745' : (type === 'error' ? '#dc3545' : '#17a2b8')}`;

    toast.querySelector('.close-toast').addEventListener('click', () => {
        toast.remove();
    });

    setTimeout(() => {
        if (toast && toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}