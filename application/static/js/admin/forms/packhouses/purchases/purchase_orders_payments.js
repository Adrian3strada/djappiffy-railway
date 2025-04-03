document.addEventListener("DOMContentLoaded", function () {

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

    function updateHiddenField(formContainer) {
        const additionalInputsData = [];

        formContainer.find('.additional-inputs input').each(function () {
            const $this = $(this);
            const fieldId = parseInt($this.data('field-id'), 10);
            const fieldName = $this.data('field-name');
            const dataType = $this.data('data_type');
            const value = $this.val();

            const attrs = {};
            $.each(this.attributes, function () {
                if (this.specified && !['type', 'value', 'name', 'id', 'class', 'data-field-id', 'data-field-name', 'data-data_type'].includes(this.name)) {
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

        let hiddenField = formContainer.find('input[name$="-additional_inputs"]');
        if (!hiddenField.length) {
            const baseName = formContainer.find('select[name$="-payment_kind"]').attr('name');
            const hiddenName = baseName.replace('payment_kind', 'additional_inputs');
            hiddenField = $(`<input type="hidden" name="${hiddenName}">`);
            formContainer.append(hiddenField);
        }
        hiddenField.val(JSON.stringify(additionalInputsData));
    }

    function updateAdditionalInputs(data, container, formContainer) {
        container.empty();

        let storedInputs = [];
        let hiddenField = formContainer.find('input[name$="-additional_inputs"]');
        if (hiddenField.length) {
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

                if (storedData) {
                    prepopulated = storedData.value;
                    inputData.data_type = storedData.data_type || inputData.data_type;

                    if (storedData.attrs) {
                        for (const [key, value] of Object.entries(storedData.attrs)) {
                            extraAttrs += `${key}="${value}" `;
                        }
                    }
                }

                const fieldHtml = `
                    <div class="form-group field-additional-${inputData.id} fade-in">
                        <div class="row">
                            <label class="col-sm-3 text-left" for="id_additional_input_${inputData.id}" style="text-transform: capitalize;">
                                ${capitalize(inputData.name)} ${inputData.is_required ? '<span class="text-red">*</span>' : ''}
                            </label>
                            <div class="col-sm-7">
                                <input type="${inputData.data_type}" ${attrs} ${extraAttrs}
                                    name="additional_input_${inputData.id}" id="id_additional_input_${inputData.id}"
                                    class="form-control vTextField"
                                    data-field-id="${inputData.id}"
                                    data-field-name="${capitalize(inputData.name)}"
                                    data-data_type="${inputData.data_type}"
                                    value="${prepopulated}">
                            </div>
                        </div>
                    </div>
                `;
                container.append(fieldHtml);

                setTimeout(() => {
                    document.querySelector(`.field-additional-${inputData.id}`).classList.add('show');
                }, 50);
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

    document.addEventListener('formset:added', (event) => {
        if (event.detail.formsetName === 'purchaseorderpayment_set') {
            const newForm = $(event.target);
            const paymentkindField = newForm.find('select[name$="-payment_kind"]');

            paymentkindField.on('change', function () {
                handlePaymentkindChange(paymentkindField, newForm);
            });

            handlePaymentkindChange(paymentkindField, newForm);
        }
    });
});
