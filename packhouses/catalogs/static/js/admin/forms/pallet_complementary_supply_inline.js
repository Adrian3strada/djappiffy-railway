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
    if (event.detail.formsetName === 'palletcomplementarysupply_set') {
      const newForm = event.target;
      const kindField = $(newForm).find('select[name$="-kind"]');
      const supplyField = $(newForm).find('select[name$="-supply"]');
      const quantityField = $(newForm).find('input[name$="-quantity"]');

      quantityField.attr('min', 1);
      updateFieldOptions(supplyField, [])

      kindField.on('change', function () {
        if (kindField.val()) {
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

  setTimeout(() => {
    const existingForms = document.querySelectorAll('tr[id^="palletcomplementarysupply_set-"].form-row.has_original.dynamic-productpresentationcomplementarysupply_set');
    existingForms.forEach((form, index) => {
      const kindField = $(form).find(`select[name="palletcomplementarysupply_set-${index}-kind"]`);
      const supplyField = $(form).find(`select[name="palletcomplementarysupply_set-${index}-supply"]`);
      const quantityField = $(form).find(`input[name="palletcomplementarysupply_set-${index}-quantity"]`);

      quantityField.attr('min', 1);
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
