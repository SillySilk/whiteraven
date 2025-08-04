// White Raven Pourhouse - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
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

    // Loading states for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Sending...';
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });

    // Menu category filtering (if on menu page)
    const categoryFilters = document.querySelectorAll('.category-filter button');
    const menuItems = document.querySelectorAll('.menu-item-card');
    
    categoryFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            const category = this.dataset.category;
            
            // Update active state
            categoryFilters.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter menu items
            menuItems.forEach(item => {
                if (category === 'all' || item.dataset.category === category) {
                    item.style.display = 'block';
                    item.classList.add('fade-in');
                } else {
                    item.style.display = 'none';
                    item.classList.remove('fade-in');
                }
            });
        });
    });

    // Contact form validation
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = this.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                    field.classList.add('is-valid');
                }
            });
            
            // Email validation
            const emailField = this.querySelector('input[type="email"]');
            if (emailField && emailField.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailField.value)) {
                    emailField.classList.add('is-invalid');
                    isValid = false;
                } else {
                    emailField.classList.remove('is-invalid');
                    emailField.classList.add('is-valid');
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Please fill in all required fields correctly.', 'error');
            }
        });
    }

    // Hours status update
    updateHoursStatus();
    
    // Update hours status every minute
    setInterval(updateHoursStatus, 60000);

    // Enhanced mobile navbar scroll effect
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');
    let isNavbarCollapsed = true;
    let isMobile = window.innerWidth < 992;
    
    // Check if navbar is collapsed
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Listen for navbar toggle
        navbarToggler.addEventListener('click', function() {
            setTimeout(() => {
                isNavbarCollapsed = !navbarCollapse.classList.contains('show');
            }, 100);
        });
        
        // Close navbar when clicking on a link (mobile)
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (isMobile && navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        });
        
        // Close navbar when clicking outside (mobile)
        document.addEventListener('click', function(event) {
            if (isMobile && navbarCollapse.classList.contains('show')) {
                if (!navbar.contains(event.target)) {
                    navbarToggler.click();
                }
            }
        });
    }
    
    // Enhanced scroll behavior with mobile considerations
    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Only hide navbar on mobile when collapsed and scrolling down
        if (isMobile && isNavbarCollapsed) {
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Scrolling down
                navbar.style.transform = 'translateY(-100%)';
                navbar.style.transition = 'transform 0.3s ease';
            } else {
                // Scrolling up
                navbar.style.transform = 'translateY(0)';
                navbar.style.transition = 'transform 0.3s ease';
            }
        } else if (!isMobile) {
            // Always show navbar on desktop
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });

    // Responsive image loading and optimization
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Load appropriate image size based on screen size
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                    } else if (img.dataset.mobile && isMobile) {
                        img.src = img.dataset.mobile;
                    } else if (img.dataset.tablet && window.innerWidth < 1200) {
                        img.src = img.dataset.tablet;
                    } else if (img.dataset.desktop) {
                        img.src = img.dataset.desktop;
                    }
                    
                    img.classList.remove('lazy');
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px', // Start loading 50px before image enters viewport
            threshold: 0.1
        });

        document.querySelectorAll('img[data-src], img[data-mobile], img[data-tablet], img[data-desktop]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Touch gesture support for mobile
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    // Add swipe gesture support for menu items and cards
    if (isMobile) {
        const swipeableElements = document.querySelectorAll('.menu-item-card, .card');
        
        swipeableElements.forEach(element => {
            element.addEventListener('touchstart', function(e) {
                touchStartX = e.changedTouches[0].screenX;
                touchStartY = e.changedTouches[0].screenY;
            }, { passive: true });

            element.addEventListener('touchend', function(e) {
                touchEndX = e.changedTouches[0].screenX;
                touchEndY = e.changedTouches[0].screenY;
                handleSwipeGesture(element);
            }, { passive: true });
        });
    }

    // Handle window resize for responsive adjustments
    window.addEventListener('resize', debounce(function() {
        isMobile = window.innerWidth < 992;
        
        // Reset navbar on resize
        if (!isMobile) {
            navbar.style.transform = 'translateY(0)';
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        }
        
        // Recalculate image sizes if needed
        const images = document.querySelectorAll('img.loaded');
        images.forEach(img => {
            if (img.dataset.mobile && isMobile && img.src !== img.dataset.mobile) {
                img.src = img.dataset.mobile;
            } else if (img.dataset.tablet && !isMobile && window.innerWidth < 1200 && img.src !== img.dataset.tablet) {
                img.src = img.dataset.tablet;
            } else if (img.dataset.desktop && window.innerWidth >= 1200 && img.src !== img.dataset.desktop) {
                img.src = img.dataset.desktop;
            }
        });
    }, 250));

    // Enhanced form handling for mobile
    const allForms = document.querySelectorAll('form');
    allForms.forEach(form => {
        // Add mobile-friendly input focus handling
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                if (isMobile) {
                    // Scroll input into view on mobile to prevent keyboard covering
                    setTimeout(() => {
                        this.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }, 300);
                }
            });
        });
    });

    // Mobile-specific menu enhancements
    if (isMobile) {
        // Add sticky filter buttons on mobile for menu page
        const menuFilters = document.querySelector('.menu-filters');
        if (menuFilters) {
            let filtersSticky = false;
            window.addEventListener('scroll', function() {
                const rect = menuFilters.getBoundingClientRect();
                if (rect.top <= 70 && !filtersSticky) {
                    menuFilters.style.position = 'sticky';
                    menuFilters.style.top = '70px';
                    menuFilters.style.zIndex = '1020';
                    menuFilters.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
                    menuFilters.style.backdropFilter = 'blur(10px)';
                    filtersSticky = true;
                } else if (rect.top > 70 && filtersSticky) {
                    menuFilters.style.position = '';
                    menuFilters.style.top = '';
                    menuFilters.style.zIndex = '';
                    menuFilters.style.backgroundColor = '';
                    menuFilters.style.backdropFilter = '';
                    filtersSticky = false;
                }
            });
        }
    }

    // Performance optimizations for mobile
    if (isMobile) {
        // Reduce animation duration on mobile for better performance
        const animatedElements = document.querySelectorAll('.card, .btn, .navbar-nav .nav-link');
        animatedElements.forEach(element => {
            element.style.transitionDuration = '0.2s';
        });
    }
});

// Utility functions
function updateHoursStatus() {
    const hoursElements = document.querySelectorAll('.hours-status');
    const now = new Date();
    const currentDay = now.getDay(); // 0 = Sunday, 1 = Monday, etc.
    const currentTime = now.getHours() * 100 + now.getMinutes(); // Convert to HHMM format
    
    // Business hours (can be made dynamic via API later)
    const hours = {
        1: { open: 600, close: 1800 },  // Monday
        2: { open: 600, close: 1800 },  // Tuesday
        3: { open: 600, close: 1800 },  // Wednesday
        4: { open: 600, close: 1800 },  // Thursday
        5: { open: 600, close: 1800 },  // Friday
        6: { open: 700, close: 1700 },  // Saturday
        0: { open: 700, close: 1700 }   // Sunday
    };
    
    const todayHours = hours[currentDay];
    const isOpen = todayHours && currentTime >= todayHours.open && currentTime <= todayHours.close;
    
    hoursElements.forEach(element => {
        if (isOpen) {
            element.innerHTML = '<span class="status-open">Open Now</span>';
            element.classList.add('status-open');
            element.classList.remove('status-closed');
        } else {
            element.innerHTML = '<span class="status-closed">Closed</span>';
            element.classList.add('status-closed');
            element.classList.remove('status-open');
        }
    });
}

function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
    alertDiv.innerHTML = `
        <i class="bi bi-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle-fill',
        'error': 'exclamation-triangle-fill',
        'warning': 'exclamation-circle-fill',
        'info': 'info-circle-fill'
    };
    return icons[type] || icons['info'];
}

// Add fade-in animation for dynamic content
function addFadeInAnimation(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    
    setTimeout(() => {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 100);
}

// Form validation helpers
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function validatePhone(phone) {
    const regex = /^[\+]?[1-9][\d]{0,15}$/;
    return regex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

// Local storage helpers for user preferences
function savePreference(key, value) {
    try {
        localStorage.setItem(`wrp_${key}`, JSON.stringify(value));
    } catch (e) {
        console.warn('localStorage not available');
    }
}

function getPreference(key, defaultValue = null) {
    try {
        const value = localStorage.getItem(`wrp_${key}`);
        return value ? JSON.parse(value) : defaultValue;
    } catch (e) {
        console.warn('localStorage not available');
        return defaultValue;
    }
}

// Handle swipe gestures
function handleSwipeGesture(element) {
    const diffX = touchEndX - touchStartX;
    const diffY = touchEndY - touchStartY;
    const minSwipeDistance = 50;
    
    // Check if it's a horizontal swipe
    if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > minSwipeDistance) {
        if (diffX > 0) {
            // Swipe right - could trigger previous item or show more info
            element.classList.add('swipe-right');
            setTimeout(() => element.classList.remove('swipe-right'), 300);
        } else {
            // Swipe left - could trigger next item or hide info
            element.classList.add('swipe-left');
            setTimeout(() => element.classList.remove('swipe-left'), 300);
        }
    }
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Detect if device supports touch
function isTouchDevice() {
    return (('ontouchstart' in window) ||
            (navigator.maxTouchPoints > 0) ||
            (navigator.msMaxTouchPoints > 0));
}

// Optimize images for different screen sizes
function optimizeImage(img) {
    const screenWidth = window.innerWidth;
    const devicePixelRatio = window.devicePixelRatio || 1;
    
    // Calculate optimal image size
    let targetWidth;
    if (screenWidth <= 480) {
        targetWidth = 480 * devicePixelRatio;
    } else if (screenWidth <= 768) {
        targetWidth = 768 * devicePixelRatio;
    } else if (screenWidth <= 1200) {
        targetWidth = 1200 * devicePixelRatio;
    } else {
        targetWidth = 1920 * devicePixelRatio;
    }
    
    // If image has data attributes for different sizes, use them
    if (img.dataset.mobile && screenWidth <= 480) {
        return img.dataset.mobile;
    } else if (img.dataset.tablet && screenWidth <= 1200) {
        return img.dataset.tablet;
    } else if (img.dataset.desktop) {
        return img.dataset.desktop;
    }
    
    return img.src;
}

// Enhanced mobile form validation
function validateFormMobile(form) {
    const inputs = form.querySelectorAll('input, textarea, select');
    let isValid = true;
    let firstInvalidField = null;
    
    inputs.forEach(input => {
        const isFieldValid = validateField(input);
        if (!isFieldValid && !firstInvalidField) {
            firstInvalidField = input;
        }
        isValid = isValid && isFieldValid;
    });
    
    // Scroll to first invalid field on mobile
    if (!isValid && firstInvalidField && window.innerWidth < 992) {
        setTimeout(() => {
            firstInvalidField.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
            firstInvalidField.focus();
        }, 100);
    }
    
    return isValid;
}

// Validate individual form field
function validateField(field) {
    let isValid = true;
    const value = field.value.trim();
    
    // Check required fields
    if (field.hasAttribute('required') && !value) {
        isValid = false;
    }
    
    // Check email fields
    if (field.type === 'email' && value && !validateEmail(value)) {
        isValid = false;
    }
    
    // Check phone fields
    if (field.type === 'tel' && value && !validatePhone(value)) {
        isValid = false;
    }
    
    // Update field visual state
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
    }
    
    return isValid;
}

// Mobile-specific performance monitoring
function monitorPerformance() {
    if ('PerformanceObserver' in window && window.innerWidth < 992) {
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach((entry) => {
                // Monitor for long tasks on mobile
                if (entry.entryType === 'longtask' && entry.duration > 50) {
                    console.warn('Long task detected on mobile:', entry.duration + 'ms');
                }
                
                // Monitor for large layout shifts
                if (entry.entryType === 'layout-shift' && entry.value > 0.1) {
                    console.warn('Large layout shift detected:', entry.value);
                }
            });
        });
        
        // Observe long tasks and layout shifts
        try {
            observer.observe({ entryTypes: ['longtask', 'layout-shift'] });
        } catch (e) {
            // Browser might not support all entry types
            console.log('Performance monitoring not fully supported');
        }
    }
}

// Initialize performance monitoring
if (window.innerWidth < 992) {
    monitorPerformance();
}

// Export functions for use in other scripts
window.WRP = {
    showAlert,
    updateHoursStatus,
    validateEmail,
    validatePhone,
    savePreference,
    getPreference,
    addFadeInAnimation,
    handleSwipeGesture,
    debounce,
    isTouchDevice,
    optimizeImage,
    validateFormMobile,
    validateField
};