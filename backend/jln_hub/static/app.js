// JLN Hub - Main Application JavaScript

class JLNApp {
    constructor() {
        this.apiBase = '/api';
        this.currentPage = 'home';
        this.currentLesson = null;
        this.init();
    }

    init() {
        this.setupNavigation();
        this.checkOnlineStatus();
        this.loadDashboardStats();
        this.loadFeaturedLessons();
    }

    // Navigation
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                this.showPage(page);
                
                // Update active nav link
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }

    showPage(pageName) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Show selected page
        const page = document.getElementById(`${pageName}-page`);
        if (page) {
            page.classList.add('active');
            this.currentPage = pageName;

            // Load page-specific data
            switch(pageName) {
                case 'subjects':
                    this.loadSubjects();
                    break;
                case 'lessons':
                    this.loadLessons();
                    this.loadFilters();
                    break;
                case 'progress':
                    this.loadProgress();
                    break;
            }
        }
    }

    // API Calls
    async fetchAPI(endpoint) {
        try {
            const response = await fetch(`${this.apiBase}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    }

    async postAPI(endpoint, data) {
        try {
            const response = await fetch(`${this.apiBase}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    }

    // Dashboard
    async loadDashboardStats() {
        const stats = await this.fetchAPI('/dashboard/stats/');
        if (stats) {
            document.getElementById('stat-subjects').textContent = stats.total_subjects || 0;
            document.getElementById('stat-capsules').textContent = stats.total_capsules || 0;
            document.getElementById('stat-quizzes').textContent = stats.total_quizzes || 0;
            document.getElementById('stat-grades').textContent = stats.total_grades || 0;
        }
    }

    async loadFeaturedLessons() {
        const container = document.getElementById('featured-lessons');
        const lessons = await this.fetchAPI('/capsules/featured/');
        
        if (lessons && lessons.length > 0) {
            container.innerHTML = lessons.map(lesson => this.createLessonCard(lesson)).join('');
        } else {
            container.innerHTML = '<p class="info-message">No featured lessons available yet. Check back soon!</p>';
        }
    }

    // Subjects
    async loadSubjects() {
        const container = document.getElementById('subjects-list');
        container.innerHTML = '<p class="loading">Loading subjects...</p>';
        
        const subjects = await this.fetchAPI('/subjects/');
        
        if (subjects && subjects.length > 0) {
            container.innerHTML = subjects.map(subject => `
                <div class="subject-card" onclick="app.filterBySubject(${subject.id})">
                    <div class="subject-icon">${subject.icon || '📚'}</div>
                    <h3>${subject.name}</h3>
                    <p>${subject.description || 'Explore lessons in this subject'}</p>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="info-message">No subjects available yet.</p>';
        }
    }

    filterBySubject(subjectId) {
        this.showPage('lessons');
        const subjectFilter = document.getElementById('subject-filter');
        if (subjectFilter) {
            subjectFilter.value = subjectId;
            this.loadLessons();
        }
    }

    // Lessons
    async loadFilters() {
        // Load subjects for filter
        const subjects = await this.fetchAPI('/subjects/');
        const subjectFilter = document.getElementById('subject-filter');
        if (subjects && subjectFilter) {
            subjectFilter.innerHTML = '<option value="">All Subjects</option>' +
                subjects.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            
            subjectFilter.addEventListener('change', () => this.loadLessons());
        }

        // Load grades for filter
        const grades = await this.fetchAPI('/grades/');
        const gradeFilter = document.getElementById('grade-filter');
        if (grades && gradeFilter) {
            gradeFilter.innerHTML = '<option value="">All Grades</option>' +
                grades.map(g => `<option value="${g.id}">${g.name}</option>`).join('');
            
            gradeFilter.addEventListener('change', () => this.loadLessons());
        }
    }

    async loadLessons() {
        const container = document.getElementById('lessons-list');
        container.innerHTML = '<p class="loading">Loading lessons...</p>';
        
        // Get filter values
        const subjectId = document.getElementById('subject-filter')?.value || '';
        const gradeId = document.getElementById('grade-filter')?.value || '';
        
        let endpoint = '/capsules/';
        const params = [];
        if (subjectId) params.push(`subject=${subjectId}`);
        if (gradeId) params.push(`grade=${gradeId}`);
        if (params.length > 0) endpoint += '?' + params.join('&');
        
        const lessons = await this.fetchAPI(endpoint);
        
        if (lessons && lessons.length > 0) {
            container.innerHTML = lessons.map(lesson => this.createLessonCard(lesson)).join('');
        } else {
            container.innerHTML = '<p class="info-message">No lessons match your filters.</p>';
        }
    }

    createLessonCard(lesson) {
        return `
            <div class="lesson-card" onclick="app.viewLesson(${lesson.id})">
                <div class="lesson-header">
                    <h3>${lesson.title}</h3>
                    <div class="lesson-meta">
                        ${lesson.subject_name} • ${lesson.grade_name}
                    </div>
                </div>
                <div class="lesson-body">
                    <p>${lesson.description}</p>
                </div>
                <div class="lesson-footer">
                    <span class="badge badge-primary">⏱️ ${lesson.estimated_duration} min</span>
                    <span class="badge badge-success">📝 ${lesson.quiz_count || 0} quizzes</span>
                </div>
            </div>
        `;
    }

    async viewLesson(lessonId) {
        this.showPage('lesson-detail');
        
        const container = document.getElementById('lesson-content');
        container.innerHTML = '<p class="loading">Loading lesson...</p>';
        
        const lesson = await this.fetchAPI(`/capsules/${lessonId}/`);
        
        if (lesson) {
            this.currentLesson = lesson;
            container.innerHTML = this.createLessonDetail(lesson);
        } else {
            container.innerHTML = '<p class="error-message">Failed to load lesson.</p>';
        }
    }

    createLessonDetail(lesson) {
        let html = `
            <div class="lesson-detail-header">
                <h2>${lesson.title}</h2>
                <p>${lesson.subject_name} • ${lesson.grade_name} • ${lesson.estimated_duration} minutes</p>
            </div>
        `;

        // Objectives
        if (lesson.objectives && lesson.objectives.length > 0) {
            html += `
                <div class="lesson-objectives">
                    <h3>Learning Objectives</h3>
                    <ul>
                        ${lesson.objectives.map(obj => `<li>${obj}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Content
        html += `
            <div class="lesson-content-body">
                ${this.formatContent(lesson.content)}
            </div>
        `;

        // Quizzes
        if (lesson.quizzes && lesson.quizzes.length > 0) {
            lesson.quizzes.forEach(quiz => {
                html += this.createQuizSection(quiz);
            });
        }

        return html;
    }

    formatContent(content) {
        // Simple content formatting
        return content.split('\n').map(line => {
            if (line.trim().startsWith('#')) {
                return `<h3>${line.replace(/^#+\s*/, '')}</h3>`;
            }
            return `<p>${line}</p>`;
        }).join('');
    }

    createQuizSection(quiz) {
        return `
            <div class="quiz-section" id="quiz-${quiz.id}">
                <h3>📝 ${quiz.title}</h3>
                <p>${quiz.instructions || 'Answer the following questions:'}</p>
                
                <form id="quiz-form-${quiz.id}" onsubmit="app.submitQuiz(event, ${quiz.id})">
                    ${quiz.questions.map((q, idx) => `
                        <div class="question">
                            <div class="question-text">${idx + 1}. ${q.question_text}</div>
                            <div class="options">
                                ${q.options.map((option, optIdx) => `
                                    <div class="option">
                                        <input type="radio" 
                                               id="q${q.id}-opt${optIdx}" 
                                               name="question-${q.id}" 
                                               value="${option}"
                                               required>
                                        <label for="q${q.id}-opt${optIdx}">${option}</label>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `).join('')}
                    
                    <button type="submit" class="btn btn-primary">Submit Quiz</button>
                </form>
                
                <div id="quiz-results-${quiz.id}"></div>
            </div>
        `;
    }

    async submitQuiz(event, quizId) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const answers = {};
        
        // Collect answers
        for (let [key, value] of formData.entries()) {
            const questionId = key.replace('question-', '');
            answers[questionId] = value;
        }
        
        // Submit to API
        const result = await this.postAPI(`/quizzes/${quizId}/submit/`, {
            quiz_id: quizId,
            answers: answers
        });
        
        if (result) {
            this.displayQuizResults(quizId, result);
        }
    }

    displayQuizResults(quizId, result) {
        const resultsContainer = document.getElementById(`quiz-results-${quizId}`);
        const form = document.getElementById(`quiz-form-${quizId}`);
        
        // Hide form
        form.style.display = 'none';
        
        const passedClass = result.passed ? 'passed' : 'failed';
        const passedText = result.passed ? '🎉 Passed!' : '📚 Keep Learning!';
        
        let html = `
            <div class="quiz-results">
                <div class="score-display ${passedClass}">
                    <h3>${passedText}</h3>
                    <p>Score: ${result.score}/${result.max_score} (${result.percentage}%)</p>
                    <p>Passing Score: ${result.passing_score}%</p>
                </div>
                
                <h4>Question Results:</h4>
        `;
        
        result.results.forEach((qResult, idx) => {
            const correctClass = qResult.is_correct ? 'correct' : 'incorrect';
            const icon = qResult.is_correct ? '✅' : '❌';
            
            html += `
                <div class="question-result ${correctClass}">
                    <p><strong>${icon} Question ${idx + 1}:</strong> ${qResult.question_text}</p>
                    <p><strong>Your Answer:</strong> ${qResult.user_answer}</p>
                    ${!qResult.is_correct ? `<p><strong>Correct Answer:</strong> ${qResult.correct_answer}</p>` : ''}
                    ${qResult.explanation ? `<p><strong>Explanation:</strong> ${qResult.explanation}</p>` : ''}
                </div>
            `;
        });
        
        html += `
                <button class="btn btn-primary" onclick="app.retakeQuiz(${quizId})">Retake Quiz</button>
            </div>
        `;
        
        resultsContainer.innerHTML = html;
    }

    retakeQuiz(quizId) {
        const form = document.getElementById(`quiz-form-${quizId}`);
        const results = document.getElementById(`quiz-results-${quizId}`);
        
        form.style.display = 'block';
        form.reset();
        results.innerHTML = '';
    }

    // Progress
    async loadProgress() {
        const summaryContainer = document.getElementById('progress-summary');
        const listContainer = document.getElementById('progress-list');
        
        summaryContainer.innerHTML = '<p class="loading">Loading progress...</p>';
        
        // This would require authentication in a real app
        summaryContainer.innerHTML = `
            <p class="info-message">
                Progress tracking is available! Start learning to track your progress.
                <br><small>Note: User authentication will be added for personalized tracking.</small>
            </p>
        `;
    }

    // Online/Offline Status
    checkOnlineStatus() {
        const updateStatus = () => {
            const statusEl = document.getElementById('online-status');
            if (navigator.onLine) {
                statusEl.textContent = '🟢 Online';
                statusEl.style.color = '#27ae60';
            } else {
                statusEl.textContent = '🔴 Offline';
                statusEl.style.color = '#e74c3c';
            }
        };
        
        updateStatus();
        window.addEventListener('online', updateStatus);
        window.addEventListener('offline', updateStatus);
    }
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new JLNApp();
});
