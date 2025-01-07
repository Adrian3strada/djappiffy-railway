document.addEventListener('DOMContentLoaded', function () {
  const categoryField = $('#id_category');
  const providerProviderField = $('#id_provider_provider');
  const vehicleField = $('#id_vehicle_provider');

  const allowedProviderProviderCategories = ['product_producer'];
  const allowedVehicleProviderCategories = ['harvesting_provider'];

  const mapAllowedProviderProviderCategories = {
    'product_producer': ['product_provider',]
  };

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

  function updateProviderProviderField() {
    const categoryId = categoryField.val();
    if (categoryId && allowedProviderProviderCategories.includes(categoryId)) {
      fetchOptions(`${API_BASE_URL}/catalogs/provider/?categories=${mapAllowedProviderProviderCategories[categoryId]}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(providerProviderField, data);
          providerProviderField.closest('.form-group').fadeIn();
          vehicleField.closest('.form-group').fadeOut();
        });
    } else if (categoryId && allowedVehicleProviderCategories.includes(categoryId)) {
      vehicleField.closest('.form-group').fadeIn();
      providerProviderField.closest('.form-group').fadeOut();
    }else {
      updateFieldOptions(providerProviderField, []);
      providerProviderField.closest('.form-group').fadeOut();
      vehicleField.closest('.form-group').fadeOut();
    }
  }

  categoryField.on('change', function () {
    updateProviderProviderField();
  });

  [categoryField, providerProviderField].forEach(field => field.select2());
  if (!categoryField.val()) {
    providerProviderField.closest('.form-group').hide();
    updateProviderProviderField();
  }
  if (categoryField.val() && !mapAllowedProviderProviderCategories[categoryField.val()]) {
    providerProviderField.closest('.form-group').hide();
  }
});
