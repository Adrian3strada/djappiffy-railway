document.addEventListener("DOMContentLoaded", async function () {
  const orderItemsWightTab = $("#jazzy-tabs .nav-item .nav-link[href='#order-items-by-weight-tab']").closest('li');
  const orderItemsPackagingTab = $("#jazzy-tabs .nav-item .nav-link[href='#order-items-by-packaging-tab']").closest('li');
  const orderItemsPalletTab = $("#jazzy-tabs .nav-item .nav-link[href='#order-items-by-pallet-tab']").closest('li');

  orderItemsWightTab.addClass('hidden')
  orderItemsPackagingTab.addClass('hidden')
  orderItemsPalletTab.addClass('hidden')

  const clientCategoryField = $("#id_client_category");
  const maquiladoraField = $("#id_maquiladora");
  const clientField = $("#id_client");
  const localDeliveryField = $("#id_local_delivery")
  const incotermsField = $("#id_incoterms")
  const productField = $("#id_product")
  const productVarietyField = $("#id_product_variety")
  const orderItemsKindField = $("#id_order_items_kind")

  let clientCategory = clientCategoryField.val();
  let maquiladora = maquiladoraField.val()
  let client = clientField.val()
  let localDelivery = localDeliveryField.val()
  let incoterms = incotermsField.val()
  let product = productField.val()
  let productVariety = productVarietyField.val()
  let orderItemsKind = orderItemsKindField.val()

  let clientProperties = null;
  let productProperties = null;
  let organization = null;
  let nationalClient = true

  localDeliveryField.closest('.form-group').hide();
  incotermsField.closest('.form-group').hide();
  productField.closest('.form-group').hide();

  const API_BASE_URL = "/rest/v1";

  let order_items_kind_options = [
    {id: "product_weight", name: "Product weight"},
    {id: "product_packaging", name: "Product packaging"},
    {id: "product_pallet", name: "Product pallet"},
  ]

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

  function updateOrderItemsKindOptions() {
    order_items_kind_options = [
      {id: "product_weight", name: "Product weight"},
      {id: "product_packaging", name: "Product packaging"},
      {id: "product_pallet", name: "Product pallet"},
    ]
    if (!nationalClient) {
      order_items_kind_options = [
        {id: "product_packaging", name: "Product packaging"},
        {id: "product_pallet", name: "Product pallet"},
      ]
    }
    updateFieldOptions(orderItemsKindField, order_items_kind_options, orderItemsKindField.val());
  }

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

  async function getClientProperties() {
    if (clientField.val()) {
      clientProperties = await fetchOptions(`/rest/v1/catalogs/client/${clientField.val()}/`)
      nationalClient = clientProperties.country === organization.country;
      updateOrderItemsKindOptions()
    } else {
      clientProperties = null;
    }
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
    orderItemsWightTab.addClass('hidden')
    orderItemsPackagingTab.addClass('hidden')
    orderItemsPalletTab.addClass('hidden')
    if (clientField.val() && productField.val() && orderItemsKindField.val()) {
      if (orderItemsKindField.val() === 'product_weight') {
        orderItemsWightTab.removeClass('hidden')
      }
      if (orderItemsKindField.val() === 'product_packaging') {
        orderItemsPackagingTab.removeClass('hidden')
      }
      if (orderItemsKindField.val() === 'product_pallet') {
        orderItemsPalletTab.removeClass('hidden')
      }
    }
    // aqui deleteOrderItemInline();
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

  function updateMaquiladoraClientOptions() {
    if (!!clientCategory && clientCategory === 'maquiladora' && maquiladoraField.val()) {
      fetchOptions(`${API_BASE_URL}/catalogs/client/?category=${clientCategory}&maquiladora=${maquiladoraField.val()}&is_enabled=1`).then(
        (data) => {
          updateFieldOptions(clientField, data, maquiladora);
        }
      );
    }
  }

  function updateMaquiladoraOptions() {
    // const clientCategory = clientCategoryField.val();
    if (clientCategory && clientCategory === 'maquiladora') {
      fetchOptions(`${API_BASE_URL}/catalogs/maquiladora/?is_enabled=1`).then(
        (data) => {
          updateFieldOptions(maquiladoraField, data, maquiladora);
        }
      );
    }
  }

  async function updateProductOptions() {
    if (!clientProperties) await getClientProperties();
    if (clientProperties) {
      fetchOptions(`${API_BASE_URL}/catalogs/product/?markets=${clientProperties.market}&is_enabled=1`).then(
        (data) => {
          updateFieldOptions(productField, data, productField.val());
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
          updateFieldOptions(productVarietyField, data, productVarietyField.val());
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
          if (data.measure_unit_category_display) {
            if (order_items_kind_options[0].id === 'product_weight') order_items_kind_options[0].name = data.measure_unit_category_display
            updateFieldOptions(orderItemsKindField, order_items_kind_options, orderItemsKindField.val());
          }
        });
    } else {
      productProperties = null;
      if (order_items_kind_options[0].id === 'product_weight') order_items_kind_options[0].name = "Product weight"
      // orderItemsKindField.val(null);
      // orderItemsKindField.trigger('change').select2();
    }
  }

  clientCategoryField.on("change", () => {
    clientCategory = clientCategoryField.val()
    if (!!clientCategory && clientCategory === 'packhouse') {
      updateClientOptions()
      maquiladoraField.closest('.form-group').fadeOut();
    } else if (!!clientCategory && clientCategory === 'maquiladora') {
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
    if (maquiladoraField.val()) {
      console.log(maquiladoraField.val())
      updateMaquiladoraClientOptions()
    } else {
      updateFieldOptions(clientField, []);
    }
  });

  clientField.on('change', async () => {
    client = clientField.val();
    await localDeliveryField.val(null).trigger('change');
    await incotermsField.val(null).trigger('change');

    if (client) {
      clientProperties = await fetchOptions(`${API_BASE_URL}/catalogs/client/${client}/`)
      await updateProductOptions();
      await getClientProperties();
      if (nationalClient) {
        incotermsField.closest('.form-group').fadeOut();
        localDeliveryField.closest('.form-group').fadeIn();
      } else {
        incotermsField.closest('.form-group').fadeIn();
        localDeliveryField.closest('.form-group').fadeOut();
      }
      await updateOrderItemsKindOptions()
      productField.closest('.form-group').fadeIn();
    } else {
      clientProperties = null;
      updateFieldOptions(productField, []);
      productField.closest('.form-group').fadeOut();
      localDeliveryField.closest('.form-group').fadeOut();
      incotermsField.closest('.form-group').fadeOut();
    }
  });

  productField.on("change", async () => {
    if (productField.val()) {
      await getProductProperties();
      await updateProductVarietyOptions();
      productVarietyField.closest('.form-group').fadeIn();
      orderItemsKindField.closest('.form-group').fadeIn();
    } else {
      productVarietyField.closest('.form-group').fadeOut();
      orderItemsKindField.closest('.form-group').fadeOut();
      productVarietyField.val(null).trigger('change');
      orderItemsKindField.val(null).trigger('change');
    }
  });

  productVarietyField.on("change", async () => {
    productVariety = productVarietyField.val();
  })

  orderItemsKindField.on('change', () => {
    orderItemsKind = orderItemsKindField.val();
    if (orderItemsKind) {
      toggleShowOrderItemInline();
    }
  })


  maquiladoraField.closest('.form-group').hide();
  localDeliveryField.closest('.form-group').hide();
  incotermsField.closest('.form-group').hide();

  if (localDeliveryField.val()) localDeliveryField.closest('.form-group').show();
  if (incotermsField.val()) incotermsField.closest('.form-group').show();

  if (productField.val()) {
    getProductProperties();
    productVarietyField.closest('.form-group').show();
    orderItemsKindField.closest('.form-group').show();
  } else {
    productVarietyField.closest('.form-group').hide();
    orderItemsKindField.closest('.form-group').hide();
  }

  if (!!clientCategory) {
    if (clientCategory === 'maquiladora') {
      maquiladoraField.closest('.form-group').show();
    }
  }

  if (clientField.val()) {
    const product = productField.val()
    const productVariety = productVarietyField.val()

    if (!organization) await getOrganization();

    fetchOptions(`${API_BASE_URL}/catalogs/client/${clientField.val()}/`)
      .then((client_data) => {
        clientProperties = client_data;
        nationalClient = client_data.country === organization.country;
        updateOrderItemsKindOptions()
        if (nationalClient) {
          localDeliveryField.closest('.form-group').show();
        } else {
          incotermsField.closest('.form-group').show();
        }
        updateProductOptions();
        setTimeout(() => {
          if (product) {
            productField.val(product);
            productField.trigger('change').select2();
          }
        }, 300);
        setTimeout(() => {
          if (productVariety) {
            productVarietyField.val(productVariety)
            productVarietyField.trigger('change').select2();
          }
          if (orderItemsKind) {
            orderItemsKindField.val(orderItemsKind)
            orderItemsKindField.trigger('change').select2();
          }
        }, 400);
      })
  }

});
