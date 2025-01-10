document.addEventListener('DOMContentLoaded', function () {
  const marketField = $('#id_market');
  const marketClassField = $('#id_market_class');
  const productField = $('#id_product');
  const productVarietyField = $('#id_product_variety');
  const productVarietySizeField = $('#id_product_variety_size');

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

  function updateMarketClass() {
    const marketId = marketField.val();
    if (marketId) {
      fetchOptions(`${API_BASE_URL}/catalogs/market_class/?market=${marketId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(marketClassField, data);
        });
    } else {
      updateFieldOptions(marketClassField, []);
    }
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

  function updateProductVarietySize() {
    const productVarietyId = productVarietyField.val();
    if (productVarietyId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_size/?is_enabled=1`)
        .then(data => {
          updateFieldOptions(productVarietySizeField, data)
        });
    } else {
      updateFieldOptions(productVarietySizeField, [])
    }
  }

  marketField.on('change', function () {
    updateMarketClass();
  });

  productField.on('change', function () {
    updateProductVariety();
  });

  productVarietyField.on('change', function () {
    updateProductVarietySize();
  });

  [marketField, marketClassField,
    productField, productVarietyField, productVarietySizeField].forEach(field => field.select2());
});
