document.addEventListener('DOMContentLoaded', async () => {
  const productField = $("#id_product");
  const clientField = $("#id_client");
  const orderItemsKindField = $("#id_order_items_kind")

  let productPhenologyOptions = [];
  let productMarketClassOptions = [];
  let productRipenessOptions = [];
  let productSizeOptions = [];

  let unitPriceLabel = 'Unit Price'

  let clientProperties = null;
  let productProperties = null;
  let productSizeCategories = 'size,mix';
  let organization = null;

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

  async function getClientProperties() {
    if (clientField.val()) {
      clientProperties = await fetchOptions(`/rest/v1/catalogs/client/${clientField.val()}/`)
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

        const productSizePromise = fetchOptions(`/rest/v1/catalogs/product-size/?market=${clientProperties.market}&product=${productProperties.id}&categories=${productSizeCategories}&is_enabled=1`)
          .then(data => {
            productSizeOptions = data;
          });

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
        productPhenologyOptions = [];
        productMarketClassOptions = [];
        resolve();
      }
    });
  }

  function getOrganizationProfile() {
    return fetchOptions(`/rest/v1/profiles/packhouse-exporter-profile/?same=1`).then(
      (data) => {
        if (data.count === 1) {
          organization = data.results.pop()
        }
      });
  }

  getOrganizationProfile()

  clientField.on('change', async () => {
    if (clientField.val()) {
      if (!organization) {
        await getOrganizationProfile();
      }
      await getClientProperties();
      if (clientProperties && organization) {
        if (clientProperties.country === organization.country) {
          productSizeCategories = 'size,mix'
        } else {
          productSizeCategories = 'size'
        }
      }
    }
  });

  productField.on('change', () => {
    if (productField.val()) {
      getProductProperties();
    }
  });

  if (clientField.val()) {
    if (!organization) {
      await getOrganizationProfile();
    }
    await getClientProperties();
    console.log("organization", organization);
    console.log("clientProperties", clientProperties);
  }

  if (productField.val()) {
    getProductProperties();
  }

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'orderitempackaging_set') {
      const newForm = event.target;
      const pricingByField = $(newForm).find('select[name$="-pricing_by"]');
      const productSizeField = $(newForm).find('select[name$="-product_size"]');
      const productPhenologyField = $(newForm).find('select[name$="-product_phenology"]');
      const productMarketClassField = $(newForm).find('select[name$="-product_market_class"]');
      const productMarketRipenessField = $(newForm).find('select[name$="-product_ripeness"]');
      const productPackagingField = $(newForm).find('select[name$="-product_packaging"]');
      const productAmountPerPackagingField = $(newForm).find('input[name$="-product_amount_per_packaging"]');
      const productPresentationQuantityPerPackagingField = $(newForm).find('input[name$="-product_presentation_quantity_per_packaging"]');

      const quantityField = $(newForm).find('input[name$="-quantity"]');
      const unitPriceField = $(newForm).find('input[name$="-unit_price"]');
      const amountPriceField = $(newForm).find('input[name$="-amount_price"]');


      amountPriceField.prop('disabled', true).attr('readonly', true).addClass('readonly-field');

      productSizeField.closest('.form-group').hide();
      productPhenologyField.closest('.form-group').hide();
      productMarketClassField.closest('.form-group').hide();
      productMarketRipenessField.closest('.form-group').hide();
      productPackagingField.closest('.form-group').hide();

      updateFieldOptions(productSizeField, []);
      updateFieldOptions(productPackagingField, []);

      updateProductOptions().then(() => {
        updateFieldOptions(productSizeField, productSizeOptions);
        updateFieldOptions(productPhenologyField, productPhenologyOptions);
        updateFieldOptions(productMarketClassField, productMarketClassOptions);
        updateFieldOptions(productMarketRipenessField, productRipenessOptions);
      });

      pricingByField.on('change', () => {
        if (pricingByField.val()) {
          if (pricingByField.val() === 'product_presentation') {
            productSizeCategories = 'size'
          } else {
            if (clientProperties.country === organization.country) {
              productSizeCategories = 'size,mix'
            } else {
              productSizeCategories = 'size'
            }
          }
          fetchOptions(`/rest/v1/catalogs/product-size/?market=${clientProperties.market}&product=${productProperties.id}&categories=${productSizeCategories}&is_enabled=1`)
            .then(data => {
              updateFieldOptions(productSizeField, data);
              productSizeField.closest('.form-group').fadeIn();
            });
        } else {
          updateFieldOptions(productSizeField, []);
          productSizeField.closest('.form-group').fadeOut();
        }
      })

      productSizeField.on('change', () => {
        if (productSizeField.val()) {
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
          } else {
            productPhenologyField.val(null).trigger('change');
            productMarketClassField.val(null).trigger('change');
            productMarketRipenessField.val(null).trigger('change');
            productPhenologyField.closest('.form-group').fadeOut();
            productMarketClassField.closest('.form-group').fadeOut();
            productMarketRipenessField.closest('.form-group').fadeOut();
          }

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
          } else {
            productPhenologyField.val(null).trigger('change');
            productMarketClassField.val(null).trigger('change');
            productMarketRipenessField.val(null).trigger('change');
            productPhenologyField.closest('.form-group').fadeOut();
            productMarketClassField.closest('.form-group').fadeOut();
            productMarketRipenessField.closest('.form-group').fadeOut();
          }

          let queryParams = {
            category: "packaging",
            market: clientProperties.market,
            product: productProperties.id,
            product_size: productSizeField.val(),
            is_enabled: 1
          }

          if (productPhenologyField.val()) {
            queryParams.phenology = productPhenologyField.val();
          }

          if (pricingByField.val() === 'product_presentation') {
            queryParams.category = "presentation";
          } else {
            queryParams.category = "packaging";
          }

          const url = `/rest/v1/catalogs/product-packaging/?${$.param(queryParams)}`;

          fetchOptions(url)
            .then(data => {
              if (data.length === 0) {
                Swal.fire({
                  icon: "info",
                  text: "No packaging found for the selected product size and pricing category, it must exists at least one for this combination at 'Product Packaging' catalog.",
                  showCancelButton: true,
                  confirmButtonText: "Entendido",
                  cancelButtonText: "Cerrar",
                  confirmButtonColor: "#4daf50",
                  cancelButtonColor: "#d33",
                  allowOutsideClick: false,
                  allowEscapeKey: false,
                })
                updateFieldOptions(productPackagingField, []);
                productPackagingField.closest('.form-group').fadeOut();
              }
              updateFieldOptions(productPackagingField, data);
              productPackagingField.closest('.form-group').fadeIn();
            });


        } else {
          updateFieldOptions(productPackagingField, []);
          productPackagingField.closest('.form-group').fadeOut();
        }

      });

      productPackagingField.on('change', () => {
        if (productPackagingField.val()) {
          fetchOptions(`/rest/v1/catalogs/product-packaging/${productPackagingField.val()}/`)
            .then(data => {
              productAmountPerPackagingField.val(data.product_amount_per_packaging);
              if (data.product_presentation) {
                productPresentationQuantityPerPackagingField.val(data.product_presentation_quantity_per_packaging);
              } else {
                productPresentationQuantityPerPackagingField.val(null);
              }
            })
        } else {
          productAmountPerPackagingField.val(null);
          productPresentationQuantityPerPackagingField.val(null);
        }
      })

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


  const existingForms = $('div[id^="orderitempackaging_set-"]').filter((index, form) => {
    return /\d+$/.test(form.id);
  });

  existingForms.each((index, form) => {
    const productSizeField = $(form).find(`select[name$="${index}-product_size"]`);
    const productPhenologyField = $(form).find(`select[name$="${index}-product_phenology"]`);
    const productMarketClassField = $(form).find(`select[name$="${index}-product_market_class"]`);
    const productMarketRipenessField = $(form).find(`select[name$="${index}-product_ripeness"]`);
    const quantityField = $(form).find(`input[name$="${index}-quantity"]`);
    const unitPriceField = $(form).find(`input[name$="${index}-unit_price"]`);
    const amountPriceField = $(form).find(`input[name$="${index}-amount_price"]`);

    amountPriceField.prop('disabled', true).attr('readonly', true).addClass('readonly-field');

    productSizeField.closest('.form-group').hide();
    productPhenologyField.closest('.form-group').hide();
    productMarketClassField.closest('.form-group').hide();
    productMarketRipenessField.closest('.form-group').hide();

    // const productSize = productSizeField.val();


    fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
      .then(data => {
        productProperties = data;
      })
      .then(() => {
        fetchOptions(`/rest/v1/catalogs/client/${clientField.val()}/`)
          .then(data => {
            clientProperties = data;
          })
      })
      .then(() => {
        updateProductOptions()
          .then(() => {
            updateFieldOptions(productSizeField, productSizeOptions, productSizeField.val());
            updateFieldOptions(productPhenologyField, productPhenologyOptions, productPhenologyField.val());
            updateFieldOptions(productMarketClassField, productMarketClassOptions, productMarketClassField.val());
            updateFieldOptions(productMarketRipenessField, productRipenessOptions, productMarketRipenessField.val());
          })
          .then(() => {
            productSizeField.closest('.form-group').fadeIn();
          })
      })

    productSizeField.on('change', () => {
      const productSizeSelectedOption = productSizeField.find('option:selected');
      const productSizeSelectedOptionCategory = productSizeSelectedOption.data('category');

      if (productSizeField.val() && productSizeSelectedOptionCategory) {
        if (['size'].includes(productSizeSelectedOptionCategory)) {
          productPhenologyField.closest('.form-group').fadeIn();
          productMarketClassField.closest('.form-group').fadeIn();
          productMarketRipenessField.closest('.form-group').fadeIn();
        } else if (['mix'].includes(productSizeSelectedOptionCategory)) {
          productPhenologyField.closest('.form-group').fadeOut();
          productMarketClassField.closest('.form-group').fadeOut();
          productMarketRipenessField.closest('.form-group').fadeIn();
          productPhenologyField.val(null).trigger('change');
          productMarketClassField.val(null).trigger('change');
        } else {
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
});
