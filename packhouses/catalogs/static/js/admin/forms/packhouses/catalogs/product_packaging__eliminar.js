document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const marketsField = $('#id_markets');
  const packagingSupplyKindField = $('#id_packaging_supply_kind');
  const productStandardPackagingField = $('#id_product_standard_packaging');
  const packagingSupplyField = $('#id_packaging_supply');
  const nameField = $('#id_name');
  const maxProductAmountPerPackageField = $('#id_max_product_amount_per_package');

  const maxProductAmountLabel = $('label[for="id_max_product_amount_per_package"]');

  let productProperties = null;
  let marketsCountries = [];
  let productStandardPackagingProperties = null;
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
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${packagingSupplyKindId}&capacity=${productStandardPackagingProperties.max_product_amount}&is_enabled=1`)
        .then(data => {
          const packagingSupplyFieldId = packagingSupplyField.val();
          updateFieldOptions(packagingSupplyField, data);
          console.log("data", data);
          console.log("packagingSupplyFieldId", packagingSupplyFieldId);
          console.log("packagingSupplyFieldId", parseInt(packagingSupplyFieldId));
          console.log("data.some(item => item.id === 3)", data.some(item => item.id === parseInt(packagingSupplyFieldId)));

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
    if (packagingSupplyKindField.val() && productStandardPackagingField.val()) {
      const packagingSupplyKindName = packagingSupplyKindField.find('option:selected').text();
      const productStandardPackagingName = productStandardPackagingField.find('option:selected').text();
      const nameString = `${packagingSupplyKindName} ${productStandardPackagingName}`
      nameField.val(nameString)
    } else {
      nameField.val('')
    }
    if (productStandardPackagingProperties && productStandardPackagingProperties.max_product_amount) {
      maxProductAmountPerPackageField.val(productStandardPackagingProperties.max_product_amount);
      maxProductAmountPerPackageField.attr('max', productStandardPackagingProperties.max_product_amount);
    } else {
      maxProductAmountPerPackageField.val('');
      maxProductAmountPerPackageField.removeAttr('max');
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
      if (listenChanges) {
        getproductStandardPackagingFieldProperties().then(() => {
          updatePackagingSupply();
          updateName();
        });
      }
    }
  });

  if (!productStandardPackagingField.val()) updateFieldOptions(productStandardPackagingField, []);

  if (marketsField.val()) {
    getMarketsCountries().then(() => {
      if (packagingSupplyKindField.val() && marketsCountries.length) {
        const productStandardPackagingId = productStandardPackagingField.val();
        const countries = marketsCountries.join(',');
        fetchOptions(`${API_BASE_URL}/base/product-standard-packaging/?supply_kind=${packagingSupplyKindField.val()}&standard__country__in=${countries}&is_enabled=1`)
          .then(data => {
            updateFieldOptions(productStandardPackagingField, data);
            if (productStandardPackagingId) {
              productStandardPackagingField.val(productStandardPackagingId).trigger('change');

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

  if (productStandardPackagingField.val()) {
    getproductStandardPackagingFieldProperties().then(() => {
      console.log("productStandardPackagingProperties", productStandardPackagingProperties);
      if (productStandardPackagingProperties && productStandardPackagingProperties.max_product_amount) {
        maxProductAmountPerPackageField.val(productStandardPackagingProperties.max_product_amount);
        maxProductAmountPerPackageField.attr('max', productStandardPackagingProperties.max_product_amount);
      } else {
        maxProductAmountPerPackageField.val('');
        maxProductAmountPerPackageField.removeAttr('max');
      }
    });
  }

  maxProductAmountPerPackageField.attr('step', '0.01');

  [productField, marketsField, packagingSupplyKindField, productStandardPackagingField, packagingSupplyField].forEach(field => field.select2());
});
