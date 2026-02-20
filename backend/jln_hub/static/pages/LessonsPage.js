// Lessons Page Component
import { apiClient } from '../utils/api.js';

export class LessonsPage {
    constructor(container) {
        this.container = container;
        this.currentFilters = {
            subject: '',
            grade: ''
        };
    }

    async render() {
        this.container.innerHTML = `
            <h2>All Lessons</h2>
            
            <div class="filters">
                <select id="subject-filter" class="filter-select">
                    <option value="">All Subjects</option>
                </select>
                <select id="grade-filter" class="filter-select">
                    <option value="">All Grades</option>
                </select>
            </div>

            <div id="lessons-list" class="lessons-grid">
                <p class="loading">Loading lessons...</p>
            </div>
        `;

        await this.loadFilters();
        await this.loadLessons();
        this.attachFilterListeners();
    }

    async loadFilters() {
        // Load subjects
        const subjectsResponse = await apiClient.get('/subjects/');
        const subjects = subjectsResponse.results || subjectsResponse;
        const subjectFilter = document.getElementById('subject-filter');
        if (subjects && subjectFilter) {
            subjectFilter.innerHTML = '<option value="">All Subjects</option>' +
                subjects.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
        }

        // Load grades
        const gradesResponse = await apiClient.get('/grades/');
        const grades = gradesResponse.results || gradesResponse;
        const gradeFilter = document.getElementById('grade-filter');
        if (grades && gradeFilter) {
            gradeFilter.innerHTML = '<option value="">All Grades</option>' +
                grades.map(g => `<option value="${g.id}">${g.name}</option>`).join('');
        }
    }

    attachFilterListeners() {
        const subjectFilter = document.getElementById('subject-filter');
        const gradeFilter = document.getElementById('grade-filter');

        if (subjectFilter) {
            subjectFilter.addEventListener('change', (e) => {
                this.currentFilters.subject = e.target.value;
                this.loadLessons();
            });
        }

        if (gradeFilter) {
            gradeFilter.addEventListener('change', (e) => {
                this.currentFilters.grade = e.target.value;
                this.loadLessons();
            });
        }
    }

    setFilters(subjectId = '', gradeId = '') {
        this.currentFilters.subject = subjectId;
        this.currentFilters.grade = gradeId;
        
        // Update the dropdown values if they exist
        const subjectFilter = document.getElementById('subject-filter');
        const gradeFilter = document.getElementById('grade-filter');
        
        if (subjectFilter && subjectId) {
            subjectFilter.value = subjectId;
        }
        if (gradeFilter && gradeId) {
            gradeFilter.value = gradeId;
        }
        
        // Reload lessons with new filters
        this.loadLessons();
    }

    async loadLessons() {
        const container = document.getElementById('lessons-list');
        container.innerHTML = '<p class="loading">Loading lessons...</p>';
        
        try {
            let endpoint = '/capsules/';
            const params = [];
            if (this.currentFilters.subject) params.push(`subject=${this.currentFilters.subject}`);
            if (this.currentFilters.grade) params.push(`grade=${this.currentFilters.grade}`);
            if (params.length > 0) endpoint += '?' + params.join('&');
            
            const response = await apiClient.get(endpoint);
            console.log('Lessons API Response:', response);
            const lessons = response.results || response;
            
            if (lessons && lessons.length > 0) {
                container.innerHTML = lessons.map(lesson => this.createLessonCard(lesson)).join('');
                // Add click handlers
                this.attachLessonClickListeners();
            } else {
                container.innerHTML = '<p class="info-message">No lessons match your filters.</p>';
            }
        } catch (error) {
            console.error('Error loading lessons:', error);
            container.innerHTML = '<p class="error-message">Failed to load lessons. Please try again.</p>';
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
    
    attachLessonClickListeners() {
        // Add click handlers to lesson cards
        document.querySelectorAll('.lesson-card').forEach(card => {
            card.addEventListener('click', () => {
                const lessonId = card.getAttribute('data-lesson-id');
                window.location.href = `lesson-detail.html?id=${lessonId}`;
            });
        });
    }

    setFilters(subjectId, gradeId) {
        this.currentFilters.subject = subjectId || '';
        this.currentFilters.grade = gradeId || '';
        
        const subjectFilter = document.getElementById('subject-filter');
        const gradeFilter = document.getElementById('grade-filter');
        
        if (subjectFilter) subjectFilter.value = this.currentFilters.subject;
        if (gradeFilter) gradeFilter.value = this.currentFilters.grade;
        
        this.loadLessons();
    }
}
