document.addEventListener('DOMContentLoaded', function () {
  const packagingSupplyKindField = $('#id_packaging_supply_kind');
  const packagingSupplyField = $('#id_packaging_supply');
  const nameField = $('#id_name');

  const API_BASE_URL = '/rest/v1';

  function updateFieldOptions(field, options) {
    field.empty().append(new Option('---------', '', true, true));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, false));
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

  function updateSupply() {
    const packagingSupplyKindId = packagingSupplyKindField.val();
    if (packagingSupplyKindId) {
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${packagingSupplyKindId}&is_enabled=1`)
        .then(data => {
          console.log("data", data);
          updateFieldOptions(packagingSupplyField, data);
        });
    } else {
      updateFieldOptions(packagingSupplyField, []);
    }
  }

  function updateName() {
    if (packagingSupplyKindField.val() && packagingSupplyField.val()) {
      nameField.val()
    }
  }

  packagingSupplyKindField.on('change', function () {
    updateSupply();
  });

  packagingSupplyField.on('change', function () {
    updateName();
  });

  [packagingSupplyKindField, packagingSupplyField].forEach(field => field.select2());
});
