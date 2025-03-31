document.addEventListener("DOMContentLoaded", function () {
  const clientCategoryField = $("#id_client_category");
  const maquiladoraField = $("#id_maquiladora");
  const clientField = $("#id_client");
  const localDeliveryField = $("#id_local_delivery")
  const incotermsField = $("#id_incoterms")
  const productField = $("#id_product")
  const productVarietyField = $("#id_product_variety")
  const orderItemsKindField = $("#id_order_items_kind")
  const pricingByField = $("#id_pricing_by")

  const orderItemsTab = $("#jazzy-tabs .nav-item .nav-link[href='#order-items-tab']").closest('li');

  let clientProperties = null;
  let productProperties = null;
  let organization = null;
  let priceMeasureUnit = null;

  const API_BASE_URL = "/rest/v1";

  let order_items_kind_options = [
    {id: "product_measure_unit", name: "Product measure unit"},
    {id: "product_packaging", name: "Product packaging"},
    {id: "product_pallet", name: "Product pallet"},
  ]

  let product_price_options = [
    {id: "product_measure_unit", name: "Product measure unit"},
    {id: "product_packaging", name: "Product packaging"},
    {id: "product_presentation", name: "Product presentation"}
  ]

  function updateOrderItemsKindOptions(nationalClient = false) {
    order_items_kind_options = [
      {id: "product_measure_unit", name: "Product measure unit"},
      {id: "product_packaging", name: "Product packaging"},
      {id: "product_pallet", name: "Product pallet"},
    ]
    if (priceMeasureUnit) {
      order_items_kind_options[0].name = priceMeasureUnit
    }
    if (!nationalClient) {
      order_items_kind_options = [
        {id: "product_packaging", name: "Product packaging"},
        {id: "product_pallet", name: "Product pallet"},
      ]
    }
    updateFieldOptions(orderItemsKindField, order_items_kind_options)
  }

  function updateFieldOptions(field, options, selected = null) {
    field.empty();
    field.append(new Option("---------", "", true, !selected));
    options.forEach((option) => {
      field.append(new Option(option.name, option.id, false, selected));
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

  const deleteOrderItemInline = () => {
    const inlineItems = document.querySelectorAll('.inline-related');
    inlineItems.forEach(item => {
      const deleteCheckbox = item.querySelector('input[type="checkbox"][name$="-DELETE"]');
      if (deleteCheckbox) {
        deleteCheckbox.checked = true;
      }
      item.remove(); // Elimina el elemento del DOM
    });
  };

  const toggleShowOrderItemInline = () => {
    if (clientField.val() && productField.val() && orderItemsKindField.val() && pricingByField.val()) {
      orderItemsTab.removeClass('hidden')
    } else {
      orderItemsTab.addClass('hidden')
    }
    // aqui deleteOrderItemInline();
  }

  function updateClientOptions() {
    const clientCategory = clientCategoryField.val();
    if (clientCategory && clientCategory === 'packhouse') {
      fetchOptions(`${API_BASE_URL}/catalogs/client/?category=${clientCategory}&is_enabled=1`).then(
        (data) => {
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
          updateFieldOptions(maquiladoraField, data);
        }
      );
    }
  }

  function updateProductOptions() {
    if (clientProperties) {
      fetchOptions(`${API_BASE_URL}/catalogs/product/?markets=${clientProperties.market}&is_enabled=1`).then(
        (data) => {
          console.log("updateProductOptions", data)
          updateFieldOptions(productField, data);
        }
      )
    } else {
      updateFieldOptions(productField, []);
    }
  }

  function updateProductVarietyOptions() {
    const product = productField.val();
    if (product) {
      fetchOptions(`${API_BASE_URL}/catalogs/product-variety/?product=${product}&is_enabled=1`).then(
        (data) => {
          updateFieldOptions(productVarietyField, data);
        });
    } else {
      updateFieldOptions(productVarietyField, []);
    }
  }

  function getProductProperties(cleanup = false) {
    if (productField.val()) {
      fetchOptions(`${API_BASE_URL}/catalogs/product/${productField.val()}/`).then(
        (data) => {
          productProperties = data;
          if (data.price_measure_unit_category_display) {
            priceMeasureUnit = data.price_measure_unit_category_display
            if (order_items_kind_options[0].id === 'product_measure_unit') order_items_kind_options[0].name = priceMeasureUnit
            product_price_options[0].name = priceMeasureUnit
            if (cleanup) {
              orderItemsKindField.val(null);
              pricingByField.val(null);
              orderItemsKindField.trigger('change').select2();
              pricingByField.trigger('change').select2();
            }
            const orderItemsKindValue = orderItemsKindField.val();
            const pricingByValue = pricingByField.val();
            updateFieldOptions(orderItemsKindField, order_items_kind_options);
            updateFieldOptions(pricingByField, product_price_options);
            if (orderItemsKindValue) {
              orderItemsKindField.val(orderItemsKindValue);
              orderItemsKindField.trigger('change').select2();
            }
            if (pricingByValue) {
              pricingByField.val(pricingByValue);
              pricingByField.trigger('change').select2();
            }
          }
        });
    } else {
      productProperties = null;
      if (order_items_kind_options[0].id === 'product_measure_unit') order_items_kind_options[0].name = "Product measure unit"
      product_price_options[0].name = "Product measure unit"
      orderItemsKindField.val(null);
      orderItemsKindField.trigger('change').select2();
      pricingByField.val(null);
      pricingByField.trigger('change').select2();
    }
  }

  productField.on("change", () => {
    updateProductVarietyOptions();
    getProductProperties(true);
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
      fetchOptions(`${API_BASE_URL}/catalogs/client/${client}/`)
        .then((data) => {
          clientProperties = data;
          updateProductOptions();
          setTimeout(() => {
            if (data.country === organization.country) {
              localDeliveryField.closest('.form-group').fadeIn();
              updateOrderItemsKindOptions(true)
            } else {
              incotermsField.closest('.form-group').fadeIn();
              updateOrderItemsKindOptions(false)
            }
          }, 300);
        })
    } else {
      clientProperties = null;
      updateFieldOptions(productField, []);
    }
  });

  orderItemsKindField.on('change', () => {
    if (orderItemsKindField.val() && orderItemsKindField.val() === 'product_measure_unit') {
      pricingByField.val(null);
      pricingByField.trigger('change').select2();
      updateFieldOptions(pricingByField, [product_price_options[0]]);
    } else {
      pricingByField.val(null);
      pricingByField.trigger('change').select2();
      updateFieldOptions(pricingByField, product_price_options);
    }
  })

  pricingByField.on('change', () => {
    toggleShowOrderItemInline();
  })

  fetchOptions(`${API_BASE_URL}/profiles/packhouse-exporter-profile/?same=1`).then(
    (data) => {
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
    const product = productField.val()
    const productVariety = productVarietyField.val()
    const orderItemsKind = orderItemsKindField.val()
    const pricingBy = pricingByField.val()

    console.log("product", product)
    console.log("productVariety", productVariety)
    console.log("orderItemsKind", orderItemsKind)
    console.log("pricingBy", pricingBy)

    fetchOptions(`${API_BASE_URL}/catalogs/client/${clientField.val()}/`)
      .then((client) => {
        clientProperties = client;
        console.log("clientProperties", clientProperties)
        if (client.country === organization.country) {
          localDeliveryField.closest('.form-group').show();
          updateOrderItemsKindOptions(true)
        } else {
          incotermsField.closest('.form-group').show();
          updateOrderItemsKindOptions(false)
        }
        updateProductOptions();
        setTimeout(() => {
          if (product) {
            productField.val(product);
            productField.trigger('change').select2();
          }
        }, 400);
        setTimeout(() => {
          if (productVariety) {
            productVarietyField.val(productVariety)
            productVarietyField.trigger('change').select2();
          }
          if (orderItemsKind) {
            orderItemsKindField.val(orderItemsKind)
            orderItemsKindField.trigger('change').select2();
          }
          if (pricingBy) {
            pricingByField.val(pricingBy)
            pricingByField.trigger('change').select2();
          }
        }, 500);
      })
  }

});
