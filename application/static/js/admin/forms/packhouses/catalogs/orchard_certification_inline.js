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

  function handleCertificationKindChange(certificationKindField, extraCodeField, verifierField) {
    const selectedVerifier = verifierField.val();
    const certificationKindId = certificationKindField.val();

    if (certificationKindId) {
      fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-kind/${certificationKindId}/`)
        .then(data => {
          extraCodeField.val(data.extra_code_name ? extraCodeField.val() : '');
          extraCodeField.prop('disabled', !data.extra_code_name);
          extraCodeField.attr('placeholder', data.extra_code_name || 'n/a');
          extraCodeField.toggleClass('disabled-field', !data.extra_code_name);

          return fetchOptions(`/rest/v1/packhouse-settings/orchard-certification-verifier/?id=${data.verifiers.join(',')}`);
        })
        .then(verifiers => {
          updateFieldOptions(verifierField, verifiers);
          if (selectedVerifier && verifiers.find(verifier => verifier.id === parseInt(selectedVerifier))) {
            verifierField.val(selectedVerifier);
          }
        })
        .catch(error => {
          console.error('Error fetching certification kind data:', error);
        });
    } else {
      updateFieldOptions(verifierField, []);
    }
  }

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'orchardcertification_set') {
      const newForm = event.target;
      const certificationKindField = $(newForm).find('select[name$="-certification_kind"]');
      const extraCodeField = $(newForm).find('input[name$="-extra_code"]');
      const verifierField = $(newForm).find('select[name$="-verifier"]');

      updateFieldOptions(verifierField, []);
      extraCodeField.prop('disabled', true).attr('placeholder', 'n/a').addClass('disabled-field');

      certificationKindField.on('change', () => handleCertificationKindChange(certificationKindField, extraCodeField, verifierField));
    }
  });

  const existingForms = $('div[id^="orchardcertification_set-"]');
  existingForms.each((index, form) => {
    const certificationKindField = $(form).find(`select[name$="${index-1}-certification_kind"]`);
    const extraCodeField = $(form).find(`input[name$="${index-1}-extra_code"]`);
    const verifierField = $(form).find(`select[name$="${index-1}-verifier"]`);

    if (certificationKindField.val()) {
      handleCertificationKindChange(certificationKindField, extraCodeField, verifierField);
    }

    certificationKindField.on('change', () => handleCertificationKindChange(certificationKindField, extraCodeField, verifierField));
  });

});
