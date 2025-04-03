document.addEventListener('DOMContentLoaded', () => {
  const productField = $("#id_product");
  const clientField = $("#id_client");
  const orderItemsKindField = $("#id_order_items_kind")

  let productSizeOptions = [];
  let productPhenologyOptions = [];
  let productMarketClassOptions = [];
  let productRipenessOptions = [];

  let unitPriceLabel = 'Unit Price'

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
            unitPriceLabel = `Price (${data.price_measure_unit_category_display})`
          } else {
            unitPriceLabel.text(`Price`);
          }
        })
    } else {
      productProperties = null;
    }
  }

  function updateProductOptions() {
    if (clientProperties && productProperties && orderItemsKindField) {
      console.log("updateProductOptions")
      console.log("orderItemsKindField", orderItemsKindField)
      let productSizeCategories = 'size,mix,waste,biomass'

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

    } else {
      productSizeOptions = [];
      productPhenologyOptions = [];
      productMarketClassOptions = [];
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

  if (clientField.val()) {
    getClientProperties();
  }

  if (productField.val()) {
    getProductProperties();
  }

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'orderitemweight_set') {
      const newForm = event.target;
      const productSizeField = $(newForm).find('select[name$="-product_size"]');
      const productPhenologyField = $(newForm).find('select[name$="-product_phenology"]');
      const productMarketClassField = $(newForm).find('select[name$="-product_market_class"]');
      const productMarketRipenessField = $(newForm).find('select[name$="-product_ripeness"]');
      const quantityField = $(newForm).find('input[name$="-quantity"]');
      const unitPriceField = $(newForm).find('input[name$="-unit_price"]');
      const amountPriceField = $(newForm).find('input[name$="-amount_price"]');

      amountPriceField.prop('disabled', true).attr('readonly', true).addClass('readonly-field');

      productSizeField.closest('.form-group').hide();
      productPhenologyField.closest('.form-group').hide();
      productMarketClassField.closest('.form-group').hide();
      productMarketRipenessField.closest('.form-group').hide();

      updateFieldOptions(productSizeField, []);
      updateProductOptions();
      productSizeField.closest('.form-group').fadeIn();

      productSizeField.on('change', () => {
        const selectedOption = productSizeField.find('option:selected');
        const category = selectedOption.data('category');
        console.log("data-category:", category);

        if (productSizeField.val() && category) {
          if (['size'].includes(category)) {
            productPhenologyField.closest('.form-group').fadeIn();
            productMarketClassField.closest('.form-group').fadeIn();
            productMarketRipenessField.closest('.form-group').fadeIn();
          }
          if (['mix'].includes(category)) {
            productPhenologyField.closest('.form-group').fadeOut();
            productMarketClassField.closest('.form-group').fadeOut();
            productMarketRipenessField.closest('.form-group').fadeIn();
            productPhenologyField.val(null).trigger('change');
            productMarketClassField.val(null).trigger('change');
          }
          if (['waste', 'biomass'].includes(category)) {
            productPhenologyField.closest('.form-group').fadeOut();
            productMarketClassField.closest('.form-group').fadeOut();
            productMarketRipenessField.closest('.form-group').fadeOut();
            productPhenologyField.val(null).trigger('change');
            productMarketClassField.val(null).trigger('change');
            productMarketRipenessField.val(null).trigger('change');
          }
        } else {
          productPhenologyField.val(null).trigger('change');
          productMarketClassField.val(null).trigger('change');
          productMarketRipenessField.val(null).trigger('change');
          productPhenologyField.closest('.form-group').fadeOut();
          productMarketClassField.closest('.form-group').fadeOut();
          productMarketRipenessField.closest('.form-group').fadeOut();
        }
      });

      quantityField.on('change', () => {
        console.log("quantityField", quantityField.val());
        if (quantityField.val() && unitPriceField.val()) {
          amountPriceField.val(quantityField.val() * unitPriceField.val());
        } else {
          amountPriceField.val(0);
        }
      })

      unitPriceField.on('change', () => {
        console.log("unitPriceField", unitPriceField.val());
        if (quantityField.val() && unitPriceField.val()) {
          amountPriceField.val(quantityField.val() * unitPriceField.val());
        } else {
          amountPriceField.val(0);
        }
      })

      setTimeout(() => {
        updateFieldOptions(productSizeField, productSizeOptions);
        updateFieldOptions(productPhenologyField, productPhenologyOptions);
        updateFieldOptions(productMarketClassField, productMarketClassOptions);
        updateFieldOptions(productMarketRipenessField, productRipenessOptions);
      }, 300);
    }
  });

  setTimeout(() => {
    const existingForms = $('div[id^="orderitemweight_set-"]').filter((index, form) => {
      return /\d+$/.test(form.id);
    });

    existingForms.each((index, form) => {
      const productSizeField = $(form).find(`select[name$="${index}-product_size"]`);
      const productPhenologyField = $(form).find(`select[name$="${index}-product_phenology"]`);
      const marketClassField = $(form).find(`select[name$="${index}-product_market_class"]`);
      const marketRipenessField = $(form).find(`select[name$="${index}-product_ripeness"]`);

      updateFieldOptions(productSizeField, productSizeOptions);
      updateFieldOptions(productPhenologyField, productPhenologyOptions);
      updateFieldOptions(marketClassField, productMarketClassOptions);
      updateFieldOptions(marketRipenessField, productRipenessOptions);
    });
  }, 2000);

});
