/**
 * AI Lesson Generator Page
 * Page wrapper for the LessonGeneration component
 */

import { LessonGenerationComponent } from '../components/LessonGeneration.js';

export class LessonGeneratorPage {
    constructor(container) {
        this.container = container;
        this.lessonGenComponent = null;
    }

    async render() {
        // Check if user is admin
        const authManager = window.AuthManager ? new window.AuthManager() : null;
        if (!authManager || !authManager.isAuthenticated()) {
            this.renderUnauthorized();
            return;
        }

        const user = authManager.getUser();
        if (!user || !user.is_staff) {
            this.renderUnauthorized();
            return;
        }

        // User is authorized, render the component
        this.container.innerHTML = '';
        
        if (!this.lessonGenComponent) {
            this.lessonGenComponent = new LessonGenerationComponent();
        }
        
        const componentElement = await this.lessonGenComponent.render();
        this.container.appendChild(componentElement);
    }

    renderUnauthorized() {
        this.container.innerHTML = `
            <div class="unauthorized-message">
                <div class="message-card">
                    <h2>🔒 Access Restricted</h2>
                    <p>This page is only available to administrators and content creators.</p>
                    <p>Please <a href="#login" class="link">login</a> with an admin account to access the AI Lesson Generator.</p>
                    <button class="btn btn-primary" onclick="app.router.navigate('home')">
                        ← Back to Home
                    </button>
                </div>
            </div>
            
            <style>
                .unauthorized-message {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 400px;
                    padding: 40px 20px;
                }

                .message-card {
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    max-width: 500px;
                }

                .message-card h2 {
                    color: #2563eb;
                    margin-bottom: 20px;
                }

                .message-card p {
                    color: #6b7280;
                    margin-bottom: 15px;
                    line-height: 1.6;
                }

                .message-card .link {
                    color: #2563eb;
                    text-decoration: none;
                }

                .message-card .link:hover {
                    text-decoration: underline;
                }

                .message-card .btn {
                    margin-top: 20px;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 1em;
                    transition: all 0.2s;
                }

                .btn-primary {
                    background: #2563eb;
                    color: white;
                }

                .btn-primary:hover {
                    background: #1d4ed8;
                }
            </style>
        `;
    }
}
