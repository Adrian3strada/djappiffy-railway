document.addEventListener('DOMContentLoaded', function () {
    const stateField = $('#id_state');
    const cityField = $('#id_city');
    const districtField = $('#id_district');

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
          fetchOptions(`/rest/v1/cities/subregion/?region=${stateId}`)
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
          fetchOptions(`/rest/v1/cities/city/?subregion=${cityId}`)
            .then(data => {
              updateFieldOptions(districtField, data);
            });
        } else {
          updateFieldOptions(districtField, []);
        }
      }
    
      stateField.on('change', function () {
        updateCity();
      });
    
      cityField.on('change', function () {
        updateDistrict();
      });
});