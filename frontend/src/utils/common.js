// Shared Auth UI Utilities for JLN Hub

export function initAuthUI() {
    const authManager = window.AuthManager ? new window.AuthManager() : null;
    const navAuthContainer = document.getElementById('nav-auth');
    const adminNavLink = document.getElementById('admin-nav-link');
    const lessonGenNavLink = document.getElementById('lesson-gen-nav-link');
    
    if (!navAuthContainer) return;
    
    if (authManager && authManager.isAuthenticated()) {
        const user = authManager.getUser();
        const profile = authManager.getProfile();
        
        navAuthContainer.innerHTML = `
            <div class="user-menu">
                <span class="user-name">👤 ${user.username}</span>
                <button class="btn btn-secondary btn-sm" id="logout-btn">Logout</button>
            </div>
        `;
        
        // Add logout handler
        document.getElementById('logout-btn').addEventListener('click', async () => {
            await authManager.logout();
            window.location.href = 'home.html';
        });
        
        // Show admin menu if user is staff
        if (user.is_staff && adminNavLink) {
            adminNavLink.style.display = 'block';
        }
        
        // Show lesson generator if user is staff
        if (user.is_staff && lessonGenNavLink) {
            lessonGenNavLink.style.display = 'block';
        }
    } else {
        navAuthContainer.innerHTML = `
            <a href="src/pages/login.html" class="btn btn-primary btn-sm">Login</a>
            <a href="src/pages/register.html" class="btn btn-secondary btn-sm">Register</a>
        `;
    }
}

// Update online status indicator
export function updateOnlineStatus() {
    const statusEl = document.getElementById('online-status');
    if (!statusEl) return;
    
    const updateIndicator = () => {
        if (navigator.onLine) {
            statusEl.textContent = '🟢 Online';
            statusEl.style.color = '#27ae60';
        } else {
            statusEl.textContent = '🔴 Offline';
            statusEl.style.color = '#e74c3c';
        }
    };
    
    updateIndicator();
    window.addEventListener('online', updateIndicator);
    window.addEventListener('offline', updateIndicator);
}

// Initialize both auth and online status
export function initCommon() {
    initAuthUI();
    updateOnlineStatus();
}
