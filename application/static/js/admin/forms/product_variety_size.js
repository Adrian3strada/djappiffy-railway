document.addEventListener('DOMContentLoaded', () => {
  // Función para actualizar el campo de `market_standard_product_size`
  function updateMarketStandardProductSize(marketId, form) {
    const marketStandardProductSizeField = form.querySelector('select[name$="-market_standard_product_size"]');
    console.log("marketStandardProductSizeField (original):", marketStandardProductSizeField);

    if (marketId !== '') {
      fetch(`/catalogs/market_standard_product_size/${marketId}/`)
        .then(response => response.json())
        .then(data => {
          marketStandardProductSizeField.innerHTML = '';
          const defaultOption = document.createElement('option');
          defaultOption.value = '';
          defaultOption.textContent = '---------';
          marketStandardProductSizeField.appendChild(defaultOption);
          data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name;
            marketStandardProductSizeField.appendChild(option);
          });
        })
        .catch(error => {
          console.error('Error fetching market standard product sizes:', error);
        });
    }
  }

  // Agregar listener para cuando se añadan formularios en el inline de `ProductVarietySize`
  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'productvarietysize_set') {
      const newForm = event.target;

      console.log("Nuevo formulario añadido en ProductVarietySize:", newForm);
      console.log("Nuevo formulario añadido en ProductVarietySize:", event.target.id);

      const marketField = newForm.querySelector('select[name$="-market"]');
      console.log("marketField (original):", marketField);

      if (marketField) {
        // Listener para cuando se selecciona una opción en el campo `market`
        $(marketField).on('select2:select', function (e) {
          console.log('Opción seleccionada:', e.params.data);
          const marketId = e.params.data.id;
          updateMarketStandardProductSize(marketId, newForm);
        });

        // Verificar si el campo ya tiene un valor y ejecutar la lógica correspondiente
        const selectedMarketId = marketField.value;
        if (selectedMarketId) {
          updateMarketStandardProductSize(selectedMarketId, newForm);
        }
      }
    }
  });

  // Verificar formularios existentes al cargar
  const existingForms = document.querySelectorAll('div[id^="productvarietysize_set-"]');
  existingForms.forEach(form => {
    const marketField = form.querySelector('select[name$="-market"]');
    if (marketField) {
      const selectedMarketId = marketField.value;
      if (selectedMarketId) {
        updateMarketStandardProductSize(selectedMarketId, form);
      }

      // Agregar listener para el nuevo formulario
      $(marketField).on('select2:select', function (e) {
        console.log('Opción seleccionada:', e.params.data);
        const marketId = e.params.data.id;
        updateMarketStandardProductSize(marketId, form);
      });
    }
  });

  // Agregar listener para cuando se eliminen formularios en el inline de `ProductVarietySize`
  document.addEventListener('formset:removed', (event) => {
    if (event.detail.formsetName === 'productvarietysize_set') {
      const removedForm = event.detail.form;
      console.log("Formulario eliminado en ProductVarietySize:", removedForm);
    }
  });
});
