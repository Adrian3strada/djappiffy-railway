document.addEventListener("DOMContentLoaded", function () {
    function fetchOptions(url) {
        return $.ajax({ url, method: 'GET', dataType: 'json' });
    }

    function capitalize(str) {
        return str.toLowerCase().replace(/(?:^|\s)[a-záéíóúñ]/g, m => m.toUpperCase());
    }

    function updateHiddenField(form) {
        const data = [];
        form.find('.additional-inputs input').each(function () {
            const el = $(this);
            const attrs = {};
            $.each(this.attributes, function () {
                if (this.specified && !['type', 'value', 'name', 'id', 'class', 'data-field-id', 'data-field-name', 'data-data_type'].includes(this.name)) {
                    attrs[this.name] = this.value;
                }
            });
            data.push({
                id: parseInt(el.data('field-id'), 10),
                field_name: el.data('field-name'),
                data_type: el.data('data_type'),
                value: el.val(),
                attrs
            });
        });
        let hidden = form.find('input[name="additional_inputs"]');
        if (!hidden.length) hidden = $('<input type="hidden" name="additional_inputs">').appendTo(form);
        hidden.val(JSON.stringify(data));
    }

    function updateAdditionalInputs(data, container, form) {
        container.empty();
        let storedInputs = [];
        const hidden = form.find('input[name="additional_inputs"]');
        if (hidden.length && hidden.val()) {
            try { storedInputs = JSON.parse(hidden.val()) || []; } catch {}
        }

        if (data?.additional_inputs?.length) {
            data.additional_inputs.forEach(input => {
                const type = input.data_type === 'int' ? 'number' : input.data_type;
                const attrs = input.data_type === 'int' ? 'step="1" min="0"' : '';
                const stored = storedInputs.find(x => x.id === input.id);
                let value = '';
                let readonly = '';
                let extraAttrs = '';

                if (stored) {
                    value = stored.value;
                    readonly = 'readonly';
                    if (stored.attrs) {
                        for (const [k, v] of Object.entries(stored.attrs)) {
                            extraAttrs += `${k}="${v}" `;
                        }
                    }
                }

                container.append(`
                    <div class="form-group field-additional-${input.id}">
                        <div class="row">
                            <label class="col-sm-3">${capitalize(input.name)} ${input.is_required ? '<span class="text-red">*</span>' : ''}</label>
                            <div class="col-sm-7">
                                <input type="${type}" ${attrs} ${extraAttrs} name="additional_input_${input.id}"
                                    class="form-control vTextField ${readonly}-field"
                                    data-field-id="${input.id}" data-field-name="${capitalize(input.name)}"
                                    data-data_type="${type}" value="${value}" ${readonly}>
                            </div>
                        </div>
                    </div>
                `);
            });

            container.find('input').on('change input', () => updateHiddenField(form));
            updateHiddenField(form);
        }
    }

    function handlePaymentKindChange(select, form) {
        const id = select.val();
        let container = form.find('.additional-inputs');
        if (!container.length) {
            select.closest('.form-group').after('<div class="additional-inputs"></div>');
            container = form.find('.additional-inputs');
        }

        if (id) {
            fetchOptions(`/rest/v1/purchases/payment-additional-inputs/?payment_kind=${id}&is_enabled=true`).then(data => {
                updateAdditionalInputs(data, container, form);
                toggleBankField(form, data.requires_bank);
            });
        } else {
            container.empty();
            updateHiddenField(form);
        }
    }

    function toggleBankField(form, show) {
        const wrapper = form.find('[name="bank"]').closest('.form-row, .form-group');
        if (show) {
            wrapper.show();
            wrapper.find('select').prop('required', true);
        } else {
            wrapper.hide();
            wrapper.find('select').prop('required', false);
        }
    }

    function toggleOrderFields(form, category) {
        form.find('select[name="purchase_order"]').closest('.form-row, .form-group').toggle(category === 'purchase_order');
        form.find('select[name="service_order"]').closest('.form-row, .form-group').toggle(category === 'service_order');
    }

    function handleCategoryChange(select, form) {
        const cat = select.val();
        const provider = form.find('select[name="provider"]');
        toggleOrderFields(form, cat);

        if (!provider.length) return;

        let url = '';
        if (cat === 'purchase_order') url = '/rest/v1/catalogs/provider/?category=supply_provider&is_enabled=true';
        if (cat === 'service_order') url = '/rest/v1/catalogs/provider/?category=service_provider&is_enabled=true';

        if (url) {
            fetchOptions(url).then(data => {
                provider.empty().append('<option value="">---------</option>');
                data.forEach(p => provider.append(`<option value="${p.id}">${p.name}</option>`));
            });
        }
    }

    function formatDate(d) {
        const date = new Date(d);
        return `${String(date.getDate()).padStart(2, '0')}/${String(date.getMonth() + 1).padStart(2, '0')}/${date.getFullYear()}`;
    }

    function handleProviderChange(providerField, form) {
        const providerId = providerField.val();
        const category = form.find('select[name="category"]').val();
        const purchase = form.find('select[name="purchase_order"]');
        const service = form.find('select[name="service_order"]');

        if (!providerId || !category) return;

        if (category === 'purchase_order') {
            fetchOptions(`/rest/v1/purchases/purchase-order/?provider=${providerId}`).then(data => {
                purchase.empty();
                data.forEach(o => purchase.append(`<option value="${o.id}" data-balance="${o.balance_payable}">Folio ${o.ooid} - $${o.balance_payable}</option>`));
            });
            service.empty();
        }

        if (category === 'service_order') {
            fetchOptions(`/rest/v1/purchases/service-order/?provider=${providerId}`).then(data => {
                service.empty();
                data.forEach(o => {
                    const label = o.category === 'time_period'
                        ? `${capitalize(o.category.replace(/_/g, ' '))} (${formatDate(o.start_date)} - ${formatDate(o.end_date)})`
                        : `${capitalize(o.category.replace(/_/g, ' '))} ${o.batch}`;
                    service.append(`<option value="${o.id}" data-balance="${o.balance_payable}">${label} - $${o.balance_payable}</option>`);
                });
            });
            purchase.empty();
        }
    }

    function updateAmountField(form) {
        // Solo calcular si NO estamos editando
        const isEditing = form.find('input[name="amount"]').data('original') === true;
        if (isEditing) return;

        const category = form.find('select[name="category"]').val();
        let total = 0;

        if (category === 'purchase_order') {
            form.find('select[name="purchase_order"] option:selected').each(function () {
                total += parseFloat($(this).data('balance') || 0);
            });
        }

        if (category === 'service_order') {
            form.find('select[name="service_order"] option:selected').each(function () {
                total += parseFloat($(this).data('balance') || 0);
            });
        }

        const amount = form.find('input[name="amount"]');
        amount.val(total.toFixed(2));
    }

    const $form = $('form');
    $form.find('input[name="amount"]').data('original', $form.find('input[name="amount"]').val() !== "");
    const categoryField = $form.find('select[name="category"]');
    const providerField = $form.find('select[name="provider"]');
    const paymentKindField = $form.find('select[name="payment_kind"]');
    const purchaseField = $form.find('select[name="purchase_order"]');
    const serviceField = $form.find('select[name="service_order"]');

    purchaseField.on('change', () => updateAmountField($form));
    serviceField.on('change', () => updateAmountField($form));

    paymentKindField.on('change', () => handlePaymentKindChange(paymentKindField, $form));
    categoryField.on('change', () => handleCategoryChange(categoryField, $form));
    providerField.on('change', () => handleProviderChange(providerField, $form));

    const hasPurchase = purchaseField.val() && purchaseField.val().length > 0;
    const hasService = serviceField.val() && serviceField.val().length > 0;
    const isEditing = hasPurchase || hasService;

    if (!isEditing) {
        categoryField.trigger('change');
        providerField.trigger('change');
    } else {
        toggleOrderFields($form, categoryField.val());
        updateAmountField($form);
    }

    if (paymentKindField.val()) handlePaymentKindChange(paymentKindField, $form);
});
