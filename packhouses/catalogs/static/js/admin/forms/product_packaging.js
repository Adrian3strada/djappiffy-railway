document.addEventListener('DOMContentLoaded', function () {
  const marketField = $('#id_market');
  const productField = $('#id_product');
  const productSizeField = $('#id_product_size');
  const packagingField = $('#id_packaging');
  const quantityField = $('#id_quantity');
  const nameField = $('#id_name');
  const aliasField = $('#id_alias');

  const maxProductAmountPerPackageField = $('#id_max_product_amount_per_package');
  const packagingSupplyQuantityField = $('#id_packaging_supply_quantity');

  let productProperties = null;
  let marketsCountries = [];
  let productStandardPackagingProperties = null;
  let packagingSupplyKindProperties = null;
  let listenChanges = false;

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

  function getProductProperties() {
    if (productField.val()) {
      fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
        .then(data => {
          productProperties = data;
          let maxProductAmountLabel = maxProductAmountLabel
          const originalText = maxProductAmountLabel.contents().filter(function () {
            return this.nodeType === 3;
          }).text().trim();

          if (data.price_measure_unit_category_display) {
            const newText = originalText.replace('amount', data.price_measure_unit_category_display);
            maxProductAmountLabel.contents().filter(function () {
              return this.nodeType === 3;
            }).first().replaceWith(newText + ' ');
          }
        })
    } else {
      productProperties = null;
    }
  }

  function getMarketCountries() {
    return new Promise((resolve, reject) => {
      if (marketField.val()) {
        let fetchPromises = fetchOptions(`/rest/v1/catalogs/market/${marketField.val()}/`)
        Promise.all(fetchPromises).then(() => {
          marketsCountries = fetchPromises.countries;
          console.log("marketsCountries", marketsCountries);
          resolve(marketsCountries);
        }).catch(error => {
          console.error('Fetch error:', error);
          reject(error);
        });
      } else {
        marketsCountries = [];
        resolve(marketsCountries);
      }
    });
  }

  function updateName() {
    const productName = productField.find('option:selected').text();
    const productSizeName = productSizeField.find('option:selected').text();
    const nameString = `${productName} ${productSizeName}`
    nameField.val(nameString)
  }

  productField.on('change', () => {
    getProductProperties()
  })

  maxProductAmountPerPackageField.attr('step', '0.01');
  maxProductAmountPerPackageField.attr('min', '0.01');
  packagingSupplyQuantityField.closest('.form-group').hide();

  [productField, marketField].forEach(field => field.select2());
});
