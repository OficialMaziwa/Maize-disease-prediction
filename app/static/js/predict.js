let currentImageData = null;
let stream = null;
let cameraMode = 'environment';
let isAnalyzing = false;
let predictAction = null;
let predictButton = null;
let currentLang = 'en';


function showPredictButton() {
    if (predictAction) {
        predictAction.style.display = 'block';
    }
}

function hidePredictButton() {
    if (predictAction) {
        predictAction.style.display = 'none';
    }
}

function setPredictButtonText(mode) {
    if (!predictButton) {
        predictButton = document.getElementById('predictButton');
    }
    const predictHint = document.getElementById('predictHint');
    if (!predictButton || !predictHint) return;

    if (mode === 'camera') {
        predictButton.innerHTML = '<i class="fas fa-play me-2"></i> Predict Captured Photo';
        predictHint.textContent = currentLang === 'sw'
            ? 'Bonyeza Predict ili kuchambua picha uliyopiga.'
            : 'Tap Predict to analyze the photo you captured.';
    } else if (mode === 'upload') {
        predictButton.innerHTML = '<i class="fas fa-play me-2"></i> Predict Uploaded Image';
        predictHint.textContent = currentLang === 'sw'
            ? 'Bonyeza Predict ili kuchambua picha uliyochagua.'
            : 'Tap Predict to analyze the image you selected.';
    } else {
        const predictText = currentLang === 'sw' ? 'Utabiri' : 'Predict';
        predictButton.innerHTML = `<i class="fas fa-play me-2"></i> ${predictText}`;
        predictHint.textContent = currentLang === 'sw'
            ? 'Chagua au piga picha kwanza, kisha bonyeza Utabiri.'
            : 'Select or capture an image first, then tap Predict.';
    }
}


document.addEventListener('DOMContentLoaded', function () {
    currentLang = document.documentElement.lang || 'en';

    predictButton = document.getElementById('predictButton');
    predictAction = document.getElementById('predictAction');

    initFileUpload();
    initCameraTab();
    initPredictButton();
    initResetButtons();
    createVerificationElements();
});


function initFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const rejectMessage = document.getElementById('rejectMessage');
    const rejectText = document.getElementById('rejectText');
    const chooseFileButton = document.getElementById('chooseFileButton');

    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                processImageFile(file, previewImg, imagePreview, uploadArea, rejectMessage, rejectText);
            }
        });
    }

    if (uploadArea) {
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
            if (file) {
                processImageFile(file, previewImg, imagePreview, uploadArea, rejectMessage, rejectText);
                if (fileInput) {
                    fileInput.files = e.dataTransfer.files;
                }
            }
        });

        uploadArea.addEventListener('click', function () {
            if (fileInput) {
                fileInput.click();
            }
        });
    }

    if (chooseFileButton) {
        chooseFileButton.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (fileInput) {
                fileInput.click();
            }
        });
    }
}

function initCameraTab() {
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
}

function setCameraMode(mode) {
    cameraMode = mode;
    const backBtn = document.getElementById('backCameraBtn');
    const frontBtn = document.getElementById('frontCameraBtn');
    if (backBtn) {
        backBtn.className = 'btn btn-sm btn-outline-primary' + (mode === 'environment' ? ' active' : '');
    }
    if (frontBtn) {
        frontBtn.className = 'btn btn-sm btn-outline-secondary' + (mode === 'user' ? ' active' : '');
    }
    const cameraTab = document.getElementById('camera-tab');
    if (cameraTab && cameraTab.classList.contains('active')) {
        initCamera(mode);
    }
}

async function initCamera(mode) {
    const video = document.getElementById('video');
    const cameraPreview = document.getElementById('cameraPreview');
    const cameraRejectMessage = document.getElementById('cameraRejectMessage');
    const cameraRejectText = document.getElementById('cameraRejectText');

    try {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: mode === 'user' ? 'user' : 'environment',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });

        if (video) {
            video.srcObject = stream;
            video.style.display = 'block';
        }
        if (cameraPreview) {
            cameraPreview.style.display = 'none';
        }
        if (cameraRejectMessage) {
            cameraRejectMessage.style.display = 'none';
        }

        const captureBtn = document.getElementById('captureBtn');
        if (captureBtn) {
            captureBtn.style.display = 'flex';
            captureBtn.onclick = capturePhoto;
        }
    } catch (err) {
        console.error('Camera error:', err);
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (video) {
                video.srcObject = stream;
                video.style.display = 'block';
            }
            if (cameraRejectMessage) {
                cameraRejectMessage.style.display = 'none';
            }
            const captureBtn = document.getElementById('captureBtn');
            if (captureBtn) {
                captureBtn.style.display = 'flex';
                captureBtn.onclick = capturePhoto;
            }
        } catch (err2) {
            console.error('Camera fallback error:', err2);
            if (cameraRejectText) {
                cameraRejectText.textContent = currentLang === 'sw'
                    ? 'Imeshindwa kufungua kamera. Tafadhali hakikisha umeipa ruhusa.'
                    : 'Unable to access camera. Please check permissions.';
            }
            if (cameraRejectMessage) {
                cameraRejectMessage.style.display = 'flex';
            }
        }
    }
}

function capturePhoto() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const cameraPreview = document.getElementById('cameraPreview');
    const cameraPreviewImg = document.getElementById('cameraPreviewImg');
    const captureBtn = document.getElementById('captureBtn');

    if (video && canvas) {
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL('image/jpeg', 0.9);
        if (cameraPreviewImg) {
            cameraPreviewImg.src = imageData;
        }
        if (cameraPreview) {
            cameraPreview.style.display = 'block';
        }

        const cameraContainer = document.querySelector('.camera-container');
        if (cameraContainer) {
            cameraContainer.style.display = 'none';
        }
        if (captureBtn) {
            captureBtn.style.display = 'none';
        }

        currentImageData = imageData;
        window.currentImageData = imageData;
        setPredictButtonText('camera');
        showPredictButton();

        stopCamera();
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

function initPredictButton() {
    predictAction = document.getElementById('predictAction');
    predictButton = document.getElementById('predictButton');

    if (predictButton) {
        predictButton.addEventListener('click', function () {
            if (!currentImageData) {
                const msg = currentLang === 'sw'
                    ? 'Tafadhali chagua au piga picha kabla ya utabiri.'
                    : 'Please select or capture an image before prediction.';
                showToast(msg, 'warning');
                return;
            }
            analyzeImage(currentImageData);
        });
    }
}


function processImageFile(file, previewImg, imagePreview, uploadArea, rejectMessage, rejectText) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif', 'image/bmp', 'image/tiff', 'image/heic', 'image/heif'];
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tif', 'tiff', 'heic', 'heif'];
    const extension = file.name.includes('.') ? file.name.split('.').pop().toLowerCase() : '';

    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(extension)) {
        if (rejectText) {
            rejectText.textContent = currentLang === 'sw'
                ? 'Tafadhali pakia picha halali kutoka kwenye simu au kompyuta yako'
                : 'Please upload a valid image file from your phone or computer';
        }
        if (rejectMessage) {
            rejectMessage.style.display = 'flex';
        }
        return;
    }

    if (file.size > 50 * 1024 * 1024) {
        if (rejectText) {
            rejectText.textContent = currentLang === 'sw'
                ? 'Faili kubwa sana. Ukubwa wa juu ni 50MB'
                : 'File too large. Maximum size is 50MB';
        }
        if (rejectMessage) {
            rejectMessage.style.display = 'flex';
        }
        return;
    }

    if (rejectMessage) {
        rejectMessage.style.display = 'none';
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        if (previewImg) {
            previewImg.src = e.target.result;
        }
        if (imagePreview) {
            imagePreview.style.display = 'block';
        }
        if (uploadArea) {
            uploadArea.style.display = 'none';
        }

        currentImageData = e.target.result;
        window.currentImageData = currentImageData;
        setPredictButtonText('upload');
        showPredictButton();

        const maizeVerification = document.getElementById('maizeVerification');
        if (maizeVerification) {
            maizeVerification.style.display = 'none';
        }
    };
    reader.readAsDataURL(file);
}

function analyzeImage(imageData) {
    if (isAnalyzing) return;
    isAnalyzing = true;

    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const maizeVerification = document.getElementById('maizeVerification');

    if (loading) loading.style.display = 'block';
    if (results) results.style.display = 'none';
    if (maizeVerification) maizeVerification.style.display = 'none';

    const apiUrl = window.apiPredictUrl || '/api/predict';

    console.log('🌽 Starting prediction...');

    fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                let message = 'Prediction failed. Please try again.';
                try {
                    const errorData = JSON.parse(text);
                    message = errorData.error || errorData.message || message;
                } catch (e) {
                    if (response.status === 413) {
                        message = currentLang === 'sw'
                            ? 'Picha kubwa sana. Tafadhali chagua picha ndogo.'
                            : 'Image is too large. Please choose a smaller image.';
                    } else if (response.status >= 500) {
                        message = currentLang === 'sw'
                            ? 'Hitilafu ya seva. Tafadhali jaribu tena.'
                            : 'Server error. Please try again.';
                    }
                }
                throw new Error(message);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('✅ Prediction response:', data);
        if (loading) loading.style.display = 'none';

        if (data.is_maize_leaf === false) {
            isAnalyzing = false;
            showMaizeLeafError(data);
            return;
        }

        if (data.success) {
            showMaizeVerification(true, data.leaf_confidence);
            displayResults(data);
            if (results) results.style.display = 'block';
            hidePredictButton();
        } else {
            isAnalyzing = false;
            const errorMsg = data.error || (currentLang === 'sw'
                ? 'Utabiri umeshindwa. Tafadhali jaribu tena.'
                : 'Prediction failed. Please try again.');
            showToast(errorMsg, 'error');
        }
    })
    .catch(error => {
        console.error('❌ Prediction error:', error);
        isAnalyzing = false;
        if (loading) loading.style.display = 'none';
        showToast(error.message || (currentLang === 'sw'
            ? 'Hitilafu ya kuunganisha. Tafadhali jaribu tena.'
            : 'Connection error. Please try again.'), 'error');
    });
}


function createVerificationElements() {
    if (document.getElementById('maizeVerification')) return;

    const results = document.getElementById('results');
    if (!results) return;

    const container = document.createElement('div');
    container.id = 'maizeVerification';
    container.className = 'mt-3';
    container.style.display = 'none';
    container.innerHTML = `<div id="verificationStatus" class="alert"></div>`;

    results.parentNode.insertBefore(container, results);
}

function showMaizeVerification(isMaize, confidence) {
    const maizeVerification = document.getElementById('maizeVerification');
    const verificationStatus = document.getElementById('verificationStatus');

    if (!maizeVerification || !verificationStatus) {
        createVerificationElements();
        return showMaizeVerification(isMaize, confidence);
    }

    maizeVerification.style.display = 'block';

    if (isMaize) {
        const message = currentLang === 'sw'
            ? '✅ Jani la mahindi limegunduliwa'
            : '✅ Maize leaf detected';
        verificationStatus.className = 'alert alert-success';
        verificationStatus.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <span class="badge bg-success ms-2">${Math.round(confidence || 0)}%</span>
        `;
    } else {
        const message = currentLang === 'sw'
            ? '❌ Picha hii sio ya jani la mahindi'
            : '❌ This image is not a maize leaf';
        verificationStatus.className = 'alert alert-danger';
        verificationStatus.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            ${message}
            <span class="badge bg-danger ms-2">${Math.round(confidence || 0)}%</span>
        `;
    }
}

function showMaizeLeafError(data) {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const maizeVerification = document.getElementById('maizeVerification');
    const verificationStatus = document.getElementById('verificationStatus');

    if (loading) loading.style.display = 'none';
    if (results) results.style.display = 'none';

    if (!maizeVerification || !verificationStatus) {
        createVerificationElements();
        return showMaizeLeafError(data);
    }

    maizeVerification.style.display = 'block';

    const confidence = data.leaf_confidence || 0;
    const errorMsg = data.error || (currentLang === 'sw'
        ? 'Tafadhali pakia picha ya jani la mahindi iliyo wazi.'
        : 'Please upload a clear image of a maize leaf.');

    verificationStatus.className = 'alert alert-danger';
    verificationStatus.innerHTML = `
        <div class="d-flex align-items-start">
            <i class="fas fa-exclamation-triangle me-3 mt-1" style="font-size: 24px;"></i>
            <div>
                <h6 class="mb-1">${currentLang === 'sw' ? 'Jani la Mahindi Halijagunduliwa' : 'Maize Leaf Not Detected'}</h6>
                <p class="mb-1">${errorMsg}</p>
                <p class="mb-0 small text-muted">
                    ${currentLang === 'sw' ? 'Uhakika:' : 'Confidence:'} ${Math.round(confidence)}%
                </p>
                <button class="btn btn-sm btn-outline-primary mt-2" onclick="resetAndRetry()">
                    <i class="fas fa-redo me-1"></i>
                    ${currentLang === 'sw' ? 'Jaribu Tena' : 'Try Again'}
                </button>
            </div>
        </div>
    `;

    hidePredictButton();
}

function resetAndRetry() {
    resetAll();
    const uploadTab = document.getElementById('upload-tab');
    if (uploadTab) {
        const bsTab = new bootstrap.Tab(uploadTab);
        bsTab.show();
    }
    const msg = currentLang === 'sw'
        ? 'Tafadhali chagua picha nyingine ya jani la mahindi'
        : 'Please select another maize leaf image';
    showToast(msg, 'info');
}


function displayResults(data) {
    const diseaseName = document.getElementById('diseaseName');
    if (diseaseName) {
        diseaseName.innerHTML = `<span class="badge bg-success fs-4">${data.disease || 'Unknown'}</span>`;
    }

    const confidence = Math.round(data.confidence || 0);
    const confidenceBar = document.getElementById('confidenceBar');
    const confidenceText = document.getElementById('confidenceText');

    if (confidenceBar) {
        confidenceBar.style.width = `${confidence}%`;
        confidenceBar.className = `progress-bar ${confidence >= 70 ? 'bg-success' : confidence >= 50 ? 'bg-warning' : 'bg-danger'}`;
    }
    if (confidenceText) {
        confidenceText.innerHTML = `${confidence}%`;
    }

    const description = document.getElementById('description');
    if (description) {
        description.innerHTML = data.description || 'No description available.';
    }

    const symptoms = document.getElementById('symptoms');
    if (symptoms) {
        symptoms.innerHTML = (data.symptoms || 'No symptoms information available.').replace(/\n/g, '<br>');
    }

    const organicList = document.getElementById('organicList');
    if (organicList) {
        organicList.innerHTML = '';
        if (data.organic_treatment && data.organic_treatment.length) {
            data.organic_treatment.forEach(item => {
                const li = document.createElement('li');
                li.className = 'mb-2';
                li.innerHTML = `<i class="fas fa-check-circle text-success me-2"></i> ${item}`;
                organicList.appendChild(li);
            });
        } else {
            organicList.innerHTML = '<li class="text-muted">No organic treatment information available.</li>';
        }
    }

    const chemicalList = document.getElementById('chemicalList');
    if (chemicalList) {
        chemicalList.innerHTML = '';
        if (data.chemical_treatment && data.chemical_treatment.length) {
            data.chemical_treatment.forEach(item => {
                const li = document.createElement('li');
                li.className = 'mb-2';
                li.innerHTML = `<i class="fas fa-flask text-warning me-2"></i> ${item}`;
                chemicalList.appendChild(li);
            });
        } else {
            chemicalList.innerHTML = '<li class="text-muted">No chemical treatment information available.</li>';
        }
    }

    const culturalList = document.getElementById('culturalList');
    if (culturalList) {
        culturalList.innerHTML = '';
        if (data.cultural_practices && data.cultural_practices.length) {
            data.cultural_practices.forEach(item => {
                const li = document.createElement('li');
                li.className = 'mb-2';
                li.innerHTML = `<i class="fas fa-tractor text-info me-2"></i> ${item}`;
                culturalList.appendChild(li);
            });
        } else {
            culturalList.innerHTML = '<li class="text-muted">No cultural practices information available.</li>';
        }
    }

    const actionPlan = document.getElementById('actionPlan');
    if (actionPlan) {
        actionPlan.innerHTML = '';
        if (data.action_plan && data.action_plan.length) {
            data.action_plan.forEach(item => {
                const li = document.createElement('li');
                li.className = 'mb-2';
                li.innerHTML = `<i class="fas fa-list-check text-primary me-2"></i> ${item}`;
                actionPlan.appendChild(li);
            });
        } else {
            actionPlan.innerHTML = '<li class="text-muted">No action plan available.</li>';
        }
    }

    const results = document.getElementById('results');
    if (results) {
        results.style.display = 'block';
    }
}


function initResetButtons() {
}

function resetUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const fileInput = document.getElementById('fileInput');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');
    const maizeVerification = document.getElementById('maizeVerification');

    if (uploadArea) uploadArea.style.display = 'block';
    if (imagePreview) imagePreview.style.display = 'none';
    if (fileInput) fileInput.value = '';
    if (results) results.style.display = 'none';
    if (loading) loading.style.display = 'none';
    if (maizeVerification) maizeVerification.style.display = 'none';

    currentImageData = null;
    window.currentImageData = null;
    isAnalyzing = false;
    hidePredictButton();
}

function resetCamera() {
    const cameraPreview = document.getElementById('cameraPreview');
    const cameraContainer = document.querySelector('.camera-container');
    const captureBtn = document.getElementById('captureBtn');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');
    const maizeVerification = document.getElementById('maizeVerification');

    if (cameraPreview) cameraPreview.style.display = 'none';
    if (cameraContainer) cameraContainer.style.display = 'block';
    if (captureBtn) captureBtn.style.display = 'flex';
    if (results) results.style.display = 'none';
    if (loading) loading.style.display = 'none';
    if (maizeVerification) maizeVerification.style.display = 'none';

    currentImageData = null;
    window.currentImageData = null;
    isAnalyzing = false;
    hidePredictButton();

    initCamera(cameraMode);
}

function resetAll() {
    resetUpload();
    resetCamera();

    const uploadTab = document.getElementById('upload-tab');
    if (uploadTab) {
        const bsTab = new bootstrap.Tab(uploadTab);
        bsTab.show();
    }
}

function showToast(message, type = 'info') {
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

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

const predictStyleSheet = document.createElement('style');
predictStyleSheet.textContent = `
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
`;
document.head.appendChild(predictStyleSheet);

window.setCameraMode = setCameraMode;
window.capturePhoto = capturePhoto;
window.resetUpload = resetUpload;
window.resetCamera = resetCamera;
window.resetAll = resetAll;
window.resetAndRetry = resetAndRetry;
window.showToast = showToast;

console.log('✅ predict.js loaded successfully');