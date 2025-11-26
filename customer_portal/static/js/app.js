// SIX3 Agency Customer Portal - Main JavaScript

// Global variables
let isAuthenticated = false;
let currentUser = null;
let sessionTimeout = null;
let notificationSocket = null;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    // Check authentication status
    checkAuthStatus();
    
    // Initialize session management
    initializeSessionManagement();
    
    // Initialize real-time notifications
    initializeNotifications();
    
    // Initialize UI enhancements
    initializeUIEnhancements();
    
    // Initialize analytics tracking
    initializeAnalytics();
    
    // Initialize error handling
    initializeErrorHandling();
    
    console.log('SIX3 Agency Portal initialized successfully');
}

// Authentication and session management
function checkAuthStatus() {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('user_data');
    
    if (token && user) {
        isAuthenticated = true;
        currentUser = JSON.parse(user);
        
        // Verify token validity
        fetch('/api/auth/verify', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (!response.ok) {
                handleLogout();
            }
        })
        .catch(error => {
            console.error('Auth verification failed:', error);
        });
    }
}

function initializeSessionManagement() {
    // Set session timeout (30 minutes)
    const TIMEOUT_DURATION = 30 * 60 * 1000;
    
    function resetSessionTimeout() {
        if (sessionTimeout) {
            clearTimeout(sessionTimeout);
        }
        
        if (isAuthenticated) {
            sessionTimeout = setTimeout(() => {
                showSessionExpiredModal();
            }, TIMEOUT_DURATION);
        }
    }
    
    // Reset timeout on user activity
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetSessionTimeout, { passive: true });
    });
    
    resetSessionTimeout();
}

function showSessionExpiredModal() {
    const modal = new bootstrap.Modal(document.getElementById('sessionExpiredModal') || createSessionExpiredModal());
    modal.show();
}

function createSessionExpiredModal() {
    const modalHtml = `
        <div class="modal fade" id="sessionExpiredModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="fas fa-clock me-2"></i>Session Expired
                        </h5>
                    </div>
                    <div class="modal-body text-center">
                        <i class="fas fa-hourglass-end fa-3x text-warning mb-3"></i>
                        <p>Your session has expired for security reasons. Please log in again to continue.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="redirectToLogin()">
                            <i class="fas fa-sign-in-alt me-1"></i>Log In
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    return document.getElementById('sessionExpiredModal');
}

function redirectToLogin() {
    handleLogout();
    window.location.href = '/login';
}

function handleLogout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    isAuthenticated = false;
    currentUser = null;
    
    if (sessionTimeout) {
        clearTimeout(sessionTimeout);
    }
    
    if (notificationSocket) {
        notificationSocket.close();
    }
}

// Real-time notifications
function initializeNotifications() {
    if (!isAuthenticated) return;
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Initialize WebSocket connection for real-time updates
    connectNotificationSocket();
    
    // Check for browser notifications every 30 seconds
    setInterval(checkForNotifications, 30000);
}

function connectNotificationSocket() {
    // Note: This would connect to a WebSocket endpoint for real-time updates
    // Implementation would depend on backend WebSocket support
    console.log('Real-time notifications initialized');
}

function checkForNotifications() {
    if (!isAuthenticated) return;
    
    fetch('/api/notifications/unread')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                updateNotificationBadge(data.count);
                
                // Show browser notification for high priority items
                data.notifications.forEach(notification => {
                    if (notification.priority === 'high' && 'Notification' in window && Notification.permission === 'granted') {
                        new Notification(notification.title, {
                            body: notification.message,
                            icon: '/static/img/logo-32.png',
                            tag: notification.id
                        });
                    }
                });
            }
        })
        .catch(error => console.error('Notification check failed:', error));
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

// UI Enhancements
function initializeUIEnhancements() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Form validation enhancements
    initializeFormValidation();
    
    // Loading states for buttons
    initializeLoadingStates();
    
    // Auto-save functionality
    initializeAutoSave();
}

function initializeFormValidation() {
    // Add real-time validation to forms
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation for individual fields
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

function initializeLoadingStates() {
    // Add loading states to buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn[data-loading]') || e.target.closest('.btn[data-loading]')) {
            const btn = e.target.matches('.btn') ? e.target : e.target.closest('.btn');
            showButtonLoading(btn);
        }
    });
}

function showButtonLoading(button) {
    const originalText = button.innerHTML;
    button.dataset.originalText = originalText;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
    button.disabled = true;
    
    // Auto-restore after 10 seconds (fallback)
    setTimeout(() => {
        hideButtonLoading(button);
    }, 10000);
}

function hideButtonLoading(button) {
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        delete button.dataset.originalText;
    }
    button.disabled = false;
}

function initializeAutoSave() {
    // Auto-save form data to localStorage
    const autoSaveForms = document.querySelectorAll('.auto-save');
    autoSaveForms.forEach(form => {
        const formId = form.id || 'auto-save-form';
        
        // Load saved data
        const savedData = localStorage.getItem(`form-data-${formId}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const field = form.querySelector(`[name="${key}"]`);
                    if (field && field.type !== 'password') {
                        field.value = data[key];
                    }
                });
            } catch (error) {
                console.error('Error loading auto-save data:', error);
            }
        }
        
        // Save data on input
        form.addEventListener('input', debounce(function() {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                if (key !== 'password' && key !== 'confirm_password') {
                    data[key] = value;
                }
            }
            localStorage.setItem(`form-data-${formId}`, JSON.stringify(data));
        }, 1000));
        
        // Clear on successful submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(`form-data-${formId}`);
        });
    });
}

// Analytics and tracking
function initializeAnalytics() {
    // Track page views
    trackPageView();
    
    // Track user interactions
    trackUserInteractions();
    
    // Track performance metrics
    trackPerformanceMetrics();
}

function trackPageView() {
    if (!isAuthenticated) return;
    
    const pageData = {
        page: window.location.pathname,
        title: document.title,
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
        referrer: document.referrer
    };
    
    fetch('/api/analytics/pageview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(pageData)
    }).catch(error => console.log('Analytics tracking failed:', error));
}

function trackUserInteractions() {
    // Track button clicks
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn') || e.target.closest('.btn')) {
            const button = e.target.matches('.btn') ? e.target : e.target.closest('.btn');
            trackEvent('button_click', {
                text: button.textContent.trim(),
                classes: button.className
            });
        }
    });
    
    // Track form submissions
    document.addEventListener('submit', function(e) {
        if (e.target.matches('form')) {
            trackEvent('form_submit', {
                form_id: e.target.id,
                action: e.target.action
            });
        }
    });
}

function trackEvent(eventName, properties) {
    if (!isAuthenticated) return;
    
    const eventData = {
        event: eventName,
        properties: properties,
        timestamp: new Date().toISOString(),
        page: window.location.pathname
    };
    
    fetch('/api/analytics/event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(eventData)
    }).catch(error => console.log('Event tracking failed:', error));
}

function trackPerformanceMetrics() {
    // Track page load time
    window.addEventListener('load', function() {
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
            trackEvent('page_performance', {
                load_time: navigation.loadEventEnd - navigation.loadEventStart,
                dom_content_loaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                first_paint: performance.getEntriesByType('paint')[0]?.startTime || null
            });
        }
    });
}

// Error handling
function initializeErrorHandling() {
    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        trackEvent('javascript_error', {
            message: e.message,
            filename: e.filename,
            line: e.lineno,
            column: e.colno
        });
    });
    
    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        trackEvent('promise_rejection', {
            reason: e.reason.toString()
        });
    });
    
    // Network error handling
    window.addEventListener('offline', function() {
        showNetworkStatus(false);
    });
    
    window.addEventListener('online', function() {
        showNetworkStatus(true);
    });
}

function showNetworkStatus(isOnline) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white ${isOnline ? 'bg-success' : 'bg-danger'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${isOnline ? 'wifi' : 'wifi-slash'} me-2"></i>
                ${isOnline ? 'Connection restored' : 'No internet connection'}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to toast container or create one
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Utility functions
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        }).catch(function() {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        showToast('Failed to copy to clipboard', 'danger');
    }
    
    document.body.removeChild(textArea);
}

function showToast(message, type = 'info', duration = 3000) {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check' : type === 'danger' ? 'exclamation-triangle' : 'info'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// API helper functions
function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('auth_token');
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
    
    const config = {
        headers: { ...defaultHeaders, ...options.headers },
        ...options
    };
    
    return fetch(endpoint, config)
        .then(response => {
            if (response.status === 401) {
                handleLogout();
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        });
}

// Export global functions for use in templates
window.SIX3Portal = {
    showToast,
    copyToClipboard,
    formatNumber,
    formatDate,
    apiRequest,
    trackEvent,
    showButtonLoading,
    hideButtonLoading
};

// Service Worker registration (for PWA features)
if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('Service Worker registered successfully:', registration);
            })
            .catch(function(error) {
                console.log('Service Worker registration failed:', error);
            });
    });
}