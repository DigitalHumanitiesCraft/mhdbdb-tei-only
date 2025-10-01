/**
 * MHDBDB Main Website - Interactive Features
 *
 * This script provides smooth scrolling, navigation highlighting,
 * and other interactive enhancements for the main website.
 */

(function() {
    'use strict';

    // ===================================
    // Smooth Scrolling for Navigation
    // ===================================
    function initSmoothScroll() {
        const navLinks = document.querySelectorAll('a[href^="#"]');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');

                // Skip if it's just "#"
                if (href === '#') return;

                e.preventDefault();

                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    const headerHeight = document.querySelector('.site-header')?.offsetHeight || 0;
                    const targetPosition = targetElement.offsetTop - headerHeight - 20;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });

                    // Update URL without jumping
                    history.pushState(null, null, href);
                }
            });
        });
    }

    // ===================================
    // Active Navigation Highlighting
    // ===================================
    function initActiveNavigation() {
        const sections = document.querySelectorAll('.section[id]');
        const navLinks = document.querySelectorAll('.nav-link[href^="#"]');

        if (sections.length === 0 || navLinks.length === 0) return;

        function highlightNavigation() {
            const scrollPosition = window.scrollY;
            const headerHeight = document.querySelector('.site-header')?.offsetHeight || 0;

            sections.forEach(section => {
                const sectionTop = section.offsetTop - headerHeight - 100;
                const sectionBottom = sectionTop + section.offsetHeight;
                const sectionId = section.getAttribute('id');

                if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                    navLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === `#${sectionId}`) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        }

        // Throttle scroll event for performance
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            if (scrollTimeout) {
                window.cancelAnimationFrame(scrollTimeout);
            }
            scrollTimeout = window.requestAnimationFrame(highlightNavigation);
        });

        // Initial highlight
        highlightNavigation();
    }

    // ===================================
    // Card Animation on Scroll
    // ===================================
    function initScrollAnimations() {
        const cards = document.querySelectorAll('.content-card, .stat-card, .feature-card, .doc-card, .contact-card');

        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '0';
                        entry.target.style.transform = 'translateY(20px)';

                        setTimeout(() => {
                            entry.target.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                            entry.target.style.opacity = '1';
                            entry.target.style.transform = 'translateY(0)';
                        }, 100);

                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            cards.forEach(card => {
                observer.observe(card);
            });
        }
    }

    // ===================================
    // External Links - Open in New Tab
    // ===================================
    function initExternalLinks() {
        const externalLinks = document.querySelectorAll('a[href^="http"]');

        externalLinks.forEach(link => {
            if (!link.hasAttribute('target')) {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            }
        });
    }

    // ===================================
    // Scroll to Top Button
    // ===================================
    function initScrollToTop() {
        // Create scroll-to-top button
        const scrollButton = document.createElement('button');
        scrollButton.innerHTML = '↑';
        scrollButton.className = 'scroll-to-top';
        scrollButton.setAttribute('aria-label', 'Scroll to top');
        scrollButton.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: var(--primary-color, #2c5f7f);
            color: white;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease, transform 0.2s ease;
            z-index: 999;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;

        document.body.appendChild(scrollButton);

        // Show/hide button based on scroll position
        window.addEventListener('scroll', () => {
            if (window.scrollY > 500) {
                scrollButton.style.opacity = '1';
                scrollButton.style.visibility = 'visible';
            } else {
                scrollButton.style.opacity = '0';
                scrollButton.style.visibility = 'hidden';
            }
        });

        // Scroll to top on click
        scrollButton.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        // Hover effect
        scrollButton.addEventListener('mouseenter', () => {
            scrollButton.style.transform = 'scale(1.1)';
        });

        scrollButton.addEventListener('mouseleave', () => {
            scrollButton.style.transform = 'scale(1)';
        });
    }

    // ===================================
    // Statistics Counter Animation
    // ===================================
    function initStatsCounter() {
        const statNumbers = document.querySelectorAll('.stat-number');

        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const target = entry.target;
                        const targetNumber = parseInt(target.textContent.replace(/,/g, ''));

                        if (isNaN(targetNumber)) return;

                        animateCounter(target, targetNumber);
                        observer.unobserve(target);
                    }
                });
            }, {
                threshold: 0.5
            });

            statNumbers.forEach(stat => {
                observer.observe(stat);
            });
        }
    }

    function animateCounter(element, targetNumber) {
        const duration = 2000; // 2 seconds
        const steps = 60;
        const stepDuration = duration / steps;
        const increment = targetNumber / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= targetNumber) {
                current = targetNumber;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current).toLocaleString('de-DE');
        }, stepDuration);
    }

    // ===================================
    // Keyboard Navigation Enhancement
    // ===================================
    function initKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Alt + H: Go to home/top
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }

            // Alt + P: Go to playground
            if (e.altKey && e.key === 'p') {
                e.preventDefault();
                window.location.href = 'playground/index.html';
            }
        });
    }

    // ===================================
    // Accessibility Improvements
    // ===================================
    function initAccessibility() {
        // Add skip to main content link
        const skipLink = document.createElement('a');
        skipLink.href = '#about';
        skipLink.className = 'skip-link';
        skipLink.textContent = 'Skip to main content';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 0;
            background: var(--primary-color, #2c5f7f);
            color: white;
            padding: 8px;
            text-decoration: none;
            z-index: 10000;
        `;

        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '0';
        });

        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });

        document.body.insertBefore(skipLink, document.body.firstChild);
    }

    // ===================================
    // Print Functionality
    // ===================================
    function initPrintButton() {
        // Add print button to footer (optional)
        const footer = document.querySelector('.footer-links');
        if (footer) {
            const printButton = document.createElement('a');
            printButton.href = '#';
            printButton.textContent = 'Drucken';
            printButton.addEventListener('click', (e) => {
                e.preventDefault();
                window.print();
            });
            footer.appendChild(printButton);
        }
    }

    // ===================================
    // Initialize All Features
    // ===================================
    function init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initAll);
        } else {
            initAll();
        }
    }

    function initAll() {
        try {
            initSmoothScroll();
            initActiveNavigation();
            initScrollAnimations();
            initExternalLinks();
            initScrollToTop();
            initStatsCounter();
            initKeyboardNavigation();
            initAccessibility();
            initPrintButton();

            console.log('MHDBDB main website initialized successfully');
        } catch (error) {
            console.error('Error initializing MHDBDB website:', error);
        }
    }

    // Start initialization
    init();

})();