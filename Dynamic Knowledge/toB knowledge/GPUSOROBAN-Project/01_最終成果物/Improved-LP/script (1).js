// Cost Calculator Functionality
function updateCalculation() {
    const hours = document.getElementById('gpu-hours').value;
    const gpuType = document.getElementById('gpu-type').value;
    
    // Update display
    document.getElementById('hours-display').textContent = `${parseInt(hours).toLocaleString()} hours/month`;
    
    // Pricing per hour (in USD)
    const prices = {
        h200: {
            gpusoroban: 2.5,
            aws: 5.2,
            gcp: 4.8,
            azure: 5.1
        },
        a100: {
            gpusoroban: 2.0,
            aws: 4.5,
            gcp: 4.2,
            azure: 4.6
        },
        v100: {
            gpusoroban: 1.2,
            aws: 3.1,
            gcp: 2.8,
            azure: 3.0
        }
    };
    
    const currentPrices = prices[gpuType];
    
    // Calculate monthly costs
    const gpusorobanCost = Math.round(currentPrices.gpusoroban * hours);
    const awsCost = Math.round(currentPrices.aws * hours);
    const gcpCost = Math.round(currentPrices.gcp * hours);
    const azureCost = Math.round(currentPrices.azure * hours);
    
    // Update display
    document.getElementById('gpusoroban-cost').textContent = `$${gpusorobanCost.toLocaleString()}`;
    document.getElementById('aws-cost').textContent = `$${awsCost.toLocaleString()}`;
    document.getElementById('gcp-cost').textContent = `$${gcpCost.toLocaleString()}`;
    document.getElementById('azure-cost').textContent = `$${azureCost.toLocaleString()}`;
    
    // Calculate differences
    document.getElementById('aws-diff').textContent = `+$${(awsCost - gpusorobanCost).toLocaleString()}`;
    document.getElementById('gcp-diff').textContent = `+$${(gcpCost - gpusorobanCost).toLocaleString()}`;
    document.getElementById('azure-diff').textContent = `+$${(azureCost - gpusorobanCost).toLocaleString()}`;
    
    // Calculate annual savings (average of competitors)
    const avgCompetitorCost = (awsCost + gcpCost + azureCost) / 3;
    const monthlySavings = avgCompetitorCost - gpusorobanCost;
    const annualSavings = monthlySavings * 12;
    
    document.getElementById('annual-savings').textContent = `$${Math.round(annualSavings).toLocaleString()}`;
}

// Initialize calculator on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCalculation();
    
    // Smooth scrolling for navigation links
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
    
    // Header scroll effect
    let lastScroll = 0;
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.98)';
            header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
        } else {
            header.style.background = 'rgba(255, 255, 255, 0.95)';
            header.style.boxShadow = 'none';
        }
        
        lastScroll = currentScroll;
    });
    
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.value-layer, .story-card, .trust-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.8s ease';
        observer.observe(el);
    });
});

// Open calculator modal or scroll to calculator
function openCalculator() {
    const calculator = document.getElementById('calculator');
    calculator.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
    
    // Add a highlight effect
    calculator.style.background = 'linear-gradient(135deg, #1B365D 0%, #FF6B35 100%)';
    setTimeout(() => {
        calculator.style.background = 'linear-gradient(135deg, #1B365D 0%, #2c5282 100%)';
    }, 2000);
}

// Form handling (placeholder)
function handleFormSubmit(formType) {
    // In a real implementation, this would send data to your backend
    alert(`Thank you for your interest! We'll contact you within 24 hours.`);
}

// Add interactive hover effects
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to cards
    document.querySelectorAll('.story-card, .trust-item').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 30px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.08)';
        });
    });
    
    // Add parallax effect to hero background
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroImg = document.querySelector('.hero-bg-img');
        if (heroImg && scrolled < window.innerHeight) {
            heroImg.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    });
});

// Language switching (placeholder)
function switchLanguage(lang) {
    // In a real implementation, this would change the language
    console.log(`Switching to ${lang}`);
    
    // Update active state
    document.querySelectorAll('.lang-switch span').forEach(span => {
        span.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Performance monitoring
function trackPerformance() {
    // Track page load performance
    window.addEventListener('load', () => {
        const perfData = performance.getEntriesByType('navigation')[0];
        console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart);
    });
    
    // Track user engagement
    let engagementTime = 0;
    let startTime = Date.now();
    
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            engagementTime += Date.now() - startTime;
        } else {
            startTime = Date.now();
        }
    });
    
    window.addEventListener('beforeunload', () => {
        engagementTime += Date.now() - startTime;
        console.log('Total engagement time:', engagementTime / 1000, 'seconds');
    });
}

// Initialize performance tracking
trackPerformance();