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

  function updateFieldOptions(field, options, selectedValue = null) {
    if (field) {
      field.empty();
      if (!field.prop('multiple')) {
        field.append(new Option('---------', '', true, !selectedValue));
      }
      options.forEach(option => {
        const newOption = new Option(option.name, option.id, false, option.id === parseInt(selectedValue));
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
          if (data.measure_unit_category_display) {
            unitPriceLabel = `Price (${data.measure_unit_category_display})`
          } else {
            unitPriceLabel.text(`Price`);
          }
        })
    } else {
      productProperties = null;
    }
  }

  function updateProductOptions() {
    return new Promise((resolve, reject) => {
      if (clientProperties && productProperties && orderItemsKindField) {
        let productSizeCategories = 'size,mix,waste,biomass'
        const productSizePromise = fetchOptions(`/rest/v1/catalogs/product-size/?market=${clientProperties.market}&product=${productProperties.id}&categories=${productSizeCategories}&is_enabled=1`)
          .then(data => {
            productSizeOptions = data;
          })

        const productPhenologyPromise = fetchOptions(`/rest/v1/catalogs/product-phenology/?product=${productProperties.id}&is_enabled=1`)
          .then(data => {
            productPhenologyOptions = data;
          })

        const productMarketClassPromise = fetchOptions(`/rest/v1/catalogs/product-market-class/?market=${clientProperties.market}&product=${productProperties.id}&is_enabled=1`)
          .then(data => {
            productMarketClassOptions = data
          })

        const productRipenessPromise = fetchOptions(`/rest/v1/catalogs/product-ripeness/?product=${productProperties.id}&is_enabled=1`)
          .then(data => {
            productRipenessOptions = data
          })

        Promise.all([productSizePromise, productPhenologyPromise, productMarketClassPromise, productRipenessPromise])
          .then(() => resolve())
          .catch(error => reject(error));
      } else {
        productSizeOptions = [];
        productPhenologyOptions = [];
        productMarketClassOptions = [];
        resolve();
      }
    });
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

      updateProductOptions().then(() => {
        updateFieldOptions(productSizeField, productSizeOptions);
        updateFieldOptions(productPhenologyField, productPhenologyOptions);
        updateFieldOptions(productMarketClassField, productMarketClassOptions);
        updateFieldOptions(productMarketRipenessField, productRipenessOptions);
        productSizeField.closest('.form-group').fadeIn();
      });

      productSizeField.on('change', () => {
        const productSizeSelectedOption = productSizeField.find('option:selected');
        const productSizeSelectedOptionCategory = productSizeSelectedOption.data('category');

        if (productSizeField.val() && productSizeSelectedOptionCategory) {
          if (['size'].includes(productSizeSelectedOptionCategory)) {
            productPhenologyField.closest('.form-group').fadeIn();
            productMarketClassField.closest('.form-group').fadeIn();
            productMarketRipenessField.closest('.form-group').fadeIn();
          }
          if (['mix'].includes(productSizeSelectedOptionCategory)) {
            productPhenologyField.closest('.form-group').fadeOut();
            productMarketClassField.closest('.form-group').fadeOut();
            productMarketRipenessField.closest('.form-group').fadeIn();
            productPhenologyField.val(null).trigger('change');
            productMarketClassField.val(null).trigger('change');
          }
          if (['waste', 'biomass'].includes(productSizeSelectedOptionCategory)) {
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
        if (quantityField.val() && unitPriceField.val()) {
          amountPriceField.val(quantityField.val() * unitPriceField.val());
        } else {
          amountPriceField.val(0);
        }
      })

      unitPriceField.on('change', () => {
        if (quantityField.val() && unitPriceField.val()) {
          amountPriceField.val(quantityField.val() * unitPriceField.val());
        } else {
          amountPriceField.val(0);
        }
      })
    }
  });

  setTimeout(async () => {
    await getProductProperties();
    await getClientProperties();

    const existingForms = $('div[id^="orderitemweight_set-"]').filter((index, form) => {
      return /^\d+$/.test(form.id.split('-').pop());
    });

    console.log("existingForms", existingForms)
    existingForms.each((index, form) => {
      const productSizeField = $(form).find(`select[name$="${index}-product_size"]`);
      const productPhenologyField = $(form).find(`select[name$="${index}-product_phenology"]`);
      const productMarketClassField = $(form).find(`select[name$="${index}-product_market_class"]`);
      const productMarketRipenessField = $(form).find(`select[name$="${index}-product_ripeness"]`);
      const quantityField = $(form).find(`input[name$="${index}-quantity"]`);
      const unitPriceField = $(form).find(`input[name$="${index}-unit_price"]`);
      const amountPriceField = $(form).find(`input[name$="${index}-amount_price"]`);
      console.log("form", index, form)
      console.log("productSizeField", productSizeField.val())


      amountPriceField.prop('disabled', true).attr('readonly', true).addClass('readonly-field');

      // productSizeField.closest('.form-group').hide();
      productPhenologyField.closest('.form-group').hide();
      productMarketClassField.closest('.form-group').hide();
      productMarketRipenessField.closest('.form-group').hide();

      updateProductOptions().then(() => {
        updateFieldOptions(productSizeField, productSizeOptions, productSizeField.val());
        updateFieldOptions(productPhenologyField, productPhenologyOptions, productPhenologyField.val());
        updateFieldOptions(productMarketClassField, productMarketClassOptions, productMarketClassField.val());
        updateFieldOptions(productMarketRipenessField, productRipenessOptions, productMarketRipenessField.val());
      })


      productSizeField.on('change', () => {
        const productSizeSelectedOption = productSizeField.find('option:selected');
        const productSizeSelectedOptionCategory = productSizeSelectedOption.data('category');

        if (productSizeField.val() && productSizeSelectedOptionCategory) {
          if (['size'].includes(productSizeSelectedOptionCategory)) {
            productPhenologyField.closest('.form-group').fadeIn();
            productMarketClassField.closest('.form-group').fadeIn();
            productMarketRipenessField.closest('.form-group').fadeIn();
          }
          if (['mix'].includes(productSizeSelectedOptionCategory)) {
            productPhenologyField.closest('.form-group').fadeOut();
            productMarketClassField.closest('.form-group').fadeOut();
            productMarketRipenessField.closest('.form-group').fadeIn();
            productPhenologyField.val(null).trigger('change');
            productMarketClassField.val(null).trigger('change');
          }
          if (['waste', 'biomass'].includes(productSizeSelectedOptionCategory)) {
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
        if (quantityField.val() && unitPriceField.val()) {
          amountPriceField.val(quantityField.val() * unitPriceField.val());
        } else {
          amountPriceField.val(0);
        }
      })

      unitPriceField.on('change', () => {
        if (quantityField.val() && unitPriceField.val()) {
          amountPriceField.val(quantityField.val() * unitPriceField.val());
        } else {
          amountPriceField.val(0);
        }
      })

    });

  }, 300);
});
