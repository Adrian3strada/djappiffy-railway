document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const varietiesField = $('#id_varieties');
  const marketsField = $('#id_markets');
  const MarketProductSizeStandardSizeField = $('#id_market_product_size_standard_size');
  const productHarvestSizeKindField = $('#id_product_harvest_size_kind');
  const productQualityKindField = $('#id_product_quality_kind');
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
          updateFieldOptions(varietiesField, data);
        });
    } else {
      updateFieldOptions(varietiesField, []);
    }
  }

  function updateMarketProductSizeStandardSize() {
    const marketIds = marketsField.val();
    if (marketIds && marketIds.length > 0) {
      fetchOptions(`${API_BASE_URL}/base/market_product_size_standard_size/?market=${marketIds}&is_enabled=1`)
        .then(data => {
          const marketNames = {};
          marketsField.find('option').each(function () {
            const option = $(this);
            marketNames[option.val()] = option.text();
          });

          data.forEach(item => {
            item.market_name = marketNames[item.market];
          });
          updateFieldOptions(MarketProductSizeStandardSizeField, data, 'market_name');
          toggleFieldVisibility(MarketProductSizeStandardSizeField, data.length > 0);
        });
    } else {
      updateFieldOptions(MarketProductSizeStandardSizeField, []);
      toggleFieldVisibility(MarketProductSizeStandardSizeField, false);
    }
  }


  function updateNameFromMarketStandardProductSize() {
    const marketStandardProductSize = MarketProductSizeStandardSizeField.val();
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

  nameField.on('input', () => {
    const value = nameField.val();
    const isNumeric = /^\d+$/.test(value);

    if (isNumeric) {
      aliasField.val(value);
    } else {
      const sanitizedValue = value.normalize('NFD').replace(/[\u0300-\u036f]/g, ''); // Remove accents
      const firstThreeChars = sanitizedValue.replace(/[^a-zA-Z0-9]/g, '').substring(0, 3).toUpperCase();
      aliasField.val(firstThreeChars);
    }
  });

  MarketProductSizeStandardSizeField.on('change', function () {
    if (MarketProductSizeStandardSizeField.val()) {
      updateNameFromMarketStandardProductSize();
    }
  });

  [productField, varietiesField, marketsField, MarketProductSizeStandardSizeField, productHarvestSizeKindField, productQualityKindField, productMassVolumeKindField].forEach(field => field.select2());
  if (!productField.val()) {
    updateProductVariety();
    if (!MarketProductSizeStandardSizeField.val()) toggleFieldVisibility(MarketProductSizeStandardSizeField, true);
  }

  if (!marketsField.val()) updateMarketProductSizeStandardSize();
  if (!MarketProductSizeStandardSizeField.val()) toggleFieldVisibility(MarketProductSizeStandardSizeField, true);
});
