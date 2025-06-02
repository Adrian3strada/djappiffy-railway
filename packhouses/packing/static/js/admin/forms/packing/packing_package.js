document.addEventListener("DOMContentLoaded", async function () {
  const batchField = $("#id_batch")
  const marketField = $("#id_market")
  const productField = $("#id_product")
  const productPhenologyField = $("#id_product_phenology")
  const productSizeField = $("#id_product_size")

  let batchProperties = null

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

      updateFieldOptions(marketField, [market], market.id);
      updateFieldOptions(productField, [product], product.id);
      updateFieldOptions(productPhenologyField, [productPhenology], productPhenology.id);
    } else {
      updateFieldOptions(marketField, []);
      updateFieldOptions(productField, []);
      updateFieldOptions(productPhenologyField, []);
    }
  });


});
