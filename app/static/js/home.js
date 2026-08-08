document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateStats();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        observer.observe(statsSection);
    }
});

function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');

    statNumbers.forEach(stat => {
        const targetText = stat.innerText;
        const isPercentage = targetText.includes('%');
        const isTime = targetText.includes('<');
        let targetValue;

        if (isPercentage) {
            targetValue = parseInt(targetText);
        } else if (isTime) {
            targetValue = parseInt(targetText.replace('<', '').replace('s', ''));
        } else {
            targetValue = parseInt(targetText);
        }

        if (isNaN(targetValue)) return;

        let currentValue = 0;
        const duration = 2000;
        const increment = targetValue / (duration / 16);

        const updateCounter = () => {
            currentValue += increment;
            if (currentValue < targetValue) {
                if (isPercentage) {
                    stat.innerText = Math.floor(currentValue) + '%+';
                } else if (isTime) {
                    stat.innerText = '<' + Math.floor(currentValue) + 's';
                } else {
                    stat.innerText = Math.floor(currentValue);
                }
                requestAnimationFrame(updateCounter);
            } else {
                stat.innerText = targetText;
            }
        };

        updateCounter();
    });
}

document.querySelectorAll('.disease-card').forEach(card => {
    card.addEventListener('mouseenter', function () {
        this.style.transform = 'scale(1.05)';
    });

    card.addEventListener('mouseleave', function () {
        this.style.transform = 'scale(1)';
    });
});

function trackPageView() {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'page_view', {
            page_title: 'Home',
            page_location: window.location.href
        });
    }
}

const getStartedBtn = document.querySelector('.btn-get-started');
if (getStartedBtn) {
    getStartedBtn.addEventListener('mouseenter', function () {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = '/predict';
        document.head.appendChild(link);
    });
}

console.log('Home page loaded');