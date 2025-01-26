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
});
