document.addEventListener("DOMContentLoaded", function () {

    function fetchOptions(url) {
        return $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json'
        }).fail(error => console.error('Error fetching options:', error));
    }

    function capitalize(str) {
        return str.toLowerCase().replace(/(?:^|\s)[a-záéíóúñ]/g, function(match) {
            return match.toUpperCase();
        });
    }

    function getFullPrefix(formContainer) {
        const $el = formContainer
            .find('[id^="id_fruitpurchaseorderpayment_set-"]')
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
        if (!fullPrefix) return;

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
                storedInputs = JSON.parse(hiddenField.val()) || [];
            } catch (e) {
                console.error("Error parsing JSON:", e);
            }
        }

        if (data && data['additional_inputs'].length) {
            data['additional_inputs'].forEach(function (inputData) {
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
                    if (typeof data.requires_bank !== 'undefined') {
                        toggleBankField(formContainer, data.requires_bank);
                    }
                })
                .catch(error => console.error('Error loading additional inputs:', error));
        } else {
            additionalContainer.empty();
            updateHiddenField(formContainer);
        }
    }

    function toggleBankField(formContainer, shouldShow) {
        const bankFieldWrapper = formContainer.find('[id$="-bank"]').closest('.form-row, .form-group');
        if (shouldShow) {
            bankFieldWrapper.show();
            bankFieldWrapper.find('select').prop('required', true);
        } else {
            bankFieldWrapper.hide();
            bankFieldWrapper.find('select').prop('required', false);
        }
    }

    // Forms ya presentes
    const existingForms = $('div[id^="fruitpurchaseorderpayment_set-"]').filter(function () {
        return !this.id.match(/TOTAL_FORMS|INITIAL_FORMS|MIN_NUM_FORMS|MAX_NUM_FORMS/);
    });

    existingForms.each((index, form) => {
        const $form = $(form);
        const idx = index > 0 ? index - 1 : 0;
        const paymentkindField = $form.find(`select[name$="${idx}-payment_kind"]`);

        if (paymentkindField.val()) {
            handlePaymentkindChange(paymentkindField, $form);
        }

        paymentkindField.on('change', () => {
            handlePaymentkindChange(paymentkindField, $form);
        });
    });

    // Obtener el ID de la orden de compra de frutas desde la URL
    function getFruitPurchaseOrderIdFromUrl() {
        const parts = window.location.pathname.split('/');
        const index = parts.indexOf('fruitpurchaseorder');
        if (index !== -1 && parts.length > index + 1) {
            return parts[index + 1];
        }
        return null;
    }


    // Nuevos forms agregados
    document.addEventListener('formset:added', (event) => {
        if (event.detail.formsetName === 'fruitpurchaseorderpayment_set') {
            setTimeout(updateSimulatedBalance, 100);
            const $newForm = $(event.target);
            const paymentkindField = $newForm.find('select[id^="id_fruitpurchaseorderpayment_set-"][name$="-payment_kind"]');
            const selectField = $newForm.find('select[id$="-fruit_purchase_order_receipt"]');
            const orderId = getFruitPurchaseOrderIdFromUrl();

            paymentkindField.on('change', function () {
                handlePaymentkindChange(paymentkindField, $newForm);
            });
            handlePaymentkindChange(paymentkindField, $newForm);
            $.get('/rest/v1/purchases/fruit-receipts/?fruit_purchase_order=' + orderId, function(data) {
                selectField.empty();
                selectField.append($('<option>', {
                    value: '',
                    text: '---------'
                }));

                data.forEach(function(receipt) {
                    selectField.append($('<option>', {
                        value: receipt.id,
                        text: '#' + receipt.ooid + " - " + receipt.provider_name
                    }));
                });
            });
        }
    });

    injectBalanceSummaryBox();

  function injectBalanceSummaryBox() {
      if ($('#balance-summary').length) return; // Evita duplicados
          const html = `
            <div id="balance-summary">
              <div><strong>Balance actual:</strong> $<span id="original-balance">—</span></div>
              <div><strong>Balance después de los pagos:</strong> $<span id="simulated-balance">—</span></div>
            </div>
          `;
          $('body').append(html);
      }

  function parseBalanceText(text) {
      if (!text) return 0;
      // Reemplaza punto de miles y coma decimal por punto
      const clean = text.replace(/\./g, '').replace(',', '.').replace(/\s/g, '');
      const num = parseFloat(clean);
      return isNaN(num) ? 0 : num;
  }

  function getOriginalBalance() {
      let total = 0;

      $('input[id^="id_fruitpurchaseorderreceipt_set-"][id$="-balance_payable"]').each(function () {
          const value = parseFloat($(this).val()) || 0;
          total += value;
      });

      return total;
  }

  function getNewPaymentsTotal() {
      let total = 0;
      const initialForms = parseInt($("#id_fruitpurchaseorderpayment_set-INITIAL_FORMS").val(), 10) || 0;

      $('div[id^="fruitpurchaseorderpayment_set-"]').each(function () {
          const formId = $(this).attr('id');

          // Se asegura que el form sea del tipo fruitpurchaseorderpayment_set-<número>
          const matchId = formId.match(/^fruitpurchaseorderpayment_set-(\d+)$/);
          if (!matchId) return;

          const amountField = $(this).find('input[name$="-amount"]');
          const nameAttr = amountField.attr('name') || '';
          const match = nameAttr.match(/fruitpurchaseorderpayment_set-(\d+)-amount/);
          if (!match) return;

          const index = parseInt(match[1], 10);
          const isNew = index >= initialForms;

          if (isNew) {
              const value = parseFloat(amountField.val().replace(',', '.')) || 0;
              total += value;
          }
      });
      return total;
  }

  function updateSimulatedBalance() {
      const original = getOriginalBalance();
      const newPayments = getNewPaymentsTotal();
      const simulated = original - newPayments;

      if(simulated < 0) {
        $('#simulated-balance').css('color', 'red');
      }else {
        $('#simulated-balance').css('color', 'black');
      }

      $('#original-balance').text(original.toLocaleString('es-MX', { minimumFractionDigits: 2 }));
      $('#simulated-balance').text(simulated.toLocaleString('es-MX', { minimumFractionDigits: 2 }));
  }

  function attachSimulatedBalanceListeners() {
      $(document).on('input', 'input[name$="-amount"]', updateSimulatedBalance);
      updateSimulatedBalance();
  }

  $(document).on('input', 'input[id^="id_fruitpurchaseorderpayment_set-"][id$="-amount"]', function () {
      updateSimulatedBalance();
  });

  attachSimulatedBalanceListeners();

});
