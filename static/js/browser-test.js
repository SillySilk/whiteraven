// Browser Compatibility Testing Script
// White Raven Pourhouse - Cross-Browser Testing

(function() {
    'use strict';
    
    // Browser detection
    const browser = {
        isChrome: navigator.userAgent.indexOf('Chrome') > -1,
        isFirefox: navigator.userAgent.indexOf('Firefox') > -1,
        isSafari: navigator.userAgent.indexOf('Safari') > -1 && navigator.userAgent.indexOf('Chrome') === -1,
        isEdge: navigator.userAgent.indexOf('Edge') > -1 || navigator.userAgent.indexOf('Edg') > -1,
        isIE: navigator.userAgent.indexOf('MSIE') > -1 || navigator.userAgent.indexOf('Trident') > -1,
        isMobile: window.innerWidth <= 768,
        isTouch: 'ontouchstart' in window || navigator.maxTouchPoints > 0
    };

    // Feature detection
    const features = {
        flexbox: checkFlexboxSupport(),
        grid: checkGridSupport(),
        customProperties: checkCustomPropertiesSupport(),
        intersectionObserver: 'IntersectionObserver' in window,
        serviceWorker: 'serviceWorker' in navigator,
        localStorage: checkLocalStorageSupport(),
        es6: checkES6Support(),
        fetch: 'fetch' in window,
        promises: 'Promise' in window
    };

    // Initialize testing
    document.addEventListener('DOMContentLoaded', function() {
        runCompatibilityTests();
        addBrowserSpecificFixes();
        logBrowserInfo();
    });

    function checkFlexboxSupport() {
        const div = document.createElement('div');
        div.style.display = 'flex';
        return div.style.display === 'flex';
    }

    function checkGridSupport() {
        const div = document.createElement('div');
        div.style.display = 'grid';
        return div.style.display === 'grid';
    }

    function checkCustomPropertiesSupport() {
        return window.CSS && CSS.supports('color', 'var(--fake-var)');
    }

    function checkLocalStorageSupport() {
        try {
            const test = 'test';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch(e) {
            return false;
        }
    }

    function checkES6Support() {
        try {
            eval('const test = () => {}');
            return true;
        } catch(e) {
            return false;
        }
    }

    function runCompatibilityTests() {
        const testResults = {
            browser: browser,
            features: features,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight,
                ratio: window.devicePixelRatio || 1
            },
            performance: {
                timeToInteractive: performance.now(),
                memoryUsage: performance.memory ? performance.memory.usedJSHeapSize : 'N/A'
            }
        };

        // Store test results
        if (features.localStorage) {
            try {
                localStorage.setItem('wrp_browser_test', JSON.stringify(testResults));
            } catch(e) {
                console.warn('Could not store test results');
            }
        }

        // Run specific tests
        testBootstrapCompatibility();
        testFormFunctionality();
        testNavigationBehavior();
        testResponsiveImages();
        
        console.log('Browser Compatibility Test Results:', testResults);
        
        // Report critical issues
        reportCriticalIssues(testResults);
    }

    function testBootstrapCompatibility() {
        const tests = {
            navbar: testElement('.navbar'),
            cards: testElement('.card'),
            buttons: testElement('.btn'),
            forms: testElement('.form-control'),
            grid: testElement('.container'),
            modals: testBootstrapJS('Modal'),
            tooltips: testBootstrapJS('Tooltip'),
            alerts: testBootstrapJS('Alert')
        };

        console.log('Bootstrap Component Tests:', tests);
        return tests;
    }

    function testElement(selector) {
        const element = document.querySelector(selector);
        if (!element) return { exists: false };

        const styles = window.getComputedStyle(element);
        return {
            exists: true,
            display: styles.display,
            position: styles.position,
            width: styles.width,
            height: styles.height,
            rendered: element.offsetWidth > 0 && element.offsetHeight > 0
        };
    }

    function testBootstrapJS(component) {
        try {
            return typeof bootstrap !== 'undefined' && 
                   typeof bootstrap[component] === 'function';
        } catch(e) {
            return false;
        }
    }

    function testFormFunctionality() {
        const forms = document.querySelectorAll('form');
        const tests = {};

        forms.forEach((form, index) => {
            const formTest = {
                exists: true,
                inputs: form.querySelectorAll('input, textarea, select').length,
                validation: form.hasAttribute('novalidate') || 
                           form.querySelector('[required]') !== null,
                submission: typeof form.onsubmit === 'function' ||
                           form.addEventListener !== undefined
            };

            tests[`form_${index}`] = formTest;
        });

        console.log('Form Functionality Tests:', tests);
        return tests;
    }

    function testNavigationBehavior() {
        const navbar = document.querySelector('.navbar');
        const navToggler = document.querySelector('.navbar-toggler');
        const navCollapse = document.querySelector('.navbar-collapse');

        const tests = {
            navbar_exists: !!navbar,
            mobile_toggle: !!navToggler,
            collapse_element: !!navCollapse,
            responsive_behavior: window.innerWidth <= 991 ? 
                (navToggler && navCollapse) : true,
            sticky_behavior: navbar ? 
                window.getComputedStyle(navbar).position.includes('sticky') ||
                window.getComputedStyle(navbar).position.includes('fixed') : false
        };

        console.log('Navigation Tests:', tests);
        return tests;
    }

    function testResponsiveImages() {
        const images = document.querySelectorAll('img');
        const tests = {
            total_images: images.length,
            responsive_images: 0,
            lazy_images: 0,
            broken_images: 0
        };

        images.forEach(img => {
            // Check for responsive classes
            if (img.classList.contains('img-fluid') || 
                img.style.maxWidth === '100%') {
                tests.responsive_images++;
            }

            // Check for lazy loading
            if (img.hasAttribute('loading') || 
                img.classList.contains('lazy')) {
                tests.lazy_images++;
            }

            // Check for broken images
            if (img.naturalWidth === 0 && img.complete) {
                tests.broken_images++;
            }
        });

        console.log('Image Tests:', tests);
        return tests;
    }

    function addBrowserSpecificFixes() {
        // Internet Explorer fixes
        if (browser.isIE) {
            addIEFixes();
        }

        // Safari fixes
        if (browser.isSafari) {
            addSafariFixes();
        }

        // Mobile browser fixes
        if (browser.isMobile) {
            addMobileFixes();
        }

        // Firefox fixes
        if (browser.isFirefox) {
            addFirefoxFixes();
        }
    }

    function addIEFixes() {
        console.log('Applying Internet Explorer fixes...');
        
        // Add CSS for IE11
        const ieStyles = document.createElement('style');
        ieStyles.innerHTML = `
            /* IE11 Flexbox fixes */
            .d-flex { display: -ms-flexbox !important; }
            .justify-content-center { -ms-flex-pack: center !important; }
            .align-items-center { -ms-flex-align: center !important; }
            
            /* IE11 Grid fallbacks */
            .row { display: block !important; }
            .col-md-4, .col-md-6, .col-lg-6 { display: inline-block; vertical-align: top; }
            
            /* Remove transforms in IE11 */
            .card:hover { transform: none !important; }
        `;
        document.head.appendChild(ieStyles);

        // Polyfill for CustomEvent
        if (!window.CustomEvent) {
            window.CustomEvent = function(event, params) {
                params = params || {bubbles: false, cancelable: false, detail: undefined};
                const evt = document.createEvent('CustomEvent');
                evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
                return evt;
            };
        }

        // Polyfill for forEach on NodeList
        if (!NodeList.prototype.forEach) {
            NodeList.prototype.forEach = Array.prototype.forEach;
        }
    }

    function addSafariFixes() {
        console.log('Applying Safari fixes...');
        
        // Fix for Safari viewport units
        const safariStyles = document.createElement('style');
        safariStyles.innerHTML = `
            /* Safari viewport fixes */
            .hero-section {
                min-height: -webkit-fill-available;
            }
            
            /* Safari form styling */
            input, textarea, select {
                -webkit-appearance: none;
                border-radius: 0;
            }
            
            /* Safari scroll behavior */
            body {
                -webkit-overflow-scrolling: touch;
            }
        `;
        document.head.appendChild(safariStyles);

        // Fix for Safari date input
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            input.style.webkitAppearance = 'none';
        });
    }

    function addMobileFixes() {
        console.log('Applying mobile browser fixes...');
        
        // Prevent zoom on form inputs
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (parseFloat(window.getComputedStyle(input).fontSize) < 16) {
                input.style.fontSize = '16px';
            }
        });

        // Add touch-friendly spacing
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            if (btn.offsetHeight < 44) {
                btn.style.minHeight = '44px';
                btn.style.paddingTop = '12px';
                btn.style.paddingBottom = '12px';
            }
        });

        // Fix viewport height issues
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', setVH);
    }

    function addFirefoxFixes() {
        console.log('Applying Firefox fixes...');
        
        // Firefox-specific CSS
        const firefoxStyles = document.createElement('style');
        firefoxStyles.innerHTML = `
            /* Firefox scroll behavior */
            html {
                scroll-behavior: smooth;
            }
            
            /* Firefox form styling */
            input[type="number"] {
                -moz-appearance: textfield;
            }
            
            input[type="number"]::-webkit-outer-spin-button,
            input[type="number"]::-webkit-inner-spin-button {
                -webkit-appearance: none;
                margin: 0;
            }
        `;
        document.head.appendChild(firefoxStyles);
    }

    function reportCriticalIssues(testResults) {
        const issues = [];

        // Check for critical browser incompatibilities
        if (browser.isIE && !features.flexbox) {
            issues.push('Internet Explorer detected without flexbox support - layout may be broken');
        }

        if (!features.localStorage) {
            issues.push('Local storage not available - user preferences cannot be saved');
        }

        if (!features.fetch && !window.XMLHttpRequest) {
            issues.push('Neither fetch nor XMLHttpRequest available - AJAX functionality disabled');
        }

        if (browser.isMobile && !features.intersectionObserver) {
            issues.push('Intersection Observer not available - lazy loading disabled');
        }

        // Report issues
        if (issues.length > 0) {
            console.warn('Critical Browser Issues Detected:', issues);
            
            // Show user-friendly warning for serious issues
            if (browser.isIE && !features.flexbox) {
                showBrowserWarning();
            }
        } else {
            console.log('✅ All browser compatibility checks passed');
        }

        return issues;
    }

    function showBrowserWarning() {
        const warning = document.createElement('div');
        warning.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            text-align: center;
            z-index: 9999;
            border-bottom: 1px solid #f5c6cb;
            font-family: Arial, sans-serif;
            font-size: 14px;
        `;
        warning.innerHTML = `
            ⚠️ Your browser may not support all features of this website. 
            For the best experience, please update to a modern browser like Chrome, Firefox, or Edge.
            <button onclick="this.parentNode.remove()" style="margin-left: 10px; background: none; border: 1px solid #721c24; color: #721c24; padding: 2px 8px; cursor: pointer;">
                ✕
            </button>
        `;
        document.body.insertBefore(warning, document.body.firstChild);
    }

    function logBrowserInfo() {
        console.group('🌐 Browser Compatibility Report');
        console.log('Browser:', browser);
        console.log('Features:', features);
        console.log('Viewport:', {
            width: window.innerWidth,
            height: window.innerHeight,
            ratio: window.devicePixelRatio || 1
        });
        console.log('User Agent:', navigator.userAgent);
        console.groupEnd();
    }

    // Export for testing
    window.BrowserTest = {
        browser,
        features,
        runCompatibilityTests,
        testBootstrapCompatibility,
        testFormFunctionality,
        testNavigationBehavior,
        testResponsiveImages
    };

})();