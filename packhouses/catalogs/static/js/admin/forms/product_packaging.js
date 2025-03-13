document.addEventListener('DOMContentLoaded', function () {
  const categoryField = $('#id_category');
  const marketField = $('#id_market');
  const productField = $('#id_product');
  const productSizeField = $('#id_product_size');
  const packagingField = $('#id_packaging');
  const productPresentationField = $('#id_product_presentation');
  const nameField = $('#id_name');
  const aliasField = $('#id_alias');

  const productAmountPerPackagingField = $('#id_product_amount_per_packaging');
  const productPresentationQuantityPerPackagingField = $('#id_product_presentation_quantity_per_packaging');

  let productProperties = null;
  let packagingProperties = null;
  let packagingSupplyProperties = null;

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

  function updateName() {
    const packagingName = packagingField.val() ? packagingField.find('option:selected').text() : '';
    const productSizeName = productSizeField.val() ? productSizeField.find('option:selected').text() : '';
    const nameString = `${packagingName} ${productSizeName}`
    nameField.val(nameString.trim())
    aliasField.val(null)
  }

  function updateProductSize() {
    if (productField.val() && marketField.val()) {
      fetchOptions(`/rest/v1/catalogs/product-size/?product=${productField.val()}&market=${marketField.val()}`)
        .then(data => {
          console.log("updateProductSize", data);
          updateFieldOptions(productSizeField, data);
        })
    } else {
      updateFieldOptions(productSizeField, []);
    }
  }

  function updatePackaging() {
    if (productField.val() && marketField.val()) {
      fetchOptions(`/rest/v1/catalogs/packaging/?product=${productField.val()}&markets=${marketField.val()}`)
        .then(data => {
          console.log("updatePackaging", data);
          updateFieldOptions(packagingField, data);
        })
    } else {
      updateFieldOptions(packagingField, []);
    }
  }

  function updatePackagingProductAmount() {
    if (packagingField.val()) {
      fetchOptions(`/rest/v1/catalogs/packaging/${packagingField.val()}/`)
        .then(packaging_data => {
          console.log("updatePackagingProductAmount", packaging_data);
          packagingProperties = packaging_data;
          fetchOptions(`/rest/v1/catalogs/supply/${packaging_data.packaging_supply}/`)
            .then(supply_data => {
              console.log("updatePackagingProductAmount supply", supply_data);
              packagingSupplyProperties = supply_data;
              productAmountPerPackagingField.val(supply_data.capacity);
              productAmountPerPackagingField.attr('max', supply_data.capacity);
              productAmountPerPackagingField.attr('min', 0.01);
            })
        })
    } else {
      packagingProperties = null;
      packagingSupplyProperties = null;
      productAmountPerPackagingField.val(null);
      productAmountPerPackagingField.removeAttr('max');
      productAmountPerPackagingField.removeAttr('min');
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

  productAmountPerPackagingField.on('change', () => {
    if (productAmountPerPackagingField.val() && categoryField.val() === 'packaging') {
      const maxProductAmount = parseFloat(packagingSupplyProperties.capacity);
      if (parseFloat(productAmountPerPackagingField.val()) > maxProductAmount) {
        productAmountPerPackagingField.val(maxProductAmount);
      }
    }
  });

  categoryField.on('change', () => {
    productAmountPerPackagingField.val(null);
    productPresentationField.val(null).trigger('change').select2();
    productPresentationQuantityPerPackagingField.val(null)

    if (categoryField.val()) {
      if (categoryField.val() === 'packaging') {
        productPresentationField.closest('.form-group').fadeOut();
        productPresentationQuantityPerPackagingField.closest('.form-group').fadeOut();
        productAmountPerPackagingField.closest('.form-group').fadeIn();
      } else if (categoryField.val() === 'presentation') {
        updateProductPresentation();
        productAmountPerPackagingField.closest('.form-group').fadeOut();
        productPresentationField.closest('.form-group').fadeIn();
        productPresentationQuantityPerPackagingField.closest('.form-group').fadeIn();
      } else {
        productAmountPerPackagingField.closest('.form-group').fadeOut();
        productPresentationField.closest('.form-group').fadeOut();
        productPresentationQuantityPerPackagingField.closest('.form-group').fadeOut();
      }
    } else {
      productAmountPerPackagingField.closest('.form-group').fadeOut();
      productPresentationField.closest('.form-group').fadeOut();
      productPresentationQuantityPerPackagingField.closest('.form-group').fadeOut();
    }
  });

  productField.on('change', () => {
    getProductProperties();
    updateProductSize();
    updatePackaging();
    if (categoryField.val() === 'presentation') {
      updateProductPresentation();
    }
  })

  marketField.on('change', () => {
    updateProductSize();
    updatePackaging();
    if (categoryField.val() === 'presentation') {
      updateProductPresentation();
    }
  });

  packagingField.on('change', () => {
    updatePackagingProductAmount();
    updateName();
  })

  productSizeField.on('change', () => {
    updateName();
  })

  productAmountPerPackagingField.attr('step', '0.01');
  productAmountPerPackagingField.attr('min', '0.01');

  if (categoryField.val()) {
    if (categoryField.val() === 'packaging') {
      productPresentationField.closest('.form-group').fadeOut();
      productPresentationQuantityPerPackagingField.closest('.form-group').fadeOut();
      productAmountPerPackagingField.closest('.form-group').fadeIn();
    } else if (categoryField.val() === 'presentation') {
      productAmountPerPackagingField.closest('.form-group').fadeOut();
      productPresentationField.closest('.form-group').fadeIn();
      productPresentationQuantityPerPackagingField.closest('.form-group').fadeIn();
    } else {
      productAmountPerPackagingField.closest('.form-group').fadeOut();
      productPresentationField.closest('.form-group').fadeOut();
      productPresentationQuantityPerPackagingField.closest('.form-group').fadeOut();
    }
  } else {
    productAmountPerPackagingField.closest('.form-group').fadeOut();
    productPresentationField.closest('.form-group').fadeOut();
    productPresentationQuantityPerPackagingField.closest('.form-group').fadeOut();
  }

  [productField, marketField, productPresentationField].forEach(field => field.select2());
});
