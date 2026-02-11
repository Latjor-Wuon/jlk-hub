// Custom Notification/Toast System

export class Notification {
    static show(message, type = 'info', duration = 4000) {
        // Remove any existing notifications
        const existing = document.querySelector('.toast-notification');
        if (existing) {
            existing.remove();
        }

        // Create notification element
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        
        // Add icon based on type
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        
        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        // Add to document
        document.body.appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('toast-show'), 10);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.remove('toast-show');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    }

    static success(message, duration) {
        this.show(message, 'success', duration);
    }

    static error(message, duration) {
        this.show(message, 'error', duration);
    }

    static warning(message, duration) {
        this.show(message, 'warning', duration);
    }

    static info(message, duration) {
        this.show(message, 'info', duration);
    }
}

// Make it globally available
window.Notification = Notification;

// Export helper function for named import compatibility
export function showNotification(message, type = 'info', duration = 4000) {
    Notification.show(message, type, duration);
}
