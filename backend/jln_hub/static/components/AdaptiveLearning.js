/**
 * Adaptive Learning Component
 * 
 * Displays personalized learning recommendations based on quiz performance.
 * Shows adaptive pathways with suggestions for revision or advancement.
 */
import { apiClient } from '../utils/api.js';

export class AdaptiveLearningComponent {
    constructor(container) {
        this.container = container;
        this.pathway = null;
    }

    async render() {
        this.container.innerHTML = `
            <div class="adaptive-learning">
                <div class="adaptive-header">
                    <h3>🎯 Your Personalized Learning Path</h3>
                    <button id="refresh-pathway" class="btn btn-sm">🔄 Refresh</button>
                </div>
                <div id="adaptive-content" class="adaptive-content">
                    <p class="loading">Analyzing your learning progress...</p>
                </div>
            </div>
        `;

        await this.loadPathway();
        this.attachEventListeners();
    }

    async loadPathway(subjectId = null) {
        const contentDiv = document.getElementById('adaptive-content');
        
        try {
            let url = '/adaptive/pathway/';
            if (subjectId) {
                url += `?subject=${subjectId}`;
            }
            
            const pathway = await apiClient.get(url);
            this.pathway = pathway;
            this.displayPathway(pathway);
        } catch (error) {
            contentDiv.innerHTML = `
                <div class="adaptive-guest">
                    <p>📚 Sign in to get personalized learning recommendations!</p>
                    <p class="text-muted">Your progress will be tracked automatically as you complete quizzes.</p>
                </div>
            `;
        }
    }

    displayPathway(pathway) {
        const contentDiv = document.getElementById('adaptive-content');
        
        contentDiv.innerHTML = `
            <!-- Performance Summary -->
            <div class="performance-summary">
                <h4>📊 Your Performance</h4>
                <div class="stats-row">
                    <div class="stat-box">
                        <span class="stat-number">${pathway.current_performance.total_quizzes_taken}</span>
                        <span class="stat-label">Quizzes Taken</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-number">${pathway.current_performance.quizzes_passed}</span>
                        <span class="stat-label">Passed</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-number">${pathway.current_performance.pass_rate}%</span>
                        <span class="stat-label">Pass Rate</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-number">${pathway.current_performance.average_score}%</span>
                        <span class="stat-label">Avg Score</span>
                    </div>
                </div>
            </div>

            <!-- Strengths & Weaknesses -->
            ${this.renderStrengthsWeaknesses(pathway.strengths, pathway.weaknesses)}

            <!-- Active Recommendations -->
            ${this.renderRecommendations(pathway.recommendations)}

            <!-- Revision Needed -->
            ${this.renderRevisionNeeded(pathway.revision_needed)}

            <!-- Suggested Next Lessons -->
            ${this.renderNextLessons(pathway.next_lessons)}

            <!-- Difficulty Levels -->
            ${this.renderDifficultyLevels(pathway.difficulty_levels)}
        `;
    }

    renderStrengthsWeaknesses(strengths, weaknesses) {
        if (!strengths?.length && !weaknesses?.length) {
            return '';
        }

        return `
            <div class="strengths-weaknesses">
                ${strengths?.length ? `
                    <div class="strengths">
                        <h5>💪 Strengths</h5>
                        <ul>
                            ${strengths.map(s => `
                                <li class="strength-item">
                                    ${s.subject} <span class="score">${s.score}%</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                ${weaknesses?.length ? `
                    <div class="weaknesses">
                        <h5>📚 Areas to Improve</h5>
                        <ul>
                            ${weaknesses.map(w => `
                                <li class="weakness-item">
                                    ${w.subject} <span class="score">${w.score}%</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderRecommendations(recommendations) {
        if (!recommendations?.length) {
            return `
                <div class="no-recommendations">
                    <p>Complete some quizzes to get personalized recommendations!</p>
                </div>
            `;
        }

        return `
            <div class="recommendations-section">
                <h4>📋 Recommendations</h4>
                <div class="recommendation-list">
                    ${recommendations.map(rec => `
                        <div class="recommendation-card ${rec.recommendation_type}" data-rec-id="${rec.id}">
                            <div class="rec-icon">${this.getRecIcon(rec.recommendation_type)}</div>
                            <div class="rec-content">
                                <h5>${rec.capsule_title}</h5>
                                <p class="rec-subject">${rec.capsule_subject}</p>
                                <p class="rec-reason">${rec.reason}</p>
                            </div>
                            <div class="rec-actions">
                                <button class="btn btn-sm btn-primary go-to-lesson" 
                                        data-capsule-id="${rec.capsule}">
                                    Go to Lesson
                                </button>
                                <button class="btn btn-sm dismiss-rec" data-rec-id="${rec.id}">
                                    ✕
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getRecIcon(type) {
        const icons = {
            'revision': '🔄',
            'practice': '✏️',
            'next_lesson': '➡️',
            'mastery': '🌟',
            'simplified': '📖'
        };
        return icons[type] || '📌';
    }

    renderRevisionNeeded(revisionList) {
        if (!revisionList?.length) {
            return '';
        }

        return `
            <div class="revision-section">
                <h4>🔄 Topics Needing Revision</h4>
                <div class="revision-list">
                    ${revisionList.map(rev => `
                        <div class="revision-item">
                            <span class="rev-title">${rev.capsule_title}</span>
                            <button class="btn btn-sm btn-warning go-to-lesson" 
                                    data-capsule-id="${rev.capsule}">
                                Review Now
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderNextLessons(lessons) {
        if (!lessons?.length) {
            return '';
        }

        return `
            <div class="next-lessons-section">
                <h4>📚 Suggested Next Lessons</h4>
                <div class="next-lessons-grid">
                    ${lessons.map(lesson => `
                        <div class="next-lesson-card">
                            <h5>${lesson.title}</h5>
                            <p>${lesson.subject} • ${lesson.grade}</p>
                            <button class="btn btn-sm btn-primary go-to-lesson" 
                                    data-capsule-id="${lesson.id}">
                                Start Learning
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderDifficultyLevels(levels) {
        if (!levels?.length) {
            return '';
        }

        return `
            <div class="difficulty-levels-section">
                <h4>📈 Your Level by Subject</h4>
                <div class="levels-list">
                    ${levels.map(level => `
                        <div class="level-item">
                            <span class="level-subject">${level.subject_name}</span>
                            <span class="level-badge ${level.current_level}">${level.current_level}</span>
                            <span class="level-stats">
                                ${level.average_score.toFixed(0)}% avg • ${level.total_attempts} attempts
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        document.getElementById('refresh-pathway')?.addEventListener('click', () => {
            this.loadPathway();
        });

        // Delegate click events for dynamic content
        this.container.addEventListener('click', async (e) => {
            // Handle "Go to Lesson" buttons
            if (e.target.classList.contains('go-to-lesson')) {
                const capsuleId = e.target.dataset.capsuleId;
                if (capsuleId) {
                    window.location.hash = `#lesson/${capsuleId}`;
                }
            }

            // Handle dismiss recommendation
            if (e.target.classList.contains('dismiss-rec')) {
                const recId = e.target.dataset.recId;
                if (recId) {
                    await this.dismissRecommendation(recId);
                }
            }
        });
    }

    async dismissRecommendation(recId) {
        try {
            await apiClient.post('/adaptive/dismiss_recommendation/', {
                recommendation_id: recId
            });
            
            // Remove from UI
            const recCard = document.querySelector(`[data-rec-id="${recId}"]`);
            if (recCard) {
                recCard.style.opacity = '0';
                setTimeout(() => recCard.remove(), 300);
            }
        } catch (error) {
            console.error('Failed to dismiss recommendation:', error);
        }
    }
}

/**
 * Triggers adaptive analysis after quiz submission
 */
export async function analyzeQuizForAdaptivePath(quizAttemptId) {
    try {
        const result = await apiClient.post('/adaptive/analyze_quiz/', {
            quiz_attempt_id: quizAttemptId
        });
        return result;
    } catch (error) {
        console.log('Note: Adaptive analysis requires authentication');
        return null;
    }
}
