/* app/static/js/theme.js */
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('theme-toggle');
  const root = document.documentElement;

  const setTheme = (theme) => {
    root.setAttribute('data-theme', theme);
    toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
  };

  const storedTheme = localStorage.getItem('theme');
  if (storedTheme) {
    setTheme(storedTheme);
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    setTheme('dark');
  } else {
    setTheme('light');
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const current = root.getAttribute('data-theme');
      const newTheme = current === 'light' ? 'dark' : 'light';
      setTheme(newTheme);
      localStorage.setItem('theme', newTheme);
    });
  }
});
