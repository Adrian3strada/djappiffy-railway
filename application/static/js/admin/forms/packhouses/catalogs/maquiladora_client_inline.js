document.addEventListener('DOMContentLoaded', () => {

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

  function updateCountry(marketId, form) {
    if (marketId) {
      fetchOptions(`/rest/v1/catalogs/market/${marketId}/`)
        .then(marketData => fetchOptions(`/rest/v1/cities/country/?id=${marketData.countries.join(',')}`))
        .then(countries => {
          updateFieldOptions(form.find('select[name$="-country"]'), countries);
          updateState(form);
        });
    } else {
      updateFieldOptions(form.find('select[name$="-country"]'), []);
      updateState(form);
    }
  }

  function updateState(form) {
    const countryId = form.find('select[name$="-country"]').val();
    if (countryId) {
      fetchOptions(`/rest/v1/cities/region/?country=${countryId}`)
        .then(data => {
          updateFieldOptions(form.find('select[name$="-state"]'), data);
          updateCity(form);
        });
    } else {
      updateFieldOptions(form.find('select[name$="-state"]'), []);
      updateCity(form);
    }
  }

  function updateCity(form) {
    const stateId = form.find('select[name$="-state"]').val();
    if (stateId) {
      fetchOptions(`/rest/v1/cities/city/?region=${stateId}`)
        .then(data => {
          updateFieldOptions(form.find('select[name$="-city"]'), data);
        });
    } else {
      updateFieldOptions(form.find('select[name$="-city"]'), []);
    }
  }

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'maquiladoraclient_set') {
      const newForm = $(event.target);
      const marketField = newForm.find('select[name$="-market"]');

      marketField.on('change', () => {
        updateCountry(marketField.val(), newForm);
      });

      newForm.find('select[name$="-country"]').on('change', () => {
        updateState(newForm);
      });

      newForm.find('select[name$="-state"]').on('change', () => {
        updateCity(newForm);
      });
    }
  });

  const existingForms = $('div[id^="maquiladoraclient_set-"]');
  existingForms.each((index, form) => {
    const marketField = $(form).find('select[name$="-market"]');
    const countryField = $(form).find('select[name$="-country"]');
    const stateField = $(form).find('select[name$="-state"]');
    const cityField = $(form).find('select[name$="-city"]');

    marketField.on('change', () => {
      updateCountry(marketField.val(), $(form));
    });

    countryField.on('change', () => {
      updateState($(form));
    });

    stateField.on('change', () => {
      updateCity($(form));
    });

    if (marketField.val()) {
      updateCountry(marketField.val(), $(form));
    }
  });
});
