/* static/js/todo.js – show/hide the datetime picker */

(() => {
    const checkbox = document.getElementById('due-checkbox');
    const container = document.getElementById('due-date-container');
    const dateInput = document.getElementById('due-date');

    if (!checkbox || !container) return;

    const toggle = () => {
        if (checkbox.checked) {
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
            dateInput.value = '';          // clear value when unchecked
        }
    };

    checkbox.addEventListener('change', toggle);
    toggle(); // initial state
})();

