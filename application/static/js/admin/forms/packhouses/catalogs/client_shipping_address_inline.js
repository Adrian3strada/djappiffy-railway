document.addEventListener('DOMContentLoaded', () => {

  function updateFieldOptions(field, options) {
    field.empty();
    if (!field.prop('multiple')) {
      field.append(new Option('---------', '', true, true));
    }
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

  // Agregar listener para cuando se añadan formularios en el inline de `clientshippingaddress_set`
  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'clientshippingaddress_set') {
      const newForm = event.target;
      const countryField = $(newForm).find('select[name$="-country"]');
      const stateField = $(newForm).find('select[name$="-state"]');
      const cityField = $(newForm).find('select[name$="-city"]');
      const districtField = $(newForm).find('select[name$="-district"]');
      updateFieldOptions(cityField, []);
      updateFieldOptions(districtField, []);


      countryField.on('change', function () {
        const countryId = $(this).val();
        if (countryId) {
          fetchOptions(`/rest/v1/cities/region/?country=${countryId}`)
            .then(data => {
              updateFieldOptions(stateField, data);
            });
        } else {
          updateFieldOptions(stateField, []);
        }
      });

      stateField.on('change', function () {
        const stateId = $(this).val();
        if (stateId) {
          fetchOptions(`/rest/v1/cities/subregion/?region=${stateId}`)
            .then(data => {
              updateFieldOptions(cityField, data);
            });
        } else {
          updateFieldOptions(cityField, []);
        }
      });

      cityField.on('change', function () {
        const cityId = $(this).val();
        if (cityId) {
          fetchOptions(`/rest/v1/cities/city/?subregion=${cityId}`)
            .then(data => {
              updateFieldOptions(districtField, data);
            });
        } else {
          updateFieldOptions(districtField, []);
        }
      });
    }
  });
});
