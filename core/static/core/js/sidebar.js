(function () {
  function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    if (sidebar) sidebar.classList.toggle('active');
    if (mainContent) mainContent.classList.toggle('active');
  }

  document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.querySelector('.sidebar-toggle');
    if (toggle) {
      toggle.addEventListener('click', toggleSidebar);
    }
  });
})();
