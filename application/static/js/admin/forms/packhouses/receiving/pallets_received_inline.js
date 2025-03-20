document.addEventListener('DOMContentLoaded', () => {

    const packhouseWeightField = $('input[name="packhouse_weight_result"]');

    function makeFieldReadonly(field) {
        field.prop("readonly", true).css({
            "pointer-events": "none",
            "background-color": "#e9ecef"
        });
    }

    function updatePackhouseWeight() {
        let totalWeight = 0;

        $('input[name$="-net_weight"]').each(function () {
            totalWeight += parseFloat($(this).val()) || 0;
        });

        packhouseWeightField.val(totalWeight.toFixed(2)).trigger('change');;
        updateAveragePerBoxes();
    }

    function initializeFormFields(form) {
        const grossWeightField = $(form).find('input[name$="-gross_weight"]');
        const totalBoxesField = $(form).find('input[name$="-total_boxes"]');
        const harvestContainerField = $(form).find('select[name$="-harvest_container"]');
        const containerTareField = $(form).find('input[name$="-container_tare"]');
        const platformTareField = $(form).find('input[name$="-platform_tare"]');
        const netWeightField = $(form).find('input[name$="-net_weight"]');

        makeFieldReadonly(containerTareField);
        makeFieldReadonly(netWeightField);

        function updateContainerTare() {
            const totalBoxes = parseFloat(totalBoxesField.val()) || 0;
            const harvestContainer = parseFloat(harvestContainerField.val()) || 0;
            containerTareField.val((totalBoxes * harvestContainer).toFixed(2));
            updateNetWeight();
        }

        function updateNetWeight() {
            const grossWeight = parseFloat(grossWeightField.val()) || 0;
            const platformTare = parseFloat(platformTareField.val()) || 0;
            const containerTare = parseFloat(containerTareField.val()) || 0;
            const netWeight = grossWeight - platformTare - containerTare;
            netWeightField.val(netWeight.toFixed(2));
            updatePackhouseWeight(); 
        }

        grossWeightField.on('input', updateNetWeight);
        totalBoxesField.on('input', updateContainerTare);
        harvestContainerField.on('change', updateContainerTare);
        platformTareField.on('input', updateNetWeight);
        netWeightField.on('input', updatePackhouseWeight); 

        updatePackhouseWeight(); 
    }

    // Inicializar formularios existentes
    document.querySelectorAll('div[id^="palletreceived_set-"]').forEach(initializeFormFields);

    // Manejar nuevos formularios añadidos dinámicamente
    document.addEventListener('formset:added', (event) => {
        if (event.detail.formsetName === 'palletreceived_set') {
            initializeFormFields(event.target);
        }
    });

    // Manejar eliminación de formularios
    document.addEventListener('formset:removed', () => {
        updatePackhouseWeight();  // Se actualiza el total cuando se elimina un formulario
    });

});
