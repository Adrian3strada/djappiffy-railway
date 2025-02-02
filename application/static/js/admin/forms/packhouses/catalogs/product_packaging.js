document.addEventListener('DOMContentLoaded', function () {
  const marketField = $('#id_market');
  const productField = $('#id_product');
  const productVarietyField = $('#id_product_variety');
  const productSizeField = $('#id_product_size');

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
      fetchOptions(`${API_BASE_URL}/catalogs/product_variety/?product=${productId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(productVarietyField, data)
        });
    } else {
      updateFieldOptions(productVarietyField, [])
    }
  }

  function updateProductSize() {
    const productVarietyId = productVarietyField.val();
    if (productVarietyId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_size/?product_varieties=${productVarietyId}`)
        .then(data => {
          updateFieldOptions(productSizeField, data)
        });
    } else {
      updateFieldOptions(productSizeField, [])
    }
  }

  productField.on('change', function () {
    updateProductVariety();
    updateProductSize();
  });

  [marketField, productField, productVarietyField, productSizeField].forEach(field => field.select2());
});
