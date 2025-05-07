document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const marketField = $('#id_market');
  const packagingSupplyKindField = $('#id_packaging_supply_kind');
  const countryStandardPackagingField = $('#id_country_standard_packaging');
  const packagingSupplyField = $('#id_packaging_supply');
  const nameField = $('#id_name');
  const packagingSupplyQuantityField = $('#id_packaging_supply_quantity');

  let productProperties = null;
  let marketCountries = [];
  let productStandardPackagingProperties = null;
  let packagingSupplyKindProperties = null;
  let listenChanges = false;

  const API_BASE_URL = '/rest/v1';

  function updateFieldOptions(field, options, selectedValue = null) {
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
          console.log("productProperties", productProperties)

          if (data.measure_unit_category_display) {
            const newText = originalText.replace('amount', data.measure_unit_category_display);
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
        let uniqueCountries = new Set();
        let fetchPromises = [];
        fetchPromises.push(
          fetchOptions(`/rest/v1/catalogs/market/${marketField.val()}/`)
            .then(data => {
              data.countries.forEach(country => {
                uniqueCountries.add(country);
              });
            })
        )

        Promise.all(fetchPromises).then(() => {
          marketCountries = Array.from(uniqueCountries);
          resolve(marketCountries);
        }).catch(error => {
          console.error('Fetch error:', error);
          reject(error);
        });
      } else {
        marketCountries = [];
        resolve(marketCountries);
      }
    });
  }

  function getPackagingSupplyKindProperties() {
    return new Promise((resolve, reject) => {
      if (packagingSupplyKindField.val()) {
        fetchOptions(`/rest/v1/base/supply-kind/${packagingSupplyKindField.val()}/`)
          .then(data => {
            packagingSupplyKindProperties = data;
            resolve(data);
          })
          .catch(error => {
            console.error('Fetch error:', error);
            reject(error);
          });
      } else {
        packagingSupplyKindProperties = null;
        resolve(null);
      }
    });
  }

  function updateProductStandardPackaging() {
    const packagingSupplyKindId = packagingSupplyKindField.val();
    if (packagingSupplyKindId && marketCountries.length) {
      const countries = marketCountries.join(',');
      let paramStandardProductKind = ''
      if (productProperties) {
        paramStandardProductKind = `&standard__product_kind=${productProperties.kind}`
      }
      fetchOptions(`${API_BASE_URL}/base/product-standard-packaging/?supply_kind=${packagingSupplyKindId}&standard__country__in=${countries}${paramStandardProductKind}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(countryStandardPackagingField, data);
          updateName();
          if (data.length > 0) {
            countryStandardPackagingField.closest('.form-group').fadeIn();
          } else {
            countryStandardPackagingField.closest('.form-group').fadeOut();
          }
        })
    } else {
      updateFieldOptions(countryStandardPackagingField, []);
      countryStandardPackagingField.closest('.form-group').fadeOut();
      updateName();
    }
  }

  function updatePackagingSupply() {
    const packagingSupplyKindId = packagingSupplyKindField.val();
    if (packagingSupplyKindId && productStandardPackagingProperties && productStandardPackagingProperties.max_product_amount) {
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${packagingSupplyKindId}&capacity=${productStandardPackagingProperties.max_product_amount}&is_enabled=1`)
        .then(data => {
          const packagingSupplyFieldId = packagingSupplyField.val();
          updateFieldOptions(packagingSupplyField, data);
          if (packagingSupplyFieldId && data.some(item => item.id === parseInt(packagingSupplyFieldId))) {
            packagingSupplyField.val(packagingSupplyFieldId).trigger('change');
          }
        });
    } else if (packagingSupplyKindId) {
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${packagingSupplyKindId}&is_enabled=1`)
        .then(data => {
          const packagingSupplyFieldId = packagingSupplyField.val();
          updateFieldOptions(packagingSupplyField, data);
          if (packagingSupplyFieldId && data.some(item => item.id === parseInt(packagingSupplyFieldId))) {
            packagingSupplyField.val(packagingSupplyFieldId).trigger('change');
          }
        });
    } else {
      updateFieldOptions(packagingSupplyField, []);
    }
  }

  function updateName() {
    if (packagingSupplyKindField.val() && countryStandardPackagingField.val()) {
      const packagingSupplyKindName = packagingSupplyKindField.find('option:selected').text();
      const productStandardPackagingName = countryStandardPackagingField.find('option:selected').text();
      const nameString = `${packagingSupplyKindName} ${productStandardPackagingName}`
      nameField.val(nameString)
    } else if (packagingSupplyKindField.val()) {
      const packagingSupplyKindName = packagingSupplyKindField.find('option:selected').text();
      nameField.val(packagingSupplyKindName)
    } else {
      nameField.val('')
    }
  }

  function getproductStandardPackagingFieldProperties() {
    return new Promise((resolve, reject) => {
      if (countryStandardPackagingField.val()) {
        fetchOptions(`/rest/v1/base/product-standard-packaging/${countryStandardPackagingField.val()}/`)
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
    getProductProperties();
  })

  marketField.on('change', () => {
    getMarketCountries().then(() => {
      updateProductStandardPackaging();
    });
  });

  packagingSupplyKindField.on('change', function () {
    getPackagingSupplyKindProperties().then(() => {
      if (packagingSupplyKindField.val() && packagingSupplyKindProperties && packagingSupplyKindProperties.usage_discount_unit_category !== 'pieces') {
        packagingSupplyQuantityField.closest('.form-group').fadeIn();
      } else {
        packagingSupplyQuantityField.val(1);
        packagingSupplyQuantityField.closest('.form-group').fadeOut();
      }
      updatePackagingSupply();
      if (marketCountries.length) {
        updateProductStandardPackaging();
      } else {
        getMarketCountries().then(() => {
          updateProductStandardPackaging();
        });
      }
    });
  });

  countryStandardPackagingField.on('change', function () {
    if (listenChanges) {
      getproductStandardPackagingFieldProperties().then(() => {
        updatePackagingSupply();
        updateName();
      });
    }
  });

  /*
    maxProductAmountPerPackageField.on('change', function () {
      if (maxProductAmountPerPackageField.val() && productStandardPackagingProperties && productStandardPackagingProperties.max_product_amount) {
        const maxProductAmount = parseFloat(productStandardPackagingProperties.max_product_amount);
        const maxProductAmountPerPackage = parseFloat(maxProductAmountPerPackageField.val());
        if (maxProductAmountPerPackage > maxProductAmount) {
          maxProductAmountPerPackageField.val(maxProductAmount);
        }
      }
    });
  */

  if (!countryStandardPackagingField.val()) updateFieldOptions(countryStandardPackagingField, []);

  if (marketField.val()) {
    getMarketCountries().then(() => {
      if (packagingSupplyKindField.val() && marketCountries.length) {
        const productStandardPackagingId = countryStandardPackagingField.val();
        const countries = marketCountries.join(',');
        fetchOptions(`${API_BASE_URL}/base/product-standard-packaging/?supply_kind=${packagingSupplyKindField.val()}&standard__country__in=${countries}&is_enabled=1`)
          .then(data => {
            updateFieldOptions(countryStandardPackagingField, data);
            if (productStandardPackagingId) {
              countryStandardPackagingField.val(productStandardPackagingId).trigger('change');

              fetchOptions(`/rest/v1/base/product-standard-packaging/${productStandardPackagingId}/`)
                .then(data => {
                  productStandardPackagingProperties = data;
                  updatePackagingSupply();
                })
                .catch(error => {
                  console.error('Fetch error:', error);
                });
            }
          })
          .then(() => {
            listenChanges = true;
          });
      } else {
        listenChanges = true;
      }
    });
  }

  if (packagingSupplyKindField.val()) {
    getPackagingSupplyKindProperties().then(() => {
      if (packagingSupplyKindField.val() && packagingSupplyKindProperties && packagingSupplyKindProperties.usage_discount_unit_category !== 'pieces') {
        packagingSupplyQuantityField.closest('.form-group').fadeIn();
      }
    });
  }

  packagingSupplyQuantityField.closest('.form-group').hide();
  countryStandardPackagingField.closest('.form-group').hide();

  if (countryStandardPackagingField.val()) countryStandardPackagingField.closest('.form-group').show();

  [productField, marketField, packagingSupplyKindField, countryStandardPackagingField, packagingSupplyField].forEach(field => field.select2());
});
