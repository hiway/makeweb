document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const menuToggle = document.getElementById('menu-toggle');
    const searchInput = document.getElementById('search');
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('img');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

    // Function to update menu icons based on sidebar visibility
    function updateMenuIcons() {
        const isVisible = sidebar.classList.contains('visible');
        menuToggle.querySelector('svg[data-icon="menu"]').setAttribute('data-active', !isVisible);
        menuToggle.querySelector('svg[data-icon="menu_open"]').setAttribute('data-active', isVisible);
    }

    // Mobile menu toggle
    menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('visible');
        localStorage.setItem('sidebarVisible', sidebar.classList.contains('visible'));
        updateMenuIcons();
    });

    // Initialize sidebar state on wide screens
    function initSidebarState() {
        const isWideScreen = window.matchMedia('(min-width: 768px)').matches;
        if (isWideScreen) {
            const storedState = localStorage.getItem('sidebarVisible');
            // Show sidebar by default unless explicitly hidden before
            sidebar.classList.toggle('visible', storedState !== 'false');
        }
        updateMenuIcons();
    }

    // Initialize sidebar on load
    initSidebarState();

    // Re-initialize on window resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(initSidebarState, 100);
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

    function getIconHtml(name) {
        const existingSvg = document.querySelector(`svg[data-icon="${name}"]`);
        if (existingSvg) {
            const svgClone = existingSvg.cloneNode(true);
            return svgClone.outerHTML;
        }
        console.warn(`SVG icon ${name} not found`);
        return '';
    }

    function updateThemeIcon(theme) {
        const themeToggle = document.getElementById('theme-toggle');
        const icons = themeToggle.querySelectorAll('svg');
        icons.forEach(icon => {
            const iconName = icon.getAttribute('data-icon');
            const isActive = iconName === `${theme}_mode`;
            icon.setAttribute('data-active', isActive);
        });
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
                text: 'Clear informational',
                filter: n => n.severity === 'error' || n.severity === 'warning',
                clearAll: false
            };
        }

        if (counts.warning > 0) {
            return {
                text: 'Clear warnings',
                filter: n => n.severity === 'error',
                clearAll: false
            };
        }

        if (counts.error > 0) {
            return {
                text: 'Clear all',
                filter: () => false,
                clearAll: true
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
        const notificationsBtn = document.getElementById('notifications');

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
    }

    function addNotification(notification) {
        const notifications = getNotifications();
        const currentSeverity = notifications.length ? getHighestSeverity(notifications) : 'none';
        const notificationsBtn = document.getElementById('notifications');

        // Compare severity priorities directly
        const shouldAnimate = currentSeverity === 'none' ||
            severityPriority[notification.severity] > severityPriority[currentSeverity];

        notifications.unshift(notification);
        saveNotifications(notifications);
        renderNotifications();
        updateNotificationIcon();

        if (shouldAnimate) {
            notificationsBtn.classList.remove('animate-once');
            void notificationsBtn.offsetWidth; // Force reflow
            notificationsBtn.classList.add('animate-once');

            setTimeout(() => {
                notificationsBtn.classList.remove('animate-once');
            }, 500);
        }
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
                const remainingNotifications = notifications.filter(clearState.filter);
                saveNotifications(remainingNotifications);
                renderNotifications();
                updateNotificationIcon();

                // Only close drawer if all notifications are cleared
                if (clearState.clearAll) {
                    notificationsList.classList.add('hidden');
                    notificationsBtn.classList.remove('drawer-open');
                }
            }
        }
    });

    notificationsBtn.addEventListener('click', () => {
        // Toggle the drawer state instead of only opening it
        notificationsList.classList.toggle('hidden');
        notificationsBtn.classList.toggle('drawer-open');
        notificationsBtn.classList.remove('unread');
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

    const preferencesBtn = document.getElementById('preferences');
    const preferencesList = document.createElement('div');
    preferencesList.className = 'preferences-list hidden';
    preferencesList.innerHTML = `
        <div class="preferences-content">
            <div class="empty-preferences">
                ${getIconHtml('settings')}
                <p>No preferences configured</p>
            </div>
        </div>
    `;
    sidebar.appendChild(preferencesList);

    // Remove the premature event listener setup since the container doesn't exist yet
    // The event listener will be added when preferences are configured and the container is created

    preferencesBtn.addEventListener('click', () => {
        // Close notifications if open
        notificationsList.classList.add('hidden');
        notificationsBtn.classList.remove('drawer-open');

        // Toggle preferences
        preferencesList.classList.toggle('hidden');
        preferencesBtn.classList.toggle('drawer-open');
    });

    // Close drawers when clicking elsewhere
    document.addEventListener('click', (e) => {
        // For notifications, only close if clicking outside AND there are no notifications
        if (!e.target.closest('#notifications') && !e.target.closest('.notifications-list')) {
            const notifications = getNotifications();
            if (notifications.length === 0) {
                notificationsList.classList.add('hidden');
                notificationsBtn.classList.remove('drawer-open');
            }
        }
        if (!e.target.closest('#preferences') && !e.target.closest('.preferences-list')) {
            preferencesList.classList.add('hidden');
            preferencesBtn.classList.remove('drawer-open');
        }
    });
});
