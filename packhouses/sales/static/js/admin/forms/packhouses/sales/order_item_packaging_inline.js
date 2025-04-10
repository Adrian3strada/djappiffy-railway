document.addEventListener('DOMContentLoaded', async () => {
  const productField = $("#id_product");
  const clientField = $("#id_client");
  const orderItemsKindField = $("#id_order_items_kind")

  let productPhenologyOptions = [];
  let productMarketClassOptions = [];
  let productRipenessOptions = [];
  let productPriceOptions = []

  let clientProperties = null;
  let productProperties = null;
  let organization = null;
  let isNationalClient = false;

  function updateFieldOptions(field, options, selectedValue = null) {
    if (field) {
      field.empty();
      if (!field.prop('multiple')) {
        field.append(new Option('---------', '', true, !selectedValue));
      }
      const selected = selectedValue ? parseInt(selectedValue) || selectedValue : null;
      options.forEach(option => {
        const newOption = new Option(option.name, option.id, false, selected === option.id);
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

  function getProductOptions() {
    return new Promise((resolve, reject) => {
      if (clientProperties && productProperties && orderItemsKindField) {

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

        Promise.all([productPhenologyPromise, productMarketClassPromise, productRipenessPromise])
          .then(() => resolve())
          .catch(error => reject(error));
      } else {
        productPhenologyOptions = [];
        productMarketClassOptions = [];
        resolve();
      }
    });
  }

  async function getClientProperties() {
    if (clientField.val()) {
      clientProperties = await fetchOptions(`/rest/v1/catalogs/client/${clientField.val()}/`)
      console.log("clientProperties", clientProperties);
    } else {
      clientProperties = null;
    }
  }

  async function getProductProperties() {
    if (productField.val()) {
      productProperties = await fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
      console.log("function productProperties", productProperties);
    } else {
      productProperties = null;
    }
  }

  function getOrganizationProfile() {
    return fetchOptions(`/rest/v1/profiles/packhouse-exporter-profile/?same=1`).then(
      (data) => {
        if (data.count === 1) {
          organization = data.results.pop()
        }
      });
  }

  await getOrganizationProfile()
  await getClientProperties()
  await getProductProperties()

  function setIsNationalClient() {
    if (clientProperties && organization) {
      isNationalClient = clientProperties.country === organization.country;
    } else {
      isNationalClient = false;
    }
    if (isNationalClient) {
      productPriceOptions = [
        {id: "product_weight", name: "Product weight"},
        {id: "product_packaging", name: "Product packaging"},
        {id: "product_presentation", name: "Product presentation"}
      ]
    } else {
      productPriceOptions = [
        {id: "product_packaging", name: "Product packaging"},
        {id: "product_presentation", name: "Product presentation"}
      ]
    }
  }

  await setIsNationalClient();

  clientField.on('change', async () => {
    await getClientProperties();
    await setIsNationalClient();
  })

  productField.on('change', async () => {
    await getProductProperties();
  })

  if (clientField.val()) {
    await getClientProperties();
    await setIsNationalClient();
  }

  if (productField.val()) {
    await getProductProperties();
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
      const productWeightPerPackagingField = $(newForm).find('input[name$="-product_weight_per_packaging"]');
      const productPresentationsPerPackagingField = $(newForm).find('input[name$="-product_presentations_per_packaging"]');
      const productPiecesPerPresentationField = $(newForm).find('input[name$="-product_pieces_per_presentation"]');

      const quantityField = $(newForm).find('input[name$="-quantity"]');
      const unitPriceField = $(newForm).find('input[name$="-unit_price"]');
      const amountPriceField = $(newForm).find('input[name$="-amount_price"]');

      let productSizeCategories = 'size,mix';

      amountPriceField.prop('disabled', true).attr('readonly', true).addClass('readonly-field');

      productPhenologyField.closest('.form-group').hide();
      productMarketClassField.closest('.form-group').hide();

      updateFieldOptions(productSizeField, []);
      updateFieldOptions(productPackagingField, []);

      getProductOptions().then(() => {
        updateFieldOptions(pricingByField, productPriceOptions);
        updateFieldOptions(productPhenologyField, productPhenologyOptions);
        updateFieldOptions(productMarketClassField, productMarketClassOptions);
        updateFieldOptions(productMarketRipenessField, productRipenessOptions);
      });

      pricingByField.on('change', () => {
        if (pricingByField.val()) {
          if (isNationalClient) {
            productSizeCategories = 'size,mix'
            if (pricingByField.val() === 'product_presentation') {
              productSizeCategories = 'size'
            }
          } else {
            productSizeCategories = 'size'
          }
          fetchOptions(`/rest/v1/catalogs/product-size/?market=${clientProperties.market}&product=${productProperties.id}&categories=${productSizeCategories}&is_enabled=1`)
            .then(data => {
              updateFieldOptions(productSizeField, data);
            });
        } else {
          updateFieldOptions(productSizeField, []);
        }
      })

      productSizeField.on('change', () => {
        if (productSizeField.val()) {
          const productSizeSelectedOption = productSizeField.find('option:selected');
          const productSizeSelectedOptionCategory = productSizeSelectedOption.data('category');

          if (productSizeField.val() && productSizeSelectedOptionCategory) {

            if (productSizeSelectedOptionCategory === 'size') {
              productPhenologyField.closest('.form-group').fadeIn();
              productMarketClassField.closest('.form-group').fadeIn();
              productMarketRipenessField.closest('.form-group').fadeIn();
            }
            if (productSizeSelectedOptionCategory === 'mix') {
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
            market: clientProperties.market,
            product: productProperties.id,
            product_size: productSizeField.val(),
            is_enabled: 1
          }

          if (productSizeSelectedOptionCategory === 'mix') {
            queryParams.category = "single";
          }

          if (pricingByField.val() === 'product_presentation' && productSizeSelectedOptionCategory === 'size') {
            queryParams.category = "presentation";
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
              }
              updateFieldOptions(productPackagingField, data);
            });

        } else {
          updateFieldOptions(productPackagingField, []);
        }
      });

      productPackagingField.on('change', () => {
        productWeightPerPackagingField.val(null);
        productPresentationsPerPackagingField.val(null);
        productPiecesPerPresentationField.val(null);
        productPresentationsPerPackagingField.closest('.form-group').fadeOut();
        productPiecesPerPresentationField.closest('.form-group').fadeOut();
        if (productPackagingField.val()) {
          fetchOptions(`/rest/v1/catalogs/product-packaging/${productPackagingField.val()}/`)
            .then(data => {
              productWeightPerPackagingField.val(data.product_weight_per_packaging);
              if (data.product_presentation) {
                productPresentationsPerPackagingField.val(data.product_presentations_per_packaging);
                productPiecesPerPresentationField.val(data.product_pieces_per_presentation)
                productPresentationsPerPackagingField.closest('.form-group').fadeIn();
                productPiecesPerPresentationField.closest('.form-group').fadeIn();
              } else {
                productPresentationsPerPackagingField.val(null);
                productPresentationsPerPackagingField.closest('.form-group').fadeOut();
                productPiecesPerPresentationField.closest('.form-group').fadeOut();
              }
            })
        }
      })

      function setAmountPrice() {
        let amountPrice = 0;

        if (pricingByField.val() === 'product_weight') {
          if (unitPriceField.val() && quantityField.val() && productWeightPerPackagingField.val() && unitPriceField.val() > 0 && quantityField.val() > 0 && productWeightPerPackagingField.val() > 0) {
            amountPrice = unitPriceField.val() * quantityField.val() * productWeightPerPackagingField.val();
          }
        }

        if (pricingByField.val() === 'product_packaging') {
          if (unitPriceField.val() && quantityField.val() && unitPriceField.val() > 0 && quantityField.val() > 0) {
            amountPrice = unitPriceField.val() * quantityField.val();
          }
        }

        if (pricingByField.val() === 'product_presentation') {
          if (unitPriceField.val() && quantityField.val() && productPresentationsPerPackagingField.val() && unitPriceField.val() > 0 && quantityField.val() > 0 && productPresentationsPerPackagingField.val() > 0) {
            amountPrice = unitPriceField.val() * quantityField.val() * productPresentationsPerPackagingField.val()
          }
        }

        amountPriceField.val(amountPrice);
      }

      quantityField.on('change', () => {
        setAmountPrice();
      })

      unitPriceField.on('change', () => {
        setAmountPrice();
      })

      productWeightPerPackagingField.on('change', () => {
        setAmountPrice();
      })

      productPresentationsPerPackagingField.on('change', () => {
        setAmountPrice();
      })

    }
  });


  setTimeout(async () => {

    await setIsNationalClient();

    const existingForms = $('div[id^="orderitempackaging_set-"]').filter((index, form) => {
      return /^\d+$/.test(form.id.split('-').pop());
    });

    existingForms.each(async (index, form) => {
      console.log("existingForms", index, form)
      const pricingByField = $(form).find(`select[name$="${index}-pricing_by"]`);
      const productSizeField = $(form).find(`select[name$="${index}-product_size"]`);
      const productPhenologyField = $(form).find(`select[name$="${index}-product_phenology"]`);
      const productMarketClassField = $(form).find(`select[name$="${index}-product_market_class"]`);
      const productMarketRipenessField = $(form).find(`select[name$="${index}-product_ripeness"]`);
      const productPackagingField = $(form).find(`select[name$="${index}-product_packaging"]`);
      const productWeightPerPackagingField = $(form).find(`input[name$="${index}-product_weight_per_packaging"]`);
      const productPresentationsPerPackagingField = $(form).find(`input[name$="${index}-product_presentations_per_packaging"]`);
      const productPiecesPerPresentationField = $(form).find(`input[name$="${index}-product_pieces_per_presentation"]`);
      const quantityField = $(form).find(`input[name$="${index}-quantity"]`);
      const unitPriceField = $(form).find(`input[name$="${index}-unit_price"]`);
      const amountPriceField = $(form).find(`input[name$="${index}-amount_price"]`);

      let productSizeCategories = 'size,mix';

      amountPriceField.prop('disabled', true).attr('readonly', true).addClass('readonly-field');

      if (!productPhenologyField.val()) productPhenologyField.closest('.form-group').hide();
      if (!productMarketClassField.val()) productMarketClassField.closest('.form-group').hide();

      getProductOptions().then(() => {
        updateFieldOptions(pricingByField, productPriceOptions, pricingByField.val());
        updateFieldOptions(productPhenologyField, productPhenologyOptions, productPhenologyField.val());
        updateFieldOptions(productMarketClassField, productMarketClassOptions, productMarketClassField.val());
        updateFieldOptions(productMarketRipenessField, productRipenessOptions, productMarketRipenessField.val());
      });

      if (pricingByField.val()) {
        if (isNationalClient) {
          productSizeCategories = 'size,mix'
          if (pricingByField.val() === 'product_presentation') {
            productSizeCategories = 'size'
          }
        } else {
          productSizeCategories = 'size'
        }
        fetchOptions(`/rest/v1/catalogs/product-size/?market=${clientProperties.market}&product=${productProperties.id}&categories=${productSizeCategories}&is_enabled=1`)
          .then(data => {
            updateFieldOptions(productSizeField, data, productSizeField.val());
          });
      }

      pricingByField.on('change', () => {
        if (pricingByField.val()) {
          if (isNationalClient) {
            productSizeCategories = 'size,mix'
            if (pricingByField.val() === 'product_presentation') {
              productSizeCategories = 'size'
            }
          } else {
            productSizeCategories = 'size'
          }
          fetchOptions(`/rest/v1/catalogs/product-size/?market=${clientProperties.market}&product=${productProperties.id}&categories=${productSizeCategories}&is_enabled=1`)
            .then(data => {
              updateFieldOptions(productSizeField, data, productSizeField.val());
            });
        } else {
          updateFieldOptions(productSizeField, []);
        }
      })

      productSizeField.on('change', () => {
        if (productSizeField.val()) {
          console.log("productSizeField", productSizeField)
          const productSizeSelectedOption = productSizeField.find('option:selected');
          const productSizeSelectedOptionCategory = productSizeSelectedOption.data('category');

          console.log("productSizeSelectedOption", productSizeSelectedOption)
          console.log("productSizeSelectedOptionCategory", productSizeSelectedOptionCategory)

          if (productSizeField.val() && productSizeSelectedOptionCategory) {

            if (productSizeSelectedOptionCategory === 'size') {
              productPhenologyField.closest('.form-group').fadeIn();
              productMarketClassField.closest('.form-group').fadeIn();
              productMarketRipenessField.closest('.form-group').fadeIn();
            }
            if (productSizeSelectedOptionCategory === 'mix') {
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
            market: clientProperties.market,
            product: productProperties.id,
            product_size: productSizeField.val(),
            is_enabled: 1
          }

          if (productSizeSelectedOptionCategory === 'mix') {
            queryParams.category = "single";
          }

          if (pricingByField.val() === 'product_presentation' && productSizeSelectedOptionCategory === 'size') {
            queryParams.category = "presentation";
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
              }
              updateFieldOptions(productPackagingField, data, productPackagingField.val());
            });

        } else {
          updateFieldOptions(productPackagingField, []);
        }
      });

      productPackagingField.on('change', () => {
        productWeightPerPackagingField.val(null);
        productPresentationsPerPackagingField.val(null);
        productPiecesPerPresentationField.val(null);
        productPresentationsPerPackagingField.closest('.form-group').fadeOut();
        productPiecesPerPresentationField.closest('.form-group').fadeOut();
        if (productPackagingField.val()) {
          fetchOptions(`/rest/v1/catalogs/product-packaging/${productPackagingField.val()}/`)
            .then(data => {
              productWeightPerPackagingField.val(data.product_weight_per_packaging);
              if (data.product_presentation) {
                productPresentationsPerPackagingField.val(data.product_presentations_per_packaging);
                productPiecesPerPresentationField.val(data.product_pieces_per_presentation)
                productPresentationsPerPackagingField.closest('.form-group').fadeIn();
                productPiecesPerPresentationField.closest('.form-group').fadeIn();
              } else {
                productPresentationsPerPackagingField.val(null);
                productPresentationsPerPackagingField.closest('.form-group').fadeOut();
                productPiecesPerPresentationField.closest('.form-group').fadeOut();
              }
            })
        }
      })

      function setAmountPrice() {
        let amountPrice = 0;
        alert(pricingByField.val())

        if (pricingByField.val() === 'product_weight') {
          if (unitPriceField.val() && quantityField.val() && productWeightPerPackagingField.val() && unitPriceField.val() > 0 && quantityField.val() > 0 && productWeightPerPackagingField.val() > 0) {
            amountPrice = unitPriceField.val() * quantityField.val() * productWeightPerPackagingField.val();
          }
        }

        if (pricingByField.val() === 'product_packaging') {
          if (unitPriceField.val() && quantityField.val() && unitPriceField.val() > 0 && quantityField.val() > 0) {
            amountPrice = unitPriceField.val() * quantityField.val();
          }
        }

        if (pricingByField.val() === 'product_presentation') {
          if (unitPriceField.val() && quantityField.val() && productPresentationsPerPackagingField.val() && unitPriceField.val() > 0 && quantityField.val() > 0 && productPresentationsPerPackagingField.val() > 0) {
            amountPrice = unitPriceField.val() * quantityField.val() * productPresentationsPerPackagingField.val()
          }
        }

        amountPriceField.val(amountPrice);
      }

      quantityField.on('change', () => {
        setAmountPrice();
      })

      unitPriceField.on('change', () => {
        setAmountPrice();
      })

      productWeightPerPackagingField.on('change', () => {
        setAmountPrice();
      })

      productPresentationsPerPackagingField.on('change', () => {
        setAmountPrice();
      })

    });

  }, 300)

});
