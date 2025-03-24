document.addEventListener('DOMContentLoaded', () => {
    const packhouseWeightResultField = $('#id_packhouse_weight_result');

    // ---------- Funciones Globales ----------
    const fetchContainerTare = (containerId) => {
        return $.ajax({
            url: `/rest/v1/catalogs/harvest-container/${containerId}`,
            method: 'GET',
            dataType: 'json'
        }).then(data => data.container_tare || data.kg_tare)
          .catch(() => 0);
    };

    const updatePackhouseWeight = () => {
        let totalWeight = 0;
        $('input[name$="-net_weight"]').each(function() {
            const $input = $(this);
            const $form = $input.closest('div[id^="palletreceived_set-"]');
            if (!$form.find('input[name$="-DELETE"]').prop('checked') && !isNaN($input.val())) {
                totalWeight += parseFloat($input.val());
            }
        });
        packhouseWeightResultField.val(totalWeight.toFixed(2)).trigger('change');
    };

    // ---------- Lógica para Formularios Existentes ----------
    const setupExistingForms = () => {
        document.querySelectorAll('div[id^="palletreceived_set-"]').forEach(form => {
            const $form = $(form);
            let tareValue = 0;

            // Elementos del formulario
            const grossWeightField = $form.find('input[name$="-gross_weight"]');
            const totalBoxesField = $form.find('input[name$="-total_boxes"]');
            const harvestContainerField = $form.find('select[name$="-harvest_container"]');
            const containerTareField = $form.find('input[name$="-container_tare"]');
            const platformTareField = $form.find('input[name$="-platform_tare"]');
            const netWeightField = $form.find('input[name$="-net_weight"]');

            // Cargar valor inicial
            fetchContainerTare(harvestContainerField.val()).then(tare => {
                tareValue = tare || 0;
                containerTareField.val((parseFloat(totalBoxesField.val()) * tareValue).toFixed(2));
            });

            // ----- Eventos con unbind -----
            // 1. Desvincular eventos previos
            harvestContainerField.off('change');
            grossWeightField.off('input');
            platformTareField.off('input');
            totalBoxesField.off('input');

            // 2. Vincular nuevos eventos
            harvestContainerField.on('change', function() {
                fetchContainerTare($(this).val()).then(tare => {
                    tareValue = tare || 0;
                    containerTareField.val((parseFloat(totalBoxesField.val()) * tareValue).toFixed(2));
                    updateNetWeight();
                    $(this).find('option:selected').prop('selected', true); // Fix visual
                });
            });

            const updateNetWeight = () => {
                const net = parseFloat(grossWeightField.val()) - parseFloat(platformTareField.val()) - parseFloat(containerTareField.val());
                netWeightField.val(net.toFixed(2));
                updatePackhouseWeight();
            };

            grossWeightField.add(platformTareField).on('input', updateNetWeight);
            totalBoxesField.on('input', () => {
                containerTareField.val((parseFloat(totalBoxesField.val()) * tareValue).toFixed(2));
                updateNetWeight();
            });
        });
    };

    // ---------- Lógica para Formularios Nuevos ----------
    const setupNewForm = (form) => {
        const $form = $(form);
        let tareValue = 0;

        // Elementos del formulario
        const grossWeightField = $form.find('input[name$="-gross_weight"]');
        const totalBoxesField = $form.find('input[name$="-total_boxes"]');
        const harvestContainerField = $form.find('select[name$="-harvest_container"]');
        const containerTareField = $form.find('input[name$="-container_tare"]');
        const platformTareField = $form.find('input[name$="-platform_tare"]');
        const netWeightField = $form.find('input[name$="-net_weight"]');

        // Inicialización forzada
        harvestContainerField.val('');
        containerTareField.val('0.00');

        // Eventos con unbind
        harvestContainerField.off('change').on('change', function() {
            fetchContainerTare($(this).val()).then(tare => {
                tareValue = tare || 0;
                containerTareField.val((parseFloat(totalBoxesField.val()) * tareValue).toFixed(2));
                updateNetWeight();
                $(this).find('option:selected').prop('selected', true); // Fix visual
            });
        });

        const updateNetWeight = () => {
            const net = parseFloat(grossWeightField.val()) - parseFloat(platformTareField.val()) - parseFloat(containerTareField.val());
            netWeightField.val(net.toFixed(2));
            updatePackhouseWeight();
        };

        grossWeightField.add(platformTareField).off('input').on('input', updateNetWeight);
        totalBoxesField.off('input').on('input', () => {
            containerTareField.val((parseFloat(totalBoxesField.val()) * tareValue).toFixed(2));
            updateNetWeight();
        });
    };

    // ---------- Inicialización ----------
    setupExistingForms();

    document.addEventListener('formset:added', (event) => {
        if (event.detail.formsetName === 'palletreceived_set') {
            setupNewForm(event.target);
        }
    });

    document.addEventListener('formset:removed', updatePackhouseWeight);
});