document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const marketsField = $('#id_markets');
  const presentationSupplyKindField = $('#id_presentation_supply_kind');
  const presentationSupplyField = $('#id_presentation_supply');
  const nameField = $('#id_name');

  const API_BASE_URL = '/rest/v1';

  function updateFieldOptions(field, options, selectedValue = null) {
    console.log("updateFieldOptions", field, options, selectedValue);
    field.empty().append(new Option('---------', '', !selectedValue, !selectedValue));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, selectedValue === option.id, selectedValue === option.id));
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
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${presentationSupplyKindId}&is_enabled=1`)
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

  presentationSupplyKindField.on('change', function () {
    updatePresentationSupply();
  });

  presentationSupplyField.on('change', function () {
    updateName();
  });

  [productField, marketsField, presentationSupplyKindField, presentationSupplyField].forEach(field => field.select2());
});
