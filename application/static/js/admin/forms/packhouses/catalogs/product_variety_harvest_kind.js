document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const productVarietyField = $('#id_product_variety');

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

  function updateProductVariety() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_variety/?product=${productId}&is_enabled=true`)
        .then(data => {
          updateFieldOptions(productVarietyField, data);
        });
    } else {
      updateFieldOptions(productVarietyField, []);
    }
  }

  productField.on('change', updateProductVariety);

  [productField, productVarietyField].forEach(field => field.select2());
  if (! productField.val()) updateProductVariety();
});
