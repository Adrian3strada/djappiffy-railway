document.addEventListener('DOMContentLoaded', function () {
  const countryField = $('#id_country');
  const stateField = $('#id_state');
  const cityField = $('#id_city');
  const legalEntityCategoryField = $('#id_legal_category');

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

  function updateState() {
    const countryId = countryField.val();
    if (countryId) {
      fetchOptions(`${API_BASE_URL}/cities/region/?country=${countryId}`)
        .then(data => {
          updateFieldOptions(stateField, data);
          updateCity();
        });
    } else {
      updateFieldOptions(stateField, []);
      updateCity();
    }
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

  function updateLegalEntityCategory() {
    const countryId = countryField.val();
    if (countryId) {
      fetchOptions(`${API_BASE_URL}/billing/legal-entity-category/?country=${countryId}`)
        .then(data => updateFieldOptions(legalEntityCategoryField, data));
    } else {
      updateFieldOptions(legalEntityCategoryField, []);
    }
  }

  countryField.on('change', function () {
    updateState();
    if(legalEntityCategoryField.length){
      updateLegalEntityCategory();
    }
  });

  stateField.on('change', function () {
    updateCity();
  });


  [countryField, stateField, cityField].forEach(field => field.select2());

});
