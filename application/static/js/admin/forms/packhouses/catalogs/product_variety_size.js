document.addEventListener('DOMContentLoaded', function () {


  const productField = $('#id_product');
  const productVarietyField = $('#id_product_variety');
  const marketField = $('#id_market');
  const marketStandardProductSizeField = $('#id_market_standard_product_size');
  const productHarvestSizeKindField = $('#id_product_harvest_size_kind');
  const nameField = $('#id_name');
  const aliasField = $('#id_alias');

  let shortName = '';
  let shortMarket = '';
  let shortVariety = '';

  const API_BASE_URL = '/rest/v1';

  function updateFieldOptions(field, options) {
    field.empty().append(new Option('---------', '', true, true));
    options.forEach(option => {
      const newOption = new Option(option.name, option.id, false, false);
      if (option.alias) {
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

  function updateNameFromMarketStandardProductSize() {
    const marketStandardProductSize = marketStandardProductSizeField.val();
    if (marketStandardProductSize) {
      fetchOptions(`${API_BASE_URL}/catalogs/market_standard_product_size/${marketStandardProductSize}/`)
        .then(data => {
          nameField.val(data.name);
          shortName = setShortAliasString(data.name);
          if (!!shortName) setAlias();
        })
    }
  }

  function toggleFieldVisibility(field, isVisible) {
    if (isVisible) {
      field.closest('.form-group').show();
    } else {
      field.closest('.form-group').hide();
    }
  }

  productField.on('change', () => {
    updateProductVariety()
    updateProductHarvestSizeKind();
  });

  productVarietyField.on('change', (event) => {
    if (productVarietyField.val()) {
      const selectedOption = event.target.options[event.target.selectedIndex];
      console.log("selectedOption", selectedOption);
      shortVariety = setShortAliasString(selectedOption.getAttribute('data-alias'));
      if (!!shortVariety) setAlias();
    }
  })

  function updateShortName() {
    shortName = setShortAliasString(nameField.val());
    if (!!shortName) setAlias();
  }

  nameField.on('input', () => {
    updateShortName();
  });

  marketField.on('change', (event) => {
    if (marketField.val()) {
      updateMarketStandardProductSize();
      const selectedOption = event.target.options[event.target.selectedIndex];
      console.log("selectedOption", selectedOption);
      shortMarket = setShortAliasString(selectedOption.getAttribute('data-alias'));
      if (!!shortMarket) setAlias();
    }
  });

  marketStandardProductSizeField.on('change', function (evt) {
    if (marketStandardProductSizeField.val()) {
      updateNameFromMarketStandardProductSize();
    }
  });

  function setShortAliasString(input) {
    // Eliminate accents and convert to uppercase
    const normalized = input.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase();

    // Check if the string is a number
    if (!isNaN(normalized)) {
      return normalized;
    }

    // Remove spaces and get the first 3 letters
    return normalized.replace(/\s/g, '').substring(0, 3);
  }

  function setAlias() {
    const alias = shortName + shortMarket + shortVariety;
    aliasField.val(shortName + shortMarket + shortVariety);
  }

  function initializeShortValues() {
    if (nameField.val()) {
      shortName = setShortAliasString(nameField.val());
    }
    if (marketField.val()) {
      const selectedOption = marketField.find('option:selected');
      shortMarket = setShortAliasString(selectedOption.data('alias'));
    }
    if (productVarietyField.val()) {
      const selectedOption = productVarietyField.find('option:selected');
      shortVariety = setShortAliasString(selectedOption.data('alias'));
    }
    setAlias();
  }

  [productField, productVarietyField, marketField, marketStandardProductSizeField].forEach(field => field.select2());
  if (!productField.val()) updateProductVariety();
  if (!marketField.val()) updateMarketStandardProductSize();
  if (!productVarietyField.val()) updateProductHarvestSizeKind();
  if (!marketStandardProductSizeField.val()) toggleFieldVisibility(marketStandardProductSizeField, false);
  initializeShortValues();
});
