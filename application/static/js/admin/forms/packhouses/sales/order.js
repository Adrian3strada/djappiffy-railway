document.addEventListener("DOMContentLoaded", function () {
  const marketField = $("#id_market");
  const countryField = $("#id_country");
  const clientField = $("#id_client");
  const incotermsField = $("#id_incoterms").closest(".field-incoterms");
  const localDeliveryField = $("#id_local_delivery").closest(".field-local_delivery");

  const API_BASE_URL = "/rest/v1";

  function updateFieldOptions(field, options) {
    field.empty().append(new Option("---------", "", true, true));
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

  function updateCountry() {
    const marketId = marketField.val();
    if (marketId) {
      fetchOptions(`${API_BASE_URL}/catalogs/market/${marketId}/`)
        .then((marketData) =>
          fetchOptions(
            `${API_BASE_URL}/cities/country/?id=${marketData.countries.join(
              ","
            )}`
          )
        )
        .then((countries) => {
          updateFieldOptions(countryField, countries);

          const selectedCountry = countryField.val();
          if (selectedCountry) {
            countryField.val(selectedCountry).trigger("change");
          }
        });
    } else {
      updateFieldOptions(countryField, []);
    }
  }

  function updateClient() {
    const countryId = countryField.val();
    const selectedClient = clientField.val();
    if (countryId) {
      fetchOptions(
        `${API_BASE_URL}/catalogs/client/?country=${countryId}&is_enabled=true`
      ).then((data) => {
        updateFieldOptions(clientField, data);

        if (selectedClient) {
          clientField.val(selectedClient).trigger("change");
        }
      });
    } else {
      updateFieldOptions(clientField, []);
    }
  }

  if (countryField.val()) {
    updateClient();
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

  // Llamar a la función cada vez que cambia el campo market
  marketField.on("change", function () {
    toggleFieldsBasedOnMarket();
    // Llamar a las funciones necesarias
    updateCountry();
    setTimeout(() => updateClient(), 300);
  });

  // Llamar a la función al cargar la página (por si ya hay un valor preseleccionado)
  toggleFieldsBasedOnMarket();

  countryField.on("change", function () {
    setTimeout(() => updateClient(), 300);
  });

  [marketField, countryField, clientField].forEach((field) => field.select2());

  const initialClientValue = clientField.val();
  if (initialClientValue) {
    clientField.val(initialClientValue).trigger("change");
  }
});
