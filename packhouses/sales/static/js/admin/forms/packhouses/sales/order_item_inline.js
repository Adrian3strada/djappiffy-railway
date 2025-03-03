document.addEventListener('DOMContentLoaded', () => {
  const productField = $("#id_product");
  const clientField = $("#id_client");
  const orderItemsByField = $("#id_order_items_by")
  const pricingByField = $("#id_pricing_by")

  let productSizeOptions = [];
  let productPhenologyOptions = [];
  let productMarketClassOptions = [];
  let productPackagingOptions = [];

  let clientProperties = null;
  let productProperties = null;


  function updateFieldOptions(field, options) {
    if (field) {
      field.empty();
      if (!field.prop('multiple')) {
        field.append(new Option('---------', '', true, true));
      }
      options.forEach(option => {
        field.append(new Option(option.name, option.id, false, false));
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
        .then(() => {
          if (clientProperties && productProperties) {
            alert("updateProductOptions() en getClientProperties()")
            updateProductOptions();
          }
        });
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
          const priceLabel = $('label[for$="-unit_price"]');
          if (data.price_measure_unit_category_display) {
            priceLabel.text(`Price (${data.price_measure_unit_category_display})`);
          } else {
            priceLabel.text(`Price`);
          }
        })
        .then(() => {
          if (clientProperties && productProperties) {
            alert("updateProductOptions() en getProductProperties()")
            updateProductOptions();
          }
        });
    } else {
      productProperties = null;
    }
  }

  function updateProductOptions() {
    console.log("updateProductOptions")
    console.log("productField.val()", productField.val())
    console.log("clientProperties", clientProperties)
    alert("updateProductOptions()")
    if (clientProperties && productProperties) {
      fetchOptions(`/rest/v1/catalogs/product-size/?market=${clientProperties.market}&product=${productProperties.id}&is_enabled=1`)
        .then(data => {
          productSizeOptions = data;
        }).then(() => {
        console.log("productSizeOptions", productSizeOptions)
      });
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
      productPackagingOptions = [];
    }
  }

  function updateMarketClassOptions() {
    if (clientProperties) {
      fetchOptions(`/rest/v1/catalogs/product-market-class/?market=${clientProperties.market}&product=${productProperties.id}&is_enabled=1`)
        .then(data => {
          console.log("updateMarketClassOptions data", data)
          productMarketClassOptions = data
        });
    } else {
      productMarketClassOptions = [];
    }
  }

  clientField.on('change', () => {
    getClientProperties();
  });

  productField.on('change', () => {
    getProductProperties();
  });

  if (clientField.val()) {
    getClientProperties();
  }

  if (productField.val()) {
    getProductProperties();
  }

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'orderitem_set') {
      const newForm = event.target;
      const productSizeField = $(newForm).find('select[name$="-product_size"]');
      const productPhenologyField = $(newForm).find('select[name$="-product_phenology"]');
      const marketClassField = $(newForm).find('select[name$="-product_market_class"]');
      const productPackagingField = $(newForm).find('select[name$="-product_packaging"]');

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
