document.addEventListener('DOMContentLoaded', () => {
  // Agregar listener para cuando se añadan formularios en el inline de `ProductVarietySize`
  document.addEventListener('formset:added', (event) => {
    // Verifica que el evento sea para el inline `productvarietysize_set`
    if (event.detail.formsetName === 'productvarietysize_set') {

      const newForm = event.target;

      console.log("Nuevo formulario añadido en ProductVarietySize:", newForm);
      console.log("Nuevo formulario añadido en ProductVarietySize:", event.target.id);

      // Seleccionar el campo `market`
      const marketField = newForm.querySelector('select[name$="-market"]');
      console.log("marketField (original):", marketField);

      if (marketField) {

        $(marketField).on('select2:select', function (e) {
          console.log('Opción seleccionada:', e.params.data);
          // Aquí puedes ejecutar lógica adicional

          const marketId = e.params.data.id;
          const marketStandardProductSizeField = newForm.querySelector('select[name$="-market_standard_product_size"]');
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
        });
      }
    }
  });

  // Agregar listener para cuando se eliminen formularios en el inline de `ProductVarietySize`
  document.addEventListener('formset:removed', (event) => {
    // Verifica que el evento sea para el inline `productvarietysize_set`
    if (event.detail.formsetName === 'productvarietysize_set') {
      const removedForm = event.detail.form;
      console.log("Formulario eliminado en ProductVarietySize:", removedForm);
      // Realiza aquí las acciones necesarias al eliminar un formulario, si es necesario
    }
  });
});
