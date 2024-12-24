document.addEventListener('DOMContentLoaded', function () {
  const API_BASE_URL = '/rest/v1';
  const vehicleField = $('#id_vehicle');
  getVehicle();

  function updateFieldOptions(field, options) {
    field.empty().append(new Option('---------', '', true, true));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, false));
    });
    field.trigger('change').select2();
  }

  function fetchOptions(url) {
    return fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Error fetching data');
        }
        return response.json();
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }

  function getVehicle() {
    fetchOptions(`${API_BASE_URL}/catalogs/vehicle/?scope=packhouse&is_enabled=true`)
      .then(data => {
        if (data && Array.isArray(data)) {
          updateFieldOptions(vehicleField, data);
        } else {
          console.error('Invalid data format:', data);
        }
      });
  }

});
