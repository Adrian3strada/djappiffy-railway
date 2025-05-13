
document.addEventListener("DOMContentLoaded", function() {
  const API_BASE_URL = "/rest/v1";

  function disableField(field) {
    field.prop("readonly", true);
    field.css({
      "pointer-events": "none",
      "background-color": "#e9ecef",
      "border": "none",
      "color": "#555"
    });
  }
  
  // Aplica a cualquier input de peso esperado
  $('input[id$="-weight_expected"]').each((_, input) => {
    disableField($(input));
  });
  
  function updateFieldOptions(field, options) {
    field.empty();
    if (!field.prop("multiple")) {
      field.append(new Option("---------", "", true, false));
    }

    const fieldName = field.attr("name");
    if (fieldName.endsWith("-orchard")) {
      options.forEach(option =>
        field.append(new Option(`${option.code} - ${option.name}`, option.id))
      );
    } else if (fieldName.endsWith("-orchard_certifications")) {
      const now = new Date();
      options.forEach(option => {
        let optionText = `${option.certification_kind_name} - #${option.certification_number}`;
        const isDisabled = now > new Date(option.expiration_date);
        if (isDisabled) {
          optionText += ` - ${option.expired_text}`;
        }
        const newOption = new Option(optionText, option.id);
        newOption.disabled = isDisabled;
        field.append(newOption);
      });
    } else {
      options.forEach(option =>
        field.append(new Option(option.name, option.id))
      );
    }

    field.trigger("change").select2();
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: "GET",
      dataType: "json",
    }).fail(error => console.error("Fetch error:", error));
  }

  function setupCertificationUpdater($orchardField, $orchardCertificationField) {
    const initialValue = $orchardCertificationField.val();

    function updateOrchardCertificationField() {
      const orchardId = $orchardField.val();
      if (orchardId) {
        fetchOptions(`${API_BASE_URL}/catalogs/orchard-certification/?orchard=${orchardId}&is_enabled=true`)
          .then(data => {
            updateFieldOptions($orchardCertificationField, data);
            if (initialValue) {
              $orchardCertificationField.val(initialValue).trigger("change");
            }
          });
      } else {
        updateFieldOptions($orchardCertificationField, []);
      }
    }

    $orchardField.on("change", () => setTimeout(updateOrchardCertificationField, 300));
    updateOrchardCertificationField();
  }

  // Aplica a todos los campos orchard existentes en todos los scheduleharvest forms
  $('select[name$="-orchard"]').each(function () {
    const $orchardField = $(this);

    // Obtener el campo orchard_certifications con el mismo índice
    const nameAttr = $orchardField.attr("name");  // ej: incomingproduct_set-0-scheduleharvest_set-0-orchard
    const baseName = nameAttr.replace("-orchard", "");
    const $orchardCertificationField = $(`select[name='${baseName}-orchard_certifications']`);

    if ($orchardCertificationField.length) {
      setupCertificationUpdater($orchardField, $orchardCertificationField);
    }
  });
});
