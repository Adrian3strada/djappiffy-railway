document.addEventListener('DOMContentLoaded', () => {
  const productField = $("#id_product");
  const clientField = $("#id_client");
  const orderItemsKindField = $("#id_order_items_kind")
  const pricingByField = $("#id_pricing_by")

  let productSizeOptions = [];
  let productPhenologyOptions = [];
  let productMarketClassOptions = [];
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

      fetchOptions(`/rest/v1/catalogs/product-phenology/?product=${productProperties.id}&is_enabled=1`)
        .then(data => {
          productPhenologyOptions = data;
        }).then(() => {
        console.log("productPhenologyOptions", productPhenologyOptions)
      });

      fetchOptions(`/rest/v1/catalogs/product-market-class/?market=${clientProperties.market}&product=${productProperties.id}&is_enabled=1`)
        .then(data => {
          productMarketClassOptions = data
        }).then(() => {
        console.log("productMarketClassOptions 1", productMarketClassOptions)
      });

      fetchOptions(`/rest/v1/catalogs/product-packaging/?product=${productProperties.id}&is_enabled=1`)
        .then(data => {
          productPackagingOptions = data;
        }).then(() => {
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

  pricingByField.on('change', () => {
    if (pricingByField.val()) {
      updateProductOptions();
    }
  });

  if (clientField.val()) {
    getClientProperties();
  }

  if (productField.val()) {
    getProductProperties();
  }

  if (pricingByField.val()) {
    updateProductOptions();
  }

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'orderitem_set') {
      const newForm = event.target;
      const productSizeField = $(newForm).find('select[name$="-product_size"]');
      const productPhenologyField = $(newForm).find('select[name$="-product_phenology"]');
      const marketClassField = $(newForm).find('select[name$="-product_market_class"]');
      const productPackagingField = $(newForm).find('select[name$="-product_packaging"]');
      const amountPerPackagingField = $(newForm).find('input[name$="-amount_per_packaging"]');

      updateFieldOptions(productSizeField, productSizeOptions);
      updateFieldOptions(productPhenologyField, productPhenologyOptions);
      updateFieldOptions(marketClassField, productMarketClassOptions);
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
