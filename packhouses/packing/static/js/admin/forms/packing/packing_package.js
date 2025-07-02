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
  const packingPallet = packingPalletField.val();

  productPresentationsPerPackagingField.closest('.form-group').hide()
  productPiecesPerPresentationField.closest('.form-group').hide()

  productWeightPerPackagingField.attr('min', 1);
  productWeightPerPackagingField.attr('step', 0.1);
  packagingQuantityField.attr('min', 1);

  function updateFieldOptions(field, options, selectedValue = null) {
    if (field) {
      field.empty();
      if (!field.prop('multiple')) {
        field.append(new Option('---------', '', true, !selectedValue));
      }
      const selected = selectedValue === "" || selectedValue === null || selectedValue === undefined
        ? null
        : (isNaN(parseInt(selectedValue)) ? selectedValue : parseInt(selectedValue));
      options.forEach(option => {
        if (!option.id && option.value) {
          option.id = option.value; // Ensure option has an id if it only has a value
        }
        const newOption = new Option(option.name, option.id, false, option.id === selected);
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
      const sizes = await fetchOptions(`/rest/v1/catalogs/product-size/?product=${batchProperties.product.id}&market=${marketField.val()}&category=size&is_enabled=1`);
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
      const pallets = await fetchOptions(`/rest/v1/packing/packing-pallet/?product=${batchProperties.product.id}&market=${marketField.val()}&product_sizes=${productSizeField.val()}&status=open`);
      console.log("Packing pallets fetched:", pallets);
      updateFieldOptions(packingPalletField, pallets, packingPalletField.val() ? packingPalletField.val() : null);
    } else {
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
    alert("Batch changed to: " + batchField.val());
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
    console.log("Size packaging changed to:", sizePackagingField.val());
    if (batchProperties && sizePackagingField.val()) {
      packagingQuantityField.attr('max', parseInt(batchProperties.available_weight / parseFloat(productWeightPerPackagingField.val())));
      console.log("packagingQuantityField.attr('max')", packagingQuantityField.attr('max'));
      if (!packagingQuantityField.val()) {
        packagingQuantityField.val(parseInt(batchProperties.available_weight / parseFloat(productWeightPerPackagingField.val())));
      }
    } else {
      packagingQuantityField.attr('max', null);
    }
  });

  statusField.on("change", function () {
    if (statusField.val() === 'open') {
      packingPalletField.val(null).trigger('change');
    }
  });

  packingPalletField.on("change", async function () {
    if (packingPalletField.val()) {
      statusField.val('ready').trigger('change');
    }
  });

  if (!batchProperties) await getBatchProperties();

  const disabledFields = [batchField, marketField, productSizeField, productMarketClassField, productRipenessField, sizePackagingField];
  disabledFields.forEach(field => {
    if (field.attr('readonly') === 'readonly' || field.attr('disabled') === 'disabled') {
      field.next('.select2-container').addClass('disabled-field');
    }
  })

});
