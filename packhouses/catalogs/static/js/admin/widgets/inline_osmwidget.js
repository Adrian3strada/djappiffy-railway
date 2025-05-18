(function () {
  function forceMapUpdate() {
    if (!window.OpenLayers || !OpenLayers.Map) return;

    for (const key in window) {
      const obj = window[key];
      if (obj instanceof OpenLayers.Map) {
        obj.updateSize();
      }
    }
  }

  // Espera a que todo se cargue
  window.addEventListener('load', () => {
    setTimeout(forceMapUpdate, 500); // importante: no muy pronto
  });

  // También al hacer click en "Agregar otro" (cuando max_num > 1)
  document.addEventListener('click', function (e) {
    if (e.target && e.target.closest('.add-row')) {
      setTimeout(forceMapUpdate, 1000); // dar tiempo a que aparezca el inline
    }
  });

  // Si el mapa está en un tab o acordeón oculto
  document.addEventListener('click', function (e) {
    if (e.target && e.target.matches('.inline-group h2, .inline-related h2')) {
      setTimeout(forceMapUpdate, 500);
    }
  });
})();
