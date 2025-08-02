// GPUSOROBAN Landing Page JavaScript

// Cost calculation functionality
function updateCalculation() {
    const hours = document.getElementById('gpu-hours').value;
    const gpuType = document.getElementById('gpu-type').value;
    
    // Update hours display
    document.getElementById('hours-display').textContent = `${parseInt(hours).toLocaleString()} hours/month`;
    
    // Hourly rates in USD
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
    
    // Calculate annual savings
    const avgCompetitorCost = (awsCost + gcpCost + azureCost) / 3;
    const monthlySavings = avgCompetitorCost - gpusorobanCost;
    const annualSavings = monthlySavings * 12;
    
    document.getElementById('annual-savings').textContent = `$${Math.round(annualSavings).toLocaleString()}`;
}

// Open calculator with smooth scroll and highlight effect
function openCalculator() {
    const calculator = document.getElementById('calculator');
    calculator.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
    
    // Highlight effect
    calculator.style.background = 'linear-gradient(135deg, #1B365D 0%, #FF6B35 100%)';
    setTimeout(() => {
        calculator.style.background = 'linear-gradient(135deg, #1B365D 0%, #2c5282 100%)';
    }, 2000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateCalculation();
    
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
});