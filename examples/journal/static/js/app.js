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

    function getEffectiveTheme() {
        return prefersDark.matches ? 'dark' : 'light';
    }

    function getNextTheme(currentTheme) {
        const effectiveTheme = getEffectiveTheme();
        const darkCycle = ['auto', 'light', 'dark'];
        const lightCycle = ['auto', 'dark', 'light'];
        const cycle = effectiveTheme === 'dark' ? darkCycle : lightCycle;

        return cycle[(cycle.indexOf(currentTheme) + 1) % cycle.length];
    }

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

    // Initialize theme
    const storedTheme = localStorage.getItem('theme') || 'auto';
    setTheme(storedTheme);

    // Theme toggle click handler
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const nextTheme = getNextTheme(currentTheme);
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

    function getNotificationsByType(notifications) {
        return notifications.reduce((acc, n) => {
            acc[n.severity] = (acc[n.severity] || 0) + 1;
            return acc;
        }, {});
    }

    function getClearButtonState(notifications) {
        const counts = getNotificationsByType(notifications);

        if (counts.info > 0 || counts.success > 0) {
            return {
                text: 'Clear',
                filter: n => n.severity === 'error' || n.severity === 'warning'
            };
        }

        if (counts.warning > 0) {
            return {
                text: 'Clear warnings',
                filter: n => n.severity === 'error'
            };
        }

        if (counts.error > 0) {
            return {
                text: 'Clear all',
                filter: () => false
            };
        }

        return null;
    }

    function renderNotifications() {
        const notifications = getNotifications();
        const clearState = getClearButtonState(notifications);

        // Clear the list first
        notificationsList.innerHTML = '';

        // Create notifications content
        const content = document.createElement('div');
        content.className = 'notifications-content';
        content.innerHTML = notifications.length
            ? notifications.map(n => `
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
            `).join('')
            : `
                <div class="empty-notifications">
                    ${getIconHtml('notifications')}
                    <p>No notifications</p>
                </div>
            `;

        // Add content first
        notificationsList.appendChild(content);

        // Then add clear button container
        const clearContainer = document.createElement('div');
        clearContainer.className = 'clear-button-container';
        clearContainer.innerHTML = clearState
            ? `<button class="clear-all">${clearState.text}</button>`
            : '';
        notificationsList.appendChild(clearContainer);
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
            const notifications = getNotifications();
            const clearState = getClearButtonState(notifications);
            if (clearState) {
                saveNotifications(notifications.filter(clearState.filter));
                renderNotifications();
                updateNotificationIcon();
            }
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
