document.addEventListener("DOMContentLoaded", function () {
  const clientCategoryField = $("#id_client_category");
  const clientField = $("#id_client");
  const incotermsField = $("#id_incoterms").closest(".field-incoterms");
  const localDeliveryField = $("#id_local_delivery").closest(".field-local_delivery");

  const clientMarketCountries = []

  const API_BASE_URL = "/rest/v1";

  function updateFieldOptions(field, options) {
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
    if (clientCategory) {
      fetchOptions(`${API_BASE_URL}/catalogs/client/?category=${clientCategory}&is_enabled=1`).then(
        (data) => {
          console.log("Client options:", data);
          updateFieldOptions(clientField, data);
        }
      );
    }
  }

  function toggleFieldsBasedOnMarket() {
    const selectedOption = marketField.find('option:selected');
    const isForeign = selectedOption.attr('data-is_foreign');

    if (isForeign === 'True') {
      // Mostrar incoterms y ocultar local_delivery
      incotermsField.show();
      incotermsField.prev("label").show(); // Asegurarse de mostrar la label de incoterms
      localDeliveryField.hide();
      localDeliveryField.prev("label").hide(); // Ocultar la label de local_delivery
    } else {
      // Mostrar local_delivery y ocultar incoterms
      incotermsField.hide();
      incotermsField.prev("label").hide(); // Ocultar la label de incoterms
      localDeliveryField.show();
      localDeliveryField.prev("label").show(); // Mostrar la label de local_delivery
    }
  }

  clientCategoryField.on("change", updateClientOptions);


  [clientField].forEach((field) => field.select2());

});
