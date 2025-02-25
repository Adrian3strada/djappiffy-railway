document.addEventListener('DOMContentLoaded', function () {
    // Selecciona todos los enlaces con la clase "inline-deletelink"
    var deleteButtons = document.querySelectorAll('.inline-deletelink');
    // Oculta cada uno de ellos
    deleteButtons.forEach(function(button) {
      button.style.display = 'none';
    });
  });
  