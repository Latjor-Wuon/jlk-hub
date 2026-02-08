// Progress Page Component
import { apiClient } from '../utils/api.js';
import { formatPercentage } from '../utils/helpers.js';
import { AdaptiveLearningComponent } from '../components/AdaptiveLearning.js';

export class ProgressPage {
    constructor(container) {
        this.container = container;
        this.adaptiveComponent = null;
        this.isAuthenticated = false;
    }

    async render() {
        this.container.innerHTML = `
            <div class="progress-page">
                <h2>📊 My Learning Progress</h2>
                
                <div class="progress-tabs">
                    <button class="tab-btn active" data-tab="overview">Overview</button>
                    <button class="tab-btn" data-tab="lessons">Lessons</button>
                    <button class="tab-btn" data-tab="quizzes">Quiz History</button>
                    <button class="tab-btn" data-tab="adaptive">Learning Path</button>
                </div>
                
                <div id="tab-content" class="tab-content">
                    <div id="progress-loading" class="loading">
                        <p>Loading your progress...</p>
                    </div>
                </div>
            </div>
        `;

        this.attachTabListeners();
        this.checkAuth();
        await this.loadOverviewTab();
    }

    attachTabListeners() {
        const tabs = this.container.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                // Load tab content
                const tabName = e.target.dataset.tab;
                this.loadTabContent(tabName);
            });
        });
    }

    checkAuth() {
        // Check using app's AuthManager or localStorage token directly
        if (window.app && window.app.authManager) {
            this.isAuthenticated = window.app.authManager.isAuthenticated();
        } else {
            // Fallback to direct localStorage check
            this.isAuthenticated = !!localStorage.getItem('jln_token');
        }
    }

    async loadTabContent(tabName) {
        switch (tabName) {
            case 'overview':
                await this.loadOverviewTab();
                break;
            case 'lessons':
                await this.loadLessonsTab();
                break;
            case 'quizzes':
                await this.loadQuizzesTab();
                break;
            case 'adaptive':
                await this.loadAdaptiveTab();
                break;
        }
    }

    async loadOverviewTab() {
        const contentDiv = document.getElementById('tab-content');
        
        if (!this.isAuthenticated) {
            contentDiv.innerHTML = `
                <div class="auth-required">
                    <h3>📚 Track Your Learning Journey</h3>
                    <p>Sign in to view your personalized progress and get learning recommendations.</p>
                    <div class="feature-preview">
                        <div class="feature-item">
                            <span class="feature-icon">📈</span>
                            <span>Track lesson completion</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">📝</span>
                            <span>Review quiz history</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">🎯</span>
                            <span>Get personalized recommendations</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">🔄</span>
                            <span>Continue where you left off</span>
                        </div>
                    </div>
                    <button class="btn btn-primary" onclick="window.location.hash='#login'">
                        Sign In to Track Progress
                    </button>
                </div>
            `;
            return;
        }

        try {
            const [summary, stats] = await Promise.all([
                apiClient.get('/progress/summary/'),
                apiClient.get('/dashboard/stats/')
            ]);

            contentDiv.innerHTML = `
                <div class="progress-overview">
                    <div class="progress-summary-grid">
                        ${this.renderProgressCard(summary?.total_capsules_started || 0, 'Lessons Started', '📖')}
                        ${this.renderProgressCard(summary?.completed_capsules || 0, 'Completed', '✅')}
                        ${this.renderProgressCard(summary?.in_progress || 0, 'In Progress', '⏳')}
                        ${this.renderProgressCard(formatPercentage(summary?.average_completion || 0), 'Avg Completion', '📊')}
                    </div>
                    
                    <div class="quiz-summary">
                        <h3>Quiz Performance</h3>
                        <div class="progress-summary-grid">
                            ${this.renderProgressCard(stats?.quizzes_taken || 0, 'Quizzes Taken', '📝')}
                            ${this.renderProgressCard(stats?.quizzes_passed || 0, 'Quizzes Passed', '🏆')}
                        </div>
                    </div>
                    
                    <div class="continue-learning">
                        <h3>Continue Learning</h3>
                        <div id="recent-progress"></div>
                    </div>
                </div>
            `;

            await this.loadRecentProgress();
        } catch (error) {
            contentDiv.innerHTML = `
                <div class="error-message">
                    <p>Unable to load progress. Please try again.</p>
                </div>
            `;
        }
    }

    renderProgressCard(value, label, icon) {
        return `
            <div class="progress-card">
                <span class="card-icon">${icon}</span>
                <h3>${value}</h3>
                <p>${label}</p>
            </div>
        `;
    }

    async loadRecentProgress() {
        const container = document.getElementById('recent-progress');
        
        try {
            const progress = await apiClient.get('/progress/?limit=5');
            
            if (!progress?.length) {
                container.innerHTML = `
                    <p class="text-muted">Start a lesson to begin tracking your progress!</p>
                    <a href="#lessons" class="btn btn-primary">Browse Lessons</a>
                `;
                return;
            }

            container.innerHTML = progress.map(p => `
                <div class="recent-progress-item">
                    <div class="progress-info">
                        <h4>${p.capsule_title || 'Lesson'}</h4>
                        <div class="progress-bar">
                            <div class="progress-bar-fill" style="width: ${p.completion_percentage}%"></div>
                        </div>
                        <span class="progress-percent">${p.completion_percentage}%</span>
                    </div>
                    <a href="#lesson/${p.capsule}" class="btn btn-sm">Continue</a>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<p class="text-muted">Unable to load recent progress.</p>';
        }
    }

    async loadLessonsTab() {
        const contentDiv = document.getElementById('tab-content');
        
        if (!this.isAuthenticated) {
            contentDiv.innerHTML = this.renderAuthRequired();
            return;
        }

        contentDiv.innerHTML = '<p class="loading">Loading lesson progress...</p>';

        try {
            const progress = await apiClient.get('/progress/');
            
            if (!progress?.length) {
                contentDiv.innerHTML = `
                    <div class="empty-state">
                        <p>No lesson progress yet.</p>
                        <a href="#lessons" class="btn btn-primary">Start Learning</a>
                    </div>
                `;
                return;
            }

            contentDiv.innerHTML = `
                <div class="lesson-progress-list">
                    <h3>All Lesson Progress</h3>
                    ${progress.map(p => `
                        <div class="lesson-progress-item ${p.is_completed ? 'completed' : ''}">
                            <div class="lesson-info">
                                <h4>${p.capsule_title || 'Lesson'}</h4>
                                <p class="meta">
                                    Last accessed: ${new Date(p.last_accessed).toLocaleDateString()}
                                    ${p.time_spent ? ` • ${p.time_spent} min spent` : ''}
                                </p>
                            </div>
                            <div class="lesson-progress">
                                <div class="progress-bar">
                                    <div class="progress-bar-fill" style="width: ${p.completion_percentage}%"></div>
                                </div>
                                <span>${p.completion_percentage}%</span>
                            </div>
                            <div class="lesson-actions">
                                ${p.is_completed 
                                    ? '<span class="badge completed">✓ Complete</span>'
                                    : `<a href="#lesson/${p.capsule}" class="btn btn-sm btn-primary">Continue</a>`
                                }
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            contentDiv.innerHTML = '<div class="error-message"><p>Unable to load lesson progress.</p></div>';
        }
    }

    async loadQuizzesTab() {
        const contentDiv = document.getElementById('tab-content');
        
        if (!this.isAuthenticated) {
            contentDiv.innerHTML = this.renderAuthRequired();
            return;
        }

        contentDiv.innerHTML = '<p class="loading">Loading quiz history...</p>';

        try {
            const attempts = await apiClient.get('/quiz-attempts/');
            
            if (!attempts?.length) {
                contentDiv.innerHTML = `
                    <div class="empty-state">
                        <p>No quiz attempts yet.</p>
                        <p class="text-muted">Complete lessons to take quizzes!</p>
                    </div>
                `;
                return;
            }

            contentDiv.innerHTML = `
                <div class="quiz-history">
                    <h3>Quiz History</h3>
                    <table class="quiz-table">
                        <thead>
                            <tr>
                                <th>Quiz</th>
                                <th>Score</th>
                                <th>Result</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${attempts.map(a => `
                                <tr class="${a.passed ? 'passed' : 'failed'}">
                                    <td>${a.quiz_title || 'Quiz'}</td>
                                    <td>${a.score}/${a.max_score} (${Math.round(a.score / a.max_score * 100)}%)</td>
                                    <td>
                                        ${a.passed 
                                            ? '<span class="badge success">Passed</span>' 
                                            : '<span class="badge warning">Needs Review</span>'
                                        }
                                    </td>
                                    <td>${new Date(a.completed_at).toLocaleDateString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } catch (error) {
            contentDiv.innerHTML = '<div class="error-message"><p>Unable to load quiz history.</p></div>';
        }
    }

    async loadAdaptiveTab() {
        const contentDiv = document.getElementById('tab-content');
        
        if (!this.isAuthenticated) {
            contentDiv.innerHTML = this.renderAuthRequired();
            return;
        }

        contentDiv.innerHTML = '<div id="adaptive-container"></div>';
        
        const adaptiveContainer = document.getElementById('adaptive-container');
        this.adaptiveComponent = new AdaptiveLearningComponent(adaptiveContainer);
        await this.adaptiveComponent.render();
    }

    renderAuthRequired() {
        return `
            <div class="auth-required">
                <p>Please sign in to view this content.</p>
                <button class="btn btn-primary" onclick="window.location.hash='#login'">
                    Sign In
                </button>
            </div>
        `;
    }
}
