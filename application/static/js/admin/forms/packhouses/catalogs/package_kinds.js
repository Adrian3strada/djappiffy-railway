document.addEventListener('DOMContentLoaded', function () {
  const packagingKindField = $('#id_packaging_kind');
  const packagingField = $('#id_packaging');

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

  function updatePackaging() {
    const packagingKindId = packagingKindField.val();
    if (packagingKindId) {
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${packagingKindId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(packagingField, data);
        });
    } else {
      updateFieldOptions(packagingField, []);
    }
  }

  packagingKindField.on('change', function () {
    updatePackaging();
  });

  [packagingKindField, packagingField].forEach(field => field.select2());
});
