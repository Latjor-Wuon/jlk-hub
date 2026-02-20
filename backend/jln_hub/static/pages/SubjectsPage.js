// Subjects Page Component
import { apiClient } from '../utils/api.js';

export class SubjectsPage {
    constructor(container) {
        this.container = container;
    }

    async render() {
        this.container.innerHTML = `
            <h2>Subjects</h2>
            <div id="subjects-list" class="subjects-grid">
                <p class="loading">Loading subjects...</p>
            </div>
        `;

        await this.loadSubjects();
    }

    async loadSubjects() {
        const container = document.getElementById('subjects-list');
        try {
            const response = await apiClient.get('/subjects/');
            console.log('API Response:', response);
            
            // DRF returns paginated response with 'results' key
            const subjects = response.results || response;
            
            console.log('Subjects loaded:', subjects);
            
            if (subjects && subjects.length > 0) {
                container.innerHTML = subjects.map(subject => `
                    <div class="subject-card" data-subject-id="${subject.id}">
                        <div class="subject-icon">${subject.icon || '📚'}</div>
                        <h3>${subject.name}</h3>
                        <p>${subject.description || 'Explore lessons in this subject'}</p>
                    </div>
                `).join('');
                
                // Add click handlers
                this.attachEventListeners();
            } else {
                container.innerHTML = '<p class="info-message">No subjects available yet.</p>';
            }
        } catch (error) {
            console.error('Error loading subjects:', error);
            container.innerHTML = '<p class="error-message">Failed to load subjects. Please try again.</p>';
        }
    }
    
    attachEventListeners() {
        // Add click handlers to subject cards
        document.querySelectorAll('.subject-card').forEach(card => {
            card.addEventListener('click', () => {
                const subjectId = card.getAttribute('data-subject-id');
                // Navigate to lessons page with subject filter
                window.location.href = `lessons.html?subject=${subjectId}`;
            });
        });
    }
}
