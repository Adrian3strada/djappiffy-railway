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
      let productPresentationQuantityPerPackaging = ' ';
      if (productPresentationQuantityPerPackagingField.val()) {
        productPresentationQuantityPerPackaging = ` ${productPresentationQuantityPerPackagingField.val()} `;
      }
      const productPresentationName = productPresentationField.find('option:selected').text();
      nameString = `${nameString}${productPresentationQuantityPerPackaging}${productPresentationName}`;
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

  productAmountPerPackagingField.on('change', () => {
    if (productAmountPerPackagingField.val() && categoryField.val() === 'packaging') {
      const maxProductAmount = parseFloat(packagingSupplyProperties.capacity);
      if (parseFloat(productAmountPerPackagingField.val()) > maxProductAmount) {
        productAmountPerPackagingField.val(maxProductAmount);
      }
    }
  });

  productPresentationQuantityPerPackagingField.on('change', () => {
    let value = productPresentationQuantityPerPackagingField.val();
    console.log(value);
    if (!isNaN(value)) {
      productPresentationQuantityPerPackagingField.val('');
    }
    if (value && categoryField.val() === 'presentation') {
      value = value.replace(/[^\d.]/g, '');
      const quantity = Math.floor(parseFloat(value));
      if (!isNaN(quantity)) {
        productPresentationQuantityPerPackagingField.val(quantity);
      }
    }
    updateName();
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

  productPresentationField.on('change', () => {
    updateName();
  })

  productSizeField.on('change', () => {
    updateName();
  })

  productAmountPerPackagingField.attr('step', '0.01');
  productAmountPerPackagingField.attr('min', '0.01');
  productPresentationQuantityPerPackagingField.attr('step', 1);
  productPresentationQuantityPerPackagingField.attr('min', 1);

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
    updatePackagingProductAmount();
  } else {
    productAmountPerPackagingField.closest('.form-group').fadeOut();
    productPresentationField.closest('.form-group').fadeOut();
    productPresentationQuantityPerPackagingField.closest('.form-group').fadeOut();
  }

  [productField, marketField, productPresentationField].forEach(field => field.select2());
});
