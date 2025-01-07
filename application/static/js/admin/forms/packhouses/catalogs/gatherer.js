document.addEventListener('DOMContentLoaded', function () {
  const API_BASE_URL = '/rest/v1';
  const vehicleField = $('#id_vehicle');
  getVehicle();

  function updateFieldOptions(field, options) {
    const currentValue = field.val();
    field.empty().append(new Option("---------", "", true, true));

    if (options && !Array.isArray(options)) {
      options = [options];
    }

    if (options && options.length) {
      options.forEach((option) => {
        const isSelected = option.id == currentValue;
        field.append(
          new Option(option.name, option.id, isSelected, isSelected)
        );
      });
    }

    field.trigger("change").select2();
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
    fetchOptions(`${API_BASE_URL}/catalogs/vehicle/?category=packhouse&is_enabled=true`)
      .then(data => {
        if (data && Array.isArray(data)) {
          updateFieldOptions(vehicleField, data);
        } else {
          console.error('Invalid data format:', data);
        }
      });
  }

});
