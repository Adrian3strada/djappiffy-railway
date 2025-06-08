document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const marketField = $('#id_market');
  const packagingSupplyKindField = $('#id_packaging_supply_kind');
  const countryStandardPackagingField = $('#id_country_standard_packaging');
  const packagingSupplyField = $('#id_packaging_supply');
  const nameField = $('#id_name');
  const packagingSupplyQuantityField = $('#id_packaging_supply_quantity');

  let productProperties = null;
  let marketProperties = null;
  let marketCountries = [];
  let productStandardPackagingProperties = null;
  let packagingSupplyKindProperties = null;
  let listenChanges = false;

  const isEditing = window.location.pathname.match(/\/change\//) !== null;


  function updateFieldOptions(field, options, selectedValue = null) {
    field.empty().append(new Option('---------', '', !selectedValue, !selectedValue));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, parseInt(selectedValue) === option.id));
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

  async function getMarketProperties() {
    if (marketField.val()) {
      marketProperties = await fetchOptions(`/rest/v1/catalogs/market/${marketField.val()}/`)
      const marketProducts = await fetchOptions(`/rest/v1/catalogs/product/?markets=${marketField.val()}&is_enabled=1`);
      updateFieldOptions(productField, marketProducts, productField.val());
    } else {
      marketProperties = null;
      updateFieldOptions(productField, []);
    }
  }

  function getProductProperties() {
    if (productField.val()) {
      fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
        .then(data => {
          productProperties = data;
          console.log("productProperties", productProperties)
        })
    } else {
      productProperties = null;
    }
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

  async function updateProductStandardPackaging() {
    if (packagingSupplyKindField.val() && marketProperties) {
      let paramStandardProductKind = ''
      if (productProperties) {
        paramStandardProductKind = `&standard__product_kind=${productProperties.kind}`
      }
      fetchOptions(`/rest/v1/base/product-standard-packaging/?supply_kind=${packagingSupplyKindField.val()}&standard__country__in=${marketProperties.country}${paramStandardProductKind}&is_enabled=1`)
        .then(async data => {
          updateFieldOptions(countryStandardPackagingField, data);
          await updateName();
          if (data.length > 0) {
            countryStandardPackagingField.closest('.form-group').fadeIn();
          } else {
            countryStandardPackagingField.closest('.form-group').fadeOut();
          }
        })
    } else {
      updateFieldOptions(countryStandardPackagingField, []);
      countryStandardPackagingField.closest('.form-group').fadeOut();
      await updateName();
    }
  }

  function updatePackagingSupply() {
    const packagingSupplyKindId = packagingSupplyKindField.val();
    if (packagingSupplyKindId && productStandardPackagingProperties && productStandardPackagingProperties.max_product_amount) {
      fetchOptions(`/rest/v1/catalogs/supply/?kind=${packagingSupplyKindId}&capacity=${productStandardPackagingProperties.max_product_amount}&is_enabled=1`)
        .then(data => {
          const packagingSupplyFieldId = packagingSupplyField.val();
          updateFieldOptions(packagingSupplyField, data);
          if (packagingSupplyFieldId && data.some(item => item.id === parseInt(packagingSupplyFieldId))) {
            packagingSupplyField.val(packagingSupplyFieldId).trigger('change');
          }
        });
    } else if (packagingSupplyKindId) {
      fetchOptions(`/rest/v1/catalogs/supply/?kind=${packagingSupplyKindId}&is_enabled=1`)
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

  async function updateName() {
    if (listenChanges) {
      if (packagingSupplyKindField.val() && countryStandardPackagingField.val()) {
        const productName = productField.find('option:selected').text();
        const marketName = marketField.find('option:selected').text();
        const packagingSupplyKindName = packagingSupplyKindField.find('option:selected').text();
        const productStandardPackagingName = countryStandardPackagingField.find('option:selected').text();
        let productAndMarket = ''
        if (productName && marketName) {
          productAndMarket = ` - (${productName}:${marketName})`;
        }
        let supplyName = ''
        if (packagingSupplyField.val()) {
          const packagingSupplyName = packagingSupplyField.find('option:selected').text();
          supplyName = ` - [${packagingSupplyName}]`;
        }
        const nameString = `${packagingSupplyKindName} ${productStandardPackagingName}${supplyName}${productAndMarket}`
        nameField.val(nameString)
      } else if (packagingSupplyKindField.val()) {
        const packagingSupplyKindName = packagingSupplyKindField.find('option:selected').text();
        nameField.val(packagingSupplyKindName)
      } else {
        nameField.val(null)
      }
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

  marketField.on('change', async () => {
    await getMarketProperties()
    await updateProductStandardPackaging();
    await updateName();
  });

  productField.on('change', async () => {
    getProductProperties();
    await updateName();
  })


  packagingSupplyField.on('change', async () => {
    if (packagingSupplyField.val()) {
      await updateName();
    }
  });

  packagingSupplyKindField.on('change', function () {
    getPackagingSupplyKindProperties().then(async () => {
      if (packagingSupplyKindField.val() && packagingSupplyKindProperties && packagingSupplyKindProperties.usage_discount_unit_category !== 'pieces') {
        packagingSupplyQuantityField.closest('.form-group').fadeIn();
      } else {
        packagingSupplyQuantityField.val(1);
        packagingSupplyQuantityField.closest('.form-group').fadeOut();
      }
      updatePackagingSupply();
      if (marketProperties) {
        await updateProductStandardPackaging();
      } else {
        await getMarketProperties()
        await updateProductStandardPackaging();
      }
    });
  });

  countryStandardPackagingField.on('change', function () {
    if (listenChanges) {
      getproductStandardPackagingFieldProperties().then(async () => {
        updatePackagingSupply();
        await updateName();
      });
    }
  });

  if (!countryStandardPackagingField.val()) updateFieldOptions(countryStandardPackagingField, []);

  if (marketField.val()) {
    getMarketProperties().then(() => {
      if (packagingSupplyKindField.val() && marketProperties) {
        fetchOptions(`/rest/v1/base/product-standard-packaging/?supply_kind=${packagingSupplyKindField.val()}&standard__country__in=${marketProperties.country}&is_enabled=1`)
          .then(data => {
            updateFieldOptions(countryStandardPackagingField, data);
            if (countryStandardPackagingField.val()) {
              countryStandardPackagingField.val(countryStandardPackagingField.val()).trigger('change');

              fetchOptions(`/rest/v1/base/product-standard-packaging/${countryStandardPackagingField.val()}/`)
                .then(data => {
                  productStandardPackagingProperties = data;
                  updatePackagingSupply();
                })
                .catch(error => {
                  console.error('Fetch error:', error);
                });
            }
          })
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

  if (isEditing) {
    setTimeout(() => {
      listenChanges = true;
    }, 300)
  } else {
    listenChanges = true;
  }

  [productField, marketField, packagingSupplyKindField, countryStandardPackagingField, packagingSupplyField].forEach(field => field.select2());
});
