document.addEventListener('DOMContentLoaded', function () {
  const stateField = $('#id_state');
  const cityField = $('#id_city');

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

  function updateCity() {
    const stateId = stateField.val();
    if (stateId) {
      fetchOptions(`${API_BASE_URL}/cities/city/?region=${stateId}`)
        .then(data => {
          updateFieldOptions(cityField, data);
        });
    } else {
      updateFieldOptions(cityField, []);
    }
  }

  stateField.on('change', function () {
    updateCity();
  });

  [stateField, cityField].forEach(field => field.select2());
});
