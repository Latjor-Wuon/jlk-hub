// Authentication Module for JLN Hub

class AuthManager {
    constructor() {
        this.token = localStorage.getItem('jln_token');
        this.user = JSON.parse(localStorage.getItem('jln_user') || 'null');
        this.profile = JSON.parse(localStorage.getItem('jln_profile') || 'null');
        this.csrfInitialized = false;
    }

    // Initialize CSRF token by making a request to the server
    async initCSRF() {
        if (this.csrfInitialized) return;
        try {
            await fetch('/api/auth/csrf/', { credentials: 'include' });
            this.csrfInitialized = true;
        } catch (error) {
            console.error('Failed to initialize CSRF:', error);
        }
    }

    // Get CSRF token from cookie
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    isAuthenticated() {
        return !!this.token;
    }

    getToken() {
        return this.token;
    }

    getUser() {
        return this.user;
    }

    getProfile() {
        return this.profile;
    }

    async register(userData) {
        try {
            await this.initCSRF();
            const csrfToken = this.getCSRFToken();
            const response = await fetch('/api/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                },
                credentials: 'include',
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(Object.values(error).flat().join(', '));
            }

            const data = await response.json();
            this.setAuthData(data);
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async login(username, password) {
        try {
            await this.initCSRF();
            const csrfToken = this.getCSRFToken();
            const response = await fetch('/api/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Login failed');
            }

            const data = await response.json();
            this.setAuthData(data);
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async logout() {
        if (this.token) {
            try {
                await fetch('/api/auth/logout/', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Token ${this.token}`,
                    },
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
        }
        this.clearAuthData();
    }

    setAuthData(data) {
        this.token = data.token;
        this.user = data.user;
        this.profile = data.profile;

        localStorage.setItem('jln_token', data.token);
        localStorage.setItem('jln_user', JSON.stringify(data.user));
        localStorage.setItem('jln_profile', JSON.stringify(data.profile));
    }

    clearAuthData() {
        this.token = null;
        this.user = null;
        this.profile = null;

        localStorage.removeItem('jln_token');
        localStorage.removeItem('jln_user');
        localStorage.removeItem('jln_profile');
    }

    async fetchWithAuth(url, options = {}) {
        const headers = {
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Token ${this.token}`;
        }

        return fetch(url, {
            ...options,
            headers,
        });
    }
}

// Export for use in main app
window.AuthManager = AuthManager;
