// Profile Page JavaScript - Complete Working Version

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

// Upload profile photo
function uploadProfilePhoto(file) {
    if (!file) {
        showToast('Please select a photo', 'error');
        return;
    }

    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showToast('Invalid file type. Please upload JPEG, PNG, GIF, or WEBP.', 'error');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showToast('File too large. Maximum size is 5MB.', 'error');
        return;
    }

    // Show preview immediately
    const reader = new FileReader();
    reader.onload = function (e) {
        const profileImage = document.getElementById('profileImage');
        const defaultAvatar = document.getElementById('defaultAvatar');

        if (profileImage) {
            profileImage.src = e.target.result;
            profileImage.style.display = 'block';
            if (defaultAvatar) defaultAvatar.style.display = 'none';
        } else {
            const wrapper = document.getElementById('profileImageWrapper');
            if (wrapper) {
                wrapper.innerHTML = `<img id="profileImage" class="profile-image" style="width:150px;height:150px;border-radius:50%;object-fit:cover;border:3px solid #28a745;" src="${e.target.result}">`;
            }
        }
    };
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('profile_photo', file);

    showToast('Uploading photo...', 'info');

    fetch('/upload-profile-photo', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log('Upload response:', data);

            if (data.success && data.filename) {
                showToast('Photo uploaded! Refreshing page...', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showToast(data.message || 'Upload failed', 'error');
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            showToast('Error uploading photo. Please try again.', 'error');
        });
}

// Delete profile photo
function deleteProfilePhoto() {
    if (confirm('Are you sure you want to remove your profile photo?')) {
        showToast('Removing photo...', 'info');

        fetch('/delete-profile-photo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Photo removed! Refreshing...', 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showToast(data.message || 'Error removing photo', 'error');
                }
            })
            .catch(error => {
                console.error('Delete error:', error);
                showToast('Error removing photo. Please try again.', 'error');
            });
    }
}

// Password strength checker
function checkPasswordStrength() {
    const password = document.getElementById('new_password');
    if (!password) return;

    const strengthDiv = document.getElementById('passwordStrength');
    if (!strengthDiv) return;

    const value = password.value;

    if (value.length === 0) {
        strengthDiv.innerHTML = '';
        strengthDiv.className = 'password-strength';
        return;
    }

    let strength = 0;
    if (value.length >= 8) strength++;
    if (value.match(/[a-z]+/)) strength++;
    if (value.match(/[A-Z]+/)) strength++;
    if (value.match(/[0-9]+/)) strength++;
    if (value.match(/[!@#$%^&*(),.?":{}|<>]+/)) strength++;

    let strengthText = '';
    let strengthClass = '';

    if (strength <= 2) {
        strengthText = '⚠️ Weak password';
        strengthClass = 'weak';
    } else if (strength <= 4) {
        strengthText = '📈 Medium password';
        strengthClass = 'medium';
    } else {
        strengthText = '✓ Strong password';
        strengthClass = 'strong';
    }

    strengthDiv.innerHTML = strengthText;
    strengthDiv.className = `password-strength ${strengthClass}`;
}

// Check password match
function checkPasswordMatch() {
    const password = document.getElementById('new_password');
    const confirm = document.getElementById('confirm_password');
    const matchDiv = document.getElementById('passwordMatch');

    if (!password || !confirm || !matchDiv) return;

    if (confirm.value.length === 0) {
        matchDiv.innerHTML = '';
        matchDiv.className = 'password-match';
        return;
    }

    if (password.value === confirm.value) {
        matchDiv.innerHTML = '✓ Passwords match';
        matchDiv.className = 'password-match match';
    } else {
        matchDiv.innerHTML = '✗ Passwords do not match';
        matchDiv.className = 'password-match no-match';
    }
}

// Change password
function changePassword() {
    const currentPassword = document.getElementById('current_password');
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');

    if (!currentPassword || !newPassword || !confirmPassword) return;

    if (!currentPassword.value || !newPassword.value || !confirmPassword.value) {
        showToast('Please fill in all password fields', 'error');
        return;
    }

    if (newPassword.value !== confirmPassword.value) {
        showToast('New passwords do not match', 'error');
        return;
    }

    if (newPassword.value.length < 4) {
        showToast('New password must be at least 4 characters long', 'error');
        return;
    }

    showToast('Updating password...', 'info');

    fetch('/api/change-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            current_password: currentPassword.value,
            new_password: newPassword.value
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                currentPassword.value = '';
                newPassword.value = '';
                confirmPassword.value = '';

                const strengthDiv = document.getElementById('passwordStrength');
                const matchDiv = document.getElementById('passwordMatch');
                if (strengthDiv) strengthDiv.innerHTML = '';
                if (matchDiv) matchDiv.innerHTML = '';
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Password error:', error);
            showToast('Error changing password. Please try again.', 'error');
        });
}

// Initialize everything
document.addEventListener('DOMContentLoaded', function () {
    console.log('Profile page initializing...');

    // Profile photo input
    const photoInput = document.getElementById('profilePhotoInput');
    if (photoInput) {
        // Clone to remove existing listeners
        const newInput = photoInput.cloneNode(true);
        photoInput.parentNode.replaceChild(newInput, photoInput);

        newInput.addEventListener('change', function (e) {
            if (this.files && this.files[0]) {
                console.log('File selected for upload:', this.files[0].name);
                uploadProfilePhoto(this.files[0]);
            }
            this.value = '';
        });
        console.log('Photo input ready');
    }

    // Password strength
    const newPassword = document.getElementById('new_password');
    if (newPassword) {
        newPassword.addEventListener('input', checkPasswordStrength);
        console.log('Password strength ready');
    }

    // Password match
    const confirmPassword = document.getElementById('confirm_password');
    if (confirmPassword) {
        confirmPassword.addEventListener('input', checkPasswordMatch);
        console.log('Password match ready');
    }

    // Profile form
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function () {
            showToast('Updating profile...', 'info');
        });
        console.log('Profile form ready');
    }

    console.log('Profile page ready');
});