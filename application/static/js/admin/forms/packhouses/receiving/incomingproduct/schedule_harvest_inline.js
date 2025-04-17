document.addEventListener("DOMContentLoaded", function() {
    const API_BASE_URL = "/rest/v1";

    function getField(selector) {
        const field = $(selector);
        return field.length ? field : null;
      }
      
      const orchardField = getField("#id_scheduleharvest-0-orchard");
      const orchardCertificationField = getField("#id_scheduleharvest-0-orchard_certification");
      const initialOrchardCertificationValue = orchardCertificationField.val();
      
      function updateFieldOptions(field, options) {
        field.empty();
        if (!field.prop('multiple')) {
          field.append(new Option('---------', '', true, false));
        }
        if (field === orchardField) {
          options.forEach(option => 
            field.append(new Option(`${option.code} - ${option.name}`, option.id))
          );
        } else if (field === orchardCertificationField) {
          const now = new Date();
          options.forEach(option => {
            let optionText = `${option.verifier_name} - #${option.certification_number}`;
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
      
      function updateOrchardCertificationField() {
        const orchardId = orchardField.val();
        if (orchardId) {
          fetchOptions(`${API_BASE_URL}/catalogs/orchard-certification/?orchard=${orchardId}&is_enabled=true`)
            .then(data => {
              updateFieldOptions(orchardCertificationField, data);
              if (initialOrchardCertificationValue) {
                orchardCertificationField.val(initialOrchardCertificationValue).trigger("change");
              }
            });
        } else {
          updateFieldOptions(orchardCertificationField, []);
        }
      }
      
      orchardField.on("change", () => setTimeout(updateOrchardCertificationField, 300));
      updateOrchardCertificationField();
      

});
