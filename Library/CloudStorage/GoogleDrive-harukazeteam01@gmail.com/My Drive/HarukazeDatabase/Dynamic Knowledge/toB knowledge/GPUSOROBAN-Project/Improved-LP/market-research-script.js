// Market Research Report JavaScript

// Country switching functionality
function showCountry(countryId) {
    // Hide all country contents
    const allContents = document.querySelectorAll('.country-content');
    allContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tabs
    const allTabs = document.querySelectorAll('.tab-btn');
    allTabs.forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected country content
    const selectedContent = document.getElementById(countryId);
    if (selectedContent) {
        selectedContent.classList.add('active');
    }
    
    // Activate selected tab
    const selectedTab = document.querySelector(`[onclick="showCountry('${countryId}')"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
}

// Chart configurations and data
const chartData = {
    marketSize: {
        labels: ['インド', 'ベトナム', 'タイ', 'インドネシア', '台湾'],
        data2025: [1200, 420, 380, 320, 480],
        data2026: [1740, 621, 513, 442, 634],
        data2027: [2523, 918, 693, 610, 837]
    },
    roiProjection: {
        labels: ['2025年', '2026年', '2027年'],
        investment: [5, 8, 15],
        revenue: [12, 45, 125],
        profit: [3, 15, 42]
    }
};

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeMarketSizeChart();
    initializeROIChart();
    setupScrollAnimations();
});

// Market Size Chart
function initializeMarketSizeChart() {
    const ctx = document.getElementById('marketSizeChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.marketSize.labels,
            datasets: [
                {
                    label: '2025年 (予測)',
                    data: chartData.marketSize.data2025,
                    backgroundColor: 'rgba(255, 107, 53, 0.8)',
                    borderColor: '#FF6B35',
                    borderWidth: 2,
                    borderRadius: 8
                },
                {
                    label: '2026年 (予測)',
                    data: chartData.marketSize.data2026,
                    backgroundColor: 'rgba(27, 54, 93, 0.8)',
                    borderColor: '#1B365D',
                    borderWidth: 2,
                    borderRadius: 8
                },
                {
                    label: '2027年 (予測)',
                    data: chartData.marketSize.data2027,
                    backgroundColor: 'rgba(100, 116, 139, 0.8)',
                    borderColor: '#64748b',
                    borderWidth: 2,
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '市場規模推移（単位：百万ドル）',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#1B365D'
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(27, 54, 93, 0.9)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y + 'M';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value + 'M';
                        },
                        font: {
                            size: 11
                        },
                        color: '#64748b'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        },
                        color: '#64748b'
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

// ROI Projection Chart
function initializeROIChart() {
    const ctx = document.getElementById('roiChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.roiProjection.labels,
            datasets: [
                {
                    label: '投資額',
                    data: chartData.roiProjection.investment,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: '#ef4444',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 8
                },
                {
                    label: '売上',
                    data: chartData.roiProjection.revenue,
                    borderColor: '#FF6B35',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#FF6B35',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 8
                },
                {
                    label: '利益',
                    data: chartData.roiProjection.profit,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '3年間収益予測（単位：百万ドル）',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: 'white'
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        color: 'white',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    titleColor: '#1B365D',
                    bodyColor: '#1B365D',
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y + 'M';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value + 'M';
                        },
                        font: {
                            size: 11
                        },
                        color: 'rgba(255, 255, 255, 0.8)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        },
                        color: 'rgba(255, 255, 255, 0.8)'
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// Counter animation removed per user request

// Setup scroll animations
function setupScrollAnimations() {
    const animatedElements = document.querySelectorAll('.summary-card, .insight, .stat-card, .target-item, .competitor-card, .sequence-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'all 0.6s ease';
        observer.observe(element);
    });
}

// Smooth scrolling for navigation
function setupSmoothScrolling() {
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
}

// Initialize smooth scrolling
document.addEventListener('DOMContentLoaded', setupSmoothScrolling);

// Add interactive features for competitor bars
function setupCompetitorBars() {
    const competitorBars = document.querySelectorAll('.competitor-bar .bar');
    
    competitorBars.forEach(bar => {
        bar.addEventListener('mouseenter', () => {
            bar.style.transform = 'scaleY(1.2)';
            bar.style.boxShadow = '0 4px 15px rgba(255, 107, 53, 0.3)';
        });
        
        bar.addEventListener('mouseleave', () => {
            bar.style.transform = 'scaleY(1)';
            bar.style.boxShadow = 'none';
        });
    });
}

// Add loading states for charts
function showLoadingState(chartId) {
    const container = document.querySelector(`#${chartId}`);
    if (container) {
        container.innerHTML = '<div style="text-align: center; padding: 2rem; color: #64748b;"><i class="fas fa-spinner fa-spin"></i> データを読み込み中...</div>';
    }
}

// Export data functionality
function exportData(format = 'json') {
    const data = {
        marketSize: chartData.marketSize,
        roiProjection: chartData.roiProjection,
        exportedAt: new Date().toISOString(),
        format: format
    };
    
    let content, mimeType, fileName;
    
    switch (format) {
        case 'json':
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
            fileName = 'market-research-data.json';
            break;
        case 'csv':
            content = convertToCSV(data);
            mimeType = 'text/csv';
            fileName = 'market-research-data.csv';
            break;
        default:
            console.error('Unsupported format:', format);
            return;
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function convertToCSV(data) {
    const headers = ['Country', '2025', '2026', '2027'];
    const rows = [headers.join(',')];
    
    data.marketSize.labels.forEach((label, index) => {
        const row = [
            label,
            data.marketSize.data2025[index],
            data.marketSize.data2026[index],
            data.marketSize.data2027[index]
        ];
        rows.push(row.join(','));
    });
    
    return rows.join('\n');
}

// Setup all interactive features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setupCompetitorBars();
    
    // Add export buttons if needed
    const exportContainer = document.querySelector('.roi-projection .container');
    if (exportContainer && !document.querySelector('.export-buttons')) {
        const exportDiv = document.createElement('div');
        exportDiv.className = 'export-buttons';
        exportDiv.style.textAlign = 'center';
        exportDiv.style.marginTop = '2rem';
        exportDiv.innerHTML = `
            <button onclick="exportData('json')" style="margin: 0 0.5rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; cursor: pointer;">
                <i class="fas fa-download"></i> JSONエクスポート
            </button>
            <button onclick="exportData('csv')" style="margin: 0 0.5rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; cursor: pointer;">
                <i class="fas fa-table"></i> CSVエクスポート
            </button>
        `;
        exportContainer.appendChild(exportDiv);
    }
});

// Print functionality
function printReport() {
    window.print();
}

// Add keyboard navigation
document.addEventListener('keydown', function(e) {
    if (e.altKey) {
        switch(e.key) {
            case '1':
                showCountry('india');
                break;
            case '2':
                showCountry('vietnam');
                break;
            case '3':
                showCountry('thailand');
                break;
            case '4':
                showCountry('indonesia');
                break;
            case '5':
                showCountry('taiwan');
                break;
        }
    }
});