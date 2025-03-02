document.addEventListener('DOMContentLoaded', function () {
  const kindField = $('#id_kind');
  const capacityField = $('#id_capacity');
  const usageDiscountQuantityField = $('#id_usage_discount_quantity');

  let kindProperties = null;

  const API_BASE_URL = '/rest/v1';

  function updateFieldOptions(field, options, selectedValue = null) {
    console.log("updateFieldOptions", field, options, selectedValue);
    field.empty().append(new Option('---------', '', !selectedValue, !selectedValue));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, selectedValue === option.id, selectedValue === option.id));
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

  function updateCapacityUnitCategoryField() {
    console.log("updateCapacityUnitCategoryField", kindField.val());
    const packagingContainerKinds = ['packaging_containment', 'packaging_separator', 'packaging_presentation'];
    fetchOptions(`${API_BASE_URL}/base/supply-kind/${kindField.val()}/`)
      .then(data => {
        console.log("updateCapacityUnitCategoryField fetchOptions", data);
        kindProperties = data;
        if (kindProperties.capacity_unit_category && packagingContainerKinds.includes(kindProperties.category)) {
          capacityField.closest('.form-group').fadeIn();
        } else {
          capacityField.val(null);
          capacityField.closest('.form-group').fadeOut();
        }
      })
      .catch(error => {
        console.error('Fetch error:', error);
        capacityField.val(null);
        capacityField.closest('.form-group').fadeOut();
      });
  }

  kindField.on('change', () => {
    updateCapacityUnitCategoryField();
  });

  capacityField.closest('.form-group').hide();

  if (kindField.val() && capacityField.val()) capacityField.closest('.form-group').show();
  if (kindField.val()) updateCapacityUnitCategoryField();

  [kindField].forEach(field => field.select2());
});
