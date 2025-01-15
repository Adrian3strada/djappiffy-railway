document.addEventListener('DOMContentLoaded', () => {
  let providers = []; // Inicializar la variable global providers

  // Función para obtener proveedores
  function fetchProviders() {
    return $.ajax({
      url: '/rest/v1/catalogs/provider/?category=harvesting_provider&is_enabled=true',
      method: 'GET',
      dataType: 'json'
    }).done(function(data) {
      providers = data;  // Asignar la respuesta de la API a la variable providers
    }).fail(function(error) {
      console.error('Error al obtener proveedores:', error);
    });
  }

  // Función para actualizar las opciones del campo vehicle
  function updateFieldOptions(field, options, selectedValue) {
    field.empty(); // Limpiar las opciones existentes
    if (!field.prop('multiple')) {
      field.append(new Option('---------', '', true, false)); // Añadir opción por defecto
    }
    options.forEach(option => {
      field.append(new Option(option.license_plate+" / "+option.name, option.id, false, option.id === selectedValue)); // Añadir cada opción
    });
    field.val(selectedValue); // Establecer el valor seleccionado
  }

  // Función para realizar una solicitud AJAX y obtener los vehículos
  function fetchVehicles(vehicleIds) {
    return $.ajax({
      url: `/rest/v1/catalogs/vehicle/?ids=${vehicleIds.join(',')}&is_enabled=true`, // Endpoint con IDs de vehículos
      method: 'GET',
      dataType: 'json'
    }).fail(error => console.error('Error al obtener vehículos:', error));
  }

  // Función para manejar el cambio de proveedor y actualizar el campo vehicle
  function handleProviderChange(providerField, vehicleField, selectedVehicle = null) {
    const providerId = providerField.val(); // Obtener el id del proveedor seleccionado

    // Si se ha seleccionado un proveedor, realizar la solicitud AJAX
    if (providerId) {
      const provider = providers.find(p => p.id == providerId); // Obtener el proveedor del listado

      if (provider && provider.vehicle_provider.length > 0) {
        fetchVehicles(provider.vehicle_provider)
          .then(vehicles => {
            updateFieldOptions(vehicleField, vehicles, selectedVehicle); // Actualizar opciones
          })
          .catch(error => console.error('Error al obtener vehículos:', error));
      } else {
        updateFieldOptions(vehicleField, [], null); // Limpiar opciones si no hay vehículos
      }
    } else {
      updateFieldOptions(vehicleField, [], null); // Limpiar opciones si no se selecciona proveedor
    }
  }

  // Manejar la adición de nuevos formularios en el formset
  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'harvestcuttingvehicle_set') {
      const newForm = event.target; // Obtener el formulario agregado
      const providerField = $(newForm).find('select[name$="-provider"]'); // Encontrar el campo proveedor
      const vehicleField = $(newForm).find('select[name$="-vehicle"]'); // Encontrar el campo vehicle

      // Manejar el cambio de proveedor en el formulario agregado
      providerField.on('change', function() {
        handleProviderChange(providerField, vehicleField);
      });

      // Actualizar las opciones del campo vehicle cuando se agrega un nuevo formulario
      handleProviderChange(providerField, vehicleField);
    }
  });

  // Esperar a que los proveedores se obtengan antes de procesar los formularios
  fetchProviders().then(() => {
      // Manejar formularios existentes
      $('div[id^="harvestcuttingvehicle_set-"]').each((index, form) => {
        const providerField = $(form).find(`select[name$="${index-1}-provider"]`); // Encontrar el campo proveedor
        const vehicleField = $(form).find(`select[name$="${index-1}-vehicle"]`); // Encontrar el campo vehicle
        const selectedVehicle = vehicleField.val(); // Obtener el valor actualmente seleccionado en vehicle

        // Si ya se ha seleccionado un proveedor, actualizar las opciones del campo vehicle
        if (providerField.val()) {
          handleProviderChange(providerField, vehicleField, selectedVehicle);
        } else {
          updateFieldOptions(vehicleField, [], null); // Limpiar opciones si no hay proveedor seleccionado
        }

        // Manejar el cambio de proveedor en formularios existentes
        providerField.on('change', function() {
          handleProviderChange(providerField, vehicleField, vehicleField.val());
        });
      });
  });
});
