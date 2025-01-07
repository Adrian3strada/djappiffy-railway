document.addEventListener('DOMContentLoaded', () => {

  function updateFieldOptions(field, options) {
    field.empty();
    if (!field.prop('multiple')) {
      field.append(new Option('---------', '', true, true));
    }
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, false));
    });
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: 'GET',
      dataType: 'json'
    }).fail(error => console.error('Fetch error:', error));
  }

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'orchardcertification_set') {
      const newForm = event.target;
      const certificationKindField = $(newForm).find('select[name$="-certification_kind"]');
      const extraCodeField = $(newForm).find('input[name$="-extra_code"]');
      const verifierField = $(newForm).find('select[name$="-verifier"]');

      updateFieldOptions(verifierField, []);

      extraCodeField.prop('disabled', true);
      extraCodeField.attr('placeholder', 'n/a');
      extraCodeField.addClass('disabled-field')

      certificationKindField.on('change', () => {
        extraCodeField.val(null);
        if (certificationKindField.val()) {
          console.log("certificationKindID", certificationKindField.val());
          fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-kind/${certificationKindField.val()}/`)
            .then(data => {
              extraCodeField.prop('disabled', !data.extra_code_name);
              extraCodeField.attr('placeholder', data.extra_code_name || 'n/a');
              data.extra_code_name ? extraCodeField.removeClass('disabled-field') : extraCodeField.addClass('disabled-field');
              fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-verifier/?id=${data.verifiers.join(',')}`)
                .then(verifiers => {
                  updateFieldOptions(verifierField, verifiers);
                });
            })
            .catch(error => {
              console.error('Error fetching certification kind data:', error);
            })
        } else {
          updateFieldOptions(verifierField, []);
        }
      });
    }
  });

  const existingForms = $('div[id^="orchardcertification_set-"]');
  existingForms.each((index, form) => {
    const certificationKindField = $(form).find(`select[name$="${index-1}-certification_kind"]`);
    const extraCodeField = $(form).find(`input[name$="${index-1}-extra_code"]`);
    const verifierField = $(form).find(`select[name$="${index-1}-verifier"]`);

    if (certificationKindField.val()) {
      const selectedVerifier = verifierField.val();
        fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-kind/${certificationKindField.val()}/`)
          .then(data => {
            extraCodeField.prop('disabled', !data.extra_code_name);
            extraCodeField.attr('placeholder', data.extra_code_name || 'n/a');
            data.extra_code_name ? extraCodeField.removeClass('disabled-field') : extraCodeField.addClass('disabled-field');
            fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-verifier/?id=${data.verifiers.join(',')}`)
              .then(verifiers => {
                console.log("verifiers 1", verifiers);
                updateFieldOptions(verifierField, verifiers);
                verifierField.val(selectedVerifier);
              });
          })
          .catch(error => {
            console.error('Error fetching certification kind data:', error);
          })
        } else {
          updateFieldOptions(verifierField, []);
      }

    certificationKindField.on('change', () => {
      if (certificationKindField.val()) {
        fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-kind/${certificationKindField.val()}/`)
          .then(data => {
            extraCodeField.prop('disabled', !data.extra_code_name);
            extraCodeField.attr('placeholder', data.extra_code_name || 'n/a');
            data.extra_code_name ? extraCodeField.removeClass('disabled-field') : extraCodeField.addClass('disabled-field');
            fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-verifier/?id=${data.verifiers.join(',')}`)
              .then(verifiers => {
                console.log("verifiers 2", verifiers);
                updateFieldOptions(verifierField, verifiers);
              });
          })
          .catch(error => {
            console.error('Error fetching certification kind data:', error);
          })
        } else {
          updateFieldOptions(verifierField, []);
      }
    });
  });

});
