document.addEventListener('DOMContentLoaded', () => {
  // Función para actualizar el campo de `market_standard_product_size`
  function updateMarketStandardProductSize(marketId, form) {
    const marketStandardSizeField = form.querySelector('select[name$="-market_standard_size"]');
    console.log("marketStandardProductSizeField (original):", marketStandardSizeField);

    if (marketId !== '') {
      fetch(`/rest/v1/catalogs/market_standard_product_size/?market=${marketId}&is_enabled=1`)
        .then(response => response.json())
        .then(data => {
          marketStandardSizeField.innerHTML = '';
          const defaultOption = document.createElement('option');
          defaultOption.value = '';
          defaultOption.textContent = '---------';
          marketStandardSizeField.appendChild(defaultOption);
          data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name;
            marketStandardSizeField.appendChild(option);
          });

          // Preseleccionar el tamaño estándar del mercado si ya está establecido
          const selectedValue = marketStandardSizeField.dataset.selectedValue;
          if (selectedValue) {
            $(marketStandardSizeField).val(selectedValue).trigger('change');
          }

          // Adjuntar el evento después de actualizar el campo
          $(marketStandardSizeField).on('select2:select', function (e) {
            console.log('Opción seleccionada:', e.params.data);
            const selectedText = e.params.data.text;
            const nameField = form.querySelector('input[name$="-name"]');
            const aliasField = form.querySelector('input[name$="-alias"]');
            if (nameField && nameField.value !== '---------') {
              nameField.value = selectedText;
            }
            if (aliasField) {
              aliasField.value = transformTextForAlias(selectedText);
            }
          });
        })
        .catch(error => {
          console.error('Error fetching market standard product sizes:', error);
        });
    }
  }

  // Función para transformar el texto para el campo alias
  function transformTextForAlias(text) {
    const accentsMap = {
      'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
      'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'
    };
    return text
      .replace(/[áéíóúÁÉÍÓÚ]/g, match => accentsMap[match])
      .replace(/[^a-zA-Z0-9]/g, '');
  }

  // Agregar listener para cuando se añadan formularios en el inline de `ProductVarietySize`
  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'productvarietysize_set') {
      const newForm = event.target;
      const marketField = newForm.querySelector('select[name$="-market"]');

      if (marketField) {
        $(marketField).on('select2:select', (e) => {
          console.log('Opción seleccionada:', e.params.data);
          const marketId = e.params.data.id;
          updateMarketStandardProductSize(marketId, newForm);
        });
      }

      // Añadir listener al campo `name` para limpiar la selección de `market_standard_size`
      const nameField = newForm.querySelector('input[name$="-name"]');
      if (nameField) {
        nameField.addEventListener('input', () => {
          const marketStandardSizeField = newForm.querySelector('select[name$="-market_standard_size"]');
          $(marketStandardSizeField).val('').trigger('change'); // Limpiar solo la selección del campo market_standard_size
        });
      }
    }
  });

  // Verificar formularios existentes al cargar
  const existingForms = document.querySelectorAll('div[id^="productvarietysize_set-"]');
  existingForms.forEach(form => {
    const marketField = form.querySelector('select[name$="-market"]');
    const marketStandardSizeField = form.querySelector('select[name$="-market_standard_size"]');

    // Almacenar el valor seleccionado para usarlo más tarde
    marketStandardSizeField.dataset.selectedValue = marketStandardSizeField.value;

    if (marketField) {
      const selectedMarketId = marketField.value;
      if (selectedMarketId) {
        updateMarketStandardProductSize(selectedMarketId, form);
      }

      $(marketField).on('select2:select', function (e) {
        console.log('Opción seleccionada:', e.params.data);
        const marketId = e.params.data.id;
        updateMarketStandardProductSize(marketId, form);
      });

      // Añadir listener al campo `name` para limpiar la selección de `market_standard_size`
      const nameField = form.querySelector('input[name$="-name"]');
      if (nameField) {
        nameField.addEventListener('input', () => {
          $(marketStandardSizeField).val('').trigger('change'); // Limpiar solo la selección del campo market_standard_size
        });
      }
    }
  });

  // Agregar listener para cuando se eliminen formularios en el inline de `ProductVarietySize`
  document.addEventListener('formset:removed', (event) => {
    if (event.detail.formsetName === 'productvarietysize_set') {
      const removedForm = event.target;
      console.log("Formulario eliminado en ProductVarietySize:", removedForm);
    }
  });
});
