document.addEventListener('DOMContentLoaded', () => {

  function updateFieldOptions(field, options) {
    field.empty().append(new Option('---------', '', true, true));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, false));
    });
    field.trigger('change').select2();
  }

  function fetchOptions(url) {
    return fetch(url).then(response => response.json());
  }

  document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'orchardcertification_set') {

      const newForm = $(event.target);
      const extraCodeField = newForm.find('input[name$="-extra_code"]');
      const certificationKindField = newForm.find('select[name$="-certification_kind"]');
      extraCodeField.prop('disabled', true);
      extraCodeField.attr('placeholder', 'n/a');

      certificationKindField.on('change', () => {
        console.log('Certification kind changed:', certificationKindField.val());
        extraCodeField.val(null);
        extraCodeField.prop('disabled', certificationKindField.val() !== 1);
        // updateCountry(certificationKind.val(), newForm);
        fetch(`/rest/v1/packhouse-settings/orchard-certification-kind/${certificationKindField.val()}/`)
          .then(response => response.json())
      });


    }
  });

  const existingForms = $('div[id^="maquiladoraclient_set-"]');
  existingForms.each((index, form) => {
    const marketField = $(form).find('select[name$="-market"]');
    const countryField = $(form).find('select[name$="-country"]');
    const stateField = $(form).find('select[name$="-state"]');
    const cityField = $(form).find('select[name$="-city"]');

    marketField.on('change', () => {
      updateCountry(marketField.val(), $(form));
    });

    countryField.on('change', () => {
      updateState($(form));
    });

    stateField.on('change', () => {
      updateCity($(form));
    });

    if (marketField.val()) {
      updateCountry(marketField.val(), $(form));
    }
  });


});
