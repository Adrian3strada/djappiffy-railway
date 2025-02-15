document.addEventListener("DOMContentLoaded", function () {
  const clientCategoryField = $("#id_client_category");
  const maquiladoraField = $("#id_maquiladora");
  const clientField = $("#id_client");
  const localDeliveryField = $("#id_local_delivery")
  const incotermsField = $("#id_incoterms")
  const productField = $("#id_product")
  const productVarietyField = $("#id_product_variety")
  const orderItemsByField = $("#id_order_items_by")
  const pricingByField = $("#id_pricing_by")

  let productProperties = null;
  let organization = null;

  const API_BASE_URL = "/rest/v1";

  function updateFieldOptions(field, options) {
    console.log("updateFieldOptions", field, options)
    field.empty();
    field.append(new Option("---------", "", true, true));
    options.forEach((option) => {
      field.append(new Option(option.name, option.id, false, false));
    });
    field.trigger("change").select2();
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: "GET",
      dataType: "json",
    }).fail((error) => console.error("Fetch error:", error));
  }

  function updateClientOptions() {
    const clientCategory = clientCategoryField.val();
    if (clientCategory && clientCategory === 'packhouse') {
      fetchOptions(`${API_BASE_URL}/catalogs/client/?category=${clientCategory}&is_enabled=1`).then(
        (data) => {
          console.log("Client options:", data);
          updateFieldOptions(clientField, data);
        }
      );
    }
  }

  function updateMaquiladoraClientOptions() {
    const clientCategory = clientCategoryField.val();
    const maquiladora = maquiladoraField.val()
    if (clientCategory && clientCategory === 'maquiladora' && maquiladora) {
      fetchOptions(`${API_BASE_URL}/catalogs/client/?category=${clientCategory}&maquiladora=${maquiladora}&is_enabled=1`).then(
        (data) => {
          console.log("Maquiladora Client options:", data);
          updateFieldOptions(clientField, data);
        }
      );
    }
  }

  function updateMaquiladoraOptions() {
    const clientCategory = clientCategoryField.val();
    if (clientCategory && clientCategory === 'maquiladora') {
      fetchOptions(`${API_BASE_URL}/catalogs/maquiladora/?is_enabled=1`).then(
        (data) => {
          console.log("Maquiladora options:", data);
          updateFieldOptions(maquiladoraField, data);
        }
      );
    }
  }

  function updateProductVarietyOptions() {
    const product = productField.val();
    if (product) {
      fetchOptions(`${API_BASE_URL}/catalogs/product-variety/?product=${product}&is_enabled=1`).then(
        (data) => {
          console.log("Product Variety options:", data);
          updateFieldOptions(productVarietyField, data);
        });
    } else {
      updateFieldOptions(productVarietyField, []);
    }
  }

  function getProductProperties() {
    if (productField.val()) {
      fetchOptions(`${API_BASE_URL}/catalogs/product/${productField.val()}/`).then(
        (data) => {
          productProperties = data;
          console.log("productProperties", productProperties)
          if (data.price_measure_unit_category_display) {
            orderItemsByField.find('option[value="product_measure_unit"]').text(data.price_measure_unit_category_display);
            pricingByField.find('option[value="product_measure_unit"]').text(data.price_measure_unit_category_display);
            orderItemsByField.trigger('change').select2();
            pricingByField.trigger('change').select2();
          }
        });
    } else {
      productProperties = null;
      orderItemsByField.find('option[value="product_measure_unit"]').text('Product measure unit');
      pricingByField.find('option[value="product_measure_unit"]').text('Product measure unit');
      orderItemsByField.trigger('change').select2();
      pricingByField.trigger('change').select2();
    }
  }

  productField.on("change", () => {
    updateProductVarietyOptions()
    getProductProperties();
  });

  clientCategoryField.on("change", () => {
    if (clientCategoryField.val() && clientCategoryField.val() === 'packhouse') {
      updateClientOptions()
      maquiladoraField.closest('.form-group').fadeOut();
    } else if (clientCategoryField.val() && clientCategoryField.val() === 'maquiladora') {
      updateMaquiladoraOptions()
      maquiladoraField.closest('.form-group').fadeIn();
      updateFieldOptions(clientField, []);
    } else {
      updateFieldOptions(maquiladoraField, []);
      updateFieldOptions(clientField, []);
      maquiladoraField.closest('.form-group').fadeOut();
    }
  });

  maquiladoraField.on("change", () => {
    const maquiladora = maquiladoraField.val()
    if (maquiladora) {
      updateMaquiladoraClientOptions()
    } else {
      updateFieldOptions(clientField, []);
    }
  });

  clientField.on('change', () => {
    const client = clientField.val();

    localDeliveryField.closest('.form-group').fadeOut();
    incotermsField.closest('.form-group').fadeOut();
    setTimeout(() => {
      localDeliveryField.val(null).trigger('change');
      incotermsField.val(null).trigger('change');
    }, 100);
    if (client) {
      fetchOptions(`${API_BASE_URL}/catalogs/client/${client}/`).then(
        (data) => {
          setTimeout(() => {
            console.log("Client data:", data);
            if (data.country === organization.country) {
              localDeliveryField.closest('.form-group').fadeIn();
            } else {
              incotermsField.closest('.form-group').fadeIn();
            }
          }, 300);
        });
    }
  });

  fetchOptions(`${API_BASE_URL}/profiles/packhouse-exporter-profile/?same=1`).then(
    (data) => {
      console.log("profiles/packhouse-exporter-profile:", data);
      if (data.count === 1) {
        organization = data.results.pop()
      }
    }
  );

  maquiladoraField.closest('.form-group').hide();
  localDeliveryField.closest('.form-group').hide();
  incotermsField.closest('.form-group').hide();

  if (localDeliveryField.val()) localDeliveryField.closest('.form-group').show();
  if (incotermsField.val()) incotermsField.closest('.form-group').show();
  if (productField.val()) getProductProperties();

  if (clientCategoryField.val()) {
    if (clientCategoryField.val() === 'maquiladora') {
      maquiladoraField.closest('.form-group').show();
    }
  }

  if (clientField.val()) {
    fetchOptions(`${API_BASE_URL}/catalogs/client/${clientField.val()}/`).then(
      (data) => {
        console.log("Client data:", data);
        if (data.country === organization.country) {
          localDeliveryField.closest('.form-group').show();
        } else {
          incotermsField.closest('.form-group').show();
        }
      });
  }

});
