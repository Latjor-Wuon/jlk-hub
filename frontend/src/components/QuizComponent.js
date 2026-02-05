// Quiz Component
import { apiClient } from '../utils/api.js';

export class QuizComponent {
    constructor(container, quiz) {
        this.container = container;
        this.quiz = quiz;
        this.formId = `quiz-form-${quiz.id}`;
        this.resultsId = `quiz-results-${quiz.id}`;
    }

    render() {
        this.container.innerHTML = `
            <div class="quiz-section" id="quiz-${this.quiz.id}">
                <h3>📝 ${this.quiz.title}</h3>
                <p>${this.quiz.instructions || 'Answer the following questions:'}</p>
                
                <form id="${this.formId}">
                    ${this.quiz.questions.map((q, idx) => this.renderQuestion(q, idx)).join('')}
                    
                    <button type="submit" class="btn btn-primary">Submit Quiz</button>
                </form>
                
                <div id="${this.resultsId}"></div>
            </div>
        `;

        this.attachEventListeners();
    }

    renderQuestion(question, index) {
        return `
            <div class="question">
                <div class="question-text">${index + 1}. ${question.question_text}</div>
                <div class="options">
                    ${question.options.map((option, optIdx) => `
                        <div class="option">
                            <input type="radio" 
                                   id="q${question.id}-opt${optIdx}" 
                                   name="question-${question.id}" 
                                   value="${option}"
                                   required>
                            <label for="q${question.id}-opt${optIdx}">${option}</label>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const form = document.getElementById(this.formId);
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    async handleSubmit(event) {
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
        const result = await apiClient.post(`/quizzes/${this.quiz.id}/submit/`, {
            quiz_id: this.quiz.id,
            answers: answers
        });
        
        if (result) {
            this.displayResults(result);
        }
    }

    displayResults(result) {
        const resultsContainer = document.getElementById(this.resultsId);
        const form = document.getElementById(this.formId);
        
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
                <button class="btn btn-primary" id="retake-quiz-${this.quiz.id}">Retake Quiz</button>
            </div>
        `;
        
        resultsContainer.innerHTML = html;

        // Attach retake listener
        const retakeBtn = document.getElementById(`retake-quiz-${this.quiz.id}`);
        if (retakeBtn) {
            retakeBtn.addEventListener('click', () => this.retakeQuiz());
        }
    }

    retakeQuiz() {
        const form = document.getElementById(this.formId);
        const results = document.getElementById(this.resultsId);
        
        form.style.display = 'block';
        form.reset();
        results.innerHTML = '';
    }
}
