document.addEventListener('DOMContentLoaded', () => {
    const providerSelect = $('#id_provider');
    const serviceSelect = $('#id_service');
    const categorySelect = $('#id_category');

    // Campos y labels
    const startDateField = $('.field-start_date');
    const endDateField = $('.field-end_date');
    const batchField = $('.field-batch');

    const startDateInput = $('#id_start_date');
    const endDateInput = $('#id_end_date');
    const batchInput = $('#id_batch');

    const batchLabel = $('label[for="id_batch"]');

    function loadServices(providerId) {
        if (!providerId) {
            serviceSelect.empty();
            serviceSelect.append($('<option></option>').text("---------"));
            return;
        }

        let previouslySelectedServiceId = serviceSelect.val();
        if (!previouslySelectedServiceId || previouslySelectedServiceId.trim() === "") {
            previouslySelectedServiceId = serviceSelect.data('initial-value');
        }

        serviceSelect.empty();

        $.ajax({
            url: '/rest/v1/catalogs/service/',
            data: {
                service_provider: providerId,
                is_enabled: true
            },
            success: function(response) {
                serviceSelect.empty();
                serviceSelect.append($('<option></option>').text("---------"));

                let found = false;

                $.each(response, function(index, service) {
                    const option = $('<option></option>')
                        .attr('value', service.id)
                        .text(service.name);

                    if (service.id == previouslySelectedServiceId) {
                        option.prop('selected', true);
                        found = true;
                    }

                    serviceSelect.append(option);
                });

                if (!found && previouslySelectedServiceId) {
                    serviceSelect.val(previouslySelectedServiceId);
                }
            },
            error: function(xhr, status, error) {
                console.error("Error al cargar los servicios:", error);
                serviceSelect.empty();
                serviceSelect.append($('<option></option>').text("Error al cargar"));
            }
        });
    }

    function toggleFieldsByCategory(categoryValue) {
        if (categoryValue === 'time_period') {
            startDateField.show();
            endDateField.show();
            batchField.hide();

            batchInput.prop('required', false);
            startDateInput.prop('required', true);
            endDateInput.prop('required', true);

            removeRequiredAsterisk(batchLabel);
        } else if (categoryValue === 'for_batch') {
            startDateField.hide();
            endDateField.hide();
            batchField.show();

            batchInput.prop('required', true);
            startDateInput.prop('required', false);
            endDateInput.prop('required', false);

            addRequiredAsterisk(batchLabel);
        } else {
            startDateField.hide();
            endDateField.hide();
            batchField.hide();

            batchInput.prop('required', false);
            startDateInput.prop('required', false);
            endDateInput.prop('required', false);

            removeRequiredAsterisk(batchLabel);
        }
    }

    function addRequiredAsterisk(label) {
        if (!label.find('.asteriskField').length) {
            label.append('<span class="asteriskField">*</span>');
        }
    }

    function removeRequiredAsterisk(label) {
        label.find('.asteriskField').remove();
    }

    // Eventos de cambio
    providerSelect.change(function () {
        const providerId = $(this).val();
        loadServices(providerId);
    });

    categorySelect.change(function () {
        const selectedCategory = $(this).val();
        toggleFieldsByCategory(selectedCategory);
    });

    // Al cargar la página
    const initialProviderId = providerSelect.val();
    if (initialProviderId && initialProviderId.trim() !== "") {
        loadServices(initialProviderId);
    }

    const initialCategory = categorySelect.val();
    toggleFieldsByCategory(initialCategory);

    function formatDecimal(value) {
    const number = parseFloat(value);
    if (isNaN(number)) return '0.00';
    return number.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

    function updateTotalCostPreview() {
        const cost = parseFloat($('#id_cost').val()) || 0;
        const tax = parseFloat($('#id_tax').val()) || 0;

        if (tax < 0 || tax > 100) return; // Evita mostrar cosas locas

        const total = cost + (cost * (tax / 100));
        const formatted = formatDecimal(total);

        $('.field-total_cost .readonly').text(formatted);
    }

    $('#id_cost, #id_tax').on('input', updateTotalCostPreview);

});
