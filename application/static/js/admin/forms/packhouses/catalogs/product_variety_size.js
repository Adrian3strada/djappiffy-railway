document.addEventListener('DOMContentLoaded', function () {


  const productField = $('#id_product');
  const productVarietyField = $('#id_product_variety');
  const marketField = $('#id_market');
  const marketStandardProductSizeField = $('#id_market_standard_product_size');
  const productVarietySizeHarvestKindField = $('#id_product_variety_size_harvest_kind');
  const nameField = $('#id_name');
  const aliasField = $('#id_alias');

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
          updateFieldOptions(productVarietyField, data);
        });
    } else {
      updateFieldOptions(productVarietyField, []);
    }
  }

  function updateMarketStandardProductSize() {
    const marketId = marketField.val();
    if (marketId) {
      fetchOptions(`${API_BASE_URL}/catalogs/market_standard_product_size/?market=${marketId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(marketStandardProductSizeField, data);
        });
    } else {
      updateFieldOptions(marketStandardProductSizeField, []);
    }
  }

  function updateProductVarietySizeHarvestKind() {
    const productVarietyId = productVarietyField.val();
    if (productVarietyId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_variety_size_harvest_kind/?product_variety=${productVarietyId}`)
        .then(data => {
          updateFieldOptions(productVarietySizeHarvestKindField, data);
        });
    } else {
      updateFieldOptions(productVarietySizeHarvestKindField, []);
    }
  }

  productField.on('change', updateProductVariety);
  marketField.on('change', updateMarketStandardProductSize);
  productVarietyField.on('change', updateProductVarietySizeHarvestKind);
  nameField.on('input', function () {
    aliasField.val(transformTextForAlias(nameField.val()));
  });

  // Función para transformar el texto para el campo alias
  function transformTextForAlias(text) {
    const accentsMap = {
      'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
      'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'
    };
    return text
      .replace(/[áéíóúÁÉÍÓÚ]/g, match => accentsMap[match])
      .replace(/[^a-zA-Z0-9]/g, '');
  }

  [productField, productVarietyField, marketField, marketStandardProductSizeField].forEach(field => field.select2());
  if (!productField.val()) updateProductVariety();
  if (!marketField.val()) updateMarketStandardProductSize();
  if (!productVarietyField.val()) updateProductVarietySizeHarvestKind();
});
