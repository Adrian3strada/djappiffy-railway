document.addEventListener("DOMContentLoaded", async function () {
  const batchField = $("#id_batch")
  const marketField = $("#id_market")
  const productField = $("#id_product")
  const productPhenologyField = $("#id_product_phenology")
  const productSizeField = $("#id_product_size")
  const productMarketClassField = $("#id_product_market_class")
  const productPackagingField = $("#id_product_packaging")
  const productWeightPerPackagingField = $("#id_product_weight_per_packaging")
  const productPresentationsPerPackagingField = $("#id_product_presentations_per_packaging")
  const productPiecesPerPresentationField = $("#id_product_pieces_per_presentation")
  const packagingQuantityField = $("#id_packaging_quantity")

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

  batchField.on("change", async function () {
    alert("Batch changed, fetching properties...");
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
  });

  marketField.on("change", async function () {
    if (marketField.val()) {
      const products = await fetchOptions(`/rest/v1/catalogs/product/?markets=${marketField.val()}&is_enabled=1`);
      updateFieldOptions(productField, products, productField.val());
      await setProductSizes();
      await setProductMarketClasses();
      await setProductPackagings();
    } else {
      updateFieldOptions(productField, []);
    }
  });

  productField.on("change", async function () {
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
  });

  productSizeField.on("change", async function () {
    if (productSizeField.val()) {
      await setProductPackagings();
    }
  });

  productPackagingField.on("change", async function () {
    if (productPackagingField.val()) {
      const packaging = productPackagingField.find(':selected');
      const weightPerPackaging = packaging.data('weight-per-packaging') || 0;
      const presentationsPerPackaging = packaging.data('presentations-per-packaging') || 0;
      const piecesPerPresentation = packaging.data('pieces-per-presentation') || 0;

      productWeightPerPackagingField.val(weightPerPackaging);
      productPresentationsPerPackagingField.val(presentationsPerPackaging);
      productPiecesPerPresentationField.val(piecesPerPresentation);

      if (packaging.data('quantity')) {
        packagingQuantityField.val(packaging.data('quantity'));
      } else {
        packagingQuantityField.val(1);
      }
    } else {
      productWeightPerPackagingField.val('');
      productPresentationsPerPackagingField.val('');
      productPiecesPerPresentationField.val('');
      packagingQuantityField.val(1);
    }
  });

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
      const packagings = await fetchOptions(`/rest/v1/catalogs/product-packaging/?product=${productField.val()}&market=${marketField.val()}&product_size=${productSizeField.val()}&is_enabled=1`);
      if (packagings.length > 0) {
        updateFieldOptions(productPackagingField, packagings, productPackagingField.val());
      } else {
        updateFieldOptions(productPackagingField, []);
      }
    } else {
      updateFieldOptions(productPackagingField, []);
    }
  }

});
