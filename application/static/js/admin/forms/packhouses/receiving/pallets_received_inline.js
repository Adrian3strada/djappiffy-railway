document.addEventListener('DOMContentLoaded', () => {
    const packhouseWeightResultField = $('#id_packhouse_weight_result');    

    // Función para obtener el peso del contenedor (container_tare)
    const fetchContainerTare = (containerId) => {
        console.log("[DEBUG] Fetching container ID:", containerId);  // 🐞
        return $.ajax({
            url: `/rest/v1/catalogs/harvest-container/${containerId}`,
            method: 'GET',
            dataType: 'json'
        }).then(data => {
            console.log("[DEBUG] API Response:", data);  // 🐞

            const tareValue = data.container_tare || data.kg_tare;
            console.log("[DEBUG] Received tare value:", tareValue);  // 🐞
            return tareValue;
            
        }).catch(error => {
            console.error("[ERROR] Failed to fetch tare value:", error);  // 🐞
            return 0; // Retorna 0 si hay un error
        });
    };

    // Función para hacer campos de solo lectura
    const makeFieldReadonly = (field) => {
        field.prop("readonly", true).css({
            "pointer-events": "none",
            "background-color": "#e9ecef"
        });
    };

    // Función principal para actualizar el peso total
    const updatePackhouseWeight = () => {
        let totalWeight = 0;
    
        $('input[name$="-net_weight"]').each(function () {
            const $input = $(this);
            const $form = $input.closest('div[id^="palletreceived_set-"]');
            
            const isDeleted = $form.find('input[name$="-DELETE"]').prop('checked');
            const isHidden = $form.css('display') === 'none';
            
            if (!isDeleted && !isHidden && !isNaN(parseFloat($input.val()))) {
                totalWeight += parseFloat($input.val());
            }
        });
    
        packhouseWeightResultField.val(totalWeight.toFixed(2)).trigger('change');
        console.log("[DEBUG] Total Packhouse Weight:", totalWeight.toFixed(2));  // 🐞
    };

    // ----- Lógica común para formularios -----
    const setupForm = (form) => {
        const $form = $(form);
        let tareValue = 0;  // Almacenará el container_tare del contenedor
        
        // Elementos del formulario
        const grossWeightField = $form.find('input[name$="-gross_weight"]');
        const totalBoxesField = $form.find('input[name$="-total_boxes"]');
        const harvestContainerField = $form.find('select[name$="-harvest_container"]');
        const containerTareField = $form.find('input[name$="-container_tare"]');
        const platformTareField = $form.find('input[name$="-platform_tare"]');
        const netWeightField = $form.find('input[name$="-net_weight"]');
        const deleteCheckbox = $form.find('input[name$="-DELETE"]');

        makeFieldReadonly(containerTareField);
        makeFieldReadonly(netWeightField);

        // Cargar valor inicial del contenedor
        const loadContainerTare = (containerId) => {
            if (containerId) {
                fetchContainerTare(containerId)
                    .then(tare => {
                        tareValue = tare || 0; // Si tare es undefined, usa 0
                        console.log("[DEBUG] Tare Value updated to:", tareValue);  // 🐞
                        updateContainerTare();  // Actualizar cálculos
                    });
            }
        };

        // Cargar valor inicial si existe
        loadContainerTare(harvestContainerField.val());

        // Manejar cambio de contenedor
        harvestContainerField.on('change', function() {
            const containerId = $(this).val();
            console.log("[DEBUG] Container changed to ID:", containerId);  // 🐞
            loadContainerTare(containerId);
        });

        // --- Funciones de actualización ---
        const updateContainerTare = () => {
            const totalBoxes = parseFloat(totalBoxesField.val()) || 0;
            console.log("[DEBUG] Calculating container tare:",  // 🐞
                `Total Boxes: ${totalBoxes} * Tare Value: ${tareValue}`
            );
            
            containerTareField.val((totalBoxes * tareValue).toFixed(2));
            console.log("[DEBUG] Container Tare result:", containerTareField.val());  // 🐞
            
            updateNetWeight();
        };

        const updateNetWeight = () => {
            const grossWeight = parseFloat(grossWeightField.val()) || 0;
            const platformTare = parseFloat(platformTareField.val()) || 0;
            const containerTare = parseFloat(containerTareField.val()) || 0;
            
            console.log("[DEBUG] Net Weight calculation:",  // 🐞
                `Gross: ${grossWeight} - Platform: ${platformTare} - Container: ${containerTare}`
            );
            
            netWeightField.val((grossWeight - platformTare - containerTare).toFixed(2));
            console.log("[DEBUG] Net Weight result:", netWeightField.val());  // 🐞
            
            updatePackhouseWeight();
        };

        // Eventos
        grossWeightField.add(platformTareField).off('input').on('input', updateNetWeight);
        totalBoxesField.off('input').on('input', updateContainerTare);
        deleteCheckbox.off('change').on('change', updatePackhouseWeight);

        updateNetWeight();
    };

    // formularios existentes
    document.querySelectorAll('div[id^="palletreceived_set-"]').forEach(setupForm);

    // formularios nuevos
    document.addEventListener('formset:added', (event) => {
        if (event.detail.formsetName === 'palletreceived_set') {
            console.log("[DEBUG] New form added:", event.target);  // 🐞
            setupForm(event.target);
        }
    });

    // eliminar formular
    document.addEventListener('formset:removed', () => {
        console.log("[DEBUG] Form removed. Updating total weight...");  // 🐞
        updatePackhouseWeight();
    });
});