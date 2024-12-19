$(document).ready(function () {
  const marketField = $('#id_market');
  const countryField = $('#id_country');
  const stateField = $('#id_state');
  const cityField = $('#id_city');
  const sameShipAddressCheckboxField = $('#id_same_ship_address');
  const legalEntityCategoryField = $('#id_legal_category');
  const inlineCountryField = $('#id_clientshipaddress-0-country');
  const inlineStateField = $('#id_clientshipaddress-0-state');
  const inlineCityField = $('#id_clientshipaddress-0-city');

  const clientAddressFields = [
    'country', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address', 'external_number', 'internal_number'
  ];

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

  function updateShipAddress(same_address_check) {
    clientAddressFields.forEach(field => {
      const shipField = $(`#id_clientshipaddress-0-${field}`);
      if (shipField.length) {
        if (same_address_check) {
          const clientField = $(`#id_${field}`);
          if (clientField.length) {
            shipField.val(clientField.val()).trigger('change');
          }
          shipField.addClass('disabled-field');
        } else {
          shipField.removeClass('disabled-field');
        }
      }
    });
    if (same_address_check) {
      syncAddressFields();
      disableInlineFields();
    } else {
      enableInlineFields();
    }
  }

  function disableInlineFields() {
    inlineCountryField.on('select2:opening select2:closing', preventDefault);
    inlineStateField.on('select2:opening select2:closing', preventDefault);
    inlineCityField.on('select2:opening select2:closing', preventDefault);
    setTimeout(() => {
      inlineCountryField.next('.select2-container').addClass('disabled-field');
      inlineStateField.next('.select2-container').addClass('disabled-field');
      inlineCityField.next('.select2-container').addClass('disabled-field');
    }, 800);
  }

  function enableInlineFields() {
    inlineCountryField.off('select2:opening select2:closing', preventDefault);
    inlineStateField.off('select2:opening select2:closing', preventDefault);
    inlineCityField.off('select2:opening select2:closing', preventDefault);
    inlineCountryField.next('.select2-container').removeClass('disabled-field');
    inlineStateField.next('.select2-container').removeClass('disabled-field');
    inlineCityField.next('.select2-container').removeClass('disabled-field');
  }

  function preventDefault(e) {
    e.preventDefault();
  }

  function syncAddressFields() {
    if (sameShipAddressCheckboxField.prop('checked')) {
      clientAddressFields.forEach(field => {
        const clientField = $(`#id_${field}`);
        const shipField = $(`#id_clientshipaddress-0-${field}`);
        if (clientField.length && shipField.length) {
          shipField.val(clientField.val()).trigger('change');
        }
      });
      inlineStateField.val(stateField.val()).trigger('change');
      inlineCityField.val(cityField.val()).trigger('change');
      setTimeout(() => {
        inlineStateField.val(stateField.val()).trigger('change');
        setTimeout(() => {
          inlineCityField.val(cityField.val()).trigger('change');
        }, 300);
      }, 300);
      setTimeout(() => {
        inlineCountryField.next('.select2-container').addClass('disabled-field');
        inlineStateField.next('.select2-container').addClass('disabled-field');
        inlineCityField.next('.select2-container').addClass('disabled-field');
      }, 400);
    }
  }

  function updateCountry() {
    const marketId = marketField.val();
    if (marketId) {
      fetchOptions(`${API_BASE_URL}/catalogs/market/${marketId}/`)
        .then(marketData => fetchOptions(`${API_BASE_URL}/cities/country/?id=${marketData.countries.join(',')}`))
        .then(countries => {
          updateFieldOptions(countryField, countries);
          updateLegalEntityCategory();
          updateState();
          updateInlineCountry();
        });
    } else {
      updateFieldOptions(countryField, []);
      updateState();
      updateInlineCountry();
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

  function updateInlineCountry() {
    const marketId = marketField.val();
    if (marketId) {
      fetchOptions(`${API_BASE_URL}/catalogs/market/${marketId}/`)
        .then(marketData => fetchOptions(`${API_BASE_URL}/cities/country/?id=${marketData.countries.join(',')}`))
        .then(countries => {
          updateFieldOptions(inlineCountryField, countries);
          if (!sameShipAddressCheckboxField.prop('checked')) {
            updateInlineState();
          }
        });
    } else {
      updateFieldOptions(inlineCountryField, []);
      if (!sameShipAddressCheckboxField.prop('checked')) {
        updateInlineState();
      }
    }
  }

  function updateInlineState() {
    const countryId = inlineCountryField.val();
    if (countryId) {
      fetchOptions(`${API_BASE_URL}/cities/region/?country=${countryId}`)
        .then(data => {
          updateFieldOptions(inlineStateField, data);
          if (!sameShipAddressCheckboxField.prop('checked')) {
            updateInlineCity();
          }
        });
    } else {
      updateFieldOptions(inlineStateField, []);
      if (!sameShipAddressCheckboxField.prop('checked')) {
        updateInlineCity();
      }
    }
  }

  function updateInlineCity() {
    const stateId = inlineStateField.val();
    if (stateId) {
      fetchOptions(`${API_BASE_URL}/cities/city/?region=${stateId}`)
        .then(data => {
          updateFieldOptions(inlineCityField, data);
        });
    } else {
      updateFieldOptions(inlineCityField, []);
    }
  }

  marketField.on('change', function () {
    updateCountry();
    updateInlineCountry();
  });

  countryField.on('change', function () {
    updateState();
    updateLegalEntityCategory();
  });

  stateField.on('change', function () {
    updateCity();
  });

  sameShipAddressCheckboxField.on('change', function () {
    const same_address_check = sameShipAddressCheckboxField.prop('checked');
    updateShipAddress(same_address_check);
  });

  clientAddressFields.forEach(field => {
    $(`#id_${field}`).on('input', function () {
      if (sameShipAddressCheckboxField.prop('checked')) {
        syncAddressFields();
      }
    });
  });

  inlineCountryField.on('change', updateInlineState);
  inlineStateField.on('change', updateInlineCity);

  [marketField, countryField, stateField, cityField, legalEntityCategoryField, inlineCountryField, inlineStateField, inlineCityField].forEach(field => field.select2());

  if (sameShipAddressCheckboxField.prop('checked')) {
    disableInlineFields();
  }

  const same_address_check = sameShipAddressCheckboxField.prop('checked');
  updateShipAddress(same_address_check);

});
