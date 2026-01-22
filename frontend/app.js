// ===== ELEMENT REFERENCES =====
const textInput = document.getElementById('textInput');
const fileInput = document.getElementById('fileInput');
const originalInput = document.getElementById('originalInput');
const dropZone = document.getElementById('dropZone');
const originalDropZone = document.getElementById('originalDropZone');
const browseBtn = document.getElementById('browseBtn');
const origBrowseBtn = document.getElementById('origBrowseBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const origToggle = document.getElementById('origToggle');
const statusMessage = document.getElementById('statusMessage');
const loadingOverlay = document.getElementById('loadingOverlay');
const resultsSection = document.getElementById('resultsSection');
const uploadSection = document.getElementById('uploadSection');
const fileInfo = document.getElementById('fileInfo');
const originalFileInfo = document.getElementById('originalFileInfo');
const originalSection = document.getElementById('originalSection');
const wordCount = document.getElementById('wordCount');

// Tab buttons
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Analysis tabs
const analysisTabs = document.querySelectorAll('.analysis-tab');
const analysisContents = document.querySelectorAll('.analysis-content');

// Step indicators
const steps = document.querySelectorAll('.step');

// ===== GLOBAL STATE =====
let currentResults = null;
let selectedFile = null;
let selectedOriginalFile = null;

// ===== CONSTANTS =====
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

const CLASSIFICATION_COLORS = {
    'MINIMAL': { bg: '#10B981', text: '#ffffff' },
    'LOW': { bg: '#3B82F6', text: '#ffffff' },
    'MODERATE': { bg: '#F59E0B', text: '#ffffff' },
    'HIGH': { bg: '#EF4444', text: '#ffffff' },
    'CRITICAL': { bg: '#7F1D1D', text: '#ffffff' }
};

// ===== UTILITY FUNCTIONS =====
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function countWords(text) {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
}

function updateStatus(message, icon = 'info-circle') {
    const statusIcon = statusMessage.querySelector('i');
    const statusText = statusMessage.querySelector('span');
    statusIcon.className = `fas fa-${icon}`;
    statusText.textContent = message;
}

function updateStepIndicator(step) {
    steps.forEach((s, index) => {
        const stepNum = index + 1;
        s.classList.remove('active', 'completed');

        if (stepNum < step) {
            s.classList.add('completed');
        } else if (stepNum === step) {
            s.classList.add('active');
        }
    });
}

// ===== WORD COUNTER =====
if (textInput) {
    textInput.addEventListener('input', () => {
        const words = countWords(textInput.value);
        wordCount.textContent = `${words} words`;

        if (words >= 100) {
            wordCount.style.color = 'var(--success)';
        } else {
            wordCount.style.color = 'var(--warning)';
        }
    });
}

// ===== TAB SWITCHING =====
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTab = btn.dataset.tab;

        // Update buttons
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update content
        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === `${targetTab}Tab`) {
                content.classList.add('active');
            }
        });

        updateStatus('Ready to analyze');
    });
});

// ===== ANALYSIS TABS =====
analysisTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetTab = tab.dataset.analysisTab;

        // Update tabs
        analysisTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update content
        analysisContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === `${targetTab}Tab`) {
                content.classList.add('active');
            }
        });
    });
});

// ===== FILE UPLOAD HANDLING =====
function setupDropZone(zone, input, infoElement, fileVar) {
    zone.addEventListener('click', () => {
        input.click();
    });

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');

        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileSelection(file, input, infoElement, fileVar);
        }
    });

    input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileSelection(file, input, infoElement, fileVar);
        }
    });
}

function handleFileSelection(file, input, infoElement, fileVar) {
    if (file.size > MAX_FILE_SIZE) {
        updateStatus(`File too large. Maximum size is ${formatFileSize(MAX_FILE_SIZE)}`, 'exclamation-triangle');
        return;
    }

    if (fileVar === 'main') {
        selectedFile = file;
    } else {
        selectedOriginalFile = file;
    }

    // Show file info
    infoElement.innerHTML = `
        <i class="fas fa-file"></i>
        <strong>${file.name}</strong>
        <span>(${formatFileSize(file.size)})</span>
    `;
    infoElement.classList.add('show');

    updateStatus('File selected successfully', 'check-circle');
}

setupDropZone(dropZone, fileInput, fileInfo, 'main');
setupDropZone(originalDropZone, originalInput, originalFileInfo, 'original');

browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

origBrowseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    originalInput.click();
});

// ===== ORIGINAL FILE TOGGLE =====
origToggle.addEventListener('change', () => {
    if (origToggle.checked) {
        originalSection.classList.remove('hidden');
    } else {
        originalSection.classList.add('hidden');
        selectedOriginalFile = null;
        originalInput.value = '';
        originalFileInfo.classList.remove('show');
    }
});

// ===== ANALYZE BUTTON =====
analyzeBtn.addEventListener('click', async () => {
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;

    // Validate input
    let hasContent = false;
    const formData = new FormData();

    if (activeTab === 'paste') {
        const text = textInput.value.trim();
        if (text) {
            formData.append('text', text);
            hasContent = true;
        }
    } else if (activeTab === 'upload') {
        if (selectedFile) {
            formData.append('file', selectedFile);
            hasContent = true;
        }
    }

    if (!hasContent) {
        updateStatus('Please provide text or upload a file', 'exclamation-triangle');
        return;
    }

    // Add original file if selected
    if (selectedOriginalFile) {
        formData.append('original_file', selectedOriginalFile);
    }

    // Show loading
    updateStepIndicator(2);
    loadingOverlay.classList.remove('hidden');
    analyzeBtn.disabled = true;

    // Animate loading steps
    animateLoadingSteps();

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Analysis failed');
        }

        const data = await response.json();
        currentResults = data;

        // Hide loading, show results
        loadingOverlay.classList.add('hidden');
        updateStepIndicator(3);

        // Render results
        renderResults(data);

        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);

    } catch (error) {
        loadingOverlay.classList.add('hidden');
        updateStatus('Analysis failed. Please try again.', 'exclamation-triangle');
        console.error(error);
    } finally {
        analyzeBtn.disabled = false;
    }
});

// ===== LOADING ANIMATION =====
function animateLoadingSteps() {
    const loadingSteps = document.querySelectorAll('.loading-step');
    let currentStep = 0;

    const interval = setInterval(() => {
        if (currentStep < loadingSteps.length) {
            loadingSteps.forEach(step => step.classList.remove('active'));
            loadingSteps[currentStep].classList.add('active');

            // Update icon
            const icon = loadingSteps[currentStep].querySelector('i');
            if (currentStep > 0) {
                const prevIcon = loadingSteps[currentStep - 1].querySelector('i');
                prevIcon.className = 'fas fa-check';
            }
            icon.className = 'fas fa-spinner fa-spin';

            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 800);
}

// ===== RENDER RESULTS =====
function renderResults(data) {
    resultsSection.classList.remove('hidden');

    // Render score
    renderScore(data);

    // Render stats
    renderQuickStats(data);

    // Render category chart
    renderCategoryChart(data.categories || {});

    // Render patterns
    renderPatterns(data.composite_patterns || [], data.advanced_analysis?.pattern_correlations?.correlation_patterns || []);

    // Render human indicators
    renderHumanIndicators(data.human_indicators || []);

    // Render markers table
    renderMarkersTable(data.categories || {});

    // Render advanced metrics
    renderAdvancedMetrics(data.advanced_analysis || {});

    // Render evidence
    renderEvidence(data.evidence || []);
}

// ===== RENDER SCORE =====
function renderScore(data) {
    const score = data.score || 0;
    const classification = data.classification || 'LOW';
    const confidence = data.confidence || 'MEDIUM';

    // Update score value
    document.getElementById('scoreValue').textContent = Math.round(score);

    // Animate score ring
    const scoreRing = document.getElementById('scoreRing');
    const circumference = 2 * Math.PI * 85; // radius = 85
    const offset = circumference - (score / 100) * circumference;

    // Add gradient definition if not exists
    if (!document.querySelector('#scoreGradient')) {
        const svg = scoreRing.closest('svg');
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        defs.innerHTML = `
            <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#10B981;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#F59E0B;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#EF4444;stop-opacity:1" />
            </linearGradient>
        `;
        svg.insertBefore(defs, svg.firstChild);
    }

    setTimeout(() => {
        scoreRing.style.strokeDashoffset = offset;
    }, 100);

    // Update classification badge
    const badge = document.getElementById('classificationBadge');
    const colors = CLASSIFICATION_COLORS[classification] || CLASSIFICATION_COLORS['LOW'];
    badge.textContent = classification + ' RISK';
    badge.style.backgroundColor = colors.bg;
    badge.style.color = colors.text;

    // Update other score details
    document.getElementById('confidenceValue').textContent = confidence;
    document.getElementById('docType').textContent = data.meta?.document?.document_type || 'General';
    document.getElementById('docWords').textContent = data.meta?.document?.word_count || 0;

    // Update recommendation
    document.getElementById('recommendationText').textContent = data.recommendation || 'No recommendation available';

    // Color recommendation box based on classification
    const recBox = document.getElementById('recommendationBox');
    if (classification === 'CRITICAL' || classification === 'HIGH') {
        recBox.style.borderLeftColor = 'var(--danger)';
    } else if (classification === 'MODERATE') {
        recBox.style.borderLeftColor = 'var(--warning)';
    } else {
        recBox.style.borderLeftColor = 'var(--success)';
    }
}

// ===== RENDER QUICK STATS =====
function renderQuickStats(data) {
    const categories = data.categories || {};
    const markers = collectAllMarkers(categories);
    const triggered = markers.filter(m => (m.count > 0 || m.score > 0)).length;
    const categoriesActive = Object.values(categories).filter(cat => cat.score > 0).length;

    document.getElementById('triggeredCount').textContent = triggered;
    document.getElementById('categoriesActive').textContent = categoriesActive;
    document.getElementById('humanIndicators').textContent = (data.human_indicators || []).length;

    const patternCount = (data.composite_patterns || []).length +
                        ((data.advanced_analysis?.pattern_correlations?.pattern_count) || 0);
    document.getElementById('patternMatches').textContent = patternCount;
}

// ===== COLLECT ALL MARKERS =====
function collectAllMarkers(categories) {
    const markers = [];
    Object.entries(categories).forEach(([catId, cat]) => {
        (cat.markers || []).forEach(marker => {
            markers.push({
                ...marker,
                category: catId
            });
        });
    });
    return markers;
}

// ===== RENDER CATEGORY CHART =====
function renderCategoryChart(categories) {
    const chartContainer = document.getElementById('categoryChart');
    chartContainer.innerHTML = '';

    if (Object.keys(categories).length === 0) {
        chartContainer.innerHTML = '<p style="color: var(--text-secondary);">No category data available</p>';
        return;
    }

    const categoryCaps = {
        'A': 450, 'B': 270, 'C': 225, 'D': 125, 'E': 155,
        'F': 100, 'G': 125, 'H': 180, 'I': 120, 'J': 105
    };

    Object.entries(categories).sort((a, b) => a[0].localeCompare(b[0])).forEach(([catId, cat]) => {
        const score = cat.score || 0;
        const cap = categoryCaps[catId] || 100;
        const percentage = Math.min(100, (score / cap) * 100);

        const barDiv = document.createElement('div');
        barDiv.className = 'category-bar';
        barDiv.innerHTML = `
            <div class="category-name">Category ${catId}</div>
            <div class="bar-container">
                <div class="bar-fill" style="width: ${percentage}%"></div>
            </div>
            <div class="category-score">${score.toFixed(1)} / ${cap}</div>
        `;

        chartContainer.appendChild(barDiv);
    });
}

// ===== RENDER PATTERNS =====
function renderPatterns(compositePatterns, correlationPatterns) {
    const container = document.getElementById('compositePatterns');
    container.innerHTML = '';

    const allPatterns = [...compositePatterns, ...(correlationPatterns || [])];

    if (allPatterns.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 16px;">No suspicious patterns detected</p>';
        return;
    }

    allPatterns.forEach(pattern => {
        const item = document.createElement('div');
        item.className = 'pattern-item';
        item.innerHTML = `
            <h5>${pattern.name || pattern.pattern_name}</h5>
            <p>${pattern.description}</p>
            <div class="pattern-meta">
                <span><i class="fas fa-plus"></i> +${pattern.bonus || pattern.bonus_score} points</span>
                <span><i class="fas fa-flag"></i> Auto: ${pattern.auto_classify}</span>
            </div>
        `;
        container.appendChild(item);
    });
}

// ===== RENDER HUMAN INDICATORS =====
function renderHumanIndicators(indicators) {
    const container = document.getElementById('humanIndicators');
    container.innerHTML = '';

    if (indicators.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 16px; font-size: 13px; text-align: center;">No human writing indicators found</p>';
        return;
    }

    indicators.forEach(indicator => {
        const item = document.createElement('div');
        item.className = 'indicator-item human-positive';
        item.innerHTML = `
            <div class="indicator-header">
                <h5>${indicator.id.replace(/_/g, ' ')}</h5>
                <span class="badge badge-success">
                    <i class="fas fa-check-circle"></i> Human Writing Detected
                </span>
            </div>
            <p class="indicator-description">${indicator.description}</p>
            <div class="indicator-meta">
                <div class="score-reduction">
                    <i class="fas fa-arrow-down"></i>
                    <strong>Reduces AI Score by ${indicator.score_reduction} points</strong>
                </div>
                <div class="rationale-text">
                    <i class="fas fa-info-circle"></i>
                    ${indicator.rationale}
                </div>
            </div>
        `;
        container.appendChild(item);
    });
}

// ===== RENDER MARKERS TABLE =====
function renderMarkersTable(categories) {
    const container = document.getElementById('markersTable');
    const toggle = document.getElementById('showOnlyTriggered');

    const markers = collectAllMarkers(categories);

    function render() {
        const showOnlyTriggered = toggle ? toggle.checked : false;
        const displayMarkers = showOnlyTriggered
            ? markers.filter(m => m.count > 0 || m.score > 0)
            : markers;

        container.innerHTML = '';

        if (displayMarkers.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary); padding: 16px;">No markers to display</p>';
            return;
        }

        displayMarkers.forEach(marker => {
            const isDetected = marker.count > 0 || marker.score > 0;
            const row = document.createElement('div');
            row.className = 'marker-row';
            row.innerHTML = `
                <div class="marker-id">${marker.id}</div>
                <div class="marker-name">${marker.name}</div>
                <div class="marker-count">${marker.count || 0}</div>
                <div class="marker-score">${(marker.score || 0).toFixed(1)}</div>
                <div>
                    <span class="marker-status ${isDetected ? 'detected' : 'clear'}">
                        ${isDetected ? 'Detected' : 'Clear'}
                    </span>
                </div>
            `;
            container.appendChild(row);
        });
    }

    render();

    if (toggle) {
        toggle.addEventListener('change', render);
    }
}

// ===== RENDER ADVANCED METRICS =====
function renderAdvancedMetrics(advanced) {
    // Lexical Diversity
    const lexicalContainer = document.getElementById('lexicalMetrics');
    if (lexicalContainer && advanced.lexical_diversity) {
        const lex = advanced.lexical_diversity;
        lexicalContainer.innerHTML = `
            <div class="metric-row">
                <span class="metric-name">Type-Token Ratio</span>
                <span class="metric-num">${lex.type_token_ratio || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">MTLD Score</span>
                <span class="metric-num">${lex.mtld || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Hapax Ratio</span>
                <span class="metric-num">${lex.hapax_legomena_ratio || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Simpson's Index</span>
                <span class="metric-num">${lex.simpson_index || 0}</span>
            </div>
        `;
    }

    // Readability
    const readabilityContainer = document.getElementById('readabilityMetrics');
    if (readabilityContainer && advanced.readability_metrics) {
        const read = advanced.readability_metrics;
        readabilityContainer.innerHTML = `
            <div class="metric-row">
                <span class="metric-name">Flesch Reading Ease</span>
                <span class="metric-num">${read.flesch_reading_ease || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Gunning Fog Index</span>
                <span class="metric-num">${read.gunning_fog || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Flesch-Kincaid Grade</span>
                <span class="metric-num">${read.flesch_kincaid_grade || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">ARI Score</span>
                <span class="metric-num">${read.ari || 0}</span>
            </div>
        `;
    }

    // Burstiness
    const burstinessContainer = document.getElementById('burstinessMetrics');
    if (burstinessContainer && advanced.burstiness) {
        const burst = advanced.burstiness;
        burstinessContainer.innerHTML = `
            <div class="metric-row">
                <span class="metric-name">Burstiness Score</span>
                <span class="metric-num">${burst.burstiness_score || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Perplexity Variance</span>
                <span class="metric-num">${burst.perplexity_variance || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Complexity Variation</span>
                <span class="metric-num">${burst.complexity_variation || 0}</span>
            </div>
        `;
    }

    // Statistical
    const statContainer = document.getElementById('statisticalMetrics');
    if (statContainer && advanced.statistical_anomalies) {
        const stats = advanced.statistical_anomalies;
        statContainer.innerHTML = `
            <div class="metric-row">
                <span class="metric-name">Text Entropy</span>
                <span class="metric-num">${advanced.text_entropy || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Anomalies Found</span>
                <span class="metric-num">${stats.anomaly_count || 0}</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Anomaly Score</span>
                <span class="metric-num">${stats.anomaly_score || 0}</span>
            </div>
        `;
    }

    // Bayesian Analysis
    const bayesianContainer = document.getElementById('bayesianAnalysis');
    if (bayesianContainer && advanced.bayesian_analysis) {
        const bayes = advanced.bayesian_analysis;
        bayesianContainer.innerHTML = `
            <div class="bayesian-item">
                <div class="bayesian-value">${bayes.posterior_probability?.toFixed(1) || 0}%</div>
                <div class="bayesian-label">Posterior Probability</div>
            </div>
            <div class="bayesian-item">
                <div class="bayesian-value">${bayes.prior_probability?.toFixed(1) || 0}%</div>
                <div class="bayesian-label">Prior Probability</div>
            </div>
            <div class="bayesian-item">
                <div class="bayesian-value">${bayes.likelihood_ratio?.toFixed(2) || 0}</div>
                <div class="bayesian-label">Likelihood Ratio</div>
            </div>
        `;
    }
}

// ===== RENDER EVIDENCE =====
function renderEvidence(evidence) {
    const container = document.getElementById('evidenceList');
    container.innerHTML = '';

    if (evidence.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 16px;">No text excerpts flagged</p>';
        return;
    }

    evidence.forEach(item => {
        const div = document.createElement('div');
        div.className = 'evidence-item';
        div.innerHTML = `
            <div class="evidence-marker">Marker ${item.marker_id}</div>
            <div class="evidence-text">"${item.text}"</div>
        `;
        container.appendChild(div);
    });
}

// ===== EXPORT FUNCTIONALITY =====
const exportBtn = document.getElementById('exportBtn');
if (exportBtn) {
    exportBtn.addEventListener('click', () => {
        if (!currentResults) {
            alert('No results to export');
            return;
        }

        const dataStr = JSON.stringify(currentResults, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `ai-detection-report-${Date.now()}.json`;
        link.click();
        URL.revokeObjectURL(url);
    });
}

// ===== TOOLTIP FUNCTIONALITY =====
const tooltipIcons = document.querySelectorAll('[data-tooltip]');
const tooltipPopup = document.getElementById('tooltipPopup');

tooltipIcons.forEach(icon => {
    icon.addEventListener('mouseenter', (e) => {
        const text = icon.dataset.tooltip;
        tooltipPopup.textContent = text;
        tooltipPopup.style.display = 'block';

        const rect = icon.getBoundingClientRect();
        tooltipPopup.style.top = (rect.bottom + 10) + 'px';
        tooltipPopup.style.left = (rect.left + rect.width / 2 - tooltipPopup.offsetWidth / 2) + 'px';
    });

    icon.addEventListener('mouseleave', () => {
        tooltipPopup.style.display = 'none';
    });
});

// ===== HELP & ABOUT FUNCTIONS =====
function showHelp() {
    alert(`AI Content Detector Help

How to Use:
1. Choose your input method (Paste Text or Upload File)
2. Paste your text or upload a document (.docx, .pdf, .txt, .md)
3. Optionally upload an original document for comparison
4. Click "Analyze Content" to start the analysis
5. Review the results in the comprehensive report

The system checks for 50+ markers across 10 categories and uses advanced AI detection algorithms including:
- Lexical diversity analysis
- Readability metrics
- Pattern correlation
- Bayesian probability
- Statistical anomalies

For more information, contact support.`);
}

function showAbout() {
    alert(`AWARE AI Detection Framework v2.0 Enhanced

The AWARE (AI Writing Analysis & Risk Evaluation) Framework is a comprehensive system for detecting AI-generated content using multiple analytical dimensions:

• 10 Detection Categories (A-J)
• 50+ Individual Markers
• Bayesian Statistical Analysis
• Advanced Lexical & Readability Metrics
• Pattern Correlation Detection
• Multi-dimensional Analysis

Version: 2.0 Enhanced
Status: Production Ready
Powered by Advanced Analytics

© 2025 AWARE Framework`);
}

// ===== INITIALIZATION =====
updateStepIndicator(1);
updateStatus('Ready to analyze');

console.log('✅ AI Content Detector v2.0 Enhanced - Loaded');
