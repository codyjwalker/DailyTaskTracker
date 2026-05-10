/* app/static/js/todo.js – show/hide the datetime picker for any form */
(() => {
  // Helper that toggles a container when the associated checkbox is changed
  const toggleContainer = (checkbox, container) => {
    if (!checkbox || !container) return;
    const toggle = () => {
      if (checkbox.checked) {
        container.style.display = 'block';
      } else {
        container.style.display = 'none';
        // Clear any entered date when unchecked
        const dateInput = container.querySelector('input[type="datetime-local"]');
        if (dateInput) dateInput.value = '';
      }
    };
    checkbox.addEventListener('change', toggle);
    toggle(); // initial state
  };

  // Find every checkbox that controls a due‑date picker
  const dueCheckboxes = document.querySelectorAll('.due-checkbox');
  dueCheckboxes.forEach(checkbox => {
    const targetId = checkbox.dataset.target;
    const container = document.getElementById(targetId);
    toggleContainer(checkbox, container);
  });
})();
