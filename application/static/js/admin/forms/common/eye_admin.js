document.addEventListener("DOMContentLoaded", function () {
    const eyeLinks = document.querySelectorAll('td.original a[title="Ver en el sitio"]');
    eyeLinks.forEach(link => {
        link.style.display = 'none';
    });
});