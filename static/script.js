// ===== PaddleOCR Land Document Intelligence & Generator — Client Logic =====

const DOM = {
    // Mode Buttons
    modeUploadBtn: () => document.getElementById('mode-upload-btn'),
    modeGenBtn: () => document.getElementById('mode-generate-btn'),
    secUpload: () => document.getElementById('section-upload'),
    secGen: () => document.getElementById('section-generate'),

    // Upload Mode
    uploadZone: () => document.getElementById('upload-zone'),
    fileInput: () => document.getElementById('file-input'),
    imagePreview: () => document.getElementById('image-preview'),
    previewImg: () => document.getElementById('preview-img'),
    removeBtn: () => document.getElementById('remove-btn'),
    ocrBtn: () => document.getElementById('ocr-btn'),
    ocrBtnText: () => document.getElementById('ocr-btn-text'),
    ocrBtnSpinner: () => document.getElementById('ocr-btn-spinner'),
    langSelect: () => document.getElementById('lang-select'),

    // Results View
    docBadgeContainer: () => document.getElementById('doc-badge-container'),
    docBadge: () => document.getElementById('doc-badge'),
    docConfidence: () => document.getElementById('doc-confidence'),
    resultsEmpty: () => document.getElementById('results-empty'),
    annotatedContainer: () => document.getElementById('annotated-container'),
    annotatedImg: () => document.getElementById('annotated-img'),
    statsBar: () => document.getElementById('stats-bar'),
    statLines: () => document.getElementById('stat-lines'),
    statDocType: () => document.getElementById('stat-doc-type'),
    statTime: () => document.getElementById('stat-time'),

    // View Tabs
    viewTabs: () => document.getElementById('view-tabs'),
    tabJsonBtn: () => document.getElementById('tab-json-btn'),
    tabLinesBtn: () => document.getElementById('tab-lines-btn'),
    tabJsonContent: () => document.getElementById('tab-json-content'),
    tabLinesContent: () => document.getElementById('tab-lines-content'),
    jsonViewer: () => document.getElementById('json-viewer'),
    textResults: () => document.getElementById('text-results'),
    copyJsonBtn: () => document.getElementById('copy-json-btn'),
    copyTextBtn: () => document.getElementById('copy-text-btn'),

    // Generator Mode
    docTypeSelect: () => document.getElementById('doc-type-select'),
    payloadEditor: () => document.getElementById('payload-editor'),
    generateBtn: () => document.getElementById('generate-btn'),
    genEmpty: () => document.getElementById('gen-empty'),
    generatedDocImg: () => document.getElementById('generated-doc-img'),
    runGenOcrBtn: () => document.getElementById('run-gen-ocr-btn'),

    // Overlay & Toast
    loadingOverlay: () => document.getElementById('loading-overlay'),
    loadingText: () => document.getElementById('loading-text'),
    toast: () => document.getElementById('toast'),
};

let selectedFile = null;
let defaultPayloads = {};
let generatedBlob = null;
let lastOcrResult = null;

// ===== Init =====
document.addEventListener('DOMContentLoaded', () => {
    setupModeSwitch();
    setupUploadZone();
    setupButtons();
    setupTabs();
    fetchDefaultPayloads();
});

// ===== Mode Switching =====
function setupModeSwitch() {
    DOM.modeUploadBtn().addEventListener('click', () => {
        DOM.modeUploadBtn().classList.add('active');
        DOM.modeGenBtn().classList.remove('active');
        DOM.secUpload().style.display = 'grid';
        DOM.secGen().style.display = 'none';
    });

    DOM.modeGenBtn().addEventListener('click', () => {
        DOM.modeGenBtn().classList.add('active');
        DOM.modeUploadBtn().classList.remove('active');
        DOM.secGen().style.display = 'grid';
        DOM.secUpload().style.display = 'none';
    });
}

// ===== Default Payloads =====
async function fetchDefaultPayloads() {
    try {
        const response = await fetch('/default_payloads');
        if (response.ok) {
            defaultPayloads = await response.json();
            updatePayloadEditor();
        }
    } catch (err) {
        console.error('Error fetching default payloads:', err);
    }
}

function updatePayloadEditor() {
    const selectedType = DOM.docTypeSelect().value;
    const payload = defaultPayloads[selectedType] || {};
    DOM.payloadEditor().value = JSON.stringify(payload, null, 2);
}

// ===== Upload Zone =====
function setupUploadZone() {
    const zone = DOM.uploadZone();
    const input = DOM.fileInput();

    zone.addEventListener('click', () => input.click());
    input.addEventListener('change', (e) => handleFiles(e.target.files));

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });
}

function handleFiles(files) {
    if (!files || files.length === 0) return;
    const file = files[0];
    selectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        DOM.previewImg().src = e.target.result;
        DOM.imagePreview().classList.add('active');
        DOM.ocrBtn().classList.add('visible');
        DOM.uploadZone().style.display = 'none';
    };
    reader.readAsDataURL(file);

    clearResults();
}

// ===== Button Listeners =====
function setupButtons() {
    DOM.removeBtn().addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        DOM.fileInput().value = '';
        DOM.imagePreview().classList.remove('active');
        DOM.ocrBtn().classList.remove('visible');
        DOM.uploadZone().style.display = '';
        clearResults();
    });

    DOM.ocrBtn().addEventListener('click', () => {
        if (selectedFile) runOCR(selectedFile);
    });

    DOM.docTypeSelect().addEventListener('change', updatePayloadEditor);

    DOM.generateBtn().addEventListener('click', generateDocumentImage);

    DOM.runGenOcrBtn().addEventListener('click', () => {
        if (generatedBlob) {
            // Switch to Upload Mode view and run OCR
            DOM.modeUploadBtn().click();
            runOCR(generatedBlob);
        }
    });

    DOM.copyJsonBtn().addEventListener('click', () => {
        if (lastOcrResult && lastOcrResult.structured_payload) {
            copyToClipboard(JSON.stringify(lastOcrResult.structured_payload, null, 2), 'Structured JSON copied!');
        }
    });

    DOM.copyTextBtn().addEventListener('click', () => {
        const items = document.querySelectorAll('.text-result-item .result-text');
        const text = Array.from(items).map(el => el.textContent).join('\n');
        copyToClipboard(text, 'All OCR text lines copied!');
    });
}

// ===== Tabs =====
function setupTabs() {
    DOM.tabJsonBtn().addEventListener('click', () => {
        DOM.tabJsonBtn().classList.add('active');
        DOM.tabLinesBtn().classList.remove('active');
        DOM.tabJsonContent().classList.add('active');
        DOM.tabLinesContent().classList.remove('active');
    });

    DOM.tabLinesBtn().addEventListener('click', () => {
        DOM.tabLinesBtn().classList.add('active');
        DOM.tabJsonBtn().classList.remove('active');
        DOM.tabLinesContent().classList.add('active');
        DOM.tabJsonContent().classList.remove('active');
    });
}

function clearResults() {
    DOM.docBadgeContainer().classList.remove('active');
    DOM.annotatedContainer().classList.remove('active');
    DOM.statsBar().classList.remove('active');
    DOM.viewTabs().classList.remove('active');
    DOM.textResults().innerHTML = '';
    DOM.jsonViewer().textContent = '';
    DOM.resultsEmpty().style.display = '';
}

// ===== Generate Document Image =====
async function generateDocumentImage() {
    const docType = DOM.docTypeSelect().value;
    let customPayload = null;

    try {
        const editorText = DOM.payloadEditor().value.trim();
        if (editorText) customPayload = JSON.parse(editorText);
    } catch (e) {
        showToast('Invalid JSON in payload editor. Using default.', 'error');
    }

    showLoading('Generating Document Image...');

    try {
        const response = await fetch('/generate_doc', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc_type: docType, payload: customPayload }),
        });

        if (!response.ok) throw new Error('Failed to generate document');

        const data = await response.json();
        const base64Img = 'data:image/png;base64,' + data.image_base64;

        DOM.generatedDocImg().src = base64Img;
        DOM.generatedDocImg().style.display = 'block';
        DOM.genEmpty().style.display = 'none';
        DOM.runGenOcrBtn().classList.add('visible');

        // Convert base64 to Blob file for OCR runner
        const fetchRes = await fetch(base64Img);
        generatedBlob = await fetchRes.blob();

        showToast(`Generated official ${docType} document!`, 'success');
    } catch (err) {
        console.error('Generator error:', err);
        showToast(`Generation failed: ${err.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// ===== OCR & Classification =====
async function runOCR(fileOrBlob) {
    showLoading('Running PaddleOCR & Schema Classifier...');

    const formData = new FormData();
    formData.append('image', fileOrBlob, 'document.png');
    formData.append('lang', DOM.langSelect().value);

    try {
        const response = await fetch('/ocr', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.error || `Server error: ${response.status}`);
        }

        const data = await response.json();
        lastOcrResult = data;
        displayResults(data);
        showToast(`Classified as ${data.classified_document_type}`, 'success');
    } catch (err) {
        console.error('OCR error:', err);
        showToast(`OCR Processing failed: ${err.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// ===== Display Results =====
function displayResults(data) {
    const results = data.results || [];
    DOM.resultsEmpty().style.display = 'none';

    // Badge & Stats
    DOM.docBadge().textContent = data.classified_document_type || 'UNKNOWN';
    DOM.docConfidence().textContent = `${(data.classification_confidence * 100).toFixed(0)}% Match`;
    DOM.docBadgeContainer().classList.add('active');

    DOM.statLines().textContent = data.total_lines || 0;
    DOM.statDocType().textContent = data.classified_document_type || 'UNKNOWN';
    DOM.statTime().textContent = `${data.processing_time || 0}s`;
    DOM.statsBar().classList.add('active');

    // Annotated Image
    if (data.annotated_image) {
        DOM.annotatedImg().src = 'data:image/png;base64,' + data.annotated_image;
        DOM.annotatedContainer().classList.add('active');
    }

    // Structured JSON Payload
    const jsonOutput = {
        classified_document_type: data.classified_document_type,
        classification_confidence: data.classification_confidence,
        payload: data.structured_payload,
    };
    DOM.jsonViewer().textContent = JSON.stringify(jsonOutput, null, 2);

    // Raw Lines List
    const textContainer = DOM.textResults();
    textContainer.innerHTML = '';
    results.forEach((r, i) => {
        const conf = (r.confidence * 100).toFixed(1);
        const item = document.createElement('div');
        item.className = 'text-result-item';
        item.innerHTML = `
            <div class="result-text">${escapeHTML(r.text)}</div>
            <div style="font-size: 0.75rem; color: var(--clr-text-muted); margin-top: 4px;">Confidence: ${conf}% | Line #${i + 1}</div>
        `;
        textContainer.appendChild(item);
    });

    DOM.viewTabs().classList.add('active');
    DOM.tabJsonBtn().click(); // Default to Structured JSON tab
}

// ===== Utilities =====
function copyToClipboard(text, successMsg) {
    navigator.clipboard.writeText(text).then(() => {
        showToast(successMsg, 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function showLoading(msg) {
    DOM.loadingText().textContent = msg;
    DOM.loadingOverlay().classList.add('active');
}

function hideLoading() {
    DOM.loadingOverlay().classList.remove('active');
}

let toastTimeout;
function showToast(message, type = 'success') {
    const toast = DOM.toast();
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => toast.classList.remove('show'), 3500);
}
