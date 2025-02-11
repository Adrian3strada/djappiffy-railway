document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const varietiesField = $('#id_varieties');
  const marketField = $('#id_market');
  const standardSizeField = $('#id_standard_size');
  const nameField = $('#id_name');
  const aliasField = $('#id_alias');

  let productProductKind = 0
  let marketCountries = ''

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

  function getProductKind(productId) {
    if (productId) {
      return fetchOptions(`${API_BASE_URL}/catalogs/product/${productId}/`)
        .then(data => {
          console.log("product", data);
          productProductKind = data.kind ? data.kind : null;
          console.log("productProductKind", productProductKind);
        });
    } else {
      productProductKind = null;
      return Promise.resolve();
    }
  }

  function getMarketCountries(marketId) {
    if (marketId) {
      return fetchOptions(`${API_BASE_URL}/catalogs/market/${marketId}/`)
        .then(data => {
          console.log("market", data)
          data.countries ? marketCountries = data.countries.join(',') : marketCountries = null
          console.log("marketCountries", marketCountries)
        });
    } else {
      marketCountries = ''
      return Promise.resolve();
    }
  }

  function updateProductVariety() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product-variety/?product=${productId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(varietiesField, data);
        });
    } else {
      updateFieldOptions(varietiesField, []);
    }
  }

  function updateMarketProductSizeStandardSize() {
    const productId = productField.val();
    const marketId = marketField.val();
    if (productId && marketId) {
      console.log("marketCountries", marketCountries)
      console.log("productId", productId)
      console.log("marketId", marketId)
      fetchOptions(`${API_BASE_URL}/base/country-product-standard-size/?countries=${marketCountries}&product_kind=${productProductKind}&is_enabled=1`)
        .then(data => {
          const marketNames = {};
          marketField.find('option').each(function () {
            const option = $(this);
            marketNames[option.val()] = option.text();
          });
          data.forEach(item => {
            item.market_name = marketNames[item.market];
          });
          updateFieldOptions(standardSizeField, data, 'market_name');
          toggleFieldVisibility(standardSizeField, data.length > 0);
        });
    } else {
      updateFieldOptions(standardSizeField, []);
      toggleFieldVisibility(standardSizeField, false);
    }
  }

  function updateNameFromMarketStandardProductSize() {
    const standardSize = standardSizeField.val();
    if (standardSize) {
      fetchOptions(`${API_BASE_URL}/base/country-product-standard-size/${standardSize}/`)
        .then(data => {
          nameField.val(data.name);
          setAliasName();
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
    getProductKind(productField.val()).then(() => {
      if (productField.val()) {
        updateProductVariety();
        if (productField.val()) {
          updateMarketProductSizeStandardSize();
        } else {
          updateFieldOptions(varietiesField, []);
          toggleFieldVisibility(standardSizeField, false);
        }
      } else {
        updateFieldOptions(varietiesField, []);
        toggleFieldVisibility(standardSizeField, false);
      }
    });
  });

  marketField.on('change', () => {
    if (marketField.val() && productField.val()) {
      getMarketCountries(marketField.val()).then(() => {
        updateMarketProductSizeStandardSize();
      });
    } else {
      updateFieldOptions(standardSizeField, []);
      toggleFieldVisibility(standardSizeField, false);
    }
  });

  function setAliasName() {
    const value = nameField.val();
    const isNumeric = /^\d+$/.test(value);
    if (isNumeric) {
      aliasField.val(value);
    } else {
      const sanitizedValue = value.normalize('NFD').replace(/[\u0300-\u036f]/g, ''); // Remove accents
      const firstThreeChars = sanitizedValue.replace(/[^a-zA-Z0-9]/g, '').substring(0, 3).toUpperCase();
      aliasField.val(firstThreeChars);
    }
  }

  nameField.on('input', () => {
    setAliasName();
  });

  standardSizeField.on('change', function () {
    if (standardSizeField.val()) {
      updateNameFromMarketStandardProductSize();
    }
  });

  [productField, varietiesField, marketField, standardSizeField].forEach(field => field.select2());
  if (!productField.val()) {
    updateProductVariety();
    if (!standardSizeField.val()) toggleFieldVisibility(standardSizeField, true);
  }

  if (!marketField.val()) updateMarketProductSizeStandardSize();

  if (productField.val()) getProductKind(productField.val());
  if (marketField.val()) getMarketCountries(marketField.val());
  if (!standardSizeField.val()) standardSizeField.closest('.form-group').hide();
});
