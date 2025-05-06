document.addEventListener('DOMContentLoaded', () => {
  let providers = []; // Inicializar la variable global providers

  function disableField(field) {
    field.prop("readonly", true);
    field.css({
      "pointer-events": "none",
      "background-color": "#e9ecef",
      "border": "none",
      "color": "#555"
    });
  }
  
  // 2) Al cargar la página, la aplicas a weight_expected
  $(function() {
    disableField($('#id_weight_expected'));
  });

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

  // Función para evitar peticiones duplicadas
  function debounce(fn, ms) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), ms);
    };
  }
  
  const capacityCache = {};
  // Función para realizar una solicitud AJAX y obtener la capacidad de los contenedores
  function fetchContainerCapacity(containerId) {
    if (capacityCache.hasOwnProperty(containerId)) {
      return $.Deferred().resolve(capacityCache[containerId]).promise();
    }
    return $.ajax({
      url: `/rest/v1/catalogs/supply/`,
      method: 'GET',
      dataType: 'json',
      data: {
        id: containerId,    
        is_enabled: true
      }
    })
    .then(data => {
      capacityCache[containerId] = data;
      return data;
    })
    .fail(error => {
      console.error('Error al obtener la capacidad de los contenedores:', error);
      throw error;
    });
  }

  // Función para calcular el total del peso esperado por vehiculo
  function calcVehicleTotal(vehicleEl) {
    var sum = 0;
    var promises = [];
  
    $(vehicleEl)
      .find('tbody[data-inline-model$="scheduleharvestcontainervehicle"]:not(.djn-empty-form)')
      .each(function() {
        var $row = $(this);
        if ($row.find('input[name$="-DELETE"]').prop('checked')) return;
  
        var sel   = $row.find('select[name$="-harvest_container"]');
        var qtyEl = $row.find('input[name$="-quantity"]');
        if (!sel.length || !qtyEl.length || !sel.val()) return;
  
        var containerId = sel.val();
        var rawQty = qtyEl.val() || '';
        var cleanQty = rawQty.replace(/\D/g, '');
        if (!/^\d+$/.test(cleanQty)) {
          return promises.push($.Deferred()
            .reject(`Invalid quantity "${rawQty}" in vehicle ${vehicleEl.id}`)
            .promise());
        }
        var qty = parseInt(cleanQty, 10);
        var p = fetchContainerCapacity(containerId).then(function(data) {
          var arr = $.isArray(data) ? data : (data.results || []);
          var cont = arr.find(item => String(item.id) === containerId);
          var w = cont && cont.capacity != null ? cont.capacity : 1;
          sum += w * qty;
        }).fail(function(err) {
          console.error('Error fetching capacity for', containerId, err);
          sum += 1 * qty; 
        });
        promises.push(p);
      });
  
    return $.when.apply($, promises).then(function() {
      return sum;
    });
  }
  
  // Función para calcular el total de peso esperado de todos los vehiculos
  function recalcGlobalTotal() {
    const groupEl = document.getElementById('scheduleharvestvehicle_set-group');
    if (!groupEl) return;
    calcVehicleTotal(groupEl).then(total => {
      $('#id_weight_expected').val(total.toFixed(2));
    });
  }
  
  // Función para inicializar los vehiculos para recalcular el peso total del vehículo ante cualquier cambio en sus contenedores.
  function initVehicle(vehicleEl) {
    $(document).on('input', 'input[name$="-quantity"]', function() {
      this.value = this.value.replace(/\D/g, '');
    });
    if (vehicleEl._inited) return;
    vehicleEl._inited = true;
    const $veh = $(vehicleEl);
  
    const recalcAndLog = debounce(function() {
      calcVehicleTotal(vehicleEl)
        .always(recalcGlobalTotal);
    }, 200);
  
    // recálculo inicial
    recalcAndLog();
  
    $veh.on('change input', 
      'select[name$="-harvest_container"], input[name$="-quantity"]', 
      recalcAndLog
    );
  
    $veh.on('click', '.djn-add-handler, .djn-remove-handler', () => setTimeout(recalcAndLog, 0));
    $veh.on('formset:added formset:removed', e => {
      if (e.detail.formsetName.endsWith('scheduleharvestcontainervehicle_set')) {
        recalcAndLog();
      }
    });
  
    const observer = new MutationObserver(muts => {
      muts.forEach(mut => {
        if (
          (mut.type === 'attributes' && mut.target.matches('input[name$="-DELETE"]')) ||
          (mut.type === 'childList' && Array.from(mut.removedNodes).some(
            node => node.nodeType === 1 && $(node).find('a.inline-deletelink').length
          ))
        ) {
          setTimeout(recalcAndLog, 0);
        }
      });
    });
    observer.observe(vehicleEl, { attributes: true, childList: true, subtree: true });
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
    if (event.detail.formsetName === 'scheduleharvestvehicle_set') {
      const newForm = event.target; // Obtener el formulario agregado
      const providerField = $(newForm).find('select[name$="-provider"]'); // Encontrar el campo proveedor
      const vehicleField = $(newForm).find('select[name$="-vehicle"]'); // Encontrar el campo vehicle

      initVehicle(event.target);

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
      $('div[id^="scheduleharvestvehicle_set-"]:not([id*="-empty"])').each((index, form) => {
        initVehicle(form);
        const providerField = $(form).find(`select[name$="${index-1}-provider"]`); // Encontrar el campo proveedor
        const vehicleField = $(form).find(`select[name$="${index-1}-vehicle"]`); // Encontrar el campo vehicle
        const selectedVehicle = vehicleField.val(); // Obtener el valor actualmente seleccionado en vehicle
        const deleteField = $(form).find(`input[name$="${index-1}-DELETE"]`); // Encontrar el campo DELETE
        const deleteLabel = $(form).find(`label[for$="${index-1}-DELETE"]`); // Encontrar el campo DELETE
        const stampField = $(form).find(`input[name$="${index-1}-stamp_number"]`); // Encontrar el campo stamp

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

        var status = $('.field-status .readonly').first().text().trim(); // Obtiene el primer "readonly" dentro de "field-status"
        if(status === 'Closed' || status === 'Canceled'){
            setTimeout(function(){
                providerField.next('.select2-container').addClass('disabled-field');
                vehicleField.next('.select2-container').addClass('disabled-field');
                stampField.addClass('disabled-field');
                deleteField.hide();
                deleteLabel.hide();

                $(".select2-selection--single").addClass('disabled-field');
                $('.djn-add-handler').hide();
            }, 200);
        }

        // Deshabilitar campos en inlines anidados
        $(form).find('div[id^="scheduleharvestvehicle_set-"][id$="-scheduleharvestcontainervehicle_set-group"]').each((nestedIndex, nestedForm) => {
            const nestedQuantityFields = $(nestedForm).find('input[id^="id_scheduleharvestvehicle_set-"][id$="-quantity"]');
            const nestedDeleteFields = $(nestedForm).find('input[id^="id_scheduleharvestvehicle_set-"][id$="-DELETE"]');
            const nestedDeleteLabels = $(nestedForm).find('label[for^="id_scheduleharvestvehicle_set-"][for$="-DELETE"]');
            const nestedAddWidget = $(nestedForm).find('a[id^="add_id_scheduleharvestvehicle_set-"]');
            const nestedChangeWidget = $(nestedForm).find('a[id^="change_id_scheduleharvestvehicle_set-"]');
            const nestedViewWidget = $(nestedForm).find('a[id^="view_id_scheduleharvestvehicle_set-"]');

            const nestedAddHandlers = $(nestedForm).find('.djn-add-handler');

            if(status === 'Closed' || status === 'Canceled'){
                setTimeout(function(){
                    nestedQuantityFields.addClass('disabled-field');
                    nestedDeleteFields.hide();
                    nestedDeleteLabels.hide();
                    nestedAddHandlers.hide();
                    nestedAddWidget.hide();
                    nestedChangeWidget.hide();
                    nestedViewWidget.hide();
                }, 200);
            }
        });
    });
  });
});
