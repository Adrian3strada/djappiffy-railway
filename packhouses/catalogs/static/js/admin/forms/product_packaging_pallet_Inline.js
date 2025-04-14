document.addEventListener('DOMContentLoaded', function () {
  const marketField = $('#id_market');
  const productField = $('#id_product');

  let palletOptions = [];

  function updateFieldOptions(field, options, selected=null) {
    field.empty()
    if (!field.prop('multiple')) {
      field.append(new Option('---------', '', true, !selected));
    }
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, selected===option.id));
    });
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: 'GET',
      dataType: 'json'
    }).fail(error => console.error('Fetch error:', error));
  }

  function setPalletOptions() {
    if (marketField.val() && productField.val()) {
      fetchOptions(`/rest/v1/catalogs/pallet/?market=${marketField.val()}&product=${productField.val()}&is_enabled=1`)
        .then(data => {
          palletOptions = data;
        })
        .catch(error => {
          console.error('Error al obtener los supplies:', error);
        });
    } else {
      palletOptions = [];
    }
  }

  setPalletOptions();
  marketField.on('change', setPalletOptions);
  productField.on('change', setPalletOptions);

  document.addEventListener('formset:added', function (event) {
    if (event.detail.formsetName === 'productpackagingpallet_set') {
      const newForm = event.target;
      const palletField = $(newForm).find('select[name$="-pallet"]');
      const productPackagingQuantityField = $(newForm).find('input[name$="-product_packaging_quantity"]');

      productPackagingQuantityField.attr('min', 1);
      updateFieldOptions(palletField, palletOptions);
    }
  });

  setTimeout(() => {
    const existingForms = document.querySelectorAll('tr[id^="productpackagingpallet_set-"].form-row.has_original.dynamic-productpackagingpallet_set');
    existingForms.forEach((form, index) => {
      const palletField = $(form).find(`select[name="productpackagingpallet_set-${index}-pallet"]`);
      const productPackagingQuantityField = $(form).find(`input[name="productpackagingpallet_set-${index}-product_packaging_quantity"]`);
      productPackagingQuantityField.attr('min', 1);
      const selectedPallet = palletField.val();
      updateFieldOptions(palletField, palletOptions, selectedPallet);
      palletField.val(selectedPallet);
    });
  }, 600);

});
