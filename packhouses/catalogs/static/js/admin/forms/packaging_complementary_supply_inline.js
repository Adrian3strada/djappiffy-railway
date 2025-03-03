// Asegúrate de que el script se ejecute una vez que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function () {

  function updateFieldOptions(field, options) {
    field.empty()
    if (!field.prop('multiple')) {
      field.append(new Option('---------', '', true, true));
    }
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, false));
    });
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: 'GET',
      dataType: 'json'
    }).fail(error => console.error('Fetch error:', error));
  }


  // Escuchar el evento cuando se agregue un nuevo formulario al formset
  document.addEventListener('formset:added', function (event) {
    if (event.detail.formsetName === 'packagingsupply_set') {

      const newForm = event.target;

      const supplyKindField = $(newForm).find('select[name$="supply_kind"]');
      const supplyField = $(newForm).find('select[name$="-supply"]');

      console.log(supplyKindField);
      console.log(supplyField);

      // Agregar un event listener para cuando cambie el SupplyKind
      supplyKindField.on('change', function () {
        const supplyKindId = $(this).val(); // Obtenemos el ID del SupplyKind seleccionado

        if (supplyKindId) {
          fetchOptions(`/rest/v1/catalogs/supply/?kind=${supplyKindId}&is_enabled=1`)
            .then(data => {
              updateFieldOptions(supplyField, data);
            })
            .catch(error => {
              console.error('Error al obtener los supplies:', error);
            });
        } else {
          updateFieldOptions(supplyField, []);
        }
      });
    }
  });

  // Repetir la misma lógica para los formularios ya existentes en la página
  initializeExistingFormsListeners()

  // Función para inicializar los listeners de SupplyKind en los formularios existentes

  function initializeExistingFormsListeners() {
    const existingForms = document.querySelectorAll('.form-row.has_original');

    existingForms.forEach((form, index) => {

      //console.log(index);
      const supplyKindField = $(form).find(`select[name="packagingsupply_set-${index}-supply_kind"]`);
      const supplyField = $(form).find(`select[name="packagingsupply_set-${index}-supply"]`);

      const selectedSupplyKind = supplyKindField.val();
      const selectedSupply = supplyField.val();

      //console.log(index, 'supply_kind', supplyKindField.val());
      //console.log(index, 'supply', supplyField.val());

      const supplyKindId = supplyKindField.val();
      const supplyFieldId = supplyField.val();

      if (supplyKindId) {
        fetchOptions(`/rest/v1/catalogs/supply/?kind=${supplyKindId}&is_enabled=1`)
          .then(data => {
            updateFieldOptions(supplyField, data);
            supplyField.val(selectedSupply);
          });
      } else {
        updateFieldOptions(supplyField, []);
        supplyField.val(selectedSupply);
      }

      supplyKindField.on('change', function () {
        const supplyKindId = $(this).val();
        if (supplyKindId) {
          fetchOptions(`/rest/v1/catalogs/supply/?kind=${supplyKindId}`)
            .then(data => {
              updateFieldOptions(supplyField, data);
            });
        } else {
          updateFieldOptions(supplyField, []);
        }
      });

    });
    console.log(existingForms);
  }

});
