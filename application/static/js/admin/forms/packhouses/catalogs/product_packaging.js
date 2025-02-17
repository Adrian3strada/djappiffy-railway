document.addEventListener('DOMContentLoaded', function () {
  const supplyKindField = $('#id_main_supply_kind');
  const supplyField = $('#id_main_supply');

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
    const supplyKindId = supplyKindField.val();
    if (supplyKindId) {
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${supplyKindId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(supplyField, data);
        });
    } else {
      updateFieldOptions(supplyField, []);
    }
  }

  supplyKindField.on('change', function () {
    updateSupply();
  });

  [supplyKindField, supplyField].forEach(field => field.select2());
});
