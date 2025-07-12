// NeuroLearn - Main JavaScript File

// Global variables
let currentUser = null;
let isAuthenticated = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setupNavigation();
});

function initializeApp() {
    // Check authentication status
    checkAuthStatus();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function setupEventListeners() {
    // Global click handlers
    document.addEventListener('click', function(e) {
        // Handle navigation active states
        if (e.target.classList.contains('nav-link')) {
            updateActiveNavigation(e.target);
        }
        
        // Handle dropdown toggles
        if (e.target.classList.contains('dropdown-toggle')) {
            e.preventDefault();
        }
    });
    
    // Handle form submissions
    document.addEventListener('submit', function(e) {
        if (e.target.classList.contains('needs-validation')) {
            e.preventDefault();
            if (e.target.checkValidity()) {
                handleFormSubmission(e.target);
            } else {
                e.target.classList.add('was-validated');
            }
        }
    });
}

function setupNavigation() {
    // Set active navigation based on current page
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/dashboard')) {
            link.classList.add('active');
        }
    });
    
    // Add smooth scrolling for navigation
    addSmoothScrolling();
    
    // Add navbar scroll effect
    addNavbarScrollEffect();
}

function addSmoothScrolling() {
    // Smooth scroll to sections when clicking nav links
    document.querySelectorAll('.nav-link[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function addNavbarScrollEffect() {
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down - hide navbar slightly
            navbar.style.transform = 'translateY(-100%)';
            navbar.style.transition = 'transform 0.3s ease';
        } else {
            // Scrolling up - show navbar
            navbar.style.transform = 'translateY(0)';
        }
        
        // Add background blur when scrolled
        if (scrollTop > 50) {
            navbar.style.backdropFilter = 'blur(20px)';
            navbar.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        } else {
            navbar.style.backdropFilter = 'blur(10px)';
            navbar.style.backgroundColor = 'rgba(255, 255, 255, 1)';
        }
        
        lastScrollTop = scrollTop;
    });
}

function updateActiveNavigation(clickedLink) {
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to clicked link
    clickedLink.classList.add('active');
}

function checkAuthStatus() {
    // Check if user is authenticated (simulate for now)
    const token = localStorage.getItem('authToken');
    if (token) {
        isAuthenticated = true;
        currentUser = JSON.parse(localStorage.getItem('userData'));
        updateUserInterface();
    } else {
        // Redirect to login if not authenticated
        if (window.location.pathname !== '/login') {
            // For demo purposes, we'll skip authentication
            isAuthenticated = true;
            currentUser = {
                name: 'Admin User',
                email: 'admin@neurolearn.com',
                role: 'admin'
            };
            updateUserInterface();
        }
    }
}

function updateUserInterface() {
    // Update user info in navigation
    const userDropdown = document.querySelector('.navbar-nav .dropdown-toggle');
    if (userDropdown && currentUser) {
        userDropdown.innerHTML = `
            <i class="fas fa-user-circle me-1"></i>${currentUser.name}
        `;
    }
}

function handleFormSubmission(form) {
    const formData = new FormData(form);
    const action = form.getAttribute('action');
    const method = form.getAttribute('method') || 'POST';
    
    showLoading();
    
    fetch(action, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showSuccess(data.message || 'Operation completed successfully');
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        } else {
            showError(data.message || 'Operation failed');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Form submission error:', error);
        showError('An error occurred. Please try again.');
    });
}

// Utility functions
function showLoading() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = 'flex';
    }
}

function hideLoading() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

function showSuccess(message) {
    showAlert('success', message);
}

function showError(message) {
    showAlert('danger', message);
}

function showWarning(message) {
    showAlert('warning', message);
}

function showInfo(message) {
    showAlert('info', message);
}

function showAlert(type, message) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'danger' ? 'exclamation-triangle' : 
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    alert.innerHTML = `
        <i class="fas fa-${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of main content
    const mainContent = document.querySelector('.main-content .container-fluid');
    if (mainContent) {
        mainContent.insertBefore(alert, mainContent.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// API utility functions
function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const requestOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    return fetch(endpoint, requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Chart utility functions
function createChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    
    const ctx = canvas.getContext('2d');
    return new Chart(ctx, config);
}

function updateChart(chart, newData) {
    if (chart) {
        chart.data = newData;
        chart.update();
    }
}

// Data formatting utilities
function formatPercentage(value) {
    return (value * 100).toFixed(1) + '%';
}

function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Navigation functions
function navigateTo(page) {
    window.location.href = page;
}

function goBack() {
    window.history.back();
}

function refreshPage() {
    window.location.reload();
}

// Modal utilities
function showModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function hideModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
        modal.hide();
    }
}

// Form utilities
function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        return form.checkValidity();
    }
    return false;
}

// Local storage utilities
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function getFromStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (error) {
        console.error('Error reading from localStorage:', error);
        return null;
    }
}

function removeFromStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Error removing from localStorage:', error);
    }
}

// Session management
function logout() {
    removeFromStorage('authToken');
    removeFromStorage('userData');
    isAuthenticated = false;
    currentUser = null;
    window.location.href = '/login';
}

// Export functions for global use
window.NeuroLearn = {
    showLoading,
    hideLoading,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    apiRequest,
    createChart,
    updateChart,
    formatPercentage,
    formatDuration,
    formatDate,
    formatDateTime,
    navigateTo,
    goBack,
    refreshPage,
    showModal,
    hideModal,
    resetForm,
    validateForm,
    saveToStorage,
    getFromStorage,
    removeFromStorage,
    logout
};

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showError('An unexpected error occurred. Please refresh the page.');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showError('An error occurred while processing your request.');
}); 