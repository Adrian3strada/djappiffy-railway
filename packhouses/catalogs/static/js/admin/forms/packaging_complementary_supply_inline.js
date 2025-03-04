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

  document.addEventListener('formset:added', function (event) {
    if (event.detail.formsetName === 'packagingcomplementarysupply_set') {
      const newForm = event.target;
      const kindField = $(newForm).find('select[name$="kind"]');
      const supplyField = $(newForm).find('select[name$="-supply"]');
      const quantityField = $(newForm).find('input[name$="-quantity"]');

      updateFieldOptions(supplyField, [])

      kindField.on('change', function () {
        const supplyKindId = kindField.val();
        if (supplyKindId) {
          fetchOptions(`/rest/v1/catalogs/supply/?kind=${supplyKindId}&is_enabled=1`)
            .then(data => {
              updateFieldOptions(supplyField, data);
              quantityField.val(null);
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


  setTimeout(() => {
    const existingForms = document.querySelectorAll('tr[id^="packagingcomplementarysupply_set-"].form-row.has_original.dynamic-packagingcomplementarysupply_set');
    console.log("existingForms", existingForms)

    existingForms.forEach((form, index) => {
      console.log("index, form", index, form)
      const kindField = $(form).find(`select[name="packagingcomplementarysupply_set-${index}-kind"]`);
      const supplyField = $(form).find(`select[name="packagingcomplementarysupply_set-${index}-supply"]`);
      const quantityField = $(form).find(`input[name="packagingcomplementarysupply_set-${index}-quantity"]`);
      const selectedSupply = supplyField.val();

      if (kindField.val()) {
        fetchOptions(`/rest/v1/catalogs/supply/?kind=${kindField.val()}&is_enabled=1`)
          .then(data => {
            updateFieldOptions(supplyField, data);
            supplyField.val(selectedSupply);
          })
          .catch(error => {
            console.error('Error al obtener los supplies:', error);
          });
      } else {
        updateFieldOptions(supplyField, []);
      }

      kindField.on('change', function () {
        const supplyKindId = kindField.val();
        if (supplyKindId) {
          fetchOptions(`/rest/v1/catalogs/supply/?kind=${supplyKindId}&is_enabled=1`)
            .then(data => {
              updateFieldOptions(supplyField, data);
              quantityField.val(null);
            })
            .catch(error => {
              console.error('Error al obtener los supplies:', error);
            });
        } else {
          updateFieldOptions(supplyField, []);
        }
      });
    });
  }, 1000);

});
