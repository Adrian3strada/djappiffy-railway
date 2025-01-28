document.addEventListener('DOMContentLoaded', () => {
  // Función para actualizar las opciones del campo harvesting_crew
  function updateFieldOptions(field, options, selectedValue) {
    field.empty(); // Limpiar las opciones existentes
    if (!field.prop('multiple')) {
      field.append(new Option('---------', '', true, false)); // Añadir opción por defecto
    }
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, option.id === selectedValue)); // Añadir cada opción
    });
    field.val(selectedValue); // Establecer el valor seleccionado
  }

  // Función para realizar una solicitud AJAX y obtener las opciones de harvesting_crew
  function fetchOptions(url) {
    return $.ajax({
      url: url, // La URL para obtener las opciones
      method: 'GET',
      dataType: 'json'
    }).fail(error => console.error('Error al obtener opciones:', error));
  }

  // Función para manejar el cambio de proveedor y actualizar el campo harvesting_crew
  function handleProviderChange(providerField, harvestingCrewField, selectedHarvestingCrew = null) {
    const providerId = providerField.val(); // Obtener el id del proveedor seleccionado

    // Si se ha seleccionado un proveedor, realizar la solicitud AJAX
    if (providerId) {
      fetchOptions(`/rest/v1/catalogs/harvesting_crew/?provider=${providerId}`)
        .then(harvestingCrews => {
          updateFieldOptions(harvestingCrewField, harvestingCrews, selectedHarvestingCrew); // Actualizar opciones
        })
        .catch(error => console.error('Error al obtener los equipos de cosecha:', error));
    } else {
      // Si no se ha seleccionado un proveedor, limpiar las opciones del campo harvesting_crew
      updateFieldOptions(harvestingCrewField, [], null);
    }
  }

  // Manejar la adición de nuevos formularios en el formset
  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'scheduleharvestharvestingcrew_set') {
      const newForm = event.target; // Obtener el formulario agregado
      const providerField = $(newForm).find('select[name$="-provider"]'); // Encontrar el campo proveedor
      const harvestingCrewField = $(newForm).find('select[name$="-harvesting_crew"]'); // Encontrar el campo harvesting_crew

      // Manejar el cambio de proveedor en el formulario agregado
      providerField.on('change', function() {
        handleProviderChange(providerField, harvestingCrewField);
      });

      // Actualizar las opciones del campo harvesting_crew cuando se agrega un nuevo formulario
      handleProviderChange(providerField, harvestingCrewField);
    }
  });

  // Manejar formularios existentes
    $('div[id^="scheduleharvestharvestingcrew_set-"]').each((index, form) => {
      const providerField = $(form).find(`select[name$="${index-1}-provider"]`); // Encontrar el campo proveedor
      const harvestingCrewField = $(form).find(`select[name$="${index-1}-harvesting_crew"]`); // Encontrar el campo harvesting_crew
      const deleteField = $(form).find(`input[name$="${index-1}-DELETE"]`); // Encontrar el campo DELETE
      const deleteLabel = $(form).find(`label[for$="${index-1}-DELETE"]`); // Encontrar el campo DELETE

      const selectedHarvestingCrew = harvestingCrewField.val(); // Obtener el valor actualmente seleccionado en harvesting_crew

      // Si ya se ha seleccionado un proveedor, actualizar las opciones del campo harvesting_crew
      if (providerField.val()) {
        handleProviderChange(providerField, harvestingCrewField, selectedHarvestingCrew);
      }

      // Manejar el cambio de proveedor en formularios existentes
      providerField.on('change', function() {
        handleProviderChange(providerField, harvestingCrewField, harvestingCrewField.val());
      });

      var status = $('.field-status .readonly').first().text().trim(); // Obtiene el primer "readonly" dentro de "field-status"
      if(status === 'Closed' || status === 'Canceled'){
        setTimeout(function(){
          providerField.next('.select2-container').addClass('disabled-field');
          harvestingCrewField.next('.select2-container').addClass('disabled-field');
          deleteField.hide();
          deleteLabel.hide();
          $('.djn-add-handler').hide();
        }, 300);
      }

    });


});
