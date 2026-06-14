// ==================== AUTHENTICATION JAVASCRIPT ====================

// Initialize all auth functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initPasswordToggle();
    initPasswordStrength();
    initPasswordMatch();
    initRoleChange();
});

// ==================== PASSWORD TOGGLE (EYE ICON) ====================
function initPasswordToggle() {
    const toggleButtons = document.querySelectorAll('.toggle-password');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);

            if (input) {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);

                // Toggle eye icon
                const icon = this.querySelector('i');
                if (icon) {
                    icon.classList.toggle('fa-eye');
                    icon.classList.toggle('fa-eye-slash');
                }
            }
        });
    });
}

// ==================== PASSWORD STRENGTH CHECKER ====================
function initPasswordStrength() {
    const passwordInput = document.getElementById('password');

    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            const password = this.value;
            const strengthDiv = document.getElementById('passwordStrength');

            if (!strengthDiv) return;

            if (password.length === 0) {
                strengthDiv.innerHTML = '';
                strengthDiv.className = 'password-strength';
                return;
            }

            // Calculate password strength
            let strength = 0;
            let strengthText = '';
            let strengthClass = '';

            if (password.length >= 8) strength++;
            if (password.length >= 12) strength++;
            if (password.match(/[a-z]+/)) strength++;
            if (password.match(/[A-Z]+/)) strength++;
            if (password.match(/[0-9]+/)) strength++;
            if (password.match(/[!@#$%^&*(),.?":{}|<>]+/)) strength++;

            if (strength <= 2) {
                strengthText = '⚠️ Very Weak Password';
                strengthClass = 'weak';
            } else if (strength <= 4) {
                strengthText = '⚠️ Weak Password';
                strengthClass = 'weak';
            } else if (strength <= 5) {
                strengthText = '📈 Medium Password';
                strengthClass = 'medium';
            } else {
                strengthText = '✓ Strong Password';
                strengthClass = 'strong';
            }

            strengthDiv.innerHTML = strengthText;
            strengthDiv.className = 'password-strength ' + strengthClass;
        });
    }
}

// ==================== PASSWORD MATCH CHECKER ====================
function initPasswordMatch() {
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');

    if (confirmInput) {
        confirmInput.addEventListener('input', function () {
            const password = passwordInput ? passwordInput.value : '';
            const confirm = this.value;
            const matchDiv = document.getElementById('passwordMatch');

            if (!matchDiv) return;

            if (confirm.length === 0) {
                matchDiv.innerHTML = '';
                matchDiv.className = 'password-match';
                return;
            }

            if (password === confirm) {
                matchDiv.innerHTML = '✓ Passwords match';
                matchDiv.className = 'password-match success';
                this.setAttribute('data-match', 'true');
            } else {
                matchDiv.innerHTML = '✗ Passwords do not match';
                matchDiv.className = 'password-match error';
                this.setAttribute('data-match', 'false');
            }
        });
    }
}

// ==================== ROLE CHANGE HANDLER ====================
function initRoleChange() {
    const roleSelect = document.getElementById('role');
    const roleInfoText = document.getElementById('roleInfoText');

    if (roleSelect && roleInfoText) {
        roleSelect.addEventListener('change', function () {
            if (this.value === 'extension_officer') {
                roleInfoText.innerHTML = 'Extension officers need admin approval before accessing the system. Your account will be reviewed by an administrator.';
            } else {
                roleInfoText.innerHTML = 'Farmers get immediate access to disease detection and prediction features.';
            }
        });
    }
}

function showConfirmation() {
    // Get all form values
    const fullName = document.getElementById('full_name')?.value || '-';
    const phoneNumber = document.getElementById('phone_number')?.value || '-';
    const email = document.getElementById('email')?.value || '-';

    // Get location values from dropdowns
    const regionSelect = document.getElementById('region');
    const districtSelect = document.getElementById('district');
    const wardSelect = document.getElementById('ward');
    const street = document.getElementById('street')?.value || '';

    const region = regionSelect ? regionSelect.options[regionSelect.selectedIndex]?.text || '' : '';
    const district = districtSelect ? districtSelect.options[districtSelect.selectedIndex]?.text || '' : '';
    const ward = wardSelect ? wardSelect.options[wardSelect.selectedIndex]?.text || '' : '';

    const roleSelect = document.getElementById('role');
    const roleText = roleSelect ? roleSelect.options[roleSelect.selectedIndex]?.text || '-' : '-';
    const roleValue = roleSelect ? roleSelect.value : '';

    // Set confirmation modal values
    const confirmFullName = document.getElementById('confirm_full_name');
    const confirmPhone = document.getElementById('confirm_phone_number');
    const confirmEmail = document.getElementById('confirm_email');
    const confirmRegion = document.getElementById('confirm_region');
    const confirmDistrict = document.getElementById('confirm_district');
    const confirmWard = document.getElementById('confirm_ward');
    const confirmStreet = document.getElementById('confirm_street');
    const confirmRole = document.getElementById('confirm_role');
    const officerWarning = document.getElementById('officerWarning');

    if (confirmFullName) confirmFullName.innerText = fullName;
    if (confirmPhone) confirmPhone.innerText = phoneNumber;
    if (confirmEmail) confirmEmail.innerText = email || 'Hakujazwa';
    if (confirmRegion) confirmRegion.innerText = region || 'Hakujazwa';
    if (confirmDistrict) confirmDistrict.innerText = district || 'Hakujazwa';
    if (confirmWard) confirmWard.innerText = ward || 'Hakujazwa';
    if (confirmStreet) confirmStreet.innerText = street || 'Hakujazwa';
    if (confirmRole) confirmRole.innerText = roleText;

    // Show warning for extension officers
    if (officerWarning) {
        officerWarning.style.display = roleValue === 'extension_officer' ? 'block' : 'none';
    }

    // Validate required fields
    if (!fullName || fullName === '-') {
        showErrorAlert('Tafadhali ingiza jina lako kamili');
        document.getElementById('full_name')?.focus();
        return;
    }

    if (!phoneNumber || phoneNumber === '-') {
        showErrorAlert('Tafadhali ingiza namba yako ya simu');
        document.getElementById('phone_number')?.focus();
        return;
    }

    if (!region) {
        showErrorAlert('Tafadhali chagua Mkoa wako');
        document.getElementById('region')?.focus();
        return;
    }

    if (!district) {
        showErrorAlert('Tafadhali chagua Wilaya yako');
        document.getElementById('district')?.focus();
        return;
    }

    if (!ward) {
        showErrorAlert('Tafadhali chagua Kata yako');
        document.getElementById('ward')?.focus();
        return;
    }

    // Check password match
    const password = document.getElementById('password')?.value;
    const confirmPassword = document.getElementById('confirm_password')?.value;

    if (!password) {
        showErrorAlert('Tafadhali weka nenosiri');
        document.getElementById('password')?.focus();
        return;
    }

    if (password.length < 6) {
        showErrorAlert('Nenosiri lazima iwe na herufi 6 au zaidi');
        document.getElementById('password')?.focus();
        return;
    }

    if (password !== confirmPassword) {
        showErrorAlert('Nenosiri hazifanani');
        document.getElementById('confirm_password')?.focus();
        return;
    }

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
    modal.show();
}
// ==================== SUBMIT FORM ====================
function submitForm() {
    // Final validation before submission
    const password = document.getElementById('password')?.value;
    const confirmPassword = document.getElementById('confirm_password')?.value;
    const fullName = document.getElementById('full_name')?.value;
    const phoneNumber = document.getElementById('phone_number')?.value;

    if (!fullName) {
        showErrorAlert('Please enter your full name');
        return;
    }

    if (!phoneNumber) {
        showErrorAlert('Please enter your phone number');
        return;
    }

    if (!password) {
        showErrorAlert('Please enter a password');
        return;
    }

    if (password !== confirmPassword) {
        showErrorAlert('Passwords do not match');
        return;
    }

    // Submit form
    document.getElementById('registerForm')?.submit();
}

// ==================== SHOW ERROR ALERT ====================
function showErrorAlert(message) {
    // Remove any existing alerts
    const existingAlert = document.querySelector('.alert-danger');
    if (existingAlert) existingAlert.remove();

    // Create new alert
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show rounded-3" role="alert">
            <i class="fas fa-exclamation-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Insert at top of auth-body
    const authBody = document.querySelector('.auth-body');
    if (authBody) {
        authBody.insertAdjacentHTML('afterbegin', alertHtml);

        // Auto-scroll to alert
        const alert = document.querySelector('.alert-danger');
        if (alert) {
            alert.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}