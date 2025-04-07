document.addEventListener('DOMContentLoaded', async function () {
  const categoryField = $('#id_category');
  const marketField = $('#id_market');
  const productField = $('#id_product');
  const productSizeField = $('#id_product_size');
  const packagingField = $('#id_packaging');
  const productWeightPerPackagingField = $('#id_product_weight_per_packaging');
  const productPresentationField = $('#id_product_presentation');
  const productPiecesPerPresentationField = $('#id_product_pieces_per_presentation');
  const productPresentationsPerPackagingField = $('#id_product_presentations_per_packaging');
  const nameField = $('#id_name');
  const aliasField = $('#id_alias');

  let productProperties = null;
  let packagingProperties = null;
  let packagingSupplyProperties = null;
  let productPresentationProperties = null;
  let productPresentationSupplyProperties = null;

  let category = categoryField.val();
  let market = marketField.val();
  let product = productField.val();
  let productSize = productSizeField.val();
  let packaging = packagingField.val();
  let productPresentation = productPresentationField.val();

  productWeightPerPackagingField.attr('step', '0.01');
  productWeightPerPackagingField.attr('min', '0.01');
  productPresentationsPerPackagingField.attr('step', 1);
  productPresentationsPerPackagingField.attr('min', 1);
  productPiecesPerPresentationField.attr('step', 1);
  productPiecesPerPresentationField.attr('min', 1);

  marketField.closest('.form-group').hide();
  productField.closest('.form-group').hide();
  productSizeField.closest('.form-group').hide();
  packagingField.closest('.form-group').hide();

  productPresentationField.closest('.form-group').hide();
  productPresentationsPerPackagingField.closest('.form-group').hide();
  productPiecesPerPresentationField.closest('.form-group').hide();

  if (market) marketField.closest('.form-group').show();
  if (product) productField.closest('.form-group').show();
  if (productSize) productSizeField.closest('.form-group').show();
  if (packaging) packagingField.closest('.form-group').show();
  if (productPresentation) productPresentationField.closest('.form-group').show();

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

  function getProductProperties() {
    if (productField.val()) {
      fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
        .then(product_data => {
          productProperties = product_data;
        })
    } else {
      productProperties = null;
    }
  }

  async function getPackagingProperties() {
    console.log("packagingField.val()", packagingField.val())
    if (packagingField.val()) {
      packagingProperties = await fetchOptions(`/rest/v1/catalogs/packaging/${packagingField.val()}/`)
    } else {
      packagingProperties = null;
    }
  }

  async function getPackagingSupplyProperties() {
    if (!packagingProperties) await getPackagingProperties();
    if (packagingProperties) {
      packagingSupplyProperties = await fetchOptions(`/rest/v1/catalogs/supply/${packagingProperties.packaging_supply}/`)
    } else {
      packagingSupplyProperties = null;
    }
  }

  function getProductPresentationProperties() {
    if (productPresentationField.val()) {
      fetchOptions(`/rest/v1/catalogs/product-presentation/${productPresentationField.val()}/`)
        .then(productpresentation_data => {
          productPresentationProperties = productpresentation_data;
          fetchOptions(`/rest/v1/catalogs/supply/${productpresentation_data.presentation_supply}/`)
            .then(productpresentationsupply_data => {
              productPresentationSupplyProperties = productpresentationsupply_data;
            });
        })
    } else {
      productPresentationProperties = null;
      productPresentationSupplyProperties = null;
    }
  }

  function updateName() {
    const packagingName = packagingField.val() ? packagingField.find('option:selected').text() : '';
    const productSizeName = productSizeField.val() ? productSizeField.find('option:selected').text() : '';

    const productWeight = productWeightPerPackagingField.val() ? ' W:' + productWeightPerPackagingField.val() : '';

    let nameString = `${packagingName} ${productSizeName}${productWeight}`

    if (categoryField.val() === 'presentation' && productPresentationField.val()) {
      let productPresentationPerPackaging = ' ';
      if (productPresentationsPerPackagingField.val()) {
        productPresentationPerPackaging = ` ${productPresentationsPerPackagingField.val()} `;
      }
      const productPresentationName = productPresentationField.find('option:selected').text();
      nameString = `${nameString}${productPresentationPerPackaging}${productPresentationName}${productWeight}`;
    }
    nameField.val(nameString.trim())
  }

  function updateProduct() {
    if (marketField.val()) {
      fetchOptions(`/rest/v1/catalogs/product/?markets=${marketField.val()}&is_enabled=1`)
        .then(data => {
          console.log("updateProduct", data);
          updateFieldOptions(productField, data, product ? product : null);
          productField.closest('.form-group').fadeIn();
        })
    } else {
      updateFieldOptions(productField, []);
    }
  }

  function updateProductSize() {
    if (categoryField.val() && productField.val() && marketField.val()) {
      let categories = 'size,mix'
      if (categoryField.val() === 'presentation') {
        categories = 'size'
      }
      fetchOptions(`/rest/v1/catalogs/product-size/?product=${productField.val()}&market=${marketField.val()}&categories=${categories}&is_enabled=1`)
        .then(data => {
          console.log("updateProductSize", data);
          updateFieldOptions(productSizeField, data, productSize ? productSize : null);
          productSizeField.closest('.form-group').fadeIn();
        })
    } else {
      updateFieldOptions(productSizeField, []);
    }
  }

  function updatePackaging() {
    if (productField.val() && marketField.val()) {
      fetchOptions(`/rest/v1/catalogs/packaging/?product=${productField.val()}&markets=${marketField.val()}&is_enabled=1`)
        .then(data => {
          console.log("updatePackaging", data);
          updateFieldOptions(packagingField, data, packaging ? packaging : null);
          packagingField.closest('.form-group').fadeIn();
        })
    } else {
      updateFieldOptions(packagingField, []);
    }
  }

  async function updateProductPackagingProductWeight() {
    if (packagingField.val()) {
      if (!packagingProperties) await getPackagingProperties();
      if (!packagingSupplyProperties) await getPackagingSupplyProperties();
      console.log("packagingProperties", packagingProperties)
      productWeightPerPackagingField.val(packagingSupplyProperties.capacity);
      productWeightPerPackagingField.attr('max', Math.floor(packagingSupplyProperties.capacity + 1));
    } else {
      productWeightPerPackagingField.val(null);
      productWeightPerPackagingField.removeAttr('max');
    }
  }

  function updateProductPresentationQuantities() {
    if (productPresentationField.val()) {
      fetchOptions(`/rest/v1/catalogs/product-presentation/${productPresentationField.val()}/`)
        .then(productpresentation_data => {
          productPresentationProperties = productpresentation_data;
          console.log("productPresentationField data", productpresentation_data);
          productPiecesPerPresentationField.val(productPresentationProperties)
          fetchOptions(`/rest/v1/catalogs/supply/${productpresentation_data.presentation_supply}/`)
            .then(supply_data => {
              productPresentationSupplyProperties = supply_data;
              console.log("supply_data", supply_data);
            });
        });
    }
  }

  function updateProductPresentation() {
    if (productField.val() && marketField.val()) {
      fetchOptions(`/rest/v1/catalogs/product-presentation/?product=${productField.val()}&markets=${marketField.val()}`)
        .then(data => {
          console.log("updateProductPresentation", data);
          updateFieldOptions(productPresentationField, data);
        })
    } else {
      updateFieldOptions(productPresentationField, []);
    }
  }


  categoryField.on('change', async () => {
    category = categoryField.val();
    if (categoryField.val()) {
      await updateProductSize();
      marketField.closest('.form-group').fadeIn();
    } else {
      marketField.closest('.form-group').fadeOut();
    }
  });

  marketField.on('change', async () => {
    market = marketField.val();
    await updateProduct();
  });

  productField.on('change', async () => {
    product = productField.val();
    await getProductProperties();
    await updateProductSize();
    await updatePackaging();
    if (categoryField.val() === 'presentation') {
      await updateProductPresentation();
    }
  })

  productSizeField.on('change', () => {
    productSize = productSizeField.val();
    updateName();
  })

  packagingField.on('change', async () => {
    packaging = packagingField.val();
    await getPackagingProperties();
    await getPackagingSupplyProperties();
    await updateProductPackagingProductWeight();
  })

  productPresentationField.on('change', () => {
    // updateName();

    // TODO: actualizar pieza por presentación
  })

  productWeightPerPackagingField.on('change', () => {
    if (productWeightPerPackagingField.val()) {
      if (packagingSupplyProperties) {
        const maxProductAmount = Math.floor(packagingSupplyProperties.capacity + 1)
        if (parseFloat(productWeightPerPackagingField.val()) > maxProductAmount) {
          productWeightPerPackagingField.val(maxProductAmount);
        }
      }
    }
    updateName();
  });

  productPresentationsPerPackagingField.on('change', () => {
    let value = productPresentationsPerPackagingField.val();
    console.log(value);
    if (!isNaN(value)) {
      productPresentationsPerPackagingField.val('');
    }
    if (value && categoryField.val() === 'presentation') {
      value = value.replace(/[^\d.]/g, '');
      const quantity = Math.floor(parseFloat(value));
      if (!isNaN(quantity)) {
        productPresentationsPerPackagingField.val(quantity);
      }
    }
    updateName();
  });


  if (categoryField.val()) {
    marketField.closest('.form-group').show();
  }

  if (marketField.val()) {

    await updateProduct();

  }

  if (packagingField.val()) {
    fetchOptions(`/rest/v1/catalogs/packaging/${packagingField.val()}/`)
      .then(packaging_data => {
        packagingProperties = packaging_data;
        fetchOptions(`/rest/v1/catalogs/supply/${packaging_data.packaging_supply}/`)
          .then(supply_data => {
            packagingSupplyProperties = supply_data;
          })
      })
  }

  [categoryField, productField, marketField, productSizeField, packagingField, productPresentationField].forEach(field => field.select2());
});
