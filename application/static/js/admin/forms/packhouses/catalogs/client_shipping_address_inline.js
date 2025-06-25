document.addEventListener('DOMContentLoaded', () => {
  function updateFieldOptions(field, options, selectedValue = null) {
    field.empty();
    field.append(new Option('---------', '', true, true));
    options.forEach(option => {
      const opt = new Option(option.name, option.id, false, false);
      if (String(option.id) === String(selectedValue)) {
        opt.selected = true;
      }
      field.append(opt);
    });
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: 'GET',
      dataType: 'json'
    }).fail(error => console.error('Fetch error:', error));
  }

  function setupEvents(countryField, stateField, cityField, districtField) {
    countryField.on('change', function () {
      const countryId = $(this).val();
      if (countryId) {
        fetchOptions(`/rest/v1/cities/region/?country=${countryId}`).then(data => {
          updateFieldOptions(stateField, data);
          updateFieldOptions(cityField, []);
          updateFieldOptions(districtField, []);
        });
      } else {
        updateFieldOptions(stateField, []);
        updateFieldOptions(cityField, []);
        updateFieldOptions(districtField, []);
      }
    });

    stateField.on('change', function () {
      const stateId = $(this).val();
      if (stateId) {
        fetchOptions(`/rest/v1/cities/subregion/?region=${stateId}`).then(data => {
          updateFieldOptions(cityField, data);
          updateFieldOptions(districtField, []);
        });
      } else {
        updateFieldOptions(cityField, []);
        updateFieldOptions(districtField, []);
      }
    });

    cityField.on('change', function () {
      const cityId = $(this).val();
      if (cityId) {
        fetchOptions(`/rest/v1/cities/city/?subregion=${cityId}`).then(data => {
          updateFieldOptions(districtField, data);
        });
      } else {
        updateFieldOptions(districtField, []);
      }
    });
  }

  // Form existente
  const existingForms = document.querySelectorAll('div[id^="clientshippingaddress_set-"]:not([id*="__prefix__"])');
  existingForms.forEach(form => {
    const $form = $(form);
    const countryField = $form.find('select[name$="-country"]');
    const stateField = $form.find('select[name$="-state"]');
    const cityField = $form.find('select[name$="-city"]');
    const districtField = $form.find('select[name$="-district"]');

    const selectedState = stateField.val();
    const selectedCity = cityField.val();
    const selectedDistrict = districtField.val();

    if (countryField.val()) {
      fetchOptions(`/rest/v1/cities/region/?country=${countryField.val()}`).then(data => {
        updateFieldOptions(stateField, data, selectedState);
        if (selectedState) {
          fetchOptions(`/rest/v1/cities/subregion/?region=${selectedState}`).then(cities => {
            updateFieldOptions(cityField, cities, selectedCity);
            if (selectedCity) {
              fetchOptions(`/rest/v1/cities/city/?subregion=${selectedCity}`).then(districts => {
                updateFieldOptions(districtField, districts, selectedDistrict);
              });
            }
          });
        }
      });
    }

    setupEvents(countryField, stateField, cityField, districtField);
  });

  // Nuevos formularios
  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'clientshippingaddress_set') {
      const $form = $(event.target);
      const countryField = $form.find('select[name$="-country"]');
      const stateField = $form.find('select[name$="-state"]');
      const cityField = $form.find('select[name$="-city"]');
      const districtField = $form.find('select[name$="-district"]');

      updateFieldOptions(stateField, []);
      updateFieldOptions(cityField, []);
      updateFieldOptions(districtField, []);

      const initialCountry = countryField.val();
      if (initialCountry) {
        fetchOptions(`/rest/v1/cities/region/?country=${initialCountry}`).then(data => {
          updateFieldOptions(stateField, data);
        });
      }

      setupEvents(countryField, stateField, cityField, districtField);
    }
  });
});
