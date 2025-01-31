document.addEventListener("DOMContentLoaded", function() {
 const categoryField = $("#id_category");
  const gathererField = $(".field-gatherer");
  const maquiladoraField = $(".field-maquiladora");
  const productField = $("#id_product");
  const varietyField = $("#id_product_variety");
  const initialVarietyValue = varietyField.val();
  const seasonField = $("#id_product_season_kind");
  const initialSeasonValue = seasonField.val();
  const harvestSizeField = $("#id_product_harvest_size_kind");
  const initialHarvestSizeValue = harvestSizeField.val();
  const orchardField = $("#id_orchard");
  const initialOrchardSizeValue = orchardField.val();
  const orchardCertificationField = $("#id_orchard_certification");
  const initialOrchardCertificationValue = orchardCertificationField.val();
  const API_BASE_URL = "/rest/v1";

  // Función para obtener el token CSRF
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  $(document).on("click", ".btn-cancel-confirm", function (e) {
    e.preventDefault();

    var url = $(this).data("url");
    var message = $(this).data("message");
    var confirmText = $(this).data("confirm");
    var cancelText = $(this).data("cancel");

    var button = $(this);

    Swal.fire({
      title: "¿Estás seguro?",
      text: message,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#4daf50",
      cancelButtonColor: "#d33",
      confirmButtonText: confirmText,
      cancelButtonText: cancelText,
    }).then((result) => {
      if (result.isConfirmed) {
        fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
          },
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then((data) => {
            if (data.success) {
              button.hide();

              var row = button.closest("tr");
              var statusCell = row.find(".field-status");
              statusCell.text("Canceled");

              Toastify({
                text: data.message,
                duration: 3000,
                close: true,
                gravity: "bottom",
                position: "right",
                backgroundColor: "#4caf50",
              }).showToast();
            } else {
              Toastify({
                text: data.message,
                duration: 3000,
                close: true,
                gravity: "bottom",
                position: "right",
                backgroundColor: "#f44336",
              }).showToast();
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            Toastify({
              text: "An error occurred while processing your request.",
              duration: 3000,
              close: true,
              gravity: "bottom",
              position: "right",
              backgroundColor: "#f44336",
            }).showToast();
          });
      }
    });
  });


  function updateFieldOptions(field, options) {
    field.empty(); // Limpiar las opciones existentes
    if (!field.prop('multiple')) {
      field.append(new Option('---------', '', true, false)); // Añadir opción por defecto
    }
    if(field===orchardField) {
      options.forEach((option) => {
       field.append(new Option(option.code+' - '+option.name, option.id, false, false));
      });
    }else if(field===orchardCertificationField){
      var fechaActual = new Date();
      options.forEach((option) => {
          var optionText = option.verifier_name + ' - #' + option.certification_number;
          var isDisabled = false;

          if (fechaActual > new Date(option.expiration_date)) {
              optionText += ' - ' + option.expired_text;
              isDisabled = true;
          }

          var newOption = new Option(optionText, option.id, false, false);
          newOption.disabled = isDisabled;
          field.append(newOption);
      });
    }else{
      options.forEach((option) => {
        field.append(new Option(option.name, option.id, false, false));
      });
    }

    field.trigger("change").select2();
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: "GET",
      dataType: "json",
    }).fail((error) => console.error("Fetch error:", error));
  }

  function updateVarietyField() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_variety/?product=${productId}&is_enabled=true`)
        .then((data) => {
          updateFieldOptions(varietyField, data);
          if (initialVarietyValue) {
            varietyField.val(initialVarietyValue).trigger("change");
          }
        });
    } else {
      updateFieldOptions(varietyField, []);
    }
  }

  function updateSeasonField() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_season_kind/?product=${productId}&is_enabled=true`)
        .then((data) => {
          updateFieldOptions(seasonField, data);
          if (initialSeasonValue) {
            seasonField.val(initialSeasonValue).trigger("change");
          }
        });
    } else {
      updateFieldOptions(seasonField, []);
    }
  }

  function updateHarvestSizeField() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_harvest_size_kind/?product=${productId}&is_enabled=true`)
        .then((data) => {
          updateFieldOptions(harvestSizeField, data);
          if (initialHarvestSizeValue) {
            harvestSizeField.val(initialHarvestSizeValue).trigger("change");
          }
        });
    } else {
      updateFieldOptions(harvestSizeField, []);
    }
  }

  function toggleFieldsBasedOnCategory() {
    const categoryValue = categoryField.val();

    if (categoryValue === "gathering") {
      gathererField.fadeIn();
      $("#id_maquiladora").val('').trigger('change');
      maquiladoraField.hide();
    } else if (categoryValue === "maquila") {
      gathererField.hide();
      $("#id_gatherer").val('').trigger('change');
      maquiladoraField.fadeIn();
    } else {
      $("#id_gatherer").val('').trigger('change');
      $("#id_maquiladora").val('').trigger('change');
      gathererField.hide();
      maquiladoraField.hide();
    }
  }

  function updateOrchardField() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/orchard/?product=${productId}&is_enabled=true`)
        .then((data) => {
          updateFieldOptions(orchardField, data);
          if (initialOrchardSizeValue) {
            orchardField.val(initialOrchardSizeValue).trigger("change");
          }
        });
    } else {
      updateFieldOptions(orchardField, []);
    }
  }

  function updateOrchardCertificationField() {
    const orchardId = orchardField.val();
    if (orchardId) {
      fetchOptions(`${API_BASE_URL}/catalogs/orchard_certification/?orchard=${orchardId}&is_enabled=true`)
        .then((data) => {
          updateFieldOptions(orchardCertificationField, data);
          if (initialOrchardCertificationValue) {
            orchardCertificationField.val(initialOrchardCertificationValue).trigger("change");
          }
        });
    } else {
      updateFieldOptions(orchardCertificationField, []);
    }
  }

  // Oculta ambos campos al inicio
  gathererField.hide();
  maquiladoraField.hide();

  // Llama a la función cuando carga la página para calcular valores iniciales
  toggleFieldsBasedOnCategory();

  productField.on("change", function () {
    setTimeout(function () {
        updateVarietyField();
        updateSeasonField();
        updateHarvestSizeField();
        updateOrchardField();
        updateOrchardCertificationField();
    }, 300);
});

  orchardField.on("change", function () {
    setTimeout(function () {
        updateOrchardCertificationField();
    }, 300);
  });


  // Llama a la función cuando el campo de categoría cambia
  categoryField.change(toggleFieldsBasedOnCategory);


  if (initialVarietyValue) {
    varietyField.val(initialVarietyValue).trigger("change");
  }

  updateVarietyField();
  updateSeasonField();
  updateHarvestSizeField();
  updateOrchardField();
  updateOrchardCertificationField();

});
