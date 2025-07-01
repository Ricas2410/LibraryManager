// Library Management System - Custom JavaScript

// Initialize form field icons on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeFormFields();
    initializeSearchFields();
    initializeNotifications();
    initializeTooltips();
    initializeFormValidation();
});

// Fix form field icon spacing - Universal solution
function initializeFormFields() {
    // Find all input and select fields with potential icon issues
    const fieldsWithIcons = document.querySelectorAll(
        'input[class*="pl-10"], input[class*="pl-12"], ' +
        'select[class*="pl-10"], select[class*="pl-12"], ' +
        '.relative input, .relative select'
    );

    fieldsWithIcons.forEach(function(field) {
        const parent = field.closest('.relative');
        if (parent) {
            const iconContainer = parent.querySelector('.absolute.inset-y-0.left-0');
            if (iconContainer) {
                // Fix icon container positioning
                iconContainer.style.paddingLeft = '1rem';
                iconContainer.style.zIndex = '10';
                iconContainer.style.pointerEvents = 'none';

                // Fix field padding based on field type
                if (field.name && (field.name.includes('price') || field.name.includes('fine') || field.name.includes('amount'))) {
                    // Currency fields need less padding
                    field.style.paddingLeft = '2.5rem';
                } else {
                    // Regular fields with icons
                    field.style.paddingLeft = '3rem';
                }

                // Style the icon
                const icon = iconContainer.querySelector('i, .fas, .far, .fab, span');
                if (icon) {
                    icon.style.color = '#9CA3AF';
                    icon.style.fontSize = '0.875rem';
                }
            }
        }
    });

    // Fix search fields specifically
    const searchFields = document.querySelectorAll(
        'input[placeholder*="Search"], input[placeholder*="search"], ' +
        'input[name="query"], input[name="search"]'
    );

    searchFields.forEach(function(field) {
        field.style.paddingLeft = '3rem';
        const parent = field.closest('.relative');
        if (parent) {
            const iconContainer = parent.querySelector('.absolute');
            if (iconContainer) {
                iconContainer.style.paddingLeft = '1rem';
                iconContainer.style.zIndex = '10';
            }
        }
    });
}

// Fix search field icon spacing
function initializeSearchFields() {
    const searchFields = document.querySelectorAll('input[placeholder*="Search"], input[placeholder*="search"], input[name="query"], input[name="search"]');
    
    searchFields.forEach(function(field) {
        const parent = field.parentElement;
        if (parent && parent.querySelector('i.fa-search')) {
            parent.classList.add('search-field');
            
            const iconContainer = parent.querySelector('.absolute');
            if (iconContainer) {
                iconContainer.classList.add('search-icon');
            }
            
            field.classList.add('search-input');
        }
    });
}

// Notification system
function initializeNotifications() {
    // Auto-hide success messages after 5 seconds
    const successMessages = document.querySelectorAll('.alert-success, .bg-green-100');
    successMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });
    
    // Make error messages dismissible
    const errorMessages = document.querySelectorAll('.alert-error, .bg-red-100');
    errorMessages.forEach(function(message) {
        if (!message.querySelector('.close-btn')) {
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '&times;';
            closeBtn.className = 'close-btn ml-auto text-xl font-bold cursor-pointer';
            closeBtn.onclick = function() {
                message.style.transition = 'opacity 0.3s ease';
                message.style.opacity = '0';
                setTimeout(function() {
                    message.remove();
                }, 300);
            };
            message.appendChild(closeBtn);
        }
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    tooltipElements.forEach(function(element) {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const title = element.getAttribute('title');
    if (!title) return;
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip absolute bg-gray-800 text-white text-sm px-2 py-1 rounded shadow-lg z-50';
    tooltip.textContent = title;
    tooltip.id = 'tooltip-' + Date.now();
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - 30) + 'px';
    
    document.body.appendChild(tooltip);
    
    // Remove title to prevent default tooltip
    element.setAttribute('data-original-title', title);
    element.removeAttribute('title');
}

function hideTooltip(event) {
    const element = event.target;
    const originalTitle = element.getAttribute('data-original-title');
    if (originalTitle) {
        element.setAttribute('title', originalTitle);
        element.removeAttribute('data-original-title');
    }
    
    // Remove custom tooltip
    const tooltips = document.querySelectorAll('[id^="tooltip-"]');
    tooltips.forEach(function(tooltip) {
        tooltip.remove();
    });
}

// Form validation and submission handling
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        // Only add visual feedback, don't interfere with submission
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        });

        // Add form submission feedback (visual only)
        addFormSubmissionFeedback(form);
    });
}

// Add form submission feedback to any form
function addFormSubmissionFeedback(form) {
    const submitBtn = form.querySelector('button[type="submit"]');

    if (submitBtn && !submitBtn.hasAttribute('data-feedback-added')) {
        submitBtn.setAttribute('data-feedback-added', 'true');

        form.addEventListener('submit', function(e) {
            // Only show loading state, don't prevent submission
            const originalText = submitBtn.innerHTML;

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';

            // Form will submit normally - this is just visual feedback
        });
    }
}

function validateForm(event) {
    // Let Django handle form validation on the server side
    // This function is now just for visual feedback
    const form = event.target;
    const requiredFields = form.querySelectorAll('input[required], select[required], textarea[required]');

    // Just add visual indicators, don't prevent submission
    requiredFields.forEach(function(field) {
        validateField({ target: field });
    });
}

function validateField(event) {
    const field = event.target;

    // Remove existing error styling
    field.classList.remove('form-error');
    const existingError = field.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    // Let Django handle validation on the server side
    // This is just for clearing visual indicators
    return true;
}

// Field error function removed - Django handles validation

function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('form-error');
    
    const existingError = field.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
}

// Enhanced notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${getNotificationClass(type)} animate-slide-in`;

    // Create notification content with icon
    const icon = getNotificationIcon(type);
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="${icon} mr-2"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

    document.body.appendChild(notification);

    // Auto-remove after specified duration
    setTimeout(function() {
        if (notification.parentElement) {
            notification.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(function() {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 500);
        }
    }, duration);
}

// Show success notification
function showSuccess(message) {
    showNotification(message, 'success');
}

// Show error notification
function showError(message) {
    showNotification(message, 'error', 8000); // Show errors longer
}

// Show warning notification
function showWarning(message) {
    showNotification(message, 'warning', 6000);
}

function getNotificationClass(type) {
    switch (type) {
        case 'success':
            return 'bg-green-500 text-white';
        case 'error':
            return 'bg-red-500 text-white';
        case 'warning':
            return 'bg-yellow-500 text-white';
        default:
            return 'bg-blue-500 text-white';
    }
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        default: return 'fas fa-info-circle';
    }
}

// Utility functions
function toggleView(viewType) {
    const tableView = document.getElementById('table-view');
    const gridView = document.getElementById('grid-view');
    const tableBtn = document.getElementById('table-view-btn');
    const gridBtn = document.getElementById('grid-view-btn');

    // Check if elements exist before manipulating them
    if (!tableView || !gridView || !tableBtn || !gridBtn) {
        return;
    }

    if (viewType === 'table') {
        tableView.classList.remove('hidden');
        gridView.classList.add('hidden');
        tableBtn.classList.add('bg-white', 'text-gray-900', 'shadow-sm');
        tableBtn.classList.remove('text-gray-500');
        gridBtn.classList.remove('bg-white', 'text-gray-900', 'shadow-sm');
        gridBtn.classList.add('text-gray-500');
    } else {
        tableView.classList.add('hidden');
        gridView.classList.remove('hidden');
        gridBtn.classList.add('bg-white', 'text-gray-900', 'shadow-sm');
        gridBtn.classList.remove('text-gray-500');
        tableBtn.classList.remove('bg-white', 'text-gray-900', 'shadow-sm');
        tableBtn.classList.add('text-gray-500');
    }

    // Save preference to localStorage
    localStorage.setItem('bookViewPreference', viewType);
}

// Load saved preferences on page load
function loadSavedPreferences() {
    const savedView = localStorage.getItem('bookViewPreference') || 'table';
    // Only call toggleView if the required elements exist
    if (document.getElementById('table-view') && document.getElementById('grid-view')) {
        toggleView(savedView);
    }
}

// Global form enhancement function
function enhanceAllForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        // Skip if already enhanced
        if (form.hasAttribute('data-enhanced')) {
            return;
        }

        form.setAttribute('data-enhanced', 'true');

        // Add enter key handling for better UX
        form.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    e.preventDefault();
                    submitBtn.click();
                }
            }
        });
    });
}

// Re-enhance forms when new content is loaded dynamically
function reEnhanceForms() {
    enhanceAllForms();
}

// Initialize saved preferences
document.addEventListener('DOMContentLoaded', function() {
    loadSavedPreferences();
    enhanceAllForms();
});
