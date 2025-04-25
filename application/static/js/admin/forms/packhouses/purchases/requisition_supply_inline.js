document.addEventListener('DOMContentLoaded', () => {
  // Función para actualizar las opciones del campo unit_category
  function updateFieldOptions(field, options, selectedValue) {
    field.innerHTML = ''; // Limpiar las opciones existentes
    const defaultOption = new Option('---------', '', true, false);
    field.appendChild(defaultOption);

    options.forEach(option => {
      const optionElement = new Option(option.name, option.id, false, option.id === selectedValue);
      field.appendChild(optionElement);
    });

    field.value = selectedValue; // Establecer el valor seleccionado
  }

  // Función para obtener los datos de una URL y manejar errores
  function fetchJson(url) {
    return fetch(url)
      .then(response => {
        if (!response.ok) throw new Error(`Error al llamar ${url}`);
        return response.json();
      });
  }

  // Función para obtener los unit categories desde la API
  function fetchUnitCategoriesByIds(ids) {
    const promises = ids.map(id => fetchJson(`/rest/v1/base/supply-measure-unit-category/${id}/`));
    return Promise.all(promises);
  }

  // Función para manejar el cambio de supply y actualizar el campo unit_category
  function handleSupplyChange(supplyField, unitCategoryField, selectedUnitCategory = null) {
    const supplyId = supplyField.value;

    if (supplyId) {
      fetchJson(`/rest/v1/catalogs/supply/${supplyId}/`)
        .then(supplyData => fetchJson(`/rest/v1/base/supply-kind/${supplyData.kind}/`))
        .then(supplyKindData => {
          const requestedIds = supplyKindData.requested_unit_category || [];

          if (requestedIds.length === 0) {
            updateFieldOptions(unitCategoryField, [], null);
            return;
          }

          fetchUnitCategoriesByIds(requestedIds)
            .then(unitCategories => {
              updateFieldOptions(unitCategoryField, unitCategories, selectedUnitCategory);
            })
            .catch(error => console.error('Error al obtener unit categories:', error));
        })
        .catch(error => console.error('Error al obtener supply o kind:', error));
    } else {
      updateFieldOptions(unitCategoryField, [], null);
    }
  }

  // Manejo de formularios agregados dinámicamente
  document.addEventListener('formset:added', (event) => {
  if (event.detail.formsetName === 'requisitionsupply_set') {
    // Busca el último formulario inline agregado
    const forms = document.querySelectorAll('.dynamic-requisitionsupply_set');
    const newForm = forms[forms.length - 1]; // último agregado

    if (!newForm) {
      console.warn('No se pudo encontrar el nuevo formulario inline.');
      return;
    }

    const supplyField = newForm.querySelector('select[name$="-supply"]');
    const unitCategoryField = newForm.querySelector('select[name$="-unit_category"]');

    if (supplyField && unitCategoryField) {

      $(supplyField).on('change', () => {
        handleSupplyChange(supplyField, unitCategoryField, null);
      });

      // Disparo inicial
      handleSupplyChange(supplyField, unitCategoryField, null);
    }
  }
});

  // Manejo de formularios existentes en el DOM
  document.querySelectorAll('div[id^="requisitionsupply_set-"]').forEach((form) => {
  const idMatch = form.id.match(/^requisitionsupply_set-(\d+)$/);
  if (!idMatch) return;

  const index = idMatch[1];

  const supplyField = form.querySelector(`select[name$="${index}-supply"]`);
  const unitCategoryField = form.querySelector(`select[name$="${index}-unit_category"]`);
  const selectedUnitCategory = unitCategoryField.value;

  if (supplyField.value) {
    handleSupplyChange(supplyField, unitCategoryField, selectedUnitCategory);
  }

  $(supplyField).on('change', () => {
    handleSupplyChange(supplyField, unitCategoryField, unitCategoryField.value);
  });
});

});
