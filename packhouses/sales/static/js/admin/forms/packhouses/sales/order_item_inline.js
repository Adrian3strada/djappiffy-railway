document.addEventListener('DOMContentLoaded', () => {
  const productField = $("#id_product");
  const clientField = $("#id_client");
  const orderItemsKindField = $("#id_order_items_kind")
  const pricingByField = $("#id_pricing_by")

  let productSizeOptions = [];
  let productPhenologyOptions = [];
  let productMarketClassOptions = [];
  let productRipenessOptions = [];
  let productPackagingOptions = [];

  let priceLabel = 'Price'

  let clientProperties = null;
  let productProperties = null;

  function updateFieldOptions(field, options) {
    if (field) {
      field.empty();
      if (!field.prop('multiple')) {
        field.append(new Option('---------', '', true, true));
      }
      options.forEach(option => {
        const newOption = new Option(option.name, option.id, false, false);
        if ('alias' in option && option.alias) {
          newOption.setAttribute('data-alias', option.alias);
        }
        if ('category' in option && option.category) {
          newOption.setAttribute('data-category', option.category);
        }
        field.append(newOption);
      });
      field.trigger('change').select2();
    }
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: 'GET',
      dataType: 'json'
    }).fail(error => console.error('Fetch error:', error));
  }

  function getClientProperties() {
    if (clientField.val()) {
      fetchOptions(`/rest/v1/catalogs/client/${clientField.val()}/`)
        .then(data => {
          clientProperties = data;
          console.log("clientProperties", clientProperties)
        })
    } else {
      clientProperties = null;
    }
  }

  function getProductProperties() {
    if (productField.val()) {
      fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
        .then(data => {
          productProperties = data;
          console.log("productProperties", productProperties)
          if (data.price_measure_unit_category_display) {
            priceLabel = `Price (${data.price_measure_unit_category_display})`
          } else {
            priceLabel.text(`Price`);
          }
        })
    } else {
      productProperties = null;
    }
  }

  function updateProductOptions() {
    if (clientProperties && productProperties && orderItemsKindField && pricingByField) {
      console.log("orderItemsKindField", orderItemsKindField)
      console.log("pricingByField", pricingByField)
      let productSizeCategories = 'none'

      if (orderItemsKindField.val() === 'product_measure_unit') {
        if (pricingByField.val() === 'product_measure_unit') {
          productSizeCategories = 'size,mix,waste,biomass'
        }
      }

      if (orderItemsKindField.val() === 'product_packaging') {
        if (pricingByField.val() === 'product_measure_unit') {
          productSizeCategories = 'size,mix'
        }
        if (pricingByField.val() === 'product_packaging') {
          productSizeCategories = 'size,mix'
        }
        if (pricingByField.val() === 'product_presentation') {
          productSizeCategories = 'size'
        }
      }

      if (orderItemsKindField.val() === 'product_pallet') {
        if (pricingByField.val() === 'product_measure_unit') {
          productSizeCategories = 'size,mix'
        }
        if (pricingByField.val() === 'product_packaging') {
          productSizeCategories = 'size,mix'
        }
        if (pricingByField.val() === 'product_presentation') {
          productSizeCategories = 'size'
        }
      }

      fetchOptions(`/rest/v1/catalogs/product-size/?market=${clientProperties.market}&product=${productProperties.id}&categories=${productSizeCategories}&is_enabled=1`)
        .then(data => {
          productSizeOptions = data;
        })
        .then(() => {
          console.log("productSizeOptions", productSizeOptions)
        });

      fetchOptions(`/rest/v1/catalogs/product-phenology/?product=${productProperties.id}&is_enabled=1`)
        .then(data => {
          productPhenologyOptions = data;
        })
        .then(() => {
          console.log("productPhenologyOptions", productPhenologyOptions)
        });

      fetchOptions(`/rest/v1/catalogs/product-market-class/?market=${clientProperties.market}&product=${productProperties.id}&is_enabled=1`)
        .then(data => {
          productMarketClassOptions = data
        })
        .then(() => {
          console.log("productMarketClassOptions 1", productMarketClassOptions)
        });

      fetchOptions(`/rest/v1/catalogs/product-ripeness/?product=${productProperties.id}&is_enabled=1`)
        .then(data => {
          productRipenessOptions = data
        })
        .then(() => {
          console.log("productRipenessOptions", productRipenessOptions)
        });

      fetchOptions(`/rest/v1/catalogs/product-packaging/?product=${productProperties.id}&is_enabled=1`)
        .then(data => {
          productPackagingOptions = data;
        })
        .then(() => {
          console.log("productPackagingOptions", productPackagingOptions)
        });

    } else {
      productSizeOptions = [];
      productPhenologyOptions = [];
      productMarketClassOptions = [];
      productPackagingOptions = [];
    }
  }

  clientField.on('change', () => {
    if (clientField.val()) {
      getClientProperties();
    }
  });

  productField.on('change', () => {
    if (productField.val()) {
      getProductProperties();
    }
  });

  setTimeout(() => {
    pricingByField.on('change', () => {
      if (pricingByField.val()) {
        updateProductOptions();
      }
    });
  }, 1000);

  if (clientField.val()) {
    getClientProperties();
  }

  if (productField.val()) {
    getProductProperties();
  }

  setTimeout(() => {
    if (pricingByField.val()) {
      updateProductOptions();
    }
  }, 1000);

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'orderitem_set') {
      const newForm = event.target;
      const productSizeField = $(newForm).find('select[name$="-product_size"]');
      const productPhenologyField = $(newForm).find('select[name$="-product_phenology"]');
      const marketClassField = $(newForm).find('select[name$="-product_market_class"]');
      const marketRipenessField = $(newForm).find('select[name$="-product_ripeness"]');
      const productPackagingField = $(newForm).find('select[name$="-product_packaging"]');
      const amountPerPackagingField = $(newForm).find('input[name$="-amount_per_packaging"]');

      productPhenologyField.closest('.form-group').hide();
      marketClassField.closest('.form-group').hide();
      marketRipenessField.closest('.form-group').hide();
      productPackagingField.closest('.form-group').hide();
      amountPerPackagingField.closest('.form-group').hide();

      productSizeField.on('change', () => {
        const selectedOption = productSizeField.find('option:selected');
        const category = selectedOption.data('category');
        console.log("data-category:", category);

        if (productSizeField.val() && category) {
          if (['size'].includes(category)) {
            productPhenologyField.closest('.form-group').fadeIn();
            marketClassField.closest('.form-group').fadeIn();
            marketRipenessField.closest('.form-group').fadeIn();
            productPackagingField.closest('.form-group').fadeIn();
            amountPerPackagingField.closest('.form-group').fadeIn();
          }
          if (['mix'].includes(category)) {
            productPhenologyField.closest('.form-group').fadeOut();
            marketClassField.closest('.form-group').fadeOut();
            marketRipenessField.closest('.form-group').fadeIn();
            productPackagingField.closest('.form-group').fadeIn();
            amountPerPackagingField.closest('.form-group').fadeIn();
            productPhenologyField.val(null).trigger('change');
            marketClassField.val(null).trigger('change');
          }
          if (['waste', 'biomass'].includes(category)) {
            productPhenologyField.closest('.form-group').fadeOut();
            marketClassField.closest('.form-group').fadeOut();
            marketRipenessField.closest('.form-group').fadeOut();
            productPackagingField.closest('.form-group').fadeOut();
            amountPerPackagingField.closest('.form-group').fadeOut();
            productPhenologyField.val(null).trigger('change');
            marketClassField.val(null).trigger('change');
            marketRipenessField.val(null).trigger('change');
            productPackagingField.val(null).trigger('change');
            amountPerPackagingField.val(null).trigger('change');
          }
        } else {
          productPhenologyField.val(null).trigger('change');
          marketClassField.val(null).trigger('change');
          marketRipenessField.val(null).trigger('change');
          productPackagingField.val(null).trigger('change');
          amountPerPackagingField.val(null).trigger('change');
          productPhenologyField.closest('.form-group').fadeOut();
          marketClassField.closest('.form-group').fadeOut();
          marketRipenessField.closest('.form-group').fadeOut();
          productPackagingField.closest('.form-group').fadeOut();
          amountPerPackagingField.closest('.form-group').fadeOut();
        }
      });

      updateFieldOptions(productSizeField, productSizeOptions);
      updateFieldOptions(productPhenologyField, productPhenologyOptions);
      updateFieldOptions(marketClassField, productMarketClassOptions);
      updateFieldOptions(marketRipenessField, productRipenessOptions);
      updateFieldOptions(productPackagingField, productPackagingOptions);
    }
  });

  setTimeout(() => {
    const existingForms = $('div[id^="orderitem_set-"]').filter((index, form) => {
      return /\d+$/.test(form.id);
    });

    existingForms.each((index, form) => {
      const productSizeField = $(form).find(`select[name$="${index}-product_size"]`);
      const productPhenologyField = $(form).find(`select[name$="${index}-product_phenology"]`);
      const marketClassField = $(form).find(`select[name$="${index}-product_market_class"]`);
      const productPackagingField = $(form).find(`select[name$="${index}-product_packaging"]`);

      updateFieldOptions(productSizeField, productSizeOptions);
      updateFieldOptions(productPhenologyField, productPhenologyOptions);
      updateFieldOptions(marketClassField, productMarketClassOptions);
      updateFieldOptions(productPackagingField, productPackagingOptions);
    });
  }, 2000);

});
