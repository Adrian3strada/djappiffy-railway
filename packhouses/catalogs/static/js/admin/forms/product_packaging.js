document.addEventListener('DOMContentLoaded', async function () {
  const marketField = $('#id_market');
  const productField = $('#id_product');
  const packagingSupplyKindField = $('#id_packaging_supply_kind');
  const countryStandardPackagingField = $('#id_country_standard_packaging');
  const packagingSupplyField = $('#id_packaging_supply');
  const nameField = $('#id_name');

  let productProperties = null;
  let marketProperties = null;
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
      let paramStandardProductKind = '';
      productProperties ? paramStandardProductKind = `&standard__product_kind=${productProperties.kind}` : paramStandardProductKind = '';
      const productStandardPackagingResponse = await fetchOptions(`/rest/v1/base/product-standard-packaging/?supply_kind=${packagingSupplyKindField.val()}&standard__country__in=${marketProperties.country}${paramStandardProductKind}&is_enabled=1`)
      updateFieldOptions(countryStandardPackagingField, productStandardPackagingResponse, countryStandardPackagingField.val() ? countryStandardPackagingField.val() : null);
      await updateName();
    } else {
      updateFieldOptions(countryStandardPackagingField, []);
      await updateName();
    }
  }

  function updatePackagingSupply() {
    const packagingSupplyKindId = packagingSupplyKindField.val();
    if (packagingSupplyKindId && productStandardPackagingProperties && productStandardPackagingProperties.max_product_amount) {
      fetchOptions(`/rest/v1/catalogs/supply/?kind=${packagingSupplyKindId}&capacity=${productStandardPackagingProperties.max_product_amount}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(packagingSupplyField, data);
          if (packagingSupplyField.val() && data.some(item => item.id === parseInt(packagingSupplyField.val()))) {
            packagingSupplyField.val(packagingSupplyField.val()).trigger('change');
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

  function getProductStandardPackagingFieldProperties() {
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

  packagingSupplyKindField.on('change', async function () {
    await getPackagingSupplyKindProperties();
    await updatePackagingSupply();
    if (marketProperties) {
      await updateProductStandardPackaging();
    } else {
      await getMarketProperties()
      await updateProductStandardPackaging();
    }
  });

  countryStandardPackagingField.on('change', async function () {
    if (listenChanges) {
      await getProductStandardPackagingFieldProperties();
      await updatePackagingSupply();
      await updateName();
    }
  });

  if (marketField.val()) {
    await getMarketProperties()
    await updateProductStandardPackaging();
    await updateName();
  }

  if (countryStandardPackagingField.val()) {
    if (listenChanges) {
      await getProductStandardPackagingFieldProperties();
      await updatePackagingSupply();
    }
  }

  if (isEditing) {
    setTimeout(() => {
      listenChanges = true;
    }, 300)
  } else {
    listenChanges = true;
  }

  [productField, marketField, packagingSupplyKindField, countryStandardPackagingField, packagingSupplyField].forEach(field => field.select2());
});
