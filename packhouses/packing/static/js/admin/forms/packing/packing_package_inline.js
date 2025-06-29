document.addEventListener("DOMContentLoaded", async function () {
  const palletProductField = $("#id_product");
  const palletMarketField = $("#id_market");
  const palletProductSizesField = $("#id_product_sizes");
  const palletField = $("#id_pallet");

  let productProperties = null;
  let marketProperties = null;
  let palletProperties = null;

  let productSizesOptions = [];
  let productMarketClassOptions = [];
  let productRipenessOptions = [];

  let availableBatches = await fetchOptions(`/rest/v1/receiving/batch/?status=ready&parent__isnull=1`);
  console.log("Available batches fetched:", availableBatches);

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
      method: "GET",
      dataType: "json",
    }).fail((error) => console.error("Fetch error:", error));
  }

  const getProductProperties = async () => {
    if (palletProductField.val()) {
      productProperties = await fetchOptions(`/rest/v1/catalogs/product/${palletProductField.val()}/`)
      console.log("Product properties fetched getProductProperties:", productProperties);
    } else {
      productProperties = null;
    }
  }

  const getMarketProperties = async () => {
    if (palletMarketField.val()) {
      marketProperties = await fetchOptions(`/rest/v1/catalogs/market/${palletMarketField.val()}/`)
      console.log("Market properties fetched getMarketProperties:", marketProperties);
    } else {
      marketProperties = null;
    }
  }

  const getPalletProperties = async () => {
    if (palletField.val()) {
      palletProperties = await fetchOptions(`/rest/v1/catalogs/pallet/${palletField.val()}/`)
    } else {
      palletProperties = null;
    }
  }

  const getProductSizesOptions = async () => {
    if (palletProductSizesField.val() && palletMarketField.val()) {
      productSizesOptions = await fetchOptions(`/rest/v1/catalogs/product-size/?is_enabled=1&id__in=${palletProductSizesField.val().join(",")}`)
    } else {
      productSizesOptions = [];
    }
  }

  const getProductMarketClassOptions = async () => {
    if (palletProductField.val() && palletMarketField.val()) {
      productMarketClassOptions = await fetchOptions(`/rest/v1/catalogs/product-market-class/?product=${palletProductField.val()}&market=${palletMarketField.val()}&is_enabled=1`);
    } else {
      productMarketClassOptions = [];
    }
  }

  const getProductRipenessOptions = async () => {
    if (palletProductField.val()) {
      productRipenessOptions = await fetchOptions(`/rest/v1/catalogs/product-ripeness/?product=${palletProductField.val()}&is_enabled=1`);
    } else {
      productRipenessOptions = [];
    }
  }

  const getBatchProperties = async (batchField) => {
    let batchProperties = null;
    if (batchField.val()) {
      batchProperties = await fetchOptions(`/rest/v1/receiving/batch/${batchField.val()}/`)
    }
    return batchProperties;
  }

  const getSizePackagingOptions = async (sizePackagingField, productSize) => {
    if (palletProductSizesField.val() && palletMarketField.val() && productSize) {
      const sizePackagings = await fetchOptions(`/rest/v1/catalogs/size-packaging/?product_packaging__market=${palletMarketField.val()}&product_packaging__product=${palletProductField.val()}&product_size=${productSize}&is_enabled=1`);
      if (sizePackagings.length > 0) {
        updateFieldOptions(sizePackagingField, sizePackagings, sizePackagingField.val() ? sizePackagingField.val() : null);
      } else {
        updateFieldOptions(sizePackagingField, []);
      }
    } else {
      updateFieldOptions(sizePackagingField, []);
    }
  }

  palletProductField.on("change", async function () {
    await getProductProperties();
    await getProductSizesOptions();
    await getProductRipenessOptions();
    await getProductMarketClassOptions();
  })

  palletMarketField.on("change", async function () {
    await getMarketProperties();
    await getProductMarketClassOptions();
  });

  palletProductSizesField.on("change", async function () {
    await getProductSizesOptions();
  })

  palletField.on("change", async function () {
    await getPalletProperties();
  });

  await getProductProperties();
  await getMarketProperties();
  await getPalletProperties();
  await getProductSizesOptions();
  await getProductMarketClassOptions();
  await getProductRipenessOptions();

  document.addEventListener('formset:added', (event) => {
    const newForm = event.target;
    const batchField = $(newForm).find('select[name$="-batch"]');
    const marketField = $(newForm).find('select[name$="-market"]');
    const productSizeField = $(newForm).find('select[name$="-product_size"]');
    const productMarketClassField = $(newForm).find('select[name$="-product_market_class"]');
    const productRipenessField = $(newForm).find('select[name$="-product_ripeness"]');
    const sizePackagingField = $(newForm).find('select[name$="-size_packaging"]');
    const productWeightPerPackagingField = $(newForm).find('input[name$="-product_weight_per_packaging"]');
    const productPresentationsPerPackagingField = $(newForm).find('input[name$="-product_presentations_per_packaging"]');
    const productPiecesPerPresentationField = $(newForm).find('input[name$="-product_pieces_per_presentation"]');
    const packagingQuantityField = $(newForm).find('input[name$="-packaging_quantity"]');
    const statusField = $(newForm).find('select[name$="-status"]');

    console.log("New form added:", newForm);

    let batchProperties = null
    let itemWeight = 0;
    let selectedAvailableBatchIndex = 0;

    marketField.closest('.form-group').hide()
    productPresentationsPerPackagingField.closest('.form-group').hide()
    productPiecesPerPresentationField.closest('.form-group').hide()
    statusField.closest('.form-group').hide()
    productWeightPerPackagingField.attr('min', 0);
    marketField.val(palletMarketField.val()).trigger('change').select2()
    sizePackagingField.prop('disabled', true);

    updateFieldOptions(batchField, availableBatches);

    console.log("Available batches:", availableBatches);

    const setItemWeight = async () => {
      setTimeout(() => {
        if (productWeightPerPackagingField.val() && productWeightPerPackagingField.val() > 0 && packagingQuantityField.val() && packagingQuantityField.val() > 0) {
          const prevItemWeight = itemWeight;
          console.log("prevItemWeight", prevItemWeight);
          const newItemWeight = parseFloat(productWeightPerPackagingField.val()) * parseInt(packagingQuantityField.val());
          console.log("newItemWeight", newItemWeight);
          itemWeight = newItemWeight;
          console.log("itemWeight", itemWeight);

          availableBatches[selectedAvailableBatchIndex].available_weight = availableBatches[selectedAvailableBatchIndex].available_weight + prevItemWeight;
          const newAvailableWeight = availableBatches[selectedAvailableBatchIndex].available_weight - newItemWeight;
          availableBatches[selectedAvailableBatchIndex].available_weight = newAvailableWeight
          console.log("newAvailableWeight", newAvailableWeight);
          availableBatches[selectedAvailableBatchIndex].name = availableBatches[selectedAvailableBatchIndex].name.replace(/AW:\d+(\.\d+)?/, `NAW:${newAvailableWeight}`);

          console.log("availableBatches[selectedAvailableBatchIndex].available_weight", availableBatches[selectedAvailableBatchIndex].available_weight);
        }
      }, 300);
    }

    const sizePackagingFieldChangeHandler = async () => {
      if (sizePackagingField.val()) {
        const size_packaging = await fetchOptions(`/rest/v1/catalogs/size-packaging/${sizePackagingField.val()}/`);
        productWeightPerPackagingField.val(size_packaging.product_weight_per_packaging);

        if (size_packaging.category === 'presentation') {
          productPresentationsPerPackagingField.closest('.form-group').fadeIn();
          productPiecesPerPresentationField.closest('.form-group').fadeIn();
          productPresentationsPerPackagingField.val(size_packaging.product_presentations_per_packaging);
          productPiecesPerPresentationField.val(size_packaging.product_pieces_per_presentation);
        } else {
          productPresentationsPerPackagingField.closest('.form-group').fadeOut();
          productPiecesPerPresentationField.closest('.form-group').fadeOut();
          productPresentationsPerPackagingField.val(null);
          productPiecesPerPresentationField.val(null);
        }

      } else {
        productPresentationsPerPackagingField.closest('.form-group').fadeOut();
        productPiecesPerPresentationField.closest('.form-group').fadeOut();
        productPresentationsPerPackagingField.val(null);
        productPiecesPerPresentationField.val(null);
        productWeightPerPackagingField.val(null);
      }
    }

    batchField.on("change", async function () {
      if (batchField.val()) {
        sizePackagingField.prop('disabled', false);
        const batchId = parseInt(batchField.val());
        batchProperties = availableBatches.find(batch => batch.id === batchId) || null;
        selectedAvailableBatchIndex = availableBatches.findIndex(batch => batch.id === batchProperties.id);
        console.log("Batch properties fetched:", batchProperties);
      } else {
        sizePackagingField.prop('disabled', true);
      }
    });

    productSizeField.on('change', async function () {
      if (productProperties.id && marketProperties.id && productSizeField.val()) {
        await getSizePackagingOptions(sizePackagingField, productSizeField.val())
      } else {
        updateFieldOptions(sizePackagingField, []);
      }
    });

    sizePackagingField.on("change", async function () {
      await sizePackagingFieldChangeHandler();
      if (batchProperties && sizePackagingField.val()) {
        packagingQuantityField.attr('max', parseInt(batchProperties.available_weight / parseFloat(productWeightPerPackagingField.val())));
        if (!packagingQuantityField.val()) {
          packagingQuantityField.val(parseInt(batchProperties.available_weight / parseFloat(productWeightPerPackagingField.val())));
        }
        await setItemWeight();
      } else {
        packagingQuantityField.attr('max', null);
      }
    });

    productWeightPerPackagingField.on('change', async function () {
      await setItemWeight();
    });

    packagingQuantityField.on('change', async function () {
      await setItemWeight();
    });

    updateFieldOptions(productSizeField, productSizesOptions, productSizeField.val() ? productSizeField.val() : null);
    updateFieldOptions(productMarketClassField, productMarketClassOptions, productMarketClassField.val() ? productMarketClassField.val() : null);
    updateFieldOptions(productRipenessField, productRipenessOptions, productRipenessField.val() ? productRipenessField.val() : null);
  });

  const existingForms = $('div[id^="packingpackage_set-"]').filter((index, form) => {
    return /^\d+$/.test(form.id.split('-').pop());
  });

  existingForms.each((index, form) => {
    const batchField = $(form).find(`select[name$="${index}-batch"]`);
    const marketField = $(form).find(`select[name$="${index}-market"]`);
    const productSizeField = $(form).find(`select[name$="${index}-product_size"]`);
    const productMarketClassField = $(form).find(`select[name$="${index}-product_market_class"]`);
    const productRipenessField = $(form).find(`select[name$="${index}-product_ripeness"]`);
    const sizePackagingField = $(form).find(`select[name$="${index}-size_packaging"]`);
    const productWeightPerPackagingField = $(form).find(`input[name$="${index}-product_weight_per_packaging"]`);
    const productPresentationsPerPackagingField = $(form).find(`input[name$="${index}-product_presentations_per_packaging"]`);
    const productPiecesPerPresentationField = $(form).find(`input[name$="${index}-product_pieces_per_presentation"]`);
    const packagingQuantityField = $(form).find(`input[name$="${index}-packaging_quantity"]`);
    const statusField = $(form).find(`select[name$="${index}-status"]`);

    console.log("form", index, form)

    marketField.closest('.form-group').hide()
    productPresentationsPerPackagingField.closest('.form-group').hide()
    productPiecesPerPresentationField.closest('.form-group').hide()
    statusField.closest('.form-group').hide()

    let batchProperties = null

    marketField.val(palletMarketField.val()).trigger('change').select2()

    const sizePackagingFieldChangeHandler = async () => {
      if (sizePackagingField.val()) {
        const size_packaging = await fetchOptions(`/rest/v1/catalogs/size-packaging/${sizePackagingField.val()}/`);
        productWeightPerPackagingField.val(size_packaging.product_weight_per_packaging);

        if (size_packaging.category === 'presentation') {
          productPresentationsPerPackagingField.closest('.form-group').fadeIn();
          productPiecesPerPresentationField.closest('.form-group').fadeIn();
          productPresentationsPerPackagingField.val(size_packaging.product_presentations_per_packaging);
          productPiecesPerPresentationField.val(size_packaging.product_pieces_per_presentation);
        } else {
          productPresentationsPerPackagingField.closest('.form-group').fadeOut();
          productPiecesPerPresentationField.closest('.form-group').fadeOut();
          productPresentationsPerPackagingField.val(null);
          productPiecesPerPresentationField.val(null);
        }

      } else {
        productPresentationsPerPackagingField.closest('.form-group').fadeOut();
        productPiecesPerPresentationField.closest('.form-group').fadeOut();
        productPresentationsPerPackagingField.val(null);
        productPiecesPerPresentationField.val(null);
        productWeightPerPackagingField.val(null);
      }
    }

    batchField.on("change", async function () {
      batchProperties = await getBatchProperties(batchField);
      if (batchField.val()) {
        sizePackagingField.prop('disabled', false);
      } else {
        sizePackagingField.prop('disabled', true);
      }
    });

    productSizeField.on('change', async function () {
      if (productProperties.id && marketProperties.id && productSizeField.val()) {
        await getSizePackagingOptions(sizePackagingField, productSizeField.val())
      } else {
        updateFieldOptions(sizePackagingField, []);
      }
    });

    sizePackagingField.on("change", async function () {
      await sizePackagingFieldChangeHandler();
      if (batchProperties && sizePackagingField.val()) {
        packagingQuantityField.attr('max', parseInt(batchProperties.available_weight / parseFloat(productWeightPerPackagingField.val())));
        if (!packagingQuantityField.val()) {
          packagingQuantityField.val(parseInt(batchProperties.available_weight / parseFloat(productWeightPerPackagingField.val())));
        }
      } else {
        packagingQuantityField.attr('max', null);
      }
    });

    updateFieldOptions(productSizeField, productSizesOptions, productSizeField.val() ? productSizeField.val() : null);
    updateFieldOptions(productMarketClassField, productMarketClassOptions, productMarketClassField.val() ? productMarketClassField.val() : null);
    updateFieldOptions(productRipenessField, productRipenessOptions, productRipenessField.val() ? productRipenessField.val() : null);

  });
});
