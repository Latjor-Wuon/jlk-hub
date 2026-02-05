// Progress Page Component
import { apiClient } from '../utils/api.js';
import { formatPercentage } from '../utils/helpers.js';

export class ProgressPage {
    constructor(container) {
        this.container = container;
    }

    async render() {
        this.container.innerHTML = `
            <h2>My Learning Progress</h2>
            <div id="progress-summary" class="progress-summary">
                <p class="loading">Loading progress...</p>
            </div>
            <div id="progress-list" class="progress-list">
            </div>
        `;

        await this.loadProgress();
    }

    async loadProgress() {
        const summaryContainer = document.getElementById('progress-summary');
        
        // This would require authentication in a real app
        summaryContainer.innerHTML = `
            <p class="info-message">
                Progress tracking is available! Start learning to track your progress.
                <br><small>Note: User authentication will be added for personalized tracking.</small>
            </p>
        `;

        // If we had a logged-in user, we would load their progress
        // const summary = await apiClient.get('/progress/summary/');
        // const progressList = await apiClient.get('/progress/');
    }

    displayProgressSummary(summary) {
        return `
            <div class="progress-card">
                <h3>${summary.total_capsules_started}</h3>
                <p>Lessons Started</p>
            </div>
            <div class="progress-card">
                <h3>${summary.completed_capsules}</h3>
                <p>Lessons Completed</p>
            </div>
            <div class="progress-card">
                <h3>${summary.in_progress}</h3>
                <p>In Progress</p>
            </div>
            <div class="progress-card">
                <h3>${formatPercentage(summary.average_completion)}</h3>
                <p>Average Completion</p>
            </div>
        `;
    }

    displayProgressList(progressList) {
        return progressList.map(progress => `
            <div class="progress-item">
                <h4>${progress.capsule_title}</h4>
                <p>Completion: ${formatPercentage(progress.completion_percentage)}</p>
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: ${progress.completion_percentage}%"></div>
                </div>
                <p class="text-secondary">Last accessed: ${new Date(progress.last_accessed).toLocaleDateString()}</p>
            </div>
        `).join('');
    }
}
