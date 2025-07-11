document.addEventListener('DOMContentLoaded', function () {
  const categoryField = $('#id_category');
  const marketField = $('#id_market');
  const countryField = $('#id_country');
  const stateField = $('#id_state');
  const cityField = $('#id_city');
  const districtField = $('#id_district');
  const capitalFrameworkField = $('#id_capital_framework');

  const API_BASE_URL = '/rest/v1';

  function updateFieldOptions(field, options) {
    field.empty().append(new Option('---------', '', true, true));
    options.forEach(option => {
      if (field === capitalFrameworkField) {
        field.append(new Option(option.code, option.id, false, false));
      } else {
        field.append(new Option(option.name, option.id, false, false));
      }
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
          updateCapitalFramework();
          updateState();
        });
    } else {
      updateFieldOptions(countryField, []);
      updateState();
    }
  }

  function updateCapitalFramework() {
    const countryId = countryField.val();
    if (countryId) {
      fetchOptions(`${API_BASE_URL}/base/capital-framework/?country=${countryId}`)
        .then(data => {
          console.log("capital framework", data);
          if (data.length === 0) {
            updateFieldOptions(capitalFrameworkField, []);
            capitalFrameworkField.closest('.form-group').fadeOut();
          } else {
            capitalFrameworkField.closest('.form-group').fadeIn();
            updateFieldOptions(capitalFrameworkField, data);
          }
        });
    } else {
      updateFieldOptions(capitalFrameworkField, []);
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
    updateCapitalFramework();
  });

  stateField.on('change', function () {
    updateCity();
  });

  cityField.on('change', function () {
    updateDistrict();
  });

  capitalFrameworkField.closest('.form-group').hide();

  if (countryField.val()) {
    if (!stateField.val()) updateState();
    if (!capitalFrameworkField.val()) updateCapitalFramework();
  }
  if (capitalFrameworkField.val().length > 0) capitalFrameworkField.closest('.form-group').show();

  [marketField, countryField, stateField, cityField, districtField, capitalFrameworkField].forEach(field => field.select2());
});
