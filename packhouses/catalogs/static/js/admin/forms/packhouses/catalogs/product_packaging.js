document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const marketsField = $('#id_markets');
  const packagingSupplyKindField = $('#id_packaging_supply_kind');
  const productStandardPackagingField = $('#id_product_standard_packaging');
  const packagingSupplyField = $('#id_packaging_supply');
  const nameField = $('#id_name');
  const maxProductAmountPerPackageField = $('#id_max_product_amount_per_package');

  let productProperties = null;
  let marketsCountries = [];
  let productStandardPackagingProperties = null;

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

  function getProductProperties() {
    if (productField.val()) {
      fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
        .then(data => {
          productProperties = data;
          const maxProductAmountLabel = $('label[for="id_max_product_amount_per_package"]');
          if (data.price_measure_unit_category_display) {
            maxProductAmountLabel.text(`Max product ${data.price_measure_unit_category_display} per package`);
          } else {
            maxProductAmountLabel.text(`Max product amount per package`);
          }
        })
    } else {
      productProperties = null;
    }
  }

  function getMarketsCountries() {
    return new Promise((resolve, reject) => {
      if (marketsField.val()) {
        let uniqueCountries = new Set();
        let fetchPromises = marketsField.val().map(marketId => {
          return fetchOptions(`/rest/v1/catalogs/market/${marketId}/`)
            .then(data => {
              data.countries.forEach(country => {
                uniqueCountries.add(country);
              });
            });
        });

        Promise.all(fetchPromises).then(() => {
          marketsCountries = Array.from(uniqueCountries);
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

  function updateProductStandardPackaging() {
    const packagingSupplyKindId = packagingSupplyKindField.val();
    if (packagingSupplyKindId && marketsCountries.length) {
      const countries = marketsCountries.join(',');
      fetchOptions(`${API_BASE_URL}/base/product-standard-packaging/?supply_kind=${packagingSupplyKindId}&standard__country__in=${countries}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(productStandardPackagingField, data);
          updateName();
        })
    } else {
      updateFieldOptions(productStandardPackagingField, []);
      updateName();
    }
  }

  function updatePackagingSupply() {
    const packagingSupplyKindId = packagingSupplyKindField.val();
    if (packagingSupplyKindId && productStandardPackagingProperties && productStandardPackagingProperties.max_product_amount) {
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${packagingSupplyKindId}&size=${productStandardPackagingProperties.max_product_amount}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(packagingSupplyField, data);
        });
    } else if (packagingSupplyKindId) {
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${packagingSupplyKindId}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(packagingSupplyField, data);
        });
    } else {
      updateFieldOptions(packagingSupplyField, []);
    }
  }

  function updateName() {
    if (packagingSupplyKindField.val() && productStandardPackagingField.val()) {
      const packagingSupplyKindName = packagingSupplyKindField.find('option:selected').text();
      const productStandardPackagingName = productStandardPackagingField.find('option:selected').text();
      const nameString = `${packagingSupplyKindName} ${productStandardPackagingName}`
      nameField.val(nameString)
    } else {
      nameField.val('')
    }
    if (productStandardPackagingProperties) {
      maxProductAmountPerPackageField.val(productStandardPackagingProperties.max_product_amount);
      maxProductAmountPerPackageField.attr('max', productStandardPackagingProperties.max_product_amount);
      maxProductAmountPerPackageField.attr('min', 0.01);
      maxProductAmountPerPackageField.attr('step', 0.01);

    } else {
      maxProductAmountPerPackageField.val('');
      maxProductAmountPerPackageField.removeAttr('max');
      maxProductAmountPerPackageField.attr('min', 0.01);
      maxProductAmountPerPackageField.attr('step', 0.01);
    }
  }

  function getproductStandardPackagingFieldProperties() {
    return new Promise((resolve, reject) => {
      if (productStandardPackagingField.val()) {
        fetchOptions(`/rest/v1/base/product-standard-packaging/${productStandardPackagingField.val()}/`)
          .then(data => {
            productStandardPackagingProperties = data;
            resolve(data);
          })
          .catch(error => {
            console.error('Fetch error:', error);
            reject(error);
          });
      } else {
        productStandardPackagingProperties = null;
        resolve(null);
      }
    });
  }

  productField.on('change', () => {
    getProductProperties()
  })

  marketsField.on('change', () => {
    getMarketsCountries().then(() => {
      updateProductStandardPackaging();
    });
  });

  packagingSupplyKindField.on('change', function () {
    updatePackagingSupply();
    if (marketsCountries.length) {
      updateProductStandardPackaging();
    } else {
      getMarketsCountries().then(() => {
        updateProductStandardPackaging();
      });
    }
  });

  productStandardPackagingField.on('change', function () {
    if (productStandardPackagingField.val()) {
      getproductStandardPackagingFieldProperties().then(() => {
        updatePackagingSupply();
        updateName();
      });
    }
  });

  [productField, marketsField, packagingSupplyKindField, productStandardPackagingField, packagingSupplyField].forEach(field => field.select2());
  updateFieldOptions(productStandardPackagingField, []);
});
