document.addEventListener('DOMContentLoaded', function () {
  const marketField = $('#id_market');
  const marketClassField = $('#id_market_class');
  const productField = $('#id_product');
  const productVarietyField = $('#id_product_variety');
  const productMarketSizeField = $('#id_product_size');
  const productRipenessField = $('#id_product_ripeness');

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
    const productId = productField.val()
    if (marketId && productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product-market-class/?market=${marketId}&product=${productId}&is_enabled=1`)
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
      fetchOptions(`${API_BASE_URL}/catalogs/product-variety/?product=${productId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(productVarietyField, data)
        });
    } else {
      updateFieldOptions(productVarietyField, [])
    }
  }
    function updateProductSize(){
      const productId = productField.val();
      const marketId = marketField.val();
      if(productId && marketId){
        fetchOptions(`${API_BASE_URL}/catalogs/product-size/?product=${productId}&market=${marketId}&is_enabled=1`)
          .then(data => {
            updateFieldOptions(productMarketSizeField, data)
          });

      } else {
        updateFieldOptions(productMarketSizeField, [])
      }
    }

  function updateProductRipness() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product-ripeness/?product=${productId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(productRipenessField, data)
        });
    } else {
      updateFieldOptions(productRipenessField, [])
    }
  }

  productField.on('change', function () {
    updateProductVariety();
    updateProductSize();
    updateProductRipness();
    updateMarketClass();
  }); 

  marketField.on('change', function () {
    updateMarketClass();
    updateProductSize();
  });


  [marketField, marketClassField,
    productField, productVarietyField, productMarketSizeField, productRipenessField].forEach(field => field.select2());
});
