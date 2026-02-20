// Lesson Detail Page Component
import { apiClient } from '../utils/api.js';
import { QuizComponent } from '../components/QuizComponent.js';

export class LessonDetailPage {
    constructor(container) {
        this.container = container;
        this.currentLesson = null;
        this.quizComponents = [];
    }

    async render(lessonId) {
        this.container.innerHTML = `
            <button class="btn-back" id="back-to-lessons">← Back to Lessons</button>
            <div id="lesson-content">
                <p class="loading">Loading lesson...</p>
            </div>
        `;

        const lesson = await apiClient.get(`/capsules/${lessonId}/`);
        
        if (lesson) {
            this.currentLesson = lesson;
            this.displayLesson(lesson);
        } else {
            document.getElementById('lesson-content').innerHTML = 
                '<p class="error-message">Failed to load lesson.</p>';
        }
    }

    displayLesson(lesson) {
        const container = document.getElementById('lesson-content');
        
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

        container.innerHTML = html;

        // Render quizzes
        if (lesson.quizzes && lesson.quizzes.length > 0) {
            lesson.quizzes.forEach(quiz => {
                const quizContainer = document.createElement('div');
                container.appendChild(quizContainer);
                
                const quizComponent = new QuizComponent(quizContainer, quiz);
                quizComponent.render();
                this.quizComponents.push(quizComponent);
            });
        }
    }

    formatContent(content) {
        return content.split('\n').map(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith('# ')) {
                return `<h3>${trimmed.replace(/^#+\s*/, '')}</h3>`;
            } else if (trimmed.startsWith('## ')) {
                return `<h4>${trimmed.replace(/^#+\s*/, '')}</h4>`;
            } else if (trimmed) {
                return `<p>${trimmed}</p>`;
            }
            return '';
        }).join('');
    }
}
