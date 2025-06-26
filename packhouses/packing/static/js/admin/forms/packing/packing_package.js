document.addEventListener("DOMContentLoaded", async function () {
  const batchField = $("#id_batch")
  const marketField = $("#id_market")
  const productSizeField = $("#id_product_size")
  const productMarketClassField = $("#id_product_market_class")
  const productRipenessField = $("#id_product_ripeness")
  const sizePackagingField = $("#id_size_packaging")
  const productWeightPerPackagingField = $("#id_product_weight_per_packaging")
  const productPresentationsPerPackagingField = $("#id_product_presentations_per_packaging")
  const productPiecesPerPresentationField = $("#id_product_pieces_per_presentation")
  const packagingQuantityField = $("#id_packaging_quantity")
  const packingPalletField = $("#id_packing_pallet")
  const statusField = $("#id_status")

  let batchProperties = null
  let statusOptions = [
    {value: 'open', name: 'Open'},
    {value: 'ready', name: 'Ready'},
  ]

  if (statusField.val() === 'closed') {
    statusOptions.push({value: 'closed', name: 'Closed'});
  }

  console.log(statusField.val())
  updateFieldOptions(statusField, statusOptions, statusField.val());

  productPresentationsPerPackagingField.closest('.form-group').hide()
  productPiecesPerPresentationField.closest('.form-group').hide()

  productWeightPerPackagingField.attr('min', 1);
  packagingQuantityField.attr('min', 1);

  function updateFieldOptions(field, options, selectedValue = null) {
    if (field) {
      field.empty();
      if (!field.prop('multiple')) {
        field.append(new Option('---------', '', true, !selectedValue));
      }
      console.log("selectedValue", selectedValue)
      const selected = selectedValue === "" || selectedValue === null || selectedValue === undefined
        ? null
        : (isNaN(parseInt(selectedValue)) ? selectedValue : parseInt(selectedValue));
      console.log("selected", selected)
      options.forEach(option => {
        const newOption = new Option(option.name, option.id, false, option.id ? selected === option.id : option.value ? selected === option.value : null );
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

  const getBatchProperties = async () => {
    if (batchField.val()) {
      batchProperties = await fetchOptions(`/rest/v1/receiving/batch/${batchField.val()}/`)
    } else {
      batchProperties = null;
    }
  }

  const setProductSizes = async () => {
    if (batchProperties && batchProperties.product && marketField.val()) {
      console.log("setProductSizes", batchProperties.product)
      const sizes = await fetchOptions(`/rest/v1/catalogs/product-size/?product=${batchProperties.product.id}&market=${marketField.val()}&category=size&is_enabled=1`);
      console.log("Sizes fetched:", sizes);
      console.log("productSizeField.val()", productSizeField.val());
      updateFieldOptions(productSizeField, sizes, productSizeField.val() ? productSizeField.val() : null);
    } else {
      if (productSizeField.val()) {
        const size = await fetchOptions(`/rest/v1/catalogs/product-size/${productSizeField.val()}/`);
        updateFieldOptions(productSizeField, [size], productSizeField.val());
      }
      updateFieldOptions(productSizeField, []);
    }
  }

  const setPackingPallets = async () => {
    if (productSizeField.val()) {
      const pallets = await fetchOptions(`/rest/v1/packing/packing-pallet/?product=${batchProperties.product.id}&market=${marketField.val()}&product_sizes=${productSizeField.val()}&status=ready`);
      console.log("Packing pallets fetched:", pallets);
      updateFieldOptions(packingPalletField, pallets, packingPalletField.val() ? packingPalletField.val() : null);
    } else {
      if (packingPalletField.val()) {
        const pallet = await fetchOptions(`/rest/v1/packing/packing-pallet/${packingPalletField.val()}/`);
        updateFieldOptions(packingPalletField, [pallet], packingPalletField.val());
      }
      updateFieldOptions(packingPalletField, []);
    }
  }

  const setProductMarketClasses = async () => {
    if (batchProperties && batchProperties.product && marketField.val()) {
      const classes = await fetchOptions(`/rest/v1/catalogs/product-market-class/?product=${batchProperties.product.id}&market=${marketField.val()}&is_enabled=1`);
      updateFieldOptions(productMarketClassField, classes, productMarketClassField.val());
    } else {
      if (productMarketClassField.val()) {
        const marketClass = await fetchOptions(`/rest/v1/catalogs/product-market-class/${productMarketClassField.val()}/`);
        updateFieldOptions(productMarketClassField, [marketClass], productMarketClassField.val());
      }
      updateFieldOptions(productMarketClassField, []);
    }
  }

  const setProductRipeness = async () => {
    if (batchProperties && batchProperties.product && marketField.val()) {
      const ripeness = await fetchOptions(`/rest/v1/catalogs/product-ripeness/?product=${batchProperties.product.id}&market=${marketField.val()}&is_enabled=1`);
      updateFieldOptions(productRipenessField, ripeness, productRipenessField.val() ? productRipenessField.val() : null);
    } else {
      if (productRipenessField.val()) {
        const ripeness = await fetchOptions(`/rest/v1/catalogs/product-ripeness/${productRipenessField.val()}/`);
        updateFieldOptions(productRipenessField, [ripeness], productRipenessField.val());
      }
      updateFieldOptions(productRipenessField, []);
    }
  }

  const setSizePackagings = async () => {
    if (batchProperties && batchProperties.product && marketField.val() && productSizeField.val()) {
      const packagings = await fetchOptions(`/rest/v1/catalogs/size-packaging/?product=${batchProperties.product.id}&market=${marketField.val()}&product_size=${productSizeField.val()}&is_enabled=1`);
      updateFieldOptions(sizePackagingField, packagings, sizePackagingField.val() ? sizePackagingField.val() : null);
    } else {
      if (sizePackagingField.val()) {
        const packaging = await fetchOptions(`/rest/v1/catalogs/size-packaging/${sizePackagingField.val()}/`);
        updateFieldOptions(sizePackagingField, [packaging], sizePackagingField.val());
      }
      updateFieldOptions(sizePackagingField, []);
    }
  }

  const batchFieldChangeHandler = async () => {
    await getBatchProperties();
    if (batchProperties) {
      console.log("Batch properties:", batchProperties);
      const market = batchProperties.market;
      marketField.val(market.id).trigger('change');
    }
  }

  const marketFieldChangeHandler = async () => {
    await setProductSizes();
    await setProductMarketClasses();
    await setProductRipeness();
    await setSizePackagings();
  }

  const productSizeFieldChangeHandler = async () => {
    if (productSizeField.val()) {
      await setSizePackagings();
    }
  }

  const sizePackagingFieldChangeHandler = async () => {
    if (sizePackagingField.val()) {
      const packaging = await fetchOptions(`/rest/v1/catalogs/size-packaging/${sizePackagingField.val()}/`);
      productWeightPerPackagingField.val(packaging.product_weight_per_packaging);

      if (packaging.category === 'presentation') {
        productPresentationsPerPackagingField.closest('.form-group').fadeIn();
        productPiecesPerPresentationField.closest('.form-group').fadeIn();
        productPresentationsPerPackagingField.val(packaging.product_presentations_per_packaging);
        productPiecesPerPresentationField.val(packaging.product_pieces_per_presentation);
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
    await batchFieldChangeHandler();
  });

  marketField.on("change", async function () {
    await marketFieldChangeHandler();
  });

  productSizeField.on("change", async function () {
    await productSizeFieldChangeHandler();
    await setPackingPallets();
  });

  sizePackagingField.on("change", async function () {
    await sizePackagingFieldChangeHandler();
    if (batchProperties && sizePackagingField.val()) {
      packagingQuantityField.attr('max', batchProperties.available_weight / parseInt(productWeightPerPackagingField.val()));
      if (!packagingQuantityField.val()) {
        packagingQuantityField.val(parseInt(batchProperties.available_weight / parseInt(productWeightPerPackagingField.val())));
      }
    } else {
      packagingQuantityField.attr('max', null);
    }
  });

  statusField.on("change", function () {
    console.log("Status changed to:", statusField.val());
    if (statusField.val() === 'open') {
      packingPalletField.val(null).trigger('change');
    }
  });

  packingPalletField.on("change", async function () {
    if (packingPalletField.val()) {
      statusField.val('ready').trigger('change');
    }
  });

  await getBatchProperties();
  await setProductSizes();
  await setProductMarketClasses();
  await setProductRipeness();
  await setSizePackagings();

});
