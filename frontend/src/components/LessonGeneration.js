/**
 * LessonGenerationComponent
 * 
 * Frontend component for AI-Assisted Interactive Lesson Generation.
 * Allows administrators to upload textbook chapters and manage lesson generation.
 */

import { apiRequest } from '../utils/api.js';
import { showNotification } from './Notification.js';

export class LessonGenerationComponent {
    constructor() {
        this.chapters = [];
        this.lessons = [];
        this.currentView = 'chapters'; // chapters, lessons, generate
        this.aiStatus = null;
        this.selectedPDF = null;
        this.currentUploadMethod = 'pdf'; // pdf or text
    }

    /**
     * Render the main lesson generation interface
     */
    async render() {
        // Load AI status first
        await this.loadAIStatus();
        
        const container = document.createElement('div');
        container.className = 'lesson-generation-container';
        container.innerHTML = `
            ${this.renderAIStatusBanner()}
            
            <div class="lesson-gen-header">
                <h2>📚 AI-Assisted Lesson Generation</h2>
                <p>Transform textbook content into interactive digital lessons</p>
            </div>

            <div class="lesson-gen-tabs">
                <button class="tab-btn active" data-view="chapters">
                    📖 Textbook Chapters
                </button>
                <button class="tab-btn" data-view="lessons">
                    ✨ Generated Lessons
                </button>
                <button class="tab-btn" data-view="upload">
                    ⬆️ Upload Chapter
                </button>
            </div>

            <div class="lesson-gen-content">
                <div id="chapters-view" class="view-panel active">
                    <div class="content-loading">Loading chapters...</div>
                </div>
                <div id="lessons-view" class="view-panel">
                    <div class="content-loading">Loading lessons...</div>
                </div>
                <div id="upload-view" class="view-panel">
                    ${this.renderUploadForm()}
                </div>
            </div>

            <style>
                .lesson-generation-container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }

                .lesson-gen-header {
                    text-align: center;
                    margin-bottom: 30px;
                }

                .lesson-gen-header h2 {
                    font-size: 2em;
                    margin-bottom: 10px;
                }

                .lesson-gen-tabs {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #e0e0e0;
                }

                .tab-btn {
                    padding: 12px 24px;
                    border: none;
                    background: transparent;
                    cursor: pointer;
                    font-size: 1em;
                    border-bottom: 3px solid transparent;
                    transition: all 0.3s;
                }

                .tab-btn:hover {
                    background: #f5f5f5;
                }

                .tab-btn.active {
                    border-bottom-color: #2563eb;
                    color: #2563eb;
                    font-weight: bold;
                }

                .view-panel {
                    display: none;
                    min-height: 400px;
                }

                .view-panel.active {
                    display: block;
                }

                .chapter-card, .lesson-card {
                    background: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .chapter-header, .lesson-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: start;
                    margin-bottom: 15px;
                }

                .status-badge {
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 0.85em;
                    font-weight: bold;
                }

                .status-uploaded { background: #dbeafe; color: #1e40af; }
                .status-processing { background: #fed7aa; color: #9a3412; }
                .status-generated { background: #dcfce7; color: #166534; }
                .status-published { background: #d1fae5; color: #065f46; }
                .status-failed { background: #fee2e2; color: #991b1b; }

                .chapter-actions, .lesson-actions {
                    display: flex;
                    gap: 10px;
                    margin-top: 15px;
                }

                .btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.9em;
                    transition: all 0.2s;
                }

                .btn-primary {
                    background: #2563eb;
                    color: white;
                }

                .btn-primary:hover {
                    background: #1d4ed8;
                }

                .btn-success {
                    background: #16a34a;
                    color: white;
                }

                .btn-success:hover {
                    background: #15803d;
                }

                .btn-secondary {
                    background: #6b7280;
                    color: white;
                }

                .upload-form {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .form-group {
                    margin-bottom: 20px;
                }

                .form-group label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: bold;
                }

                .form-group input,
                .form-group select,
                .form-group textarea {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    font-size: 1em;
                }

                .form-group textarea {
                    min-height: 300px;
                    font-family: monospace;
                }

                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }

                .stat-card {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }

                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #2563eb;
                }

                .stat-label {
                    color: #6b7280;
                    margin-top: 5px;
                }
            </style>
        `;

        this.attachEventListeners(container);
        this.loadInitialData();

        return container;
    }

    /**
     * Render upload form
     */
    renderUploadForm() {
        return `
            <div class="upload-form">
                <h3>Upload Textbook Chapter</h3>
                
                <div class="upload-method-tabs">
                    <button type="button" class="method-tab active" data-method="pdf">
                        📄 Upload PDF
                    </button>
                    <button type="button" class="method-tab" data-method="text">
                        ✍️ Paste Text
                    </button>
                </div>

                <form id="chapter-upload-form">
                    <div class="form-group">
                        <label for="chapter-title">Chapter Title *</label>
                        <input type="text" id="chapter-title" required 
                               placeholder="e.g., Introduction to Fractions">
                    </div>

                    <div class="form-group">
                        <label for="chapter-subject">Subject *</label>
                        <select id="chapter-subject" required>
                            <option value="">Select Subject</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="chapter-grade">Grade *</label>
                        <select id="chapter-grade" required>
                            <option value="">Select Grade</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="chapter-number">Chapter Number</label>
                        <input type="text" id="chapter-number" 
                               placeholder="e.g., Chapter 3.1">
                    </div>

                    <div class="form-group">
                        <label for="source-book">Source Book</label>
                        <input type="text" id="source-book" 
                               placeholder="e.g., Mathematics for Primary 5">
                    </div>

                    <!-- PDF Upload Section -->
                    <div id="pdf-upload-section" class="upload-section active">
                        <div class="form-group">
                            <label for="pdf-file">📄 PDF File *</label>
                            <div class="file-upload-area" id="pdf-drop-zone">
                                <input type="file" id="pdf-file" accept=".pdf" hidden>
                                <div class="file-upload-content">
                                    <span class="upload-icon">📁</span>
                                    <p>Drag & drop PDF here or <button type="button" class="btn-link" id="pdf-browse-btn">browse</button></p>
                                    <small>Maximum file size: 10MB</small>
                                </div>
                                <div class="file-selected" id="pdf-selected" style="display: none;">
                                    <span class="file-icon">📄</span>
                                    <span class="file-name"></span>
                                    <button type="button" class="btn-remove" id="pdf-remove-btn">✕</button>
                                </div>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group half">
                                <label for="start-page">Start Page (optional)</label>
                                <input type="number" id="start-page" min="1" placeholder="1">
                            </div>
                            <div class="form-group half">
                                <label for="end-page">End Page (optional)</label>
                                <input type="number" id="end-page" min="1" placeholder="Last">
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="auto-generate-pdf">
                                ✨ Automatically generate lesson after upload
                            </label>
                        </div>
                    </div>

                    <!-- Text Input Section -->
                    <div id="text-upload-section" class="upload-section">
                        <div class="form-group">
                            <label for="page-numbers">Page Numbers</label>
                            <input type="text" id="page-numbers" 
                                   placeholder="e.g., 45-52">
                        </div>

                        <div class="form-group">
                            <label for="chapter-content">Chapter Content * (min. 100 words)</label>
                            <textarea id="chapter-content"
                                      placeholder="Paste or type the textbook chapter content here..."></textarea>
                            <small id="word-count">0 words</small>
                        </div>
                    </div>

                    <div class="form-group form-actions">
                        <button type="submit" class="btn btn-primary btn-lg" id="upload-btn">
                            📤 Upload & Process
                        </button>
                    </div>
                </form>
            </div>

            <style>
                .upload-method-tabs {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 25px;
                }

                .method-tab {
                    flex: 1;
                    padding: 15px 20px;
                    border: 2px solid #e0e0e0;
                    background: white;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 1em;
                    transition: all 0.3s;
                }

                .method-tab:hover {
                    border-color: #2563eb;
                }

                .method-tab.active {
                    border-color: #2563eb;
                    background: #eff6ff;
                    color: #2563eb;
                    font-weight: bold;
                }

                .upload-section {
                    display: none;
                }

                .upload-section.active {
                    display: block;
                }

                .file-upload-area {
                    border: 2px dashed #d1d5db;
                    border-radius: 8px;
                    padding: 40px 20px;
                    text-align: center;
                    transition: all 0.3s;
                    background: #fafafa;
                }

                .file-upload-area:hover,
                .file-upload-area.drag-over {
                    border-color: #2563eb;
                    background: #eff6ff;
                }

                .file-upload-content .upload-icon {
                    font-size: 3em;
                    display: block;
                    margin-bottom: 10px;
                }

                .btn-link {
                    background: none;
                    border: none;
                    color: #2563eb;
                    cursor: pointer;
                    text-decoration: underline;
                    font-size: inherit;
                }

                .file-selected {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    padding: 15px;
                    background: #dcfce7;
                    border-radius: 6px;
                }

                .file-selected .file-icon {
                    font-size: 1.5em;
                }

                .file-selected .file-name {
                    font-weight: bold;
                    color: #166534;
                }

                .btn-remove {
                    background: #fee2e2;
                    border: none;
                    color: #991b1b;
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    cursor: pointer;
                    font-size: 12px;
                }

                .form-row {
                    display: flex;
                    gap: 15px;
                }

                .form-group.half {
                    flex: 1;
                }

                .checkbox-label {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    cursor: pointer;
                }

                .checkbox-label input {
                    width: auto;
                }

                .form-actions {
                    margin-top: 20px;
                }

                .btn-lg {
                    padding: 15px 30px;
                    font-size: 1.1em;
                }
            </style>
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners(container) {
        // Tab switching
        container.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                this.switchView(view, container);
            });
        });

        // Form submission (delegated)
        container.addEventListener('submit', (e) => {
            if (e.target.id === 'chapter-upload-form') {
                e.preventDefault();
                this.handleChapterUpload(e.target);
            }
        });

        // Word count
        container.addEventListener('input', (e) => {
            if (e.target.id === 'chapter-content') {
                this.updateWordCount(e.target);
            }
        });

        // Upload method tab switching
        container.addEventListener('click', (e) => {
            if (e.target.classList.contains('method-tab')) {
                const method = e.target.dataset.method;
                this.switchUploadMethod(method, container);
            }
        });

        // PDF file input
        this.setupPDFUpload(container);
    }

    /**
     * Setup PDF upload handlers
     */
    setupPDFUpload(container) {
        const dropZone = container.querySelector('#pdf-drop-zone');
        const fileInput = container.querySelector('#pdf-file');
        const browseBtn = container.querySelector('#pdf-browse-btn');
        const removeBtn = container.querySelector('#pdf-remove-btn');
        const selectedDisplay = container.querySelector('#pdf-selected');
        const uploadContent = container.querySelector('.file-upload-content');

        if (!dropZone || !fileInput) return;

        // Browse button click
        browseBtn?.addEventListener('click', () => fileInput.click());

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handlePDFSelected(e.target.files[0], container);
            }
        });

        // Drag and drop
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type === 'application/pdf') {
                fileInput.files = files;
                this.handlePDFSelected(files[0], container);
            } else {
                showNotification('Please drop a PDF file', 'warning');
            }
        });

        // Remove file
        removeBtn?.addEventListener('click', () => {
            fileInput.value = '';
            this.selectedPDF = null;
            selectedDisplay.style.display = 'none';
            uploadContent.style.display = 'block';
        });
    }

    /**
     * Handle PDF file selected
     */
    handlePDFSelected(file, container) {
        if (file.size > 10 * 1024 * 1024) {
            showNotification('File size exceeds 10MB limit', 'error');
            return;
        }

        this.selectedPDF = file;
        
        const selectedDisplay = container.querySelector('#pdf-selected');
        const uploadContent = container.querySelector('.file-upload-content');
        const fileName = selectedDisplay.querySelector('.file-name');
        
        if (selectedDisplay && uploadContent && fileName) {
            fileName.textContent = file.name;
            uploadContent.style.display = 'none';
            selectedDisplay.style.display = 'flex';
        }
    }

    /**
     * Switch upload method (PDF or Text)
     */
    switchUploadMethod(method, container) {
        // Update tabs
        container.querySelectorAll('.method-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.method === method);
        });

        // Show/hide sections
        const pdfSection = container.querySelector('#pdf-upload-section');
        const textSection = container.querySelector('#text-upload-section');

        if (method === 'pdf') {
            pdfSection?.classList.add('active');
            textSection?.classList.remove('active');
        } else {
            pdfSection?.classList.remove('active');
            textSection?.classList.add('active');
        }

        this.currentUploadMethod = method;
    }

    /**
     * Switch between views
     */
    switchView(view, container) {
        // Update tabs
        container.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });

        // Update panels
        container.querySelectorAll('.view-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        const targetPanel = container.querySelector(`#${view}-view`);
        if (targetPanel) {
            targetPanel.classList.add('active');

            // Load data if needed
            if (view === 'chapters' && this.chapters.length === 0) {
                this.loadChapters(targetPanel);
            } else if (view === 'lessons' && this.lessons.length === 0) {
                this.loadLessons(targetPanel);
            } else if (view === 'upload') {
                this.loadFormData(container);
            }
        }
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        const chaptersPanel = document.querySelector('#chapters-view');
        if (chaptersPanel) {
            await this.loadChapters(chaptersPanel);
        }
    }

    /**
     * Load textbook chapters
     */
    async loadChapters(panel) {
        try {
            const response = await apiRequest('/api/chapters/', 'GET');
            // Handle both paginated response and direct array
            this.chapters = Array.isArray(response) ? response : (response.results || []);

            panel.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${this.chapters.length}</div>
                        <div class="stat-label">Total Chapters</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${this.chapters.filter(c => c.status === 'uploaded').length}</div>
                        <div class="stat-label">Ready to Process</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${this.chapters.filter(c => c.status === 'generated').length}</div>
                        <div class="stat-label">Lessons Generated</div>
                    </div>
                </div>

                <h3>All Chapters</h3>
                ${this.chapters.map(chapter => this.renderChapterCard(chapter)).join('')}
            `;

            this.attachChapterActions(panel);
        } catch (error) {
            panel.innerHTML = `<div class="error">Failed to load chapters</div>`;
            console.error(error);
        }
    }

    /**
     * Render chapter card
     */
    renderChapterCard(chapter) {
        return `
            <div class="chapter-card" data-chapter-id="${chapter.id}">
                <div class="chapter-header">
                    <div>
                        <h4>${chapter.title}</h4>
                        <p>${chapter.subject_name} - ${chapter.grade_name}</p>
                    </div>
                    <span class="status-badge status-${chapter.status}">
                        ${chapter.status.toUpperCase()}
                    </span>
                </div>
                <div class="chapter-info">
                    <p><strong>Chapter:</strong> ${chapter.chapter_number || 'N/A'}</p>
                    <p><strong>Words:</strong> ${chapter.word_count || 0}</p>
                    <p><strong>Uploaded:</strong> ${new Date(chapter.created_at).toLocaleDateString()}</p>
                </div>
                <div class="chapter-actions">
                    ${chapter.status === 'uploaded' || chapter.status === 'failed' ? `
                        <button class="btn btn-primary generate-lesson-btn" 
                                data-chapter-id="${chapter.id}">
                            ✨ Generate Lesson
                        </button>
                    ` : ''}
                    ${chapter.status === 'generated' ? `
                        <button class="btn btn-success view-lesson-btn" 
                                data-chapter-id="${chapter.id}">
                            👁️ View Lesson
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Attach chapter action listeners
     */
    attachChapterActions(panel) {
        panel.querySelectorAll('.generate-lesson-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const chapterId = e.target.dataset.chapterId;
                await this.generateLesson(chapterId);
            });
        });

        panel.querySelectorAll('.view-lesson-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const chapterId = e.target.dataset.chapterId;
                this.viewGeneratedLesson(chapterId);
            });
        });
    }

    /**
     * Generate lesson from chapter
     */
    async generateLesson(chapterId) {
        try {
            showNotification('Generating lesson... This may take a moment.', 'info');

            const response = await apiRequest(
                `/api/chapters/${chapterId}/generate_lesson/`,
                'POST',
                { use_openai: false, validate_only: false }
            );

            if (response.status === 'success') {
                showNotification('Lesson generated successfully!', 'success');
                this.loadChapters(document.querySelector('#chapters-view'));
            } else {
                showNotification('Lesson generation failed', 'error');
            }
        } catch (error) {
            showNotification('Error generating lesson', 'error');
            console.error(error);
        }
    }

    /**
     * View generated lesson for a chapter
     */
    async viewGeneratedLesson(chapterId) {
        try {
            // Fetch lessons for this chapter
            const response = await apiRequest(`/api/generated-lessons/?chapter=${chapterId}`, 'GET');
            const lessons = Array.isArray(response) ? response : (response.results || []);
            
            if (lessons.length === 0) {
                showNotification('No lesson found for this chapter', 'warning');
                return;
            }

            const lesson = lessons[0];
            
            // Switch to lessons tab and show details
            const lessonsPanel = document.querySelector('#lessons-view');
            if (lessonsPanel) {
                // Activate lessons tab
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.view-panel').forEach(panel => panel.classList.remove('active'));
                document.querySelector('[data-view="lessons"]')?.classList.add('active');
                lessonsPanel.classList.add('active');

                // Show lesson details
                lessonsPanel.innerHTML = `
                    <div class="lesson-detail">
                        <button class="btn btn-secondary back-btn" onclick="this.closest('.lesson-detail').remove(); document.querySelector('#lessons-view').innerHTML = '<div class=\\'content-loading\\'>Loading lessons...</div>';">
                            ← Back to Lessons
                        </button>
                        <h3>${lesson.title}</h3>
                        <div class="lesson-meta">
                            <p><strong>Subject:</strong> ${lesson.subject_name || 'N/A'}</p>
                            <p><strong>Grade:</strong> ${lesson.grade_name || 'N/A'}</p>
                            <p><strong>Status:</strong> ${lesson.status}</p>
                            <p><strong>Quality Score:</strong> ${lesson.quality_score ? (lesson.quality_score * 100).toFixed(0) + '%' : 'N/A'}</p>
                            <p><strong>Estimated Duration:</strong> ${lesson.estimated_duration || 'N/A'} min</p>
                        </div>
                        <div class="lesson-content">
                            <h4>Overview</h4>
                            <p>${lesson.learning_objectives || 'No objectives defined'}</p>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            showNotification('Failed to load lesson details', 'error');
            console.error(error);
        }
    }

    /**
     * Handle chapter upload (both PDF and text)
     */
    async handleChapterUpload(form) {
        const isPDFUpload = this.currentUploadMethod === 'pdf' || !this.currentUploadMethod;
        const pdfSection = form.querySelector('#pdf-upload-section');
        const isPDFActive = pdfSection?.classList.contains('active');

        if (isPDFActive && this.selectedPDF) {
            // Handle PDF upload
            await this.handlePDFUpload(form);
        } else {
            // Handle text upload
            await this.handleTextUpload(form);
        }
    }

    /**
     * Handle PDF file upload
     */
    async handlePDFUpload(form) {
        if (!this.selectedPDF) {
            showNotification('Please select a PDF file', 'warning');
            return;
        }

        const title = form.querySelector('#chapter-title').value;
        const subject = form.querySelector('#chapter-subject').value;
        const grade = form.querySelector('#chapter-grade').value;

        if (!title || !subject || !grade) {
            showNotification('Please fill in title, subject, and grade', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('pdf_file', this.selectedPDF);
        formData.append('title', title);
        formData.append('subject', subject);
        formData.append('grade', grade);
        formData.append('chapter_number', form.querySelector('#chapter-number').value || '');
        formData.append('source_book', form.querySelector('#source-book').value || '');
        
        const startPage = form.querySelector('#start-page')?.value;
        const endPage = form.querySelector('#end-page')?.value;
        if (startPage) formData.append('start_page', startPage);
        if (endPage) formData.append('end_page', endPage);

        const autoGenerate = form.querySelector('#auto-generate-pdf')?.checked;
        if (autoGenerate) formData.append('auto_generate', 'true');

        try {
            showNotification('Uploading PDF and extracting text... This may take a moment.', 'info');

            const response = await fetch('/api/chapters/upload_pdf/', {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('jln_token')}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showNotification(data.message || 'PDF uploaded successfully!', 'success');
                form.reset();
                this.selectedPDF = null;
                
                // Reset file display
                const selectedDisplay = form.querySelector('#pdf-selected');
                const uploadContent = form.querySelector('.file-upload-content');
                if (selectedDisplay) selectedDisplay.style.display = 'none';
                if (uploadContent) uploadContent.style.display = 'block';
                
                // Show extraction info
                if (data.extraction_metadata) {
                    const meta = data.extraction_metadata;
                    showNotification(
                        `Extracted ${meta.word_count} words from ${meta.extracted_pages} pages`,
                        'info'
                    );
                }

                // Reload chapters
                this.loadChapters(document.querySelector('#chapters-view'));
                
                // If lesson was auto-generated, switch to lessons tab
                if (data.lesson) {
                    setTimeout(() => {
                        const lessonsTab = document.querySelector('[data-view="lessons"]');
                        lessonsTab?.click();
                    }, 1500);
                }
            } else {
                showNotification(data.message || 'Upload failed', 'error');
            }
        } catch (error) {
            showNotification('Upload failed: ' + error.message, 'error');
            console.error(error);
        }
    }

    /**
     * Handle text content upload
     */
    async handleTextUpload(form) {
        const content = form.querySelector('#chapter-content').value;
        
        if (!content || content.trim().split(/\s+/).length < 100) {
            showNotification('Please enter at least 100 words of content', 'warning');
            return;
        }

        const formData = {
            title: form.querySelector('#chapter-title').value,
            subject: form.querySelector('#chapter-subject').value,
            grade: form.querySelector('#chapter-grade').value,
            chapter_number: form.querySelector('#chapter-number').value,
            source_book: form.querySelector('#source-book').value,
            page_numbers: form.querySelector('#page-numbers').value,
            raw_content: content
        };

        try {
            showNotification('Uploading chapter...', 'info');

            const response = await apiRequest('/api/chapters/', 'POST', formData);

            showNotification('Chapter uploaded successfully!', 'success');
            form.reset();
            
            // Reload chapters
            this.loadChapters(document.querySelector('#chapters-view'));
        } catch (error) {
            showNotification('Upload failed: ' + error.message, 'error');
            console.error(error);
        }
    }

    /**
     * Load AI integration status
     */
    async loadAIStatus() {
        try {
            this.aiStatus = await apiRequest('/api/system/ai-status/', 'GET');
        } catch (error) {
            console.error('Failed to load AI status:', error);
            this.aiStatus = {
                integrated: true,
                models_available: false,
                status_message: 'Unable to check AI status',
                status_level: 'warning'
            };
        }
    }

    /**
     * Render AI status banner
     */
    renderAIStatusBanner() {
        if (!this.aiStatus) {
            return '<div class="ai-status-banner loading">Loading AI status...</div>';
        }

        const levelColors = {
            'success': '#dcfce7',
            'warning': '#fef3c7',
            'error': '#fee2e2'
        };

        const levelIcons = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        };

        const bgColor = levelColors[this.aiStatus.status_level] || '#f3f4f6';
        const icon = levelIcons[this.aiStatus.status_level] || 'ℹ️';

        let installInstructions = '';
        if (this.aiStatus.status_level !== 'success' && this.aiStatus.installation) {
            installInstructions = `
                <div class="install-instructions">
                    <h4>📦 Installation Required:</h4>
                    <p>To enable AI lesson generation, install the required dependencies:</p>
                    <div class="code-block">
                        <code>${this.aiStatus.installation.quick_install}</code>
                        <button class="btn-copy" onclick="navigator.clipboard.writeText('${this.aiStatus.installation.quick_install}')">
                            📋 Copy
                        </button>
                    </div>
                    <p><small>${this.aiStatus.installation.note || ''}</small></p>
                </div>
            `;
        }

        let statsDisplay = '';
        if (this.aiStatus.statistics) {
            const stats = this.aiStatus.statistics;
            statsDisplay = `
                <div class="ai-stats">
                    <div class="stat-item">
                        <strong>${stats.total_chapters}</strong>
                        <span>Chapters</span>
                    </div>
                    <div class="stat-item">
                        <strong>${stats.total_lessons}</strong>
                        <span>Generated Lessons</span>
                    </div>
                    <div class="stat-item">
                        <strong>${stats.lessons_published}</strong>
                        <span>Published</span>
                    </div>
                    <div class="stat-item">
                        <strong>${stats.lessons_draft}</strong>
                        <span>Pending Review</span>
                    </div>
                </div>
            `;
        }

        return `
            <div class="ai-status-banner" style="background-color: ${bgColor};">
                <div class="status-content">
                    ${statsDisplay}
                </div>
                ${installInstructions}
            </div>
            
            <style>
                .ai-status-banner {
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid #2563eb;
                }

                .status-content {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: 20px;
                }

                .status-message {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-size: 1.1em;
                }

                .status-icon {
                    font-size: 1.5em;
                }

                .ai-stats {
                    display: flex;
                    gap: 20px;
                }

                .stat-item {
                    text-align: center;
                }

                .stat-item strong {
                    display: block;
                    font-size: 1.5em;
                    color: #2563eb;
                }

                .stat-item span {
                    font-size: 0.85em;
                    color: #6b7280;
                }

                .install-instructions {
                    margin-top: 15px;
                    padding-top: 15px;
                    border-top: 1px solid rgba(0,0,0,0.1);
                }

                .install-instructions h4 {
                    margin-bottom: 10px;
                }

                .code-block {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    background: #1f2937;
                    color: #f3f4f6;
                    padding: 12px;
                    border-radius: 6px;
                    margin: 10px 0;
                    font-family: 'Courier New', monospace;
                }

                .code-block code {
                    flex: 1;
                }

                .btn-copy {
                    padding: 6px 12px;
                    background: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 0.9em;
                }

                .btn-copy:hover {
                    background: #1d4ed8;
                }

                .install-instructions p small {
                    color: #6b7280;
                }
            </style>
        `;
    }

    /**
     * Update word count
     */
    updateWordCount(textarea) {
        const words = textarea.value.trim().split(/\s+/).filter(w => w.length > 0);
        const count = words.length;
        const counter = textarea.parentElement.querySelector('#word-count');
        
        if (counter) {
            counter.textContent = `${count} words`;
            counter.style.color = count >= 100 ? 'green' : 'red';
        }
    }

    /**
     * Load form data (subjects and grades)
     */
    async loadFormData(container) {
        try {
            const [subjectsResponse, gradesResponse] = await Promise.all([
                apiRequest('/api/subjects/', 'GET'),
                apiRequest('/api/grades/', 'GET')
            ]);

            // Handle both paginated response and direct array
            const subjects = Array.isArray(subjectsResponse) ? subjectsResponse : (subjectsResponse.results || []);
            const grades = Array.isArray(gradesResponse) ? gradesResponse : (gradesResponse.results || []);

            const subjectSelect = container.querySelector('#chapter-subject');
            const gradeSelect = container.querySelector('#chapter-grade');

            if (subjectSelect) {
                subjectSelect.innerHTML = '<option value="">Select Subject</option>' +
                    subjects.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            }

            if (gradeSelect) {
                gradeSelect.innerHTML = '<option value="">Select Grade</option>' +
                    grades.map(g => `<option value="${g.id}">${g.name}</option>`).join('');
            }
        } catch (error) {
            console.error('Failed to load form data:', error);
        }
    }

    /**
     * Load generated lessons
     */
    async loadLessons(panel) {
        try {
            const response = await apiRequest('/api/generated-lessons/', 'GET');
            // Handle both paginated response and direct array
            this.lessons = Array.isArray(response) ? response : (response.results || []);

            panel.innerHTML = `
                <h3>Generated Lessons</h3>
                ${this.lessons.length === 0 ? '<p>No lessons generated yet.</p>' : this.lessons.map(lesson => this.renderLessonCard(lesson)).join('')}
            `;

            // Attach event listeners
            this.attachLessonActions(panel);
        } catch (error) {
            panel.innerHTML = `<div class="error">Failed to load lessons</div>`;
            console.error(error);
        }
    }

    /**
     * Attach lesson action listeners
     */
    attachLessonActions(panel) {
        panel.querySelectorAll('.view-details-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const lessonId = e.target.dataset.lessonId;
                await this.viewLessonDetails(lessonId);
            });
        });

        panel.querySelectorAll('.publish-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const lessonId = e.target.dataset.lessonId;
                await this.publishLesson(lessonId);
            });
        });
    }

    /**
     * View lesson details
     */
    async viewLessonDetails(lessonId) {
        try {
            const lesson = await apiRequest(`/api/generated-lessons/${lessonId}/`, 'GET');
            const panel = document.querySelector('#lessons-view');
            
            if (panel) {
                panel.innerHTML = `
                    <div class="lesson-detail">
                        <button class="btn btn-secondary back-btn">← Back to Lessons</button>
                        
                        <h3>${lesson.title}</h3>
                        
                        <div class="lesson-meta">
                            <span class="status-badge status-${lesson.status}">${lesson.status.toUpperCase()}</span>
                            <p><strong>Subject:</strong> ${lesson.subject_name || 'N/A'}</p>
                            <p><strong>Grade:</strong> ${lesson.grade_name || 'N/A'}</p>
                            <p><strong>Quality Score:</strong> ${lesson.quality_score ? (lesson.quality_score * 100).toFixed(0) + '%' : 'N/A'}</p>
                            <p><strong>Duration:</strong> ${lesson.estimated_duration || 'N/A'} min</p>
                            <p><strong>Difficulty:</strong> ${lesson.difficulty_level || 'N/A'}</p>
                            <p><strong>AI Model:</strong> ${lesson.ai_model_used || 'Rule-based'}</p>
                        </div>

                        <div class="lesson-section">
                            <h4>Introduction</h4>
                            <p>${lesson.introduction || 'No introduction available'}</p>
                        </div>

                        <div class="lesson-section">
                            <h4>Learning Objectives</h4>
                            <p>${lesson.learning_objectives || 'No objectives defined'}</p>
                        </div>

                        <div class="lesson-section">
                            <h4>Key Concepts</h4>
                            <p>${lesson.key_concepts || 'No key concepts defined'}</p>
                        </div>

                        ${lesson.sections && lesson.sections.length ? `
                            <div class="lesson-section">
                                <h4>Sections (${lesson.sections.length})</h4>
                                ${lesson.sections.map((s, i) => `
                                    <div class="section-item">
                                        <strong>${i + 1}. ${s.title}</strong>
                                        <span class="section-type">(${s.section_type})</span>
                                        <p>${s.content ? s.content.substring(0, 200) + '...' : ''}</p>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}

                        ${lesson.questions && lesson.questions.length ? `
                            <div class="lesson-section">
                                <h4>Questions (${lesson.questions.length})</h4>
                                ${lesson.questions.map((q, i) => `
                                    <div class="question-item">
                                        <p><strong>Q${i + 1}:</strong> ${q.question_text}</p>
                                        <p class="answer"><em>Answer: ${q.correct_answer || 'N/A'}</em></p>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}

                        <div class="lesson-actions-detail">
                            ${lesson.status === 'draft' ? `
                                <button class="btn btn-primary approve-btn" data-lesson-id="${lesson.id}">✓ Approve</button>
                            ` : ''}
                            ${lesson.status === 'approved' && !lesson.published_capsule_id ? `
                                <button class="btn btn-success publish-btn" data-lesson-id="${lesson.id}">🚀 Publish</button>
                            ` : ''}
                        </div>
                    </div>

                    <style>
                        .lesson-detail { padding: 20px; }
                        .lesson-detail .back-btn { margin-bottom: 20px; }
                        .lesson-meta { background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
                        .lesson-section { margin-bottom: 20px; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; }
                        .lesson-section h4 { margin-bottom: 10px; color: #2563eb; }
                        .section-item, .question-item { padding: 10px; background: #fafafa; margin-bottom: 10px; border-radius: 4px; }
                        .section-type { color: #666; font-size: 0.9em; }
                        .answer { color: #059669; }
                        .lesson-actions-detail { margin-top: 20px; display: flex; gap: 10px; }
                    </style>
                `;

                // Attach back button listener
                panel.querySelector('.back-btn')?.addEventListener('click', () => {
                    this.loadLessons(panel);
                });

                // Attach approve button listener
                panel.querySelector('.approve-btn')?.addEventListener('click', async (e) => {
                    await this.approveLesson(e.target.dataset.lessonId);
                });

                // Attach publish button listener
                panel.querySelector('.publish-btn')?.addEventListener('click', async (e) => {
                    await this.publishLesson(e.target.dataset.lessonId);
                });
            }
        } catch (error) {
            showNotification('Failed to load lesson details', 'error');
            console.error(error);
        }
    }

    /**
     * Approve a lesson
     */
    async approveLesson(lessonId) {
        try {
            await apiRequest(`/api/generated-lessons/${lessonId}/review/`, 'POST', {
                status: 'approved',
                review_notes: ''
            });
            showNotification('Lesson approved!', 'success');
            await this.viewLessonDetails(lessonId);
        } catch (error) {
            showNotification('Failed to approve lesson', 'error');
            console.error(error);
        }
    }

    /**
     * Publish a lesson
     */
    async publishLesson(lessonId) {
        try {
            await apiRequest(`/api/generated-lessons/${lessonId}/publish/`, 'POST');
            showNotification('Lesson published!', 'success');
            await this.viewLessonDetails(lessonId);
        } catch (error) {
            showNotification('Failed to publish lesson', 'error');
            console.error(error);
        }
    }

    /**
     * Render lesson card
     */
    renderLessonCard(lesson) {
        return `
            <div class="lesson-card">
                <div class="lesson-header">
                    <div>
                        <h4>${lesson.title}</h4>
                        <p>${lesson.subject_name} - ${lesson.grade_name}</p>
                    </div>
                    <span class="status-badge status-${lesson.status}">
                        ${lesson.status.toUpperCase()}
                    </span>
                </div>
                <div class="lesson-info">
                    <p><strong>Sections:</strong> ${lesson.sections_count}</p>
                    <p><strong>Questions:</strong> ${lesson.questions_count}</p>
                    <p><strong>Quality:</strong> ${(lesson.quality_score * 100).toFixed(0)}%</p>
                    <p><strong>Duration:</strong> ${lesson.estimated_duration} min</p>
                </div>
                <div class="lesson-actions">
                    <button class="btn btn-primary view-details-btn" 
                            data-lesson-id="${lesson.id}">
                        📋 View Details
                    </button>
                    ${lesson.status === 'approved' && !lesson.published_capsule_id ? `
                        <button class="btn btn-success publish-btn" 
                                data-lesson-id="${lesson.id}">
                            🚀 Publish
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }
}

export default LessonGenerationComponent;
