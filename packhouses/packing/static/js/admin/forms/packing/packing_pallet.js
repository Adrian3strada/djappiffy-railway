document.addEventListener("DOMContentLoaded", async function () {
  const productField = $("#id_product")
  const marketField = $("#id_market")
  const productSizesField = $("#id_product_sizes")
  const palletField = $("#id_pallet")
  // const isEditing = window.location.pathname.match(/\/change\//) !== null;

  let productProperties = null
  let allMarkets = await fetchOptions(`/rest/v1/catalogs/market/?is_enabled=1`);
  let marketOptions = []

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
      console.log("Product properties fetched getProductProperties:", productProperties);
    } else {
      productProperties = null;
    }
  }

  const setMarketOptions = async () => {
    if (productProperties) {
      marketOptions = allMarkets.filter(market => productProperties.markets.includes(market.id));
      updateFieldOptions(marketField, marketOptions, marketField.val() ? marketField.val() : null);
    }
  }

  const setProductSizes = async () => {
    if (productProperties && productProperties.id && marketField.val()) {
      const sizes = await fetchOptions(`/rest/v1/catalogs/product-size/?product=${productProperties.id}&market=${marketField.val()}&category=size&is_enabled=1`);
      updateFieldOptions(productSizesField, sizes, productSizesField.val() ? productSizesField.val() : null);
    } else {
      if (productSizesField.val()) {
        const sizes = await fetchOptions(`/rest/v1/catalogs/product-size/?id__in=${productSizesField.val()}`);
        updateFieldOptions(productSizesField, sizes, productSizesField.val());
      }
      updateFieldOptions(productSizesField, []);
    }
  }

  const setPallets = async () => {
    if (productField.val() && marketField.val()) {
      let pallets = await fetchOptions(`/rest/v1/catalogs/pallet/?product=${productField.val()}&market=${marketField.val()}&is_enabled=1`);
      console.log("Pallets fetched setPallets:", pallets);
      pallets = pallets.map(pallet => ({
        ...pallet,
        name: `${pallet.name} (Q:${pallet.max_packages_quantity})`
      }));
      updateFieldOptions(palletField, pallets, palletField.val() ? palletField.val() : null);
    } else {
      if (palletField.val()) {
        const pallets = await fetchOptions(`/rest/v1/catalogs/pallet/${palletField.val()}/`);
        updateFieldOptions(palletField, pallets, palletField.val());
      }
      updateFieldOptions(palletField, []);
    }
  }

  const marketFieldChangeHandler = async () => {
    await setProductSizes();
    await setPallets();
  }

  productField.on("change", async function () {
    await getProductProperties();
    await setMarketOptions();
    await setProductSizes();
  });

  marketField.on("change", async function () {
    await marketFieldChangeHandler();
  });

  await getProductProperties();
  await setProductSizes();
});
