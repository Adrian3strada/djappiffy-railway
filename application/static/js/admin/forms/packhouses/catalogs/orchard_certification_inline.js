document.addEventListener('DOMContentLoaded', () => {

  function updateFieldOptions(field, options) {
    const selectedValue = field.val();
    field.empty().append(new Option('---------', '', true, true));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, false));
    });
    if (selectedValue) {
      field.val(selectedValue);
    }
    field.trigger('change').select2();
  }

  function fetchOptions(url) {
    return fetch(url).then(response => response.json());
  }

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'orchardcertification_set') {
      const newForm = $(event.target);
      const certificationKindField = newForm.find('select[name$="-certification_kind"]');
      const extraCodeField = newForm.find('input[name$="-extra_code"]');
      extraCodeField.prop('disabled', true);
      extraCodeField.attr('placeholder', 'n/a');

      certificationKindField.on('change', () => {
        const certificationKindID = certificationKindField.val();
        extraCodeField.val(null);
        extraCodeField.prop('disabled', true);
        if (certificationKindID) {
          fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-kind/${certificationKindField.val()}/`)
            .then(data => {
              extraCodeField.prop('disabled', !data.extra_code_name);
              extraCodeField.attr('placeholder', data.extra_code_name || 'n/a');
              fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-verifier/?id=${data.verifiers.join(',')}`)
                .then(verifiers => {
                  updateFieldOptions(newForm.find('select[name$="-verifier"]'), verifiers);
                });
            })
            .catch(error => {
              console.error('Error fetching certification kind data:', error);
            })
        }
      });
    }
  });

  const existingForms = $('tr[id^="orchardcertification_set-"]');
  existingForms.each((index, form) => {
    console.log("form", form);

    const certificationKindField = $(form).find('select[name$="-certification_kind"]');
    const extraCodeField = $(form).find('input[name$="-extra_code"]');
    const verifierField = $(form).find('select[name$="-verifier"]');
    extraCodeField.prop('disabled', true);
    extraCodeField.attr('placeholder', 'n/a');

    const certificationKindID = certificationKindField.val();

    if (certificationKindID) {
      fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-kind/${certificationKindField.val()}/`)
        .then(data => {
          extraCodeField.prop('disabled', !data.extra_code_name);
          extraCodeField.attr('placeholder', data.extra_code_name || 'n/a');
          fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-verifier/?id=${data.verifiers.join(',')}`)
            .then(verifiers => {
              updateFieldOptions(verifierField, verifiers);
              verifierField.val(verifierField.val()).trigger('change');
            });
        })
        .catch(error => {
          console.error('Error fetching certification kind data:', error);
        })
    }

    certificationKindField.on('change', () => {
      extraCodeField.val(null);
      extraCodeField.prop('disabled', true);
      if (certificationKindID) {
        fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-kind/${certificationKindField.val()}/`)
          .then(data => {
            extraCodeField.prop('disabled', !data.extra_code_name);
            extraCodeField.attr('placeholder', data.extra_code_name || 'n/a');
            fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-verifier/?id=${data.verifiers.join(',')}`)
              .then(verifiers => {
                console.log("verifiers", verifiers);
                updateFieldOptions(verifierField, verifiers);
              });
          })
          .catch(error => {
            console.error('Error fetching certification kind data:', error);
          })
      }
    });
  });

});
