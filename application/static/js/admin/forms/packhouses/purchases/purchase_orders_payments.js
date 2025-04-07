document.addEventListener("DOMContentLoaded", function () {

    function fetchOptions(url) {
        return $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json'
        }).fail(error => console.error('Error al obtener opciones:', error));
    }

    function capitalize(str) {
        return str.toLowerCase().replace(/(?:^|\s)[a-záéíóúñ]/g, function(match) {
            return match.toUpperCase();
        });
    }

    function getFullPrefix(formContainer) {
      // Buscar el primer elemento cuyo name comience con "purchaseorderpayment_set-"
      // y que NO contenga "TOTAL_FORMS", "INITIAL_FORMS", "MIN_NUM_FORMS" o "MAX_NUM_FORMS"
      const $el = formContainer
        .find('[id^="id_purchaseorderpayment_set-"]')
        .filter(function () {
          const name = $(this).attr('name');
          return !/(TOTAL_FORMS|INITIAL_FORMS|MIN_NUM_FORMS|MAX_NUM_FORMS)/.test(name);
        })
        .first();
      return $el.length ? $el.attr('name').split('-').slice(0, 2).join('-') : null;
    }

    function updateHiddenField(formContainer) {
        const additionalInputsData = [];
        const fullPrefix = getFullPrefix(formContainer);
        if (!fullPrefix) return; // Si no se pudo obtener el prefijo, salimos

        // Recorrer solo los inputs dentro de .additional-inputs de este formset
        formContainer.find('.additional-inputs input').each(function () {
            const $this = $(this);
            const fieldId = parseInt($this.data('field-id'), 10);
            const fieldName = $this.data('field-name');
            const dataType = $this.data('data_type');
            const value = $this.val();

            const attrs = {};
            $.each(this.attributes, function () {
                if (
                  this.specified &&
                  !['type', 'value', 'name', 'id', 'class', 'data-field-id', 'data-field-name', 'data-data_type'].includes(this.name)
                ) {
                    attrs[this.name] = this.value;
                }
            });

            additionalInputsData.push({
                id: fieldId,
                field_name: fieldName,
                data_type: dataType,
                value: value,
                attrs: attrs
            });
        });

        // Buscar o crear el campo oculto para este formset específico
        let hiddenField = formContainer.find(`input[name="${fullPrefix}-additional_inputs"]`);
        if (!hiddenField.length) {
            hiddenField = $(`<input type="hidden" name="${fullPrefix}-additional_inputs">`);
            formContainer.append(hiddenField);
        }
        hiddenField.val(JSON.stringify(additionalInputsData));
    }

    function updateAdditionalInputs(data, container, formContainer) {
        container.empty();
        const fullPrefix = getFullPrefix(formContainer);
        if (!fullPrefix) return;

        let storedInputs = [];
        const hiddenField = formContainer.find(`input[name="${fullPrefix}-additional_inputs"]`);
        if (hiddenField.length && hiddenField.val()) {
            try {
                storedInputs = JSON.parse(hiddenField.val());
            } catch (e) {
                console.error("Error al parsear el JSON almacenado:", e);
            }
        }

        if (data && data.length) {
            data.forEach(function (inputData) {
                let attrs = '';
                if (inputData.data_type === 'int') {
                    inputData.data_type = 'number';
                    attrs = 'step="1" min="0" oninput="this.value = Math.abs(this.value)"';
                }

                let prepopulated = '';
                let storedData = storedInputs.find(x => x.id === inputData.id);
                let extraAttrs = '';
                let readonly = '';

                if (storedData) {
                    prepopulated = storedData.value;
                    inputData.data_type = storedData.data_type || inputData.data_type;
                    if (storedData.attrs) {
                        for (const [key, value] of Object.entries(storedData.attrs)) {
                            extraAttrs += `${key}="${value}" `;
                        }
                    }
                    readonly = 'readonly';
                }

                const uniqueFieldId = `${fullPrefix}-${inputData.id}`;

                const fieldHtml = `
                    <div class="form-group field-additional-${uniqueFieldId}">
                        <div class="row">
                            <label class="col-sm-3 text-left" for="${fullPrefix}-additional_input_${inputData.id}" style="text-transform: capitalize;">
                                ${capitalize(inputData.name)} ${inputData.is_required ? '<span class="text-red">*</span>' : ''}
                            </label>
                            <div class="col-sm-7">
                                <input type="${inputData.data_type}" ${attrs} ${extraAttrs}
                                    name="${fullPrefix}-additional_input_${inputData.id}"
                                    id="id_${fullPrefix}-additional_input_${inputData.id}"
                                    class="form-control vTextField ${readonly}-field"
                                    data-field-id="${inputData.id}"
                                    data-field-name="${capitalize(inputData.name)}"
                                    data-data_type="${inputData.data_type}"
                                    value="${prepopulated}"
                                    ${readonly}
                                    >
                            </div>
                        </div>
                    </div>
                `;
                container.append(fieldHtml);

                setTimeout(() => {
                    container.find(`.field-additional-${uniqueFieldId}`).addClass('show');
                }, 150);
            });

            container.find('input').on('change input', function () {
                updateHiddenField(formContainer);
            });

            updateHiddenField(formContainer);
        } else {
            updateHiddenField(formContainer);
        }
    }

function handlePaymentkindChange(paymentkindField, formContainer) {
    const paymentkindId = paymentkindField.val();
    let additionalContainer = formContainer.find('.additional-inputs');
    if (!additionalContainer.length) {
        paymentkindField.closest('.form-group').after('<div class="additional-inputs"></div>');
        additionalContainer = formContainer.find('.additional-inputs');
    }

    if (paymentkindId) {
        fetchOptions(`/rest/v1/purchases/payment-additional-inputs/?payment_kind=${paymentkindId}&is_enabled=true`)
            .then(data => {
                updateAdditionalInputs(data, additionalContainer, formContainer);
            })
            .catch(error => console.error('Error al obtener los inputs adicionales:', error));
    } else {
        additionalContainer.empty();
        updateHiddenField(formContainer);
    }
}

// Maneja los forms ya existentes en el DOM, excluyendo los management forms
const existingForms = $('div[id^="purchaseorderpayment_set-"]').filter(function () {
  return !this.id.match(/TOTAL_FORMS|INITIAL_FORMS|MIN_NUM_FORMS|MAX_NUM_FORMS/);
});
existingForms.each((index, form) => {
  const $form = $(form);
  // Para el selector usamos index-1: si index > 0, sino 0
  const idx = index > 0 ? index - 1 : 0;
  const paymentkindField = $form.find(`select[name$="${idx}-payment_kind"]`);

  if (paymentkindField.val()) {
    handlePaymentkindChange(paymentkindField, $form);
  }

  paymentkindField.on('change', () => {
    handlePaymentkindChange(paymentkindField, $form);
  });
});

// Maneja los nuevos forms agregados
document.addEventListener('formset:added', (event) => {
  if (event.detail.formsetName === 'purchaseorderpayment_set') {
    const $newForm = $(event.target);
    const paymentkindField = $newForm.find('select[id^="id_purchaseorderpayment_set-"][name$="-payment_kind"]');
    paymentkindField.on('change', function () {
      handlePaymentkindChange(paymentkindField, $newForm);
    });
    handlePaymentkindChange(paymentkindField, $newForm);
  }
});

});
