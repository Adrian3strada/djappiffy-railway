document.addEventListener('DOMContentLoaded', function () {


  const productField = $('#id_product');
  const productVarietiesField = $('#id_product_varieties');
  const marketsField = $('#id_markets');
  const marketStandardProductSizeField = $('#id_market_standard_product_size');
  const productHarvestSizeKindField = $('#id_product_harvest_size_kind');
  const productSeasonKindField = $('#id_product_season_kind');
  const productMassVolumeKindField = $('#id_product_mass_volume_kind');

  const nameField = $('#id_name');
  const aliasField = $('#id_alias');

  const API_BASE_URL = '/rest/v1';

  function updateFieldOptions(field, options, prefix_field_name) {
    field.empty();
    if (!field.prop('multiple')) {
      field.append(new Option('---------', '', true, true));
    }
    options.forEach(option => {
      const newOption = new Option(option[prefix_field_name] ? option[prefix_field_name] + ': ' + option.name : option.name, option.id, false, false);
      if ('alias' in option && option.alias) {
        newOption.setAttribute('data-alias', option.alias);
      }
      field.append(newOption);
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
          updateFieldOptions(productVarietiesField, data);
        });
    } else {
      updateFieldOptions(productVarietiesField, []);
    }
  }

  function updateMarketStandardProductSize() {
    const marketIds = marketsField.val();
    if (marketIds && marketIds.length > 0) {
      console.log("marketIds", marketIds);
      fetchOptions(`${API_BASE_URL}/catalogs/market_standard_product_size/?markets=${marketIds}&is_enabled=1`)
        .then(data => {
          const marketNames = {};
          marketsField.find('option').each(function () {
            const option = $(this);
            marketNames[option.val()] = option.text();
          });

          data.forEach(item => {
            item.market_name = marketNames[item.market];
          });
          updateFieldOptions(marketStandardProductSizeField, data, 'market_name');
          toggleFieldVisibility(marketStandardProductSizeField, data.length > 0);
        });
    } else {
      updateFieldOptions(marketStandardProductSizeField, []);
      toggleFieldVisibility(marketStandardProductSizeField, false);
    }
  }

  function updateProductHarvestSizeKind() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_harvest_size_kind/?product=${productId}`)
        .then(data => {
          updateFieldOptions(productHarvestSizeKindField, data);
        });
    } else {
      updateFieldOptions(productHarvestSizeKindField, []);
    }
  }

  function updateProductSeasonKind() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_season_kind/?product=${productId}`)
        .then(data => {
          updateFieldOptions(productSeasonKindField, data);
        });
    } else {
      updateFieldOptions(productSeasonKindField, []);
    }
  }

  function updateProductMassVolumeKind() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_mass_volume_kind/?product=${productId}`)
        .then(data => {
          updateFieldOptions(productMassVolumeKindField, data);
        });
    } else {
      updateFieldOptions(productMassVolumeKindField, []);
    }
  }

  function updateNameFromMarketStandardProductSize() {
    const marketStandardProductSize = marketStandardProductSizeField.val();
    if (marketStandardProductSize) {
      fetchOptions(`${API_BASE_URL}/catalogs/market_standard_product_size/${marketStandardProductSize}/`)
        .then(data => {
          nameField.val(data.name);
        })
    }
  }

  function toggleFieldVisibility(field, isVisible) {
    if (isVisible) {
      field.closest('.form-group').fadeIn();
    } else {
      field.closest('.form-group').fadeOut();
    }
  }

  productField.on('change', () => {
    updateProductVariety()
    updateProductHarvestSizeKind();
    updateProductSeasonKind();
    updateProductMassVolumeKind();
  });

  marketsField.on('change', () => {
    updateMarketStandardProductSize();
  });

  nameField.on('input', () => {
    const value = nameField.val();
    const hasLetters = /[a-zA-Z]/.test(value);

    if (hasLetters) {
      const sanitizedValue = value.normalize('NFD').replace(/[\u0300-\u036f]/g, ''); // Remove accents
      const letters = sanitizedValue.match(/[a-zA-Z]/g) || [];
      const firstThreeLetters = letters.slice(0, 3).join('').toUpperCase();
      const numbers = sanitizedValue.match(/[0-9]/g) || [];
      aliasField.val(numbers.join('') + firstThreeLetters);
    } else {
      aliasField.val(value);
    }
  });

  function updateAliasField() {
    const value = nameField.val();
    const isNumeric = /^\d+$/.test(value);

    if (isNumeric) {
      aliasField.val(value);
    } else {
      const sanitizedValue = value.normalize('NFD').replace(/[\u0300-\u036f]/g, ''); // Remove accents
      const firstThreeChars = sanitizedValue.replace(/[^a-zA-Z0-9]/g, '').substring(0, 4).toUpperCase();
      aliasField.val(firstThreeChars);
    }
  }

  nameField.on('input', updateAliasField);

  marketStandardProductSizeField.on('change', function () {
    if (marketStandardProductSizeField.val()) {
      updateNameFromMarketStandardProductSize();
      setTimeout(updateAliasField, 100);
    }
  });

  [productField, productVarietiesField, marketsField, marketStandardProductSizeField, productHarvestSizeKindField, productSeasonKindField, productMassVolumeKindField].forEach(field => field.select2());
  if (!productField.val()) {
    updateProductVariety();
    updateProductHarvestSizeKind();
    updateProductSeasonKind();
    updateProductMassVolumeKind();
    if (!marketStandardProductSizeField.val()) toggleFieldVisibility(marketStandardProductSizeField, true);
  }

  if (!marketsField.val()) updateMarketStandardProductSize();
  if (!marketStandardProductSizeField.val()) marketStandardProductSizeField.closest('.form-group').hide();
});
