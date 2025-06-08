document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const marketsField = $('#id_markets');
  const presentationSupplyKindField = $('#id_presentation_supply_kind');
  const presentationSupplyField = $('#id_presentation_supply');
  const nameField = $('#id_name');

  let productProperties = null;

  function updateFieldOptions(field, options, selectedValue = null) {
    console.log("updateFieldOptions", field, options, selectedValue);
    field.empty().append(new Option('---------', '', !selectedValue, !selectedValue));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, selectedValue === option.id, parseInt(selectedValue) === option.id));
    });
    field.trigger('change').select2();
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: 'GET',
      dataType: 'json'
    }).fail(error => console.error('Fetch error:', error));
  }

  function updatePresentationSupply() {
    const presentationSupplyKindId = presentationSupplyKindField.val();
    if (presentationSupplyKindId) {
      fetchOptions(`/rest/v1/catalogs/supply/?kind=${presentationSupplyKindId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(presentationSupplyField, data);
        });
    } else {
      updateFieldOptions(presentationSupplyField, []);
    }
  }

  function updateName() {
    if (presentationSupplyKindField.val() && presentationSupplyField.val()) {
      const packagingSupplyKindName = presentationSupplyKindField.find('option:selected').text();
      const presentationSupplyName = presentationSupplyField.find('option:selected').text();
      const nameString = `${packagingSupplyKindName} ${presentationSupplyName}`
      nameField.val(nameString)
    } else {
      nameField.val('')
    }
  }

  productField.on('change', async function () {
    if (productField.val()) {
      productProperties = await fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
      const productMaketsResult = await fetchOptions(`/rest/v1/catalogs/market/?product=${productField.val()}&is_enabled=1`);
      updateFieldOptions(marketsField, productMaketsResult, marketsField.val() ? marketsField.val() : null);
    } else {
      productProperties = null;
    }
  });

  presentationSupplyKindField.on('change', function () {
    updatePresentationSupply();
  });

  presentationSupplyField.on('change', function () {
    updateName();
  });

  [productField, marketsField, presentationSupplyKindField, presentationSupplyField].forEach(field => field.select2());
});
