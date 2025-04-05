document.addEventListener('DOMContentLoaded', function () {
  const categoryField = $('#id_category');
  const marketField = $('#id_market');
  const productField = $('#id_product');
  const productSizeField = $('#id_product_size');
  const packagingField = $('#id_packaging');
  const productPresentationField = $('#id_product_presentation');
  const nameField = $('#id_name');
  const aliasField = $('#id_alias');

  const productWeightPerPackagingField = $('#id_product_weight_per_packaging');
  const productPresentationPerPackagingField = $('#id_product_presentation_per_packaging');
  const productPiecesPerPresentationField = $('#id_product_pieces_per_presentation');

  let productProperties = null;
  let packagingProperties = null;
  let presentationProperties = null;
  let packagingSupplyProperties = null;
  let presentationSupplyProperties = null;


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
    let nameString = `${packagingName} ${productSizeName}`
    if (categoryField.val() === 'presentation' && productPresentationField.val()) {
      let productPresentationPerPackaging = ' ';
      if (productPresentationPerPackagingField.val()) {
        productPresentationPerPackaging = ` ${productPresentationPerPackagingField.val()} `;
      }
      const productPresentationName = productPresentationField.find('option:selected').text();
      nameString = `${nameString}${productPresentationPerPackaging}${productPresentationName}`;
    }
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
          packagingProperties = packaging_data;
          fetchOptions(`/rest/v1/catalogs/supply/${packaging_data.packaging_supply}/`)
            .then(supply_data => {
              packagingSupplyProperties = supply_data;
              productWeightPerPackagingField.val(supply_data.capacity);
              productWeightPerPackagingField.attr('max', supply_data.capacity);
              productWeightPerPackagingField.attr('min', 0.01);
            })
        })
    } else {
      packagingProperties = null;
      packagingSupplyProperties = null;
      productWeightPerPackagingField.val(null);
      productWeightPerPackagingField.removeAttr('max');
      productWeightPerPackagingField.removeAttr('min');
    }
  }

  function updateProductPresentationQuantityPerPackaging() {
    if (productPresentationField.val()) {
      fetchOptions(`/rest/v1/catalogs/product-presentation/${productPresentationField.val()}/`)
        .then(productpresentation_data => {
          presentationProperties = productpresentation_data;
          console.log("productPresentationField data", productpresentation_data);
          fetchOptions(`/rest/v1/catalogs/supply/${productpresentation_data.presentation_supply}/`)
            .then(supply_data => {
              presentationSupplyProperties = supply_data;
              console.log("supply_data", supply_data);
            });
        });
    } else {
      presentationProperties = null;
      presentationSupplyProperties = null;
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

  productWeightPerPackagingField.on('change', () => {
    if (productWeightPerPackagingField.val() && categoryField.val() === 'packaging') {
      const maxProductAmount = parseFloat(packagingSupplyProperties.capacity);
      if (parseFloat(productWeightPerPackagingField.val()) > maxProductAmount) {
        productWeightPerPackagingField.val(maxProductAmount);
      }
    }
  });

  productPresentationPerPackagingField.on('change', () => {
    let value = productPresentationPerPackagingField.val();
    console.log(value);
    if (!isNaN(value)) {
      productPresentationPerPackagingField.val('');
    }
    if (value && categoryField.val() === 'presentation') {
      value = value.replace(/[^\d.]/g, '');
      const quantity = Math.floor(parseFloat(value));
      if (!isNaN(quantity)) {
        productPresentationPerPackagingField.val(quantity);
      }
    }
    updateName();
  });

  categoryField.on('change', () => {
    productWeightPerPackagingField.val(null);
    productPresentationField.val(null).trigger('change').select2();
    productPresentationPerPackagingField.val(null)

    if (categoryField.val()) {
      if (categoryField.val() === 'packaging') {
        productPresentationField.closest('.form-group').fadeOut();
        productPresentationPerPackagingField.closest('.form-group').fadeOut();
        productWeightPerPackagingField.closest('.form-group').fadeIn();
      } else if (categoryField.val() === 'presentation') {
        updateProductPresentation();
        productWeightPerPackagingField.closest('.form-group').fadeOut();
        productPresentationField.closest('.form-group').fadeIn();
        productPresentationPerPackagingField.closest('.form-group').fadeIn();
      } else {
        productWeightPerPackagingField.closest('.form-group').fadeOut();
        productPresentationField.closest('.form-group').fadeOut();
        productPresentationPerPackagingField.closest('.form-group').fadeOut();
      }
    } else {
      productWeightPerPackagingField.closest('.form-group').fadeOut();
      productPresentationField.closest('.form-group').fadeOut();
      productPresentationPerPackagingField.closest('.form-group').fadeOut();
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

  productPresentationField.on('change', () => {
    updateName();
  })

  productSizeField.on('change', () => {
    updateName();
  })

  productWeightPerPackagingField.attr('step', '0.01');
  productWeightPerPackagingField.attr('min', '0.01');
  productPresentationPerPackagingField.attr('step', 1);
  productPresentationPerPackagingField.attr('min', 1);
  productPiecesPerPresentationField.attr('step', 1);
  productPiecesPerPresentationField.attr('min', 1);

  if (categoryField.val()) {
    if (categoryField.val() === 'packaging') {
      productPresentationField.closest('.form-group').fadeOut();
      productPresentationPerPackagingField.closest('.form-group').fadeOut();
      productPiecesPerPresentationField.closest('.form-group').fadeOut();
      productWeightPerPackagingField.closest('.form-group').fadeIn();
    } else if (categoryField.val() === 'presentation') {
      productWeightPerPackagingField.closest('.form-group').fadeOut();
      productPresentationField.closest('.form-group').fadeIn();
      productPresentationPerPackagingField.closest('.form-group').fadeIn();
      productPiecesPerPresentationField.closest('.form-group').fadeIn();
    } else {
      productWeightPerPackagingField.closest('.form-group').fadeOut();
      productPresentationField.closest('.form-group').fadeOut();
      productPresentationPerPackagingField.closest('.form-group').fadeOut();
      productPiecesPerPresentationField.closest('.form-group').fadeOut();
    }
    updatePackagingProductAmount();
  } else {
    productWeightPerPackagingField.closest('.form-group').fadeOut();
    productPresentationField.closest('.form-group').fadeOut();
    productPresentationPerPackagingField.closest('.form-group').fadeOut();
  }

  [productField, marketField, productPresentationField].forEach(field => field.select2());
});
