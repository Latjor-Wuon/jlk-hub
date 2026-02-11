// API Configuration and Helper Functions

export const API_BASE_URL = '/api';
const API_BASE = API_BASE_URL;

// Get CSRF token from cookie
function getCsrfToken() {
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

// Get auth token from localStorage
function getAuthToken() {
    return localStorage.getItem('jln_token');
}

// Build headers with auth and CSRF tokens
function buildHeaders(includeAuth = true) {
    const headers = {
        'Content-Type': 'application/json',
    };
    
    const csrfToken = getCsrfToken();
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }
    
    if (includeAuth) {
        const authToken = getAuthToken();
        if (authToken) {
            headers['Authorization'] = `Token ${authToken}`;
        }
    }
    
    return headers;
}

class APIClient {
    constructor() {
        this.baseURL = API_BASE;
    }

    async get(endpoint) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            console.log('API GET:', url);
            const response = await fetch(url, {
                headers: buildHeaders(),
                credentials: 'same-origin'
            });
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Response data:', data);
            return data;
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    }

    async post(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: buildHeaders(),
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });
            if (!response.ok) {
                const errorText = await response.text();
                console.error('POST Error Response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            return null;
        }
    }

    async put(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'PUT',
                headers: buildHeaders(),
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API PUT Error:', error);
            return null;
        }
    }

    async delete(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'DELETE',
                headers: buildHeaders(),
                credentials: 'same-origin'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return true;
        } catch (error) {
            console.error('API DELETE Error:', error);
            return false;
        }
    }
}

export const apiClient = new APIClient();

// Wrapper function for API requests that matches the expected signature
export async function apiRequest(url, method = 'GET', data = null) {
    const endpoint = url.startsWith('/api') ? url.substring(4) : url;
    
    try {
        switch (method.toUpperCase()) {
            case 'GET':
                return await apiClient.get(endpoint);
            case 'POST':
                // Handle FormData differently
                if (data instanceof FormData) {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCsrfToken(),
                            'Authorization': `Token ${getAuthToken()}`
                        },
                        body: data,
                        credentials: 'same-origin'
                    });
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return await response.json();
                }
                return await apiClient.post(endpoint, data);
            case 'PUT':
                return await apiClient.put(endpoint, data);
            case 'DELETE':
                return await apiClient.delete(endpoint);
            default:
                throw new Error(`Unsupported method: ${method}`);
        }
    } catch (error) {
        console.error(`API ${method} Error:`, error);
        throw error;
    }
}
