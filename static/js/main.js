// Main JavaScript for DurinsGate Portal

// Session timeout warning
(function () {
    if (typeof sessionTimeoutMinutes === 'undefined') {
        var sessionTimeoutMinutes = 15; // Default from config
    }

    var warningTime = (sessionTimeoutMinutes - 2) * 60 * 1000; // 2 minutes before timeout
    var timeoutTime = sessionTimeoutMinutes * 60 * 1000;

    var warningTimer;
    var timeoutTimer;
    var sessionWarningModal;

    function resetTimers() {
        clearTimeout(warningTimer);
        clearTimeout(timeoutTimer);

        // Hide modal if showing
        if (sessionWarningModal) {
            var modalInstance = bootstrap.Modal.getInstance(document.getElementById('sessionWarningModal'));
            if (modalInstance) {
                modalInstance.hide();
            }
        }

        // Set new timers
        warningTimer = setTimeout(showWarning, warningTime);
        timeoutTimer = setTimeout(logout, timeoutTime);
    }

    function showWarning() {
        var modalElement = document.getElementById('sessionWarningModal');
        if (modalElement) {
            sessionWarningModal = new bootstrap.Modal(modalElement);
            sessionWarningModal.show();

            // Update countdown
            var timeRemaining = 120; // 2 minutes in seconds
            var countdownElement = document.getElementById('timeRemaining');

            var countdownInterval = setInterval(function () {
                timeRemaining--;
                var minutes = Math.floor(timeRemaining / 60);
                var seconds = timeRemaining % 60;
                countdownElement.textContent = minutes + ' minute' + (minutes !== 1 ? 's' : '') +
                    ' ' + seconds + ' second' + (seconds !== 1 ? 's' : '');

                if (timeRemaining <= 0) {
                    clearInterval(countdownInterval);
                }
            }, 1000);
        }
    }

    function logout() {
        window.location.href = '/auth/logout';
    }

    // Reset timers on user activity
    document.addEventListener('mousemove', resetTimers);
    document.addEventListener('keypress', resetTimers);
    document.addEventListener('click', resetTimers);
    document.addEventListener('scroll', resetTimers);

    // Handle "Stay Logged In" button
    var stayLoggedInBtn = document.getElementById('stayLoggedIn');
    if (stayLoggedInBtn) {
        stayLoggedInBtn.addEventListener('click', function () {
            resetTimers();
            var modalInstance = bootstrap.Modal.getInstance(document.getElementById('sessionWarningModal'));
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }

    // Initialize timers
    resetTimers();
})();

// File search functionality
document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Download confirmation
    var downloadButtons = document.querySelectorAll('.download-btn');
    downloadButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            // Show loading state
            var originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Preparing...';
            this.disabled = true;

            // Re-enable after 3 seconds
            setTimeout(function () {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 3000);
        });
    });

    // Form validation feedback
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Password strength indicator
    var passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            var password = this.value;
            var strength = 0;

            if (password.length >= 12) strength++;
            if (/[a-z]/.test(password)) strength++;
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^a-zA-Z0-9]/.test(password)) strength++;

            var strengthIndicator = document.getElementById('passwordStrength');
            if (strengthIndicator) {
                var strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
                var strengthColor = ['danger', 'warning', 'info', 'primary', 'success'];

                strengthIndicator.className = 'badge bg-' + strengthColor[strength - 1];
                strengthIndicator.textContent = strengthText[strength - 1] || '';
            }
        });
    }

    // Tooltips initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Search filter functionality
function filterFiles() {
    var searchInput = document.getElementById('fileSearch');
    var categoryFilter = document.getElementById('categoryFilter');

    if (searchInput || categoryFilter) {
        var searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        var selectedCategory = categoryFilter ? categoryFilter.value : '';

        var fileRows = document.querySelectorAll('.file-row');

        fileRows.forEach(function (row) {
            var fileName = row.dataset.filename ? row.dataset.filename.toLowerCase() : '';
            var fileCategory = row.dataset.category || '';

            var matchesSearch = !searchTerm || fileName.includes(searchTerm);
            var matchesCategory = !selectedCategory || fileCategory === selectedCategory;

            if (matchesSearch && matchesCategory) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
}

// Export functions for global use
window.filterFiles = filterFiles;
