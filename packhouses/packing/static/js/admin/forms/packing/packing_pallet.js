document.addEventListener("DOMContentLoaded", async function () {
  const productField = $("#id_product")
  const marketField = $("#id_market")
  const productSizeField = $("#id_product_size")
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
      console.log("productProperties.markets", productProperties.markets);
      console.log("allMarkets", allMarkets);
      console.log("productProperties.markets", productProperties.markets);
      console.log("marketOptions", marketOptions);
      updateFieldOptions(marketField, marketOptions, marketField.val() ? marketField.val() : null);
    }
  }

  const setProductSizes = async () => {
    if (productProperties && productProperties.id && marketField.val()) {
      const sizes = await fetchOptions(`/rest/v1/catalogs/product-size/?product=${productProperties.id}&market=${marketField.val()}&category=size&is_enabled=1`);
      updateFieldOptions(productSizeField, sizes, productSizeField.val() ? productSizeField.val() : null);
    } else {
      if (productSizeField.val()) {
        const size = await fetchOptions(`/rest/v1/catalogs/product-size/${productSizeField.val()}/`);
        updateFieldOptions(productSizeField, [size], productSizeField.val());
      }
      updateFieldOptions(productSizeField, []);
    }
  }

  const marketFieldChangeHandler = async () => {
    await setProductSizes();
  }

  productField.on("change", async function () {
    await getProductProperties();
    await setMarketOptions();
  });

  marketField.on("change", async function () {
    await marketFieldChangeHandler();
  });

  await getProductProperties();
  await setProductSizes();
});
