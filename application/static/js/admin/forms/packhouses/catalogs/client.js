document.addEventListener('DOMContentLoaded', function () {
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

  function updateFieldOptions(field, options) {
    field.empty().append(new Option('---------', '', true, true));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, false));
    });
    field.trigger('change').select2();
  }

  function fetchOptions(url) {
    return fetch(url).then(response => response.json());
  }

  function updateShipAddress(same_address_check) {
    clientAddressFields.forEach(field => {
      const shipField = $(`#id_clientshipaddress-0-${field}`);
      console.log("shipField", shipField);
      if (shipField.length) {
        shipField.prop('disabled', same_address_check);
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
    }
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
        // Esperar un segundo para forzar que visualmente se actualicen el campo state
        inlineStateField.val(stateField.val()).trigger('change');
        setTimeout(() => {
          // Esperar un segundo para forzar que visualmente se actualicen el campo city
          inlineCityField.val(cityField.val()).trigger('change');
        }, 200);
      }, 200);
    }
  }

  function updateCountry() {
    const marketId = marketField.val();
    if (marketId) {
      fetchOptions(`/rest/v1/catalogs/market/${marketId}/`)
        .then(marketData => fetchOptions(`/rest/v1/cities/country/?id=${marketData.countries.join(',')}`))
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
      fetchOptions(`/rest/v1/billing/legal-entity-category/?country=${countryId}`)
        .then(data => updateFieldOptions(legalEntityCategoryField, data));
    } else {
      updateFieldOptions(legalEntityCategoryField, []);
    }
  }

  function updateState() {
    const countryId = countryField.val();
    if (countryId) {
      fetchOptions(`/rest/v1/cities/region/?country=${countryId}`)
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
      fetchOptions(`/rest/v1/cities/city/?region=${stateId}`)
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
      fetchOptions(`/rest/v1/catalogs/market/${marketId}/`)
        .then(marketData => fetchOptions(`/rest/v1/cities/country/?id=${marketData.countries.join(',')}`))
        .then(countries => {
          updateFieldOptions(inlineCountryField, countries);
          if (!sameShipAddressCheckboxField.prop('checked')) {
            updateInlineState();
          }
        });
    } else {
      updateFieldOptions(inlineCountryField, []);
      if (!sameShipAddressCheckboxField.prop('checked')) {
        updateInlineState(); // Llamar a updateInlineState solo si el campo no está deshabilitado
      }
    }
  }

  function updateInlineState() {
    const countryId = inlineCountryField.val();
    if (countryId) {
      fetchOptions(`/rest/v1/cities/region/?country=${countryId}`)
        .then(data => {
          updateFieldOptions(inlineStateField, data);
          if (!sameShipAddressCheckboxField.prop('checked')) {
            updateInlineCity(); // Llamar a updateInlineCity solo si el campo no está deshabilitado
          }
        });
    } else {
      updateFieldOptions(inlineStateField, []);
      if (!sameShipAddressCheckboxField.prop('checked')) {
        updateInlineCity(); // Llamar a updateInlineCity solo si el campo no está deshabilitado
      }
    }
  }

  function updateInlineCity() {
    const stateId = inlineStateField.val();
    if (stateId) {
      fetchOptions(`/rest/v1/cities/city/?region=${stateId}`)
        .then(data => {
          updateFieldOptions(inlineCityField, data);
        });
    } else {
      updateFieldOptions(inlineCityField, []);
    }
  }

  marketField.on('change', () => {
    updateCountry();
    updateInlineCountry();
  });
  countryField.on('change', () => {
    updateState();
    updateLegalEntityCategory();
  });
  stateField.on('change', () => {
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

  // Eventos para actualizar los inlines
  inlineCountryField.on('change', updateInlineState);
  inlineStateField.on('change', updateInlineCity);

  // Inicializar select2 en los campos
  [marketField, countryField, stateField, cityField, legalEntityCategoryField].forEach(field => field.select2());
});
