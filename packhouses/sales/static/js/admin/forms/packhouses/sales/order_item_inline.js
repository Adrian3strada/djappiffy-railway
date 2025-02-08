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

      updateFieldOptions(verifierField, []);
    }
  });

  const existingForms = $('div[id^="orchardcertification_set-"]');
  existingForms.each((index, form) => {
    const certificationKindField = $(form).find(`select[name$="${index-1}-certification_kind"]`);
  });

});
