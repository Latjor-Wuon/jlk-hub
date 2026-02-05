// Navigation Component
export class Navigation {
    constructor() {
        this.currentPage = 'home';
    }

    init() {
        this.attachEventListeners();
        this.checkOnlineStatus();
    }

    attachEventListeners() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                // Navigation is now handled by Router in index.js
                // Just update active state
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }

    setActivePage(pageName) {
        this.currentPage = pageName;
    }

    checkOnlineStatus() {
        const updateStatus = () => {
            const statusEl = document.getElementById('online-status');
            if (!statusEl) return;
            
            if (navigator.onLine) {
                statusEl.textContent = '🟢 Online';
                statusEl.style.color = '#27ae60';
            } else {
                statusEl.textContent = '🔴 Offline';
                statusEl.style.color = '#e74c3c';
            }
        };
        
        updateStatus();
        window.addEventListener('online', updateStatus);
        window.addEventListener('offline', updateStatus);
    }
}
