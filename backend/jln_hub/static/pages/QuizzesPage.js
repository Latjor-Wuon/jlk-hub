/**
 * Quizzes Page
 * 
 * Allows users to browse and take quizzes independently from lessons.
 * Provides filtering by subject and grade level.
 */
import { apiClient } from '../utils/api.js';
import { QuizComponent } from '../components/QuizComponent.js';

export class QuizzesPage {
    constructor(container) {
        this.container = container;
        this.quizzes = [];
        this.currentQuiz = null;
    }

    async render() {
        this.container.innerHTML = `
            <div class="quizzes-page">
                <header class="page-header">
                    <h1>📝 Practice Quizzes</h1>
                    <p>Test your knowledge with interactive quizzes and get instant feedback!</p>
                </header>

                <div class="quiz-filters">
                    <select id="quiz-subject-filter" class="filter-select">
                        <option value="">All Subjects</option>
                    </select>
                    <select id="quiz-grade-filter" class="filter-select">
                        <option value="">All Grades</option>
                    </select>
                </div>

                <div id="quizzes-content">
                    <div id="quizzes-grid" class="quizzes-grid">
                        <p class="loading">Loading quizzes...</p>
                    </div>
                    
                    <div id="quiz-viewer" class="quiz-viewer" style="display: none;">
                        <button id="back-to-quizzes" class="btn btn-back">← Back to Quizzes</button>
                        <div id="quiz-container"></div>
                    </div>
                </div>
            </div>
        `;

        await this.loadFilters();
        await this.loadQuizzes();
        this.attachEventListeners();
    }

    async loadFilters() {
        try {
            const [subjectsResponse, gradesResponse] = await Promise.all([
                apiClient.get('/subjects/'),
                apiClient.get('/grades/')
            ]);

            // Handle paginated responses or direct arrays
            const subjects = Array.isArray(subjectsResponse) ? subjectsResponse : (subjectsResponse?.results || []);
            const grades = Array.isArray(gradesResponse) ? gradesResponse : (gradesResponse?.results || []);

            const subjectSelect = document.getElementById('quiz-subject-filter');
            const gradeSelect = document.getElementById('quiz-grade-filter');

            if (subjects.length && subjectSelect) {
                subjects.forEach(subject => {
                    subjectSelect.innerHTML += `<option value="${subject.id}">${subject.name}</option>`;
                });
            }

            if (grades.length && gradeSelect) {
                grades.forEach(grade => {
                    gradeSelect.innerHTML += `<option value="${grade.id}">${grade.name}</option>`;
                });
            }
        } catch (error) {
            console.error('Failed to load filters:', error);
        }
    }

    async loadQuizzes() {
        const grid = document.getElementById('quizzes-grid');
        
        try {
            // Get all capsules with quizzes
            const capsulesResponse = await apiClient.get('/capsules/');
            const capsules = Array.isArray(capsulesResponse) ? capsulesResponse : (capsulesResponse?.results || []);
            
            // Get quiz details for capsules that have quizzes
            this.quizzes = [];
            
            for (const capsule of capsules) {
                if (capsule.quiz_count > 0) {
                    // Fetch full capsule details to get quizzes
                    const fullCapsule = await apiClient.get(`/capsules/${capsule.id}/`);
                    if (fullCapsule && fullCapsule.quizzes) {
                        fullCapsule.quizzes.forEach(quiz => {
                            this.quizzes.push({
                                ...quiz,
                                capsule_id: capsule.id,
                                capsule_title: capsule.title,
                                subject_id: capsule.subject,
                                subject_name: capsule.subject_name,
                                grade_id: capsule.grade,
                                grade_name: capsule.grade_name
                            });
                        });
                    }
                }
            }

            this.displayQuizzes();
        } catch (error) {
            console.error('Failed to load quizzes:', error);
            grid.innerHTML = `
                <div class="error-message">
                    <p>Unable to load quizzes. Please try again later.</p>
                </div>
            `;
        }
    }

    displayQuizzes() {
        const grid = document.getElementById('quizzes-grid');
        
        // Apply filters
        const subjectFilter = document.getElementById('quiz-subject-filter')?.value;
        const gradeFilter = document.getElementById('quiz-grade-filter')?.value;
        
        let filteredQuizzes = this.quizzes;
        
        if (subjectFilter) {
            filteredQuizzes = filteredQuizzes.filter(q => q.subject_id == subjectFilter);
        }
        if (gradeFilter) {
            filteredQuizzes = filteredQuizzes.filter(q => q.grade_id == gradeFilter);
        }

        if (!filteredQuizzes.length) {
            grid.innerHTML = `
                <div class="no-quizzes">
                    <h3>📚 No quizzes available yet</h3>
                    <p>Check back soon or try different filters!</p>
                    <p class="text-muted">Quizzes are attached to lessons. Browse lessons to find embedded quizzes.</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = filteredQuizzes.map(quiz => `
            <div class="quiz-card" data-quiz-id="${quiz.id}">
                <div class="quiz-card-header">
                    <span class="quiz-icon">📝</span>
                    <span class="question-count">${quiz.questions?.length || 0} questions</span>
                </div>
                <h3 class="quiz-title">${quiz.title}</h3>
                <p class="quiz-lesson">From: ${quiz.capsule_title}</p>
                <div class="quiz-meta">
                    <span class="subject-badge">${quiz.subject_name}</span>
                    <span class="grade-badge">${quiz.grade_name}</span>
                </div>
                <p class="quiz-instructions">${quiz.instructions || 'Test your knowledge!'}</p>
                <div class="quiz-footer">
                    <span class="passing-score">Pass: ${quiz.passing_score}%</span>
                    <button class="btn btn-primary start-quiz" data-quiz-id="${quiz.id}">
                        Start Quiz
                    </button>
                </div>
            </div>
        `).join('');
    }

    attachEventListeners() {
        // Filter changes
        document.getElementById('quiz-subject-filter')?.addEventListener('change', () => {
            this.displayQuizzes();
        });

        document.getElementById('quiz-grade-filter')?.addEventListener('change', () => {
            this.displayQuizzes();
        });

        // Start quiz
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('start-quiz')) {
                const quizId = e.target.dataset.quizId;
                this.openQuiz(quizId);
            }
        });

        // Back to quizzes
        document.getElementById('back-to-quizzes')?.addEventListener('click', () => {
            this.closeQuiz();
        });
    }

    openQuiz(quizId) {
        const quiz = this.quizzes.find(q => q.id == quizId);
        if (!quiz) return;

        const grid = document.getElementById('quizzes-grid');
        const viewer = document.getElementById('quiz-viewer');
        const container = document.getElementById('quiz-container');

        grid.style.display = 'none';
        viewer.style.display = 'block';

        // Create quiz info header
        container.innerHTML = `
            <div class="quiz-detail-header">
                <h2>${quiz.title}</h2>
                <p class="quiz-detail-meta">
                    <span>${quiz.subject_name}</span> • 
                    <span>${quiz.grade_name}</span> • 
                    <span>${quiz.questions?.length || 0} questions</span> •
                    <span>Pass: ${quiz.passing_score}%</span>
                </p>
                <p class="quiz-detail-lesson">From lesson: <a href="#lesson/${quiz.capsule_id}">${quiz.capsule_title}</a></p>
            </div>
            <div id="quiz-component-container"></div>
        `;

        // Render quiz component
        const quizComponentContainer = document.getElementById('quiz-component-container');
        const quizComponent = new QuizComponent(quizComponentContainer, quiz);
        quizComponent.render();
        this.currentQuiz = quizComponent;
    }

    closeQuiz() {
        const grid = document.getElementById('quizzes-grid');
        const viewer = document.getElementById('quiz-viewer');
        const container = document.getElementById('quiz-container');

        viewer.style.display = 'none';
        grid.style.display = 'grid';
        container.innerHTML = '';
        this.currentQuiz = null;
    }
}
