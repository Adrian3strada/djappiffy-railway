document.addEventListener("DOMContentLoaded", async function () {
  const batchField = $("#id_batch")
  const marketField = $("#id_market")
  const productField = $("#id_product")
  const productPhenologyField = $("#id_product_phenology")
  const productSizeField = $("#id_product_size")

  let batchProperties = null


  const API_BASE_URL = "/rest/v1";

  function getOrganization() {
    fetchOptions(`${API_BASE_URL}/profiles/packhouse-exporter-profile/?same=1`).then(
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
      batchProperties = await fetchOptions(`/rest/v1/catalogs/client/${clientField.val()}/`)
    } else {
      batchProperties = null;
    }
  }


  function updateClientOptions() {
    // clientCategory = clientCategoryField.val();
    if (!!clientCategory && clientCategory === 'packhouse') {
      fetchOptions(`${API_BASE_URL}/catalogs/client/?category=${clientCategory}&is_enabled=1`).then(
        (data) => {
          updateFieldOptions(clientField, data, client);
        }
      );
    }
  }


});
