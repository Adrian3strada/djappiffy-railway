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

  let packagingProperties = null;
  let packagingSupplyProperties = null;
  let productPresentationProperties = null;
  let productPresentationSupplyProperties = null;

  let category = categoryField.val();
  let productSize = productSizeField.val();
  let packaging = packagingField.val();
  let productWeightPerPackaging = productWeightPerPackagingField.val();
  let productPresentation = productPresentationField.val();
  let productPiecesPerPresentation = productPiecesPerPresentationField.val();
  let productPresentationsPerPackaging = productPresentationsPerPackagingField.val();

  productWeightPerPackagingField.attr('step', '0.01');
  productWeightPerPackagingField.attr('min', '0.01');
  productPresentationsPerPackagingField.attr('step', 1);
  productPresentationsPerPackagingField.attr('min', 1);
  productPiecesPerPresentationField.attr('step', 1);
  productPiecesPerPresentationField.attr('min', 1);

  productWeightPerPackagingField.closest('.form-group').hide();

  productPresentationField.closest('.form-group').hide();
  productPresentationsPerPackagingField.closest('.form-group').hide();
  productPiecesPerPresentationField.closest('.form-group').hide();

  if (productWeightPerPackaging) productWeightPerPackagingField.closest('.form-group').show();
  if (productPresentation) productPresentationField.closest('.form-group').show();
  if (productPresentationsPerPackaging) productPresentationsPerPackagingField.closest('.form-group').show();
  if (productPiecesPerPresentation) productPiecesPerPresentationField.closest('.form-group').show();

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

  async function getPackagingProperties() {
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

  async function getProductPresentationProperties() {
    if (productPresentationField.val()) {
      productPresentationProperties = await fetchOptions(`/rest/v1/catalogs/product-presentation/${productPresentationField.val()}/`)
    } else {
      productPresentationProperties = null;
    }
  }

  async function getProductPresentationSupplyProperties() {
    if (productPresentationField.val()) {
      await getProductPresentationProperties();
      productPresentationSupplyProperties = await fetchOptions(`/rest/v1/catalogs/supply/${productPresentationProperties.presentation_supply}/`)
    } else {
      productPresentationSupplyProperties = null;
    }
  }

  function updateName() {

    if (categoryField.val() === 'single') {

      if (packagingField.val() && productSizeField.val() && productWeightPerPackagingField.val()) {
        const packagingName = packagingField.val() ? packagingField.find('option:selected').text() + ' ' : '';
        const productSizeName = productSizeField.val() ? productSizeField.find('option:selected').text() + ' - ' : '';
        const productWeight = productWeightPerPackagingField.val() ? 'W:' + productWeightPerPackagingField.val() : '';
        let nameString = `${packagingName}${productSizeName}${productWeight}`
        nameField.val(nameString.trim())
      }
    } else if (categoryField.val() === 'presentation') {
      if (packagingField.val() && productSizeField.val() && productWeightPerPackagingField.val() && productPresentationField.val() && productPiecesPerPresentationField.val() && productPresentationsPerPackagingField.val()) {
        const packagingName = packagingField.val() ? packagingField.find('option:selected').text() + ' - ' : '';
        const productSizeName = productSizeField.val() ? productSizeField.find('option:selected').text() + ' - ' : '';
        const productWeight = productWeightPerPackagingField.val() ? 'W:' + productWeightPerPackagingField.val() : '';
        const productPresentationName = productPresentationField.val() ? productPresentationField.find('option:selected').text() + ' - ' : '';
        const productPiecesPerPresentation = productPiecesPerPresentationField.val() ? 'P:' + productPiecesPerPresentationField.val() + ', ' : '';
        const productPresentationPerPackaging = productPresentationsPerPackagingField.val() ? 'Q:' + productPresentationsPerPackagingField.val() + ', ' : '';
        let nameString = `${packagingName}${productSizeName}${productPresentationName}${productPiecesPerPresentation}${productPresentationPerPackaging}${productWeight}`
        nameField.val(nameString.trim())
      }
    } else {
      nameField.val('');
    }
  }

  function updateProductSize() {
    if (categoryField.val()) {
      let categories = 'size,mix'
      if (categoryField.val() === 'presentation') {
        categories = 'size'
      }
      fetchOptions(`/rest/v1/catalogs/product-size/?product=${packagingProperties.product}&market=${packagingProperties.market}&categories=${categories}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(productSizeField, data, productSize ? productSize : null);
          productSizeField.closest('.form-group').fadeIn();
        })
    } else {
      updateFieldOptions(productSizeField, []);
    }
  }

  function updatePackaging() {
    if (productField.val() && marketField.val()) {
      fetchOptions(`/rest/v1/catalogs/packaging/?product=${productField.val()}&market=${marketField.val()}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(packagingField, data, packaging ? packaging : null);
          packagingField.closest('.form-group').fadeIn();
          productWeightPerPackagingField.closest('.form-group').fadeIn();
          if (categoryField.val() === 'presentation') {
            productPresentationField.closest('.form-group').fadeIn();
            productPresentationsPerPackagingField.closest('.form-group').fadeIn();
            productPiecesPerPresentationField.closest('.form-group').fadeIn();
          }
        })
    } else {
      updateFieldOptions(packagingField, []);
    }
  }

  async function updateProductPackagingProductWeight() {
    if (packagingField.val()) {
      if (!packagingProperties) await getPackagingProperties();
      if (!packagingSupplyProperties) await getPackagingSupplyProperties();
      productWeightPerPackagingField.val(packagingSupplyProperties.capacity);
      productWeightPerPackagingField.attr('max', Math.floor(packagingSupplyProperties.capacity + 1));
    } else {
      productWeightPerPackagingField.val(null);
      productWeightPerPackagingField.removeAttr('max');
    }
  }

  async function updateProductPresentationQuantities() {
    if (productPresentationField.val()) {
      if (!productPresentationProperties) await getProductPresentationProperties();
      if (!productPresentationSupplyProperties) await getProductPresentationSupplyProperties();
      productPiecesPerPresentationField.val(productPresentationSupplyProperties.capacity)
    }
  }

  function updateProductPresentation() {
    if (productField.val() && marketField.val()) {
      fetchOptions(`/rest/v1/catalogs/product-presentation/?product=${productField.val()}&markets=${marketField.val()}`)
        .then(data => {
          updateFieldOptions(productPresentationField, data, productPresentation ? productPresentation : null);
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

  productSizeField.on('change', () => {
    productSize = productSizeField.val();
    updateName();
  })

  packagingField.on('change', async () => {
    packaging = packagingField.val();
    await getPackagingProperties();
    await getPackagingSupplyProperties();
    await updateProductPackagingProductWeight();
    updateName();
  })

  productPresentationField.on('change', async () => {
    productPresentation = productPresentationField.val();
    await getProductPresentationSupplyProperties();
    await updateProductPresentationQuantities();
    updateName();
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

  productPiecesPerPresentationField.on('change', () => {
    updateName();
  });

  productPresentationsPerPackagingField.on('change', () => {
    let value = productPresentationsPerPackagingField.val();
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
