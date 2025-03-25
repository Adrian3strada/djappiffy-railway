document.addEventListener('DOMContentLoaded', () => {
    const packhouseWeightResultField = $('#id_packhouse_weight_result');
    const palletReceivedField = $('#id_pallets_received');

    // ================ CONSTANTES ================
    const PALLET_FORM_SELECTOR = 'div[id^="palletreceived_set-"]:not([id*="group"], [id*="empty"])';
    const CONTAINER_FORM_SELECTOR = 'tbody[id*="-palletcontainer_set-"]:not([id*="empty"])';
    let debounceTimeout;

    // Función debounce genérica
    const debounce = (func, wait) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    };

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
            return response.kg_tare || 0;
        } catch (error) {
            return 0;
        }
    };

    // ================ ACTUALIZAR CONTEO DE PALLETS ================
    const updatePalletCount = () => {
        const palletCount = $(PALLET_FORM_SELECTOR).length;
        palletReceivedField.val(palletCount).trigger('change');
    };

    // ================ CÁLCULO DE TARA ================
    const calculatePalletTare = async ($palletForm) => {
        let totalTare = 0;
        let totalBoxes = 0;
        const containers = $palletForm.find(CONTAINER_FORM_SELECTOR);

        for (const container of containers) {
            const $container = $(container);
            
            if ($container.find('input[name$="-DELETE"]').prop('checked')) {
                continue;
            }

            const harvestContainerId = $container.find('select[name$="-harvest_container"]').val();
            const quantity = parseFloat($container.find('input[name$="-quantity"]').val()) || 0;
            if (harvestContainerId) {
                totalBoxes += quantity;
            }

            if (harvestContainerId && quantity > 0) {
                const tare = await fetchContainerTare(harvestContainerId);
                totalTare += quantity * tare;
            }
        }
        const truncatedTare = Math.floor(totalTare * 1000) / 1000;
        $palletForm.find('input[name$="-container_tare"]').val(truncatedTare);
        $palletForm.find('input[name$="-total_boxes"]').val(totalBoxes); 
        updateNetWeight($palletForm);
    };

    // ================ ACTUALIZAR PESO NETO ================
    const updateNetWeight = ($palletForm) => {
        const gross = parseFloat($palletForm.find('input[name$="-gross_weight"]').val()) || 0;
        const platform = parseFloat($palletForm.find('input[name$="-platform_tare"]').val()) || 0;
        const container = parseFloat($palletForm.find('input[name$="-container_tare"]').val()) || 0;
        
        const net = Math.floor((gross - platform - container) * 1000) / 1000;
        $palletForm.find('input[name$="-net_weight"]').val(net);
        debouncedUpdatePackhouse();
    };

    // ================ PESO TOTAL PACKHOUSE ================
    const updatePackhouseWeight = () => {
        let total = 0;

        $(PALLET_FORM_SELECTOR).each(function() {
            const $pallet = $(this);
            if ($pallet.find('input[name$="-DELETE"]').prop('checked')) return;
            
            const netWeight = parseFloat($pallet.find('input[name$="-net_weight"]').val()) || 0;
            total += netWeight;
        });

        const truncatedTotal = Math.floor(total * 1000) / 1000;
        packhouseWeightResultField.val(truncatedTotal).trigger('change');
    };

    const debouncedUpdatePackhouse = debounce(updatePackhouseWeight, 300);

    // ================ INICIALIZAR PALLETS ================
    const initializePallet = (palletForm) => {
        const $pallet = $(palletForm);
        
        // Debounce específico para este pallet
        const debouncedCalculateTare = debounce(() => calculatePalletTare($pallet), 300);

        // Eventos en tiempo real para campos principales
        $pallet.on('input', 'input[name$="-gross_weight"], input[name$="-platform_tare"]', () => {
            updateNetWeight($pallet);
        });

        // Eventos en tiempo real para contenedores
        $pallet.on('input', 'input[name$="-quantity"]', debouncedCalculateTare);
        $pallet.on('change', 'select[name$="-harvest_container"]', debouncedCalculateTare);

        // Inicialización
        calculatePalletTare($pallet);
        updatePalletCount();
    };

    // ================ INICIALIZACIÓN PRINCIPAL ================
    $(PALLET_FORM_SELECTOR).each((i, form) => initializePallet(form));

    // ================ MANEJO DE FORMSETS ================
    document.addEventListener('formset:added', (event) => {
        const formsetName = event.detail.formsetName;
        
        if (formsetName === 'palletreceived_set') {
            initializePallet(event.target);
        }
        else if (formsetName === 'palletcontainer_set') {
            const $pallet = $(event.target).closest(PALLET_FORM_SELECTOR);
            debounce(() => calculatePalletTare($pallet), 300)();
        }
        
        updatePalletCount();
    });

    document.addEventListener('formset:removed', () => {
        debouncedUpdatePackhouse();
        updatePalletCount();
    });
});