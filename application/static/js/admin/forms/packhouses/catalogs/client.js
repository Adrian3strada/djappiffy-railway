document.addEventListener('DOMContentLoaded', function () {
  const marketField = $('#id_market');
  const countryField = $('#id_country');
  const stateField = $('#id_state');
  const cityField = $('#id_city');
  const districtField = $('#id_district');
  const legalCategoryField = $('#id_legal_category');

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

  function updateCountry() {
    const marketId = marketField.val();
    if (marketId) {
      fetchOptions(`${API_BASE_URL}/catalogs/market/${marketId}/`)
        .then(marketData => fetchOptions(`${API_BASE_URL}/cities/country/?id=${marketData.countries.join(',')}`))
        .then(countries => {
          console.log("market countries", countries);
          updateFieldOptions(countryField, countries);
          updateLegalEntityCategory();
          updateState();
        });
    } else {
      updateFieldOptions(countryField, []);
      updateState();
    }
  }

  function updateLegalEntityCategory() {
    const countryId = countryField.val();
    if (countryId) {
      fetchOptions(`${API_BASE_URL}/billing/legal-entity-category/?country=${countryId}`)
        .then(data => updateFieldOptions(legalCategoryField, data));
    } else {
      updateFieldOptions(legalCategoryField, []);
    }
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
      fetchOptions(`${API_BASE_URL}/cities/subregion/?region=${stateId}`)
        .then(data => {
          updateFieldOptions(cityField, data);
        });
    } else {
      updateFieldOptions(cityField, []);
    }
  }

  function updateDistrict() {
    const cityId = cityField.val();
    if (cityId) {
      fetchOptions(`${API_BASE_URL}/cities/city/?subregion=${cityId}`)
        .then(data => {
          updateFieldOptions(districtField, data);
        });
    } else {
      updateFieldOptions(districtField, []);
    }
  }

  marketField.on('change', function () {
    updateCountry();
  });

  countryField.on('change', function () {
    updateState();
    updateLegalEntityCategory();
  });

  stateField.on('change', function () {
    updateCity();
  });

  cityField.on('change', function () {
    updateDistrict();
  });

  [marketField, countryField, stateField, cityField, districtField, legalCategoryField].forEach(field => field.select2());
});
