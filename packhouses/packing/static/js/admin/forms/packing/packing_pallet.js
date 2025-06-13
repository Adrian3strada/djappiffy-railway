document.addEventListener("DOMContentLoaded", async function () {
  const batchField = $("#id_batch")
  const marketField = $("#id_market")
  const productField = $("#id_product")
  const productPhenologyField = $("#id_product_phenology")
  const productSizeField = $("#id_product_size")
  const productMarketClassField = $("#id_product_market_class")
  const sizePackagingField = $("#id_size_packaging")
  const productWeightPerPackagingField = $("#id_product_weight_per_packaging")
  const productPresentationsPerPackagingField = $("#id_product_presentations_per_packaging")
  const productPiecesPerPresentationField = $("#id_product_pieces_per_presentation")
  const isEditing = window.location.pathname.match(/\/change\//) !== null;

  let batchProperties = null

  productPresentationsPerPackagingField.closest('.form-group').hide()
  productPiecesPerPresentationField.closest('.form-group').hide()

  function getOrganization() {
    fetchOptions(`/rest/v1/profiles/packhouse-exporter-profile/?same=1`).then(
      (data) => {
        if (data.count === 1) {
          organization = data.results.pop()
        }
      }
    );
  }

  await getOrganization();

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

  async function getBatchProperties() {
    if (batchField.val()) {
      batchProperties = await fetchOptions(`/rest/v1/receiving/batch/${batchField.val()}/`)
    } else {
      batchProperties = null;
    }
  }

  const setProductSizes = async () => {
    if (productField.val() && marketField.val()) {
      const sizes = await fetchOptions(`/rest/v1/catalogs/product-size/?product=${productField.val()}&market=${marketField.val()}&category=size&is_enabled=1`);
      updateFieldOptions(productSizeField, sizes, productSizeField.val());
    } else {
      updateFieldOptions(productSizeField, []);
    }
  }

  const setProductMarketClasses = async () => {
    if (productField.val() && marketField.val()) {
      const classes = await fetchOptions(`/rest/v1/catalogs/product-market-class/?product=${productField.val()}&market=${marketField.val()}&is_enabled=1`);
      if (classes.length > 0) {
        updateFieldOptions(productMarketClassField, classes, productMarketClassField.val());
      } else {
        updateFieldOptions(productMarketClassField, []);
      }
    } else {
      updateFieldOptions(productMarketClassField, []);
    }
  }

  const setProductPackagings = async () => {
    if (marketField.val() && productField.val() && productSizeField.val()) {
      const packagings = await fetchOptions(`/rest/v1/catalogs/size-packaging/?product=${productField.val()}&market=${marketField.val()}&product_size=${productSizeField.val()}&is_enabled=1`);
      if (packagings.length > 0) {
        updateFieldOptions(sizePackagingField, packagings, sizePackagingField.val());
      } else {
        updateFieldOptions(sizePackagingField, []);
      }
    } else {
      updateFieldOptions(sizePackagingField, []);
    }
  }

  const batchFieldChangeHandler = async () => {
    await getBatchProperties();
    if (batchProperties) {
      console.log("Batch properties:", batchProperties);
      const market = batchProperties.market;
      const product = batchProperties.product;
      const productPhenology = batchProperties.product_phenology;
      marketField.val(market.id).trigger('change');
      productField.val(product.id).trigger('change');
      productPhenologyField.val(productPhenology.id).trigger('change');
    }
  }

  const marketFieldChangeHandler = async () => {
    if (marketField.val()) {
      const products = await fetchOptions(`/rest/v1/catalogs/product/?markets=${marketField.val()}&is_enabled=1`);
      updateFieldOptions(productField, products, productField.val());
      await setProductSizes();
      await setProductMarketClasses();
      await setProductPackagings();
    } else {
      updateFieldOptions(productField, []);
    }
  }

  const productFieldChangeHandler = async () => {
    if (productField.val()) {
      const phenologies = await fetchOptions(`/rest/v1/catalogs/product-phenology/?product=${productField.val()}&is_enabled=1`);
      updateFieldOptions(productPhenologyField, phenologies, productPhenologyField.val());
      await setProductSizes();
      await setProductMarketClasses();
      await setProductPackagings();
    } else {
      updateFieldOptions(productPhenologyField, []);
      updateFieldOptions(productSizeField, []);
    }
  }

  const productSizeFieldChangeHandler = async () => {
    if (productSizeField.val()) {
      await setProductPackagings();
    }
  }

  const productPackagingFieldChangeHandler = async () => {
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

  productField.on("change", async function () {
    await productFieldChangeHandler();
  });

  productSizeField.on("change", async function () {
    await productSizeFieldChangeHandler();
  });

  sizePackagingField.on("change", async function () {
    await productPackagingFieldChangeHandler();
  });

  if (marketField.val()) {
    await marketFieldChangeHandler();
  }

  if (productField.val()) {
    await productFieldChangeHandler();
  }

  if (productSizeField.val()) {
    await productSizeFieldChangeHandler();
  }


});
