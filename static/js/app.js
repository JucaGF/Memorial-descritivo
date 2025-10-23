// Global variables
let selectedFile = null;
let memorialData = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeDropZone();
    initializeFileInput();
});

// Drop zone functionality
function initializeDropZone() {
    const dropZone = document.getElementById('drop-zone');
    
    dropZone.addEventListener('click', () => {
        document.getElementById('file-input').click();
    });
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });
}

// File input functionality
function initializeFileInput() {
    const fileInput = document.getElementById('file-input');
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });
}

// Handle file selection
function handleFileSelection(file) {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Por favor, selecione apenas arquivos PDF.');
        return;
    }
    
    // Validate file size (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('O arquivo é muito grande. Tamanho máximo: 50MB');
        return;
    }
    
    selectedFile = file;
    displayFileInfo(file);
    
    // Hide drop zone, show file info
    document.getElementById('drop-zone').style.display = 'none';
    document.getElementById('file-info').style.display = 'block';
    
    // Enable submit button
    document.getElementById('submit-btn').disabled = false;
}

// Display file information
function displayFileInfo(file) {
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
}

// Remove file
function removeFile() {
    selectedFile = null;
    
    // Show drop zone, hide file info
    document.getElementById('drop-zone').style.display = 'block';
    document.getElementById('file-info').style.display = 'none';
    
    // Disable submit button
    document.getElementById('submit-btn').disabled = true;
    
    // Reset file input
    document.getElementById('file-input').value = '';
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Generate memorial
async function generateMemorial() {
    if (!selectedFile) {
        alert('Por favor, selecione um arquivo PDF primeiro.');
        return;
    }
    
    // Get form data
    const clientId = document.getElementById('client-id').value;
    const includeImages = document.getElementById('include-images').checked;
    const customInstructions = document.getElementById('custom-instructions').value;
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('client_id', clientId);
    formData.append('include_images', includeImages);
    if (customInstructions) {
        formData.append('custom_instructions', customInstructions);
    }
    
    // Hide upload section, show processing
    document.getElementById('upload-section').style.display = 'none';
    document.getElementById('processing-section').style.display = 'block';
    
    // Start processing animation
    simulateProcessing();
    
    try {
        const response = await fetch('/api/v1/generate_memorial', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao processar o arquivo');
        }
        
        const data = await response.json();
        memorialData = data;
        
        // Show results
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        displayError(error.message);
    }
}

// Simulate processing steps
function simulateProcessing() {
    const steps = [
        { id: 'step-1', text: 'Fazendo upload...', progress: 20 },
        { id: 'step-2', text: 'Extraindo dados do PDF...', progress: 40 },
        { id: 'step-3', text: 'Analisando com IA...', progress: 60 },
        { id: 'step-4', text: 'Gerando memorial...', progress: 80 },
        { id: 'step-5', text: 'Revisando documento...', progress: 100 }
    ];
    
    let currentStep = 0;
    
    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            const step = steps[currentStep];
            
            // Update progress
            document.getElementById('processing-status').textContent = step.text;
            document.getElementById('progress-fill').style.width = step.progress + '%';
            
            // Mark step as active
            document.getElementById(step.id).classList.add('active');
            
            // Mark previous steps as completed
            if (currentStep > 0) {
                document.getElementById(steps[currentStep - 1].id).classList.remove('active');
                document.getElementById(steps[currentStep - 1].id).classList.add('completed');
            }
            
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 1000);
}

// Display results
function displayResults(data) {
    // Hide processing, show results
    document.getElementById('processing-section').style.display = 'none';
    document.getElementById('result-section').style.display = 'block';
    
    // Update stats
    document.getElementById('stat-pages').textContent = data.pages_processed || '-';
    document.getElementById('stat-time').textContent = data.processing_time_seconds 
        ? `${data.processing_time_seconds}s` 
        : '-';
    
    // Update project info from structured data
    if (data.structured_data) {
        document.getElementById('stat-project').textContent = 
            data.structured_data.project_name || '-';
        document.getElementById('stat-area').textContent = 
            data.structured_data.area_total_m2 
                ? `${data.structured_data.area_total_m2} m²` 
                : '-';
    } else {
        document.getElementById('stat-project').textContent = '-';
        document.getElementById('stat-area').textContent = '-';
    }
    
    // Display warnings if any
    if (data.warnings && data.warnings.length > 0) {
        const warningsSection = document.getElementById('warnings-section');
        const warningsList = document.getElementById('warnings-list');
        
        warningsList.innerHTML = '';
        data.warnings.forEach(warning => {
            const li = document.createElement('li');
            li.textContent = warning;
            warningsList.appendChild(li);
        });
        
        warningsSection.style.display = 'block';
    }
    
    // Display memorial text
    document.getElementById('memorial-text').textContent = data.memorial_text;
    
    // Scroll to results
    document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
}

// Display error
function displayError(message) {
    // Hide processing, show error
    document.getElementById('processing-section').style.display = 'none';
    document.getElementById('error-section').style.display = 'block';
    
    document.getElementById('error-message').textContent = message;
    
    // Scroll to error
    document.getElementById('error-section').scrollIntoView({ behavior: 'smooth' });
}

// Copy memorial to clipboard
async function copyMemorial() {
    const text = document.getElementById('memorial-text').textContent;
    
    try {
        await navigator.clipboard.writeText(text);
        alert('Memorial copiado para a área de transferência!');
    } catch (err) {
        console.error('Failed to copy:', err);
        alert('Erro ao copiar. Por favor, selecione e copie manualmente.');
    }
}

// Download memorial as text file
function downloadMemorial() {
    if (!memorialData) return;
    
    const text = memorialData.memorial_text;
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = 'memorial_descritivo.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Download complete data as JSON
function downloadJSON() {
    if (!memorialData) return;
    
    const json = JSON.stringify(memorialData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = 'memorial_dados_completos.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Reset form
function resetForm() {
    // Reset file selection
    removeFile();
    
    // Reset form fields
    document.getElementById('client-id').value = 'default';
    document.getElementById('include-images').checked = false;
    document.getElementById('custom-instructions').value = '';
    
    // Hide all sections except upload
    document.getElementById('upload-section').style.display = 'block';
    document.getElementById('processing-section').style.display = 'none';
    document.getElementById('result-section').style.display = 'none';
    document.getElementById('error-section').style.display = 'none';
    
    // Reset processing animation
    document.getElementById('progress-fill').style.width = '0';
    document.getElementById('processing-status').textContent = 'Iniciando processamento...';
    
    // Reset steps
    for (let i = 1; i <= 5; i++) {
        const step = document.getElementById(`step-${i}`);
        step.classList.remove('active', 'completed');
    }
    
    // Clear memorial data
    memorialData = null;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Smooth scroll for navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        if (link.getAttribute('href').startsWith('#')) {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});

