// Home Page Component
import { apiClient } from '../utils/api.js';
import { formatDuration } from '../utils/helpers.js';

export class HomePage {
    constructor(container) {
        this.container = container;
    }

    async render() {
        this.container.innerHTML = `
            <section class="hero">
                <h2>Welcome to JLN Hub</h2>
                <p>Access South Sudan's national curriculum anytime, anywhere - even offline!</p>
                <div class="stats-grid" id="dashboard-stats">
                    <div class="stat-card">
                        <h3 id="stat-subjects">0</h3>
                        <p>Subjects</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="stat-capsules">0</h3>
                        <p>Lessons Available</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="stat-quizzes">0</h3>
                        <p>Quizzes</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="stat-grades">0</h3>
                        <p>Grade Levels</p>
                    </div>
                </div>
            </section>

            <section class="featured-section">
                <h3>Featured Lessons</h3>
                <div id="featured-lessons" class="lessons-grid">
                    <p class="loading">Loading lessons...</p>
                </div>
            </section>
        `;

        await this.loadStats();
        await this.loadFeaturedLessons();
    }

    async loadStats() {
        const stats = await apiClient.get('/dashboard/stats/');
        if (stats) {
            document.getElementById('stat-subjects').textContent = stats.total_subjects || 0;
            document.getElementById('stat-capsules').textContent = stats.total_capsules || 0;
            document.getElementById('stat-quizzes').textContent = stats.total_quizzes || 0;
            document.getElementById('stat-grades').textContent = stats.total_grades || 0;
        }
    }

    async loadFeaturedLessons() {
        const container = document.getElementById('featured-lessons');
        const response = await apiClient.get('/capsules/featured/');
        const lessons = response.results || response;
        
        if (lessons && lessons.length > 0) {
            container.innerHTML = lessons.map(lesson => this.createLessonCard(lesson)).join('');
        } else {
            container.innerHTML = '<p class="info-message">No featured lessons available yet. Check back soon!</p>';
        }
    }

    createLessonCard(lesson) {
        return `
            <div class="lesson-card" data-lesson-id="${lesson.id}">
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
}
