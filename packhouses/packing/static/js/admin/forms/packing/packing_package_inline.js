document.addEventListener("DOMContentLoaded", async function () {
  const productField = $("#id_product");
  const marketField = $("#id_market");
  const productSizesField = $("#id_product_sizes");
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
    if (productField.val()) {
      productProperties = await fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
    } else {
      productProperties = null;
    }
  }

  const getMarketProperties = async () => {
    if (marketField.val()) {
      marketProperties = await fetchOptions(`/rest/v1/catalogs/market/${marketField.val()}/`)
    } else {
      marketProperties = null;
    }
  }

  const getPalletProperties = async () => {
    if (marketField.val()) {
      palletProperties = await fetchOptions(`/rest/v1/catalogs/pallet/${palletField.val()}/`)
    } else {
      palletProperties = null;
    }
  }

  const getProductSizesOptions = async () => {
    if (productSizesField.val()) {
      productSizesOptions = await fetchOptions(`/rest/v1/catalogs/product-size/?is_enabled=1&id__in=${productSizesField.val().join(",")}`)
    } else {
      productSizesOptions = [];
    }
  }

  const getProductMarketClassOptions = async () => {
    if (productField.val() && marketField.val()) {
      productMarketClassOptions = await fetchOptions(`/rest/v1/catalogs/product-market-class/?product=${productField.val()}&market=${marketField.val()}&is_enabled=1`);
    } else {
      productMarketClassOptions = [];
    }
  }

  const getProductRipenessOptions = async () => {
    if (productField.val()) {
      productRipenessOptions = await fetchOptions(`/rest/v1/catalogs/product-ripeness/?product=${productField.val()}&is_enabled=1`);
    } else {
      productRipenessOptions = [];
    }
  }

  productField.on("change", async function () {
    await getProductProperties();
  })

  marketField.on("change", async function () {
    await getMarketProperties();
  });

  productSizesField.on("change", async function () {
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
  });

});
