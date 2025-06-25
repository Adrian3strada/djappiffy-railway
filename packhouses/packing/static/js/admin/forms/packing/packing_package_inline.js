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
      console.log("Product sizes options fetched getProductSizesOptions:", productSizesOptions);
    } else {
      productSizesOptions = [];
    }
  }

  const getProductMarketClassOptions = async () => {
    if (palletProductField.val() && palletMarketField.val()) {
      productMarketClassOptions = await fetchOptions(`/rest/v1/catalogs/product-market-class/?product=${palletProductField.val()}&market=${palletMarketField.val()}&is_enabled=1`);
      console.log("Product market class options fetched getProductMarketClassOptions:", productMarketClassOptions);
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
    const productWeightPerPackagingField = $(newForm).find('select[name$="-product_weight_per_packaging"]');
    const productPresentationsPerPackagingField = $(newForm).find('select[name$="-product_presentations_per_packaging"]');
    const productPiecesPerPresentationField = $(newForm).find('select[name$="-product_pieces_per_presentation"]');
    const packagingQuantityField = $(newForm).find('select[name$="-packaging_quantity"]');

    console.log("New form added:", newForm);

    marketField.val(palletMarketField.val()).trigger('change').select2()
    marketField.prop('disabled', true);

    productSizeField.on('change', async function () {
      if (productSizeField.val() && marketProperties.id && productProperties.id) {
      const sizePackagings = await fetchOptions(`/rest/v1/catalogs/size-packaging/?product_size=${productSizeField.val()}&product_packaging__market=${marketProperties.id}&product_packaging__product=${productProperties.id}&is_enabled=1`);
      console.log("Size packagings fetched:", sizePackagings);
      }
    });

    updateFieldOptions(productSizeField, productSizesOptions, productSizeField.val() ? productSizeField.val() : null);
    updateFieldOptions(productMarketClassField, productMarketClassOptions, productMarketClassField.val() ? productMarketClassField.val() : null);
    updateFieldOptions(productRipenessField, productRipenessOptions, productRipenessField.val() ? productRipenessField.val() : null);
  });

});
