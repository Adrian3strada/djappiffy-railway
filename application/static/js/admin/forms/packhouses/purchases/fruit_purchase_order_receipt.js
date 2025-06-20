document.addEventListener("DOMContentLoaded", function () {

    function fetchOptions(url) {
        return $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json'
        }).fail(error => console.error('Error al obtener proveedores/productores:', error));
    }

    function getFormPrefixFromName(nameAttr) {
        if (!nameAttr) return null;
        const match = nameAttr.match(/^(fruitpurchaseorderreceipt_set-\d+)-/);
        return match ? match[1] : null;
    }

    function handleReceiptKindChange(receiptKindField) {
        const prefix = getFormPrefixFromName(receiptKindField.attr("name"));
        if (!prefix) return;

        const providerField = $(`#id_${prefix}-provider`);
        const kind = receiptKindField.val();

        const batchField = $("#id_batch");
        let batchId;

        const batchIdReadonly = getBatchId();
        if (batchIdReadonly) {
           batchId = batchIdReadonly;
        }else{
            batchId = batchField.val();
        }


        if (!batchId) {
            providerField.empty().append($('<option>').val('').text('---------'));
            return;
        }

        const endpoint = `/rest/v1/receiving/batch/?id=${batchId}`;

        fetchOptions(endpoint).then(data => {
            providerField.empty().append($('<option>').val('').text('---------'));

            if (!Array.isArray(data) || data.length === 0) return;

            const batch = data[0];
            let provider = null;

            if (kind === "producer") {
                provider = batch.yield_orchard_producer;
            } else if (kind === "provider") {
                provider = batch.harvest_product_provider;
            }

            if (provider) {
                const $opt = $('<option>').val(provider.id).text(provider.name).prop('selected', true);
                providerField.append($opt);
            }
        }).fail(error => {
            console.error('Error al obtener proveedor desde el batch:', error);
        });
    }

    function handleContainerVisibility(priceCategoryField, formElement) {
        const prefix = getFormPrefixFromName(priceCategoryField.attr("name"));
        if (!prefix) return;

        const containerRow = formElement.find(`#id_${prefix}-container_capacity`).closest('.form-row, .form-group');
        containerRow.hide();

        const categoryId = priceCategoryField.val();
        if (!categoryId) {
            containerRow.hide();
            return;
        }

        const url = `/rest/v1/base/fruit-purchase-price-category/?id=${categoryId}&is_enabled=true`;

        $.get(url, function (data) {
            if (Array.isArray(data) && data.length > 0 && data[0].is_container === true) {
                containerRow.show();
            } else {
                containerRow.hide();
                formElement.find(`#id_${prefix}-container_capacity`).val('');
            }
        });
    }

    function updateTotalCostInForm(prefix) {
        const quantityField = $(`#id_${prefix}-quantity`);
        const unitPriceField = $(`#id_${prefix}-unit_price`);
        const totalCostField = $(`#id_${prefix}-total_cost`);

        const quantity = parseFloat(quantityField.val());
        const unitPrice = parseFloat(unitPriceField.val());

        if (!isNaN(quantity) && !isNaN(unitPrice)) {
            const total = (quantity * unitPrice).toFixed(2);
            totalCostField.val(total);
        } else {
            totalCostField.val('');
        }
    }

    function attachRealtimeTotalCalculation(formElement) {
        const quantityField = formElement.find('input[name$="-quantity"]');
        const unitPriceField = formElement.find('input[name$="-unit_price"]');
        const prefix = getFormPrefixFromName(quantityField.attr("name"));

        function onChangeHandler() {
            updateTotalCostInForm(prefix);
        }

        quantityField.on('input', onChangeHandler);
        unitPriceField.on('input', onChangeHandler);

        // Trigger inicial si ya hay valores cargados
        onChangeHandler();
    }

    // Formularios existentes al cargar la página
    $('select[name$="-receipt_kind"]').each(function () {
        const field = $(this);
        handleReceiptKindChange(field);
        updateReceiptKindOptions();
        field.on('change', function () {
            handleReceiptKindChange(field);
            updateReceiptKindOptions();
        });
    });

    $('select[name$="-price_category"]').each(function () {
        const field = $(this);
        const $form = field.closest('div[id^="fruitpurchaseorderreceipt_set-"]');
        handleContainerVisibility(field, $form);
        field.on('change', function () {
            handleContainerVisibility(field, $form);
        });
    });

    $('div[id^="fruitpurchaseorderreceipt_set-"]').each(function () {
        const $form = $(this);
        attachRealtimeTotalCalculation($form);
    });

    function ensureBatchInfoBox() {
        if ($("#batch-info-box").length === 0) {
            const html = `
                <div class="form-group field-batch-summary" id="batch-info-box">
                    <div class="row" style="margin-bottom: 1rem;">
                        <label class="col-sm-3 text-left">Productor</label>
                        <div class="col-sm-7 field-batch-summary-producer">
                            <div id="batch-yield-producer" class="readonly">—</div>
                            <div class="help-block red"></div>
                            <div class="help-block text-red"></div>
                        </div>
                    </div>
                    <div class="row" style="margin-bottom: 1rem;">
                        <label class="col-sm-3 text-left">Proveedor</label>
                        <div class="col-sm-7 field-batch-summary-provider">
                            <div id="batch-harvest-provider" class="readonly">—</div>
                            <div class="help-block red"></div>
                            <div class="help-block text-red"></div>
                        </div>
                    </div>
                    <div class="row" style="margin-bottom: 1rem;">
                        <label class="col-sm-3 text-left">Peso ingresado</label>
                        <div class="col-sm-7 field-batch-summary-weight">
                            <div id="batch-weight_received" class="readonly">—</div>
                            <div class="help-block red"></div>
                            <div class="help-block text-red"></div>
                        </div>
                    </div>
                </div>
            `;
            $(".field-batch").closest(".form-group").after(html);
        }
    }

    function getBatchId() {
        const $batchLink = $('.field-batch .readonly a');
        if ($batchLink.length === 0) return null;

        const href = $batchLink.attr('href');
        const match = href.match(/\/batch\/(\d+)\/change/);
        return match ? match[1] : null;
    }

    $(document).on('change', '#id_batch', function () {
        const batchId = $(this).val();
        const endpoint = `/rest/v1/receiving/batch/?id=${batchId}`;

        if (!batchId){
          if($("#batch-yield-producer").length ) {
            $("#batch-yield-producer").text('—');
            $("#batch-harvest-provider").text('—');
            $("#batch-weight_received").text('—');
          }
          return;
        }

        ensureBatchInfoBox();

        $.get(endpoint, function (data) {
            if (!Array.isArray(data) || data.length === 0) return;

            const batch = data[0];

            $("#batch-yield-producer").text(batch.yield_orchard_producer?.name || '—');
            $("#batch-harvest-provider").text(batch.harvest_product_provider?.name || '—');
            $("#batch-weight_received").text(
                batch.weight_received != null ? `${batch.weight_received}` : '—'
            );
        });

        // Refresca los providers de los recibos
        $('select[name$="-receipt_kind"]').each(function () {
            handleReceiptKindChange($(this));
            updateReceiptKindOptions();
        });
    });

    const batchIdReadonly = getBatchId();
      if (batchIdReadonly) {
          ensureBatchInfoBox();
          const endpoint = `/rest/v1/receiving/batch/?id=${batchIdReadonly}`;

          $.get(endpoint, function (data) {

              if (!Array.isArray(data) || data.length === 0) return;

              const batch = data[0];
              $("#batch-yield-producer").text(batch.yield_orchard_producer?.name || '—');
              $("#batch-harvest-provider").text(batch.harvest_product_provider?.name || '—');
              $("#batch-weight_received").text(
                  batch.weight_received != null ? `${batch.weight_received}` : '—'
              );
          });

          // Y actualiza también los providers de los inlines por si acaso
          $('select[name$="-receipt_kind"]').each(function () {
              handleReceiptKindChange($(this));
              updateReceiptKindOptions();
          });
      }

    // Lógica al agregar un nuevo formulario inline
    document.addEventListener('formset:added', (event) => {
        if (event.detail.formsetName === 'fruitpurchaseorderreceipt_set') {
            const $form = $(event.target);
            const receiptKindField = $form.find('select[name$="-receipt_kind"]');
            const priceCategoryField = $form.find('select[name$="-price_category"]');

            // Al cambiar el kind, actualiza el proveedor
            receiptKindField.on('change', function () {
                handleReceiptKindChange(receiptKindField);
                updateReceiptKindOptions();
            });

            // Ejecuta una vez por default al agregarse
            handleReceiptKindChange(receiptKindField);

            // Lógica para mostrar u ocultar el container_capacity
            priceCategoryField.on('change', function () {
                handleContainerVisibility(priceCategoryField, $form);
            });

            handleContainerVisibility(priceCategoryField, $form);

            // Lógica para el cálculo en tiempo real
            attachRealtimeTotalCalculation($form);
        }
    });

      function updateReceiptKindOptions() {
          const selects = $('select[name$="-receipt_kind"]').filter(function () {
              const deleteCheckbox = $(this).closest('.inline-related').find('input[type="checkbox"][name$="-DELETE"]');
              return !(deleteCheckbox.length && deleteCheckbox.is(':checked'));
          });

          const selectedValues = selects
              .map(function () {
                  return $(this).val();
              })
              .get()
              .filter(Boolean);

          selects.each(function () {
              const currentSelect = $(this);
              const currentValue = currentSelect.val();

              currentSelect.find('option').each(function () {
                  const option = $(this);
                  const optionVal = option.attr('value');

                  option.prop('disabled', optionVal && selectedValues.includes(optionVal) && optionVal !== currentValue);
              });
          });
      }

      $(document).on('click', '.inline-deletelink', function(){
          setTimeout(updateReceiptKindOptions, 100);
      });

      $(document).on('change', 'input[type="checkbox"][name$="-DELETE"]', function(){
          setTimeout(updateReceiptKindOptions, 100);
      });


});
