// Main Application Entry Point
import { Navigation } from './components/Navigation.js';
import { Notification } from './components/Notification.js';
import { Router } from './utils/Router.js';
import { HomePage } from './pages/HomePage.js';
import { SubjectsPage } from './pages/SubjectsPage.js';
import { LessonsPage } from './pages/LessonsPage.js';
import { LessonDetailPage } from './pages/LessonDetailPage.js';
import { ProgressPage } from './pages/ProgressPage.js';
import { AdminDashboardPage } from './pages/AdminDashboardPage.js';
import { SimulationsPage } from './pages/SimulationsPage.js';
import { QuizzesPage } from './pages/QuizzesPage.js';

class JLNApp {
    constructor() {
        this.navigation = new Navigation();
        this.router = new Router();
        this.currentPage = null;
        this.pages = {};
        this.authManager = new window.AuthManager();
        this.init();
    }

    init() {
        // Initialize navigation
        this.navigation.init();
        this.updateAuthUI();

        // Register routes
        this.router.register('home', (params) => this.showPage('home', params));
        this.router.register('subjects', (params) => this.showPage('subjects', params));
        this.router.register('lessons', (params) => this.showPage('lessons', params));
        this.router.register('lesson', (params) => this.showLessonDetail(params.id));
        this.router.register('progress', (params) => this.showPage('progress', params));
        this.router.register('simulations', (params) => this.showPage('simulations', params));
        this.router.register('quizzes', (params) => this.showPage('quizzes', params));
        this.router.register('admin-dashboard', (params) => this.showPage('admin-dashboard', params));
        this.router.register('login', (params) => this.showPage('login', params));
        this.router.register('register', (params) => this.showPage('register', params));

        // Listen for navigation clicks
        document.addEventListener('click', (e) => {
            const navLink = e.target.closest('.nav-link');
            if (navLink) {
                e.preventDefault();
                const page = navLink.getAttribute('data-page');
                this.router.navigate(page);
                return;
            }

            const lessonCard = e.target.closest('.lesson-card');
            if (lessonCard) {
                const lessonId = lessonCard.dataset.lessonId;
                if (lessonId) {
                    this.router.navigate('lesson', { id: lessonId });
                }
                return;
            }

            const subjectCard = e.target.closest('.subject-card');
            if (subjectCard) {
                const subjectId = subjectCard.dataset.subjectId;
                if (subjectId) {
                    this.router.navigate('lessons', { subject: subjectId });
                }
                return;
            }

            const backButton = e.target.closest('#back-to-lessons');
            if (backButton) {
                this.router.navigate('lessons');
            }
        });
    }

    updateAuthUI() {
        const navAuth = document.getElementById('nav-auth');
        const adminNavLink = document.getElementById('admin-nav-link');
        
        if (!navAuth) return;

        if (this.authManager.isAuthenticated()) {
            const user = this.authManager.getUser();
            navAuth.innerHTML = `
                <div class="user-info">
                    <span>👤 ${user.username}</span>
                </div>
                <button class="btn-auth btn-logout" onclick="app.handleLogout()">Logout</button>
            `;
            
            // Show/hide admin dashboard link based on user role
            if (adminNavLink) {
                adminNavLink.style.display = user.is_staff ? 'block' : 'none';
            }
        } else {
            navAuth.innerHTML = `
                <button class="btn-auth btn-login" onclick="app.router.navigate('login')">Login</button>
                <button class="btn-auth btn-register" onclick="app.router.navigate('register')">Register</button>
            `;
            
            // Hide admin dashboard link when not authenticated
            if (adminNavLink) {
                adminNavLink.style.display = 'none';
            }
        }
    }

    async handleLogout() {
        await this.authManager.logout();
        this.updateAuthUI();
        this.router.navigate('home');
        Notification.success('You have been logged out successfully');
    }

    async showPage(pageName, params = {}) {
        console.log('Showing page:', pageName, 'with params:', params);
        
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Show selected page
        const pageElement = document.getElementById(`${pageName}-page`);
        if (!pageElement) {
            console.error('Page element not found:', `${pageName}-page`);
            return;
        }

        pageElement.classList.add('active');
        this.navigation.setActivePage(pageName);

        // Render page content
        switch(pageName) {
            case 'home':
                if (!this.pages.home) {
                    this.pages.home = new HomePage(pageElement);
                }
                this.pages.home.render();
                break;

            case 'subjects':
                if (!this.pages.subjects) {
                    this.pages.subjects = new SubjectsPage(pageElement);
                }
                this.pages.subjects.render();
                break;

            case 'lessons':
                if (!this.pages.lessons) {
                    this.pages.lessons = new LessonsPage(pageElement);
                }
                await this.pages.lessons.render();
                // Apply filters from URL params
                if (params.subject || params.grade) {
                    this.pages.lessons.setFilters(params.subject || '', params.grade || '');
                }
                break;

            case 'progress':
                if (!this.pages.progress) {
                    this.pages.progress = new ProgressPage(pageElement);
                }
                await this.pages.progress.render();
                break;

            case 'simulations':
                if (!this.pages.simulations) {
                    this.pages.simulations = new SimulationsPage(pageElement);
                }
                await this.pages.simulations.render();
                break;

            case 'quizzes':
                if (!this.pages.quizzes) {
                    this.pages.quizzes = new QuizzesPage(pageElement);
                }
                await this.pages.quizzes.render();
                break;

            case 'admin-dashboard':
                if (!this.authManager.isAuthenticated()) {
                    Notification.warning('Please login as admin to access the dashboard');
                    this.router.navigate('login');
                    return;
                }
                const user = this.authManager.getUser();
                if (!user.is_staff) {
                    Notification.error('Access denied: Admin privileges required');
                    this.router.navigate('home');
                    return;
                }
                pageElement.innerHTML = '';
                pageElement.appendChild(AdminDashboardPage());
                break;

            case 'login':
                await this.renderLoginPage(pageElement);
                break;

            case 'register':
                await this.renderRegisterPage(pageElement);
                break;
        }

        this.currentPage = pageName;
    }

    async renderLoginPage(pageElement) {
        const response = await fetch('/static/pages/login.html');
        const html = await response.text();
        pageElement.innerHTML = html;

        const form = document.getElementById('login-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const username = formData.get('username');
                const password = formData.get('password');

                const result = await this.authManager.login(username, password);
                
                if (result.success) {
                    this.updateAuthUI();
                    this.router.navigate('home');
                    Notification.success('Login successful! Welcome back.');
                } else {
                    const errorDiv = document.getElementById('login-error');
                    errorDiv.textContent = result.error;
                    errorDiv.style.display = 'block';
                }
            });
        }
    }

    async renderRegisterPage(pageElement) {
        const response = await fetch('/static/pages/register.html');
        const html = await response.text();
        pageElement.innerHTML = html;

        // Load grades for dropdown
        try {
            const gradesResp = await fetch('/api/grades/');
            const gradesData = await gradesResp.json();
            // Handle DRF paginated response
            const grades = gradesData.results || gradesData;
            const gradeSelect = document.getElementById('reg-grade');
            if (gradeSelect && grades) {
                gradeSelect.innerHTML = '<option value="">Select Grade</option>' +
                    grades.map(g => `<option value="${g.id}">${g.name}</option>`).join('');
            }
        } catch (error) {
            console.error('Failed to load grades:', error);
        }

        const form = document.getElementById('register-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                
                const userData = {
                    username: formData.get('username'),
                    email: formData.get('email'),
                    first_name: formData.get('first_name'),
                    last_name: formData.get('last_name'),
                    password: formData.get('password'),
                    password2: formData.get('password2'),
                    grade: formData.get('grade'),
                    school_name: formData.get('school_name')
                };

                const result = await this.authManager.register(userData);
                
                if (result.success) {
                    this.updateAuthUI();
                    this.router.navigate('home');
                    Notification.success('Registration successful! Welcome to JLN Hub.');
                } else {
                    const errorDiv = document.getElementById('register-error');
                    errorDiv.textContent = result.error;
                    errorDiv.style.display = 'block';
                }
            });
        }
    }

    showLessonDetail(lessonId) {
        const pageElement = document.getElementById('lesson-detail-page');
        if (!pageElement) return;

        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        pageElement.classList.add('active');

        // Create and render lesson detail
        const lessonDetailPage = new LessonDetailPage(pageElement);
        lessonDetailPage.render(lessonId);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new JLNApp();
});
