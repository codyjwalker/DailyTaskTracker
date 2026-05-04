/* static/js/theme.js – light/dark theme toggle */

(() => {
    const themeKey = 'theme';
    const body = document.body;
    const toggle = document.getElementById('theme-toggle');
    const icon  = document.getElementById('theme-label');

    // Apply the theme (sets data-theme, checkbox state, and icon)
    const applyTheme = theme => {
        body.setAttribute('data-theme', theme);
        if (toggle) toggle.checked = (theme === 'dark');
        if (icon)   icon.textContent = theme === 'dark' ? '🌙' : '☀️';
    };

    /* ── Initialise theme on page load ─────────────────────── */
    const stored = localStorage.getItem(themeKey);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    let theme = stored ?? (prefersDark ? 'dark' : 'light');
    applyTheme(theme);

    /* ── Listen for toggle changes ─────────────────────────── */
    if (toggle) {
        toggle.addEventListener('change', () => {
            const newTheme = toggle.checked ? 'dark' : 'light';
            localStorage.setItem(themeKey, newTheme);
            applyTheme(newTheme);
        });
    }
})();

