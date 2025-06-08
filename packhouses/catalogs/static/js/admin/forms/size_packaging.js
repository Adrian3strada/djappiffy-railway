document.addEventListener('DOMContentLoaded', async function () {
  const categoryField = $('#id_category');
  const productPackagingField = $('#id_product_packaging');
  const productSizeField = $('#id_product_size');
  const productWeightPerPackagingField = $('#id_product_weight_per_packaging');
  const productPresentationField = $('#id_product_presentation');
  const productPiecesPerPresentationField = $('#id_product_pieces_per_presentation');
  const productPresentationsPerPackagingField = $('#id_product_presentations_per_packaging');
  const nameField = $('#id_name');
  const aliasField = $('#id_alias');
  const isEditing = window.location.pathname.match(/\/change\//) !== null;

  let packagingProperties = null;
  let packagingSupplyProperties = null;
  let productPresentationProperties = null;
  let productPresentationSupplyProperties = null;

  let categories = 'size,mix';
  let allowChangeName = false;

  productWeightPerPackagingField.attr('step', '0.01');
  productWeightPerPackagingField.attr('min', '0.01');
  productPresentationsPerPackagingField.attr('step', 1);
  productPresentationsPerPackagingField.attr('min', 1);
  productPiecesPerPresentationField.attr('step', 1);
  productPiecesPerPresentationField.attr('min', 1);

  productPresentationField.closest('.form-group').hide();
  productPresentationsPerPackagingField.closest('.form-group').hide();
  productPiecesPerPresentationField.closest('.form-group').hide();

  if (productPresentationField.val()) productPresentationField.closest('.form-group').show();
  if (productPresentationsPerPackagingField.val()) productPresentationsPerPackagingField.closest('.form-group').show();
  if (productPiecesPerPresentationField.val()) productPiecesPerPresentationField.closest('.form-group').show();

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
    if (productPackagingField.val()) {
      packagingProperties = await fetchOptions(`/rest/v1/catalogs/packaging/${productPackagingField.val()}/`)
      packagingSupplyProperties = await fetchOptions(`/rest/v1/catalogs/supply/${packagingProperties.packaging_supply}/`)
      console.log("Packaging Properties:", packagingProperties);
      console.log("Packaging Supply Properties:", packagingSupplyProperties);
    } else {
      packagingProperties = null;
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
    if (allowChangeName) {
      if (categoryField.val() === 'single') {
        if (productPackagingField.val() && productSizeField.val() && productWeightPerPackagingField.val()) {
          const packagingName = productPackagingField.val() ? productPackagingField.find('option:selected').text() + ' ' : '';
          const productSizeName = productSizeField.val() ? 'S:' + productSizeField.find('option:selected').text() + ' - ' : '';
          const productWeight = productWeightPerPackagingField.val() ? 'W:' + productWeightPerPackagingField.val() : '';
          let nameString = `${packagingName}${productSizeName}${productWeight}`
          nameField.val(nameString.trim())
        }
      } else if (categoryField.val() === 'presentation') {
        if (productPackagingField.val() && productSizeField.val() && productWeightPerPackagingField.val() && productPresentationField.val() && productPiecesPerPresentationField.val() && productPresentationsPerPackagingField.val()) {
          const packagingName = productPackagingField.val() ? productPackagingField.find('option:selected').text() + ' - ' : '';
          const productSizeName = productSizeField.val() ? 'S:' + productSizeField.find('option:selected').text() + ' - ' : '';
          const productWeight = productWeightPerPackagingField.val() ? 'W:' + productWeightPerPackagingField.val() : '';
          const productPresentationName = productPresentationField.val() ? productPresentationField.find('option:selected').text() + ' - ' : '';
          const productPiecesPerPresentation = productPiecesPerPresentationField.val() ? 'P:' + productPiecesPerPresentationField.val() + ', ' : '';
          const productPresentationPerPackaging = productPresentationsPerPackagingField.val() ? 'Q:' + productPresentationsPerPackagingField.val() + ', ' : '';
          let nameString = `${packagingName}${productSizeName}${productPresentationName}${productPiecesPerPresentation}${productPresentationPerPackaging}${productWeight}`
          nameField.val(nameString.trim())
        }
      } else {
        // pass
      }
    }
  }

  async function updateProductSize() {
    if (productPackagingField.val()) {
      const productSizes = await fetchOptions(`/rest/v1/catalogs/product-size/?product=${packagingProperties.product}&market=${packagingProperties.market}&categories=${categories}&is_enabled=1`)
      updateFieldOptions(productSizeField, productSizes, productSizeField.val() ? productSizeField.val() : null);
    } else {
      updateFieldOptions(productSizeField, []);
    }
  }

  async function updateProductPackagingProductWeight() {
    if (productPackagingField.val()) {
      if (!packagingProperties) await getPackagingProperties();
      productWeightPerPackagingField.val(packagingSupplyProperties.capacity);
      productWeightPerPackagingField.attr('max', packagingSupplyProperties.capacity);
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

  async function updateProductPresentation() {
    if (packagingProperties && categoryField.val() && categoryField.val() === 'presentation') {
      const productPresentations = await fetchOptions(`/rest/v1/catalogs/product-presentation/?product=${packagingProperties.product}&markets=${packagingProperties.market}`)
      updateFieldOptions(productPresentationField, productPresentations, productPresentationField.val() ? productPresentationField.val() : null);
    } else {
      updateFieldOptions(productPresentationField, []);
    }
  }

  categoryField.on('change', async () => {
    categoryField.val() === 'presentation' ? categories = 'size' : categories = 'size,mix';
    if (categoryField.val() === 'presentation') {
      categories = 'size'
      productPresentationField.closest('.form-group').fadeIn();
      productPresentationsPerPackagingField.closest('.form-group').fadeIn();
      productPiecesPerPresentationField.closest('.form-group').fadeIn();
    } else {
      categories = 'size,mix'
      productPresentationField.val(null);
      productPresentationsPerPackagingField.val(null);
      productPiecesPerPresentationField.val(null);
      productPresentationField.closest('.form-group').fadeOut();
      productPresentationsPerPackagingField.closest('.form-group').fadeOut();
      productPiecesPerPresentationField.closest('.form-group').fadeOut();
    }
    await updateProductPresentation();

    updateName();
  });

  if (categoryField.val()) {
    if (categoryField.val() === 'presentation') {
      categories = 'size'
    } else {
      categories = 'size,mix';
    }
  }

  productPackagingField.on('change', async () => {
    await getPackagingProperties();
    await updateProductSize();
    await updateProductPresentation();
    await updateProductPackagingProductWeight();
    updateName();
  })

  productSizeField.on('change', () => {
    updateName();
  })

  productPresentationField.on('change', async () => {
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

  if (productPackagingField.val()) {
    await getPackagingProperties();
    await updateProductSize();
    await updateProductPresentation();
  }

  if (isEditing) {
    setTimeout(() => {
      allowChangeName = true;
    }, 200)
  } else {
    allowChangeName = true;
  }

  [categoryField, productSizeField, productPackagingField, productPresentationField].forEach(field => field.select2());
});
