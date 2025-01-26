document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const menuToggle = document.getElementById('menu-toggle');
    const searchInput = document.getElementById('search');
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('img');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

    // Mobile menu toggle
    menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('visible');
    });

    // Search functionality
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            const response = await fetch(`/search?q=${encodeURIComponent(e.target.value)}`);
            const data = await response.json();
            // Will implement search results display
        }, 300);
    });

    function updateThemeIcon(theme) {
        const iconBase = themeIcon.src.substring(0, themeIcon.src.lastIndexOf('/') + 1);
        themeIcon.src = `${iconBase}${theme}_mode.svg`;
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        updateThemeIcon(theme);

        if (theme === 'auto') {
            if (prefersDark.matches) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        } else if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }

    // Initialize theme icon
    updateThemeIcon(localStorage.getItem('theme') || 'auto');

    // Theme toggle click handler
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const themes = ['auto', 'light', 'dark'];
        const nextTheme = themes[(themes.indexOf(currentTheme) + 1) % themes.length];
        setTheme(nextTheme);
    });

    // Listen for system theme changes when in auto mode
    prefersDark.addEventListener('change', (e) => {
        if (document.documentElement.getAttribute('data-theme') === 'auto') {
            if (e.matches) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        }
    });

    const notificationsBtn = document.getElementById('notifications');
    const notificationsList = document.createElement('div');
    notificationsList.className = 'notifications-list hidden';
    sidebar.appendChild(notificationsList);

    function getNotifications() {
        return JSON.parse(localStorage.getItem('notifications') || '[]');
    }

    function saveNotifications(notifications) {
        localStorage.setItem('notifications', JSON.stringify(notifications));
    }

    const severityIcons = {
        info: 'info',
        success: 'check_circle',
        warning: 'warning',
        error: 'error'
    };

    function getIconHtml(name) {
        return `<img src="${notificationsBtn.querySelector('img').src.replace('notifications', name)}" alt="${name}">`;
    }

    function renderNotifications() {
        const notifications = getNotifications();
        notificationsList.innerHTML = notifications.length
            ? `
                <button class="clear-all">Clear All</button>
                ${notifications.map(n => `
                    <div class="notification ${n.severity}" data-id="${n.id}">
                        <div class="notification-header">
                            <div class="notification-title">
                                <span class="severity-icon">${getIconHtml(severityIcons[n.severity])}</span>
                                <span class="title">${n.title}</span>
                            </div>
                            <button class="dismiss" title="Dismiss">${getIconHtml('close')}</button>
                        </div>
                        <div class="message">${n.message}</div>
                        <div class="timestamp">
                            ${getIconHtml('schedule')}
                            ${new Date(n.timestamp).toLocaleString()}
                        </div>
                    </div>
                `).join('')}`
            : `
                <div class="empty-notifications">
                    ${getIconHtml('notifications')}
                    <p>No notifications</p>
                </div>
            `;
    }

    const severityPriority = {
        error: 3,
        warning: 2,
        success: 1,
        info: 0
    };

    function getHighestSeverity(notifications) {
        if (!notifications.length) return 'none';
        return notifications.reduce((highest, n) => {
            return severityPriority[n.severity] > severityPriority[highest] ? n.severity : highest;
        }, 'info');
    }

    function updateNotificationIcon() {
        const notifications = getNotifications();
        const severity = getHighestSeverity(notifications);
        const icon = notificationsBtn.querySelector('img');

        // Remove existing indicator if any
        const existingIndicator = notificationsBtn.querySelector('.notification-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        // Add new indicator if there are notifications
        if (severity !== 'none') {
            const indicator = document.createElement('div');
            indicator.className = `notification-indicator ${severity}`;
            notificationsBtn.appendChild(indicator);
        }

        // Reset any existing icon styles
        icon.style = '';
    }

    function addNotification(notification) {
        const notifications = getNotifications();
        notifications.unshift(notification);
        saveNotifications(notifications);
        renderNotifications();
        updateNotificationIcon();
    }

    notificationsList.addEventListener('click', (e) => {
        const dismissBtn = e.target.closest('.dismiss');
        if (dismissBtn) {
            const id = dismissBtn.closest('.notification').dataset.id;
            const notifications = getNotifications().filter(n => n.id !== id);
            saveNotifications(notifications);
            renderNotifications();
            updateNotificationIcon();
        } else if (e.target.classList.contains('clear-all')) {
            saveNotifications([]);
            renderNotifications();
            updateNotificationIcon();
        }
    });

    notificationsBtn.addEventListener('click', () => {
        notificationsList.classList.toggle('hidden');
    });

    // Initialize SSE connection
    const eventSource = new EventSource('/notifications/stream');
    eventSource.addEventListener('notification', (e) => {
        const notification = JSON.parse(e.data);
        addNotification(notification);
    });

    // Initial render
    renderNotifications();

    // Initial icon update
    updateNotificationIcon();
});
