document.addEventListener('DOMContentLoaded', function () {
  const marketField = $('#id_market');
  const countryField = $('#id_country');
  const stateField = $('#id_state');
  const cityField = $('#id_city');
  const sameShipAddressCheckbox = $('#id_same_ship_address');
  const clientAddressFields = [
    'country', 'state', 'city', 'district', 'neighborhood', 'postal_code', 'address', 'external_number', 'internal_number'
  ];

  function updateShipAddress(same_address_check) {
    clientAddressFields.forEach(field => {
      const shipField = $(`#id_clientshipaddress-0-${field}`);
      if (shipField.length) {
        shipField.prop('disabled', same_address_check);
        if (same_address_check) {
          const clientField = $(`#id_${field}`);
          if (clientField.length) {
            shipField.val(clientField.val());
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
    if (sameShipAddressCheckbox.prop('checked')) {
      clientAddressFields.forEach(field => {
        const clientField = $(`#id_${field}`);
        const shipField = $(`#id_clientshipaddress-0-${field}`);
        if (clientField) {
          shipField.val(clientField.val());
        }
      });
    }
  }

  function updateCountry() {
    const marketId = marketField.val();
    if (marketId) {
      fetch(`/rest/v1/catalogs/market/${marketId}/`)
        .then(response => response.json())
        .then(marketData => {
          return fetch(`/rest/v1/cities/country/?id=${marketData.countries.join(',')}`);
        })
        .then(response => response.json())
        .then(countries => {
          console.log('Countries:', countries);
          countryField.empty().append(new Option('---------', '', true, true));
          countries.forEach(country => {
            console.log('Country:', country);
            const option = new Option(country.name, country.id, false, false);
            countryField.append(option);
          });
          countryField.trigger('change');
          updateState();
        });
    } else {
      countryField.empty().append(new Option('---------', '', true, true)).trigger('change');
      updateState();
    }
  }

  function updateState() {
    const countryId = countryField.val();
    if (countryId) {
      fetch(`/rest/v1/cities/region/?country=${countryId}`)
        .then(response => response.json())
        .then(data => {
          stateField.empty().append(new Option('---------', '', true, true));
          data.forEach(state => {
            const option = new Option(state.name, state.id, false, false);
            stateField.append(option);
          });
          stateField.trigger('change');
          updateCity();
        });
    } else {
      stateField.empty().append(new Option('---------', '', true, true)).trigger('change');
      updateCity();
    }
  }

  function updateCity() {
    const stateId = stateField.val();
    if (stateId) {
      fetch(`/rest/v1/cities/city/?region=${stateId}`)
        .then(response => response.json())
        .then(data => {
          cityField.empty().append(new Option('---------', '', true, true));
          data.forEach(city => {
            const option = new Option(city.name, city.id, false, false);
            cityField.append(option);
          });
          cityField.trigger('change');
        });
    } else {
      cityField.empty().append(new Option('---------', '', true, true)).trigger('change');
    }
  }

  marketField.on('change', updateCountry);
  countryField.on('change', updateState);
  stateField.on('change', updateCity);

  sameShipAddressCheckbox.on('change', function () {
    const same_address_check = sameShipAddressCheckbox.prop('checked');
    updateShipAddress(same_address_check);
  });

  clientAddressFields.forEach(field => {
    $(`#id_${field}`).on('input', syncAddressFields);
  });

  // Inicializar select2 en los campos
  marketField.select2();
  countryField.select2();
  stateField.select2();
  cityField.select2();
});
