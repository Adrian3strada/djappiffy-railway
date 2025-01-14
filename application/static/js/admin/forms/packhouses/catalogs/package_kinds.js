document.addEventListener('DOMContentLoaded', function () {
  const externalSupplyKindField = $('#id_external_supply_kind');
  const externalSupplyField = $('#id_external_supply');

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

  function updatePrimarySupply() {
    const externalSupplyKindId = externalSupplyKindField.val();
    if (externalSupplyKindId) {
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${externalSupplyKindId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(externalSupplyField, data);
        });
    } else {
      updateFieldOptions(externalSupplyField, []);
    }
  }

  externalSupplyKindField.on('change', function () {
    updatePrimarySupply();
  });

  [externalSupplyKindField, externalSupplyField].forEach(field => field.select2());
});
