document.addEventListener('DOMContentLoaded', () => {
    const packhouseWeightResultField = $('#id_packhouse_weight_result');

    // ================ CONSTANTES ================
    const PALLET_FORM_SELECTOR = 'div[id^="palletreceived_set-"][id$="-0"]:not([id*="group"])';
    const CONTAINER_FORM_SELECTOR = 'tbody[id*="-palletcontainer_set-"]:not([id*="empty"])';
    let debounceTimeout;

    const fetchContainerTare = async (containerId) => {
        if (!containerId) {
            return 0;
        }
        try {
            const response = await $.ajax({
                url: `/rest/v1/catalogs/supply/${containerId}/`,
                method: 'GET',
                dataType: 'json',
                timeout: 5000
            });   
            const tare = response.container_tare || response.kg_tare || 0;
            return tare;
        } catch (error) {
            return 0;
        }
    };

    // ================ CÁLCULO DE TARA ================
    const calculatePalletTare = async ($palletForm) => {
        const palletId = $palletForm.attr('id');
        
        let totalTare = 0;
        const containers = $palletForm.find(CONTAINER_FORM_SELECTOR);

        for (const container of containers) {
            const $container = $(container);
            const containerId = $container.attr('id');
            
            // Verificar si está marcado para eliminar
            if ($container.find('input[name$="-DELETE"]').prop('checked')) {
                continue;
            }

            // Obtener valores
            const harvestContainerId = $container.find('select[name$="-harvest_container"]').val();
            const quantity = parseFloat($container.find('input[name$="-quantity"]').val()) || 0;

            // Calcular contribución
            if (harvestContainerId && quantity > 0) {
                const tare = await fetchContainerTare(harvestContainerId);
                const contribution = quantity * tare;
                totalTare += contribution;
            }
        }

        // Actualizar padre
        $palletForm.find('input[name$="-container_tare"]').val(totalTare.toFixed(2));
        console.groupEnd();
        updateNetWeight($palletForm);
    };

    // ================ ACTUALIZAR PESO NETO ================
    const updateNetWeight = ($palletForm) => {
        const palletId = $palletForm.attr('id');

        const gross = parseFloat($palletForm.find('input[name$="-gross_weight"]').val()) || 0;
        const platform = parseFloat($palletForm.find('input[name$="-platform_tare"]').val()) || 0;
        const container = parseFloat($palletForm.find('input[name$="-container_tare"]').val()) || 0;
        const net = (gross - platform - container).toFixed(2);
        
        $palletForm.find('input[name$="-net_weight"]').val(net);
        
        console.groupEnd();
        debouncedUpdatePackhouse();
    };

    // ================ PESO TOTAL PACKHOUSE ================
    const updatePackhouseWeight = () => {
        let total = 0;

        $(PALLET_FORM_SELECTOR).each(function() {
            const $pallet = $(this);
            const palletId = $pallet.attr('id');

            if ($pallet.find('input[name$="-DELETE"]').prop('checked')) {
                console.log(`🚮 [${palletId}] Pallet eliminado - omitiendo`);
                return;
            }

            const netWeight = parseFloat($pallet.find('input[name$="-net_weight"]').val()) || 0;
            total += netWeight;
        });

       
        packhouseWeightResultField.val(total.toFixed(2)).trigger('change');
        console.groupEnd();
    };

    const debouncedUpdatePackhouse = () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(updatePackhouseWeight, 300);
    };

    // ================ INICIALIZAR PALLETS ================
    const initializePallet = (palletForm) => {
        const $pallet = $(palletForm);
        const palletId = $pallet.attr('id');

        // Eventos para campos del padre
        $pallet.on('input', 'input[name$="-gross_weight"], input[name$="-platform_tare"]', () => {
            updateNetWeight($pallet);
        });

        // Eventos para contenedores anidados
        $pallet.on('change', 'select[name$="-harvest_container"], input[name$="-quantity"]', (e) => {
            const $container = $(e.target).closest(CONTAINER_FORM_SELECTOR);
            calculatePalletTare($pallet);
        });

        // Cálculo inicial
        calculatePalletTare($pallet);
        console.groupEnd();
    };

    // ================ INICIALIZACIÓN PRINCIPAL ================
    $(PALLET_FORM_SELECTOR).each((i, form) => initializePallet(form));
    console.groupEnd();

    // ================ MANEJO DE FORMSETS ================
    document.addEventListener('formset:added', (event) => {
        const formsetName = event.detail.formsetName;
        const $form = $(event.target);

        if (formsetName === 'palletreceived_set') {
            initializePallet(event.target);
        }
        
        if (formsetName === 'palletcontainer_set') {
            const $pallet = $form.closest(PALLET_FORM_SELECTOR);
            calculatePalletTare($pallet);
        }

        console.groupEnd();
    });

    document.addEventListener('formset:removed', () => {
        debouncedUpdatePackhouse();
    });

});