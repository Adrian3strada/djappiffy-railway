document.addEventListener('DOMContentLoaded', () => {
    const packhouseWeightResultField = $('#id_packhouse_weight_result');
    const palletReceivedField = $('#id_pallets_received');

    // ================ CONSTANTES ================
    const PALLET_FORM_SELECTOR = 'div[id^="palletreceived_set-"]:not([id*="group"], [id*="empty"])';
    const CONTAINER_FORM_SELECTOR = 'tbody[id*="-palletcontainer_set-"]:not([id*="empty"])';

    const debounce = (func, wait) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    };

    // ================ OBTENCIÓN DE TARA DEL CONTAINER ================
    const fetchContainerTare = async (containerId) => {
        if (!containerId) return 0;
        try {
            const response = await $.ajax({
                url: `/rest/v1/catalogs/supply/${containerId}/`,
                method: 'GET',
                timeout: 5000
            });
            return parseFloat(response.kg_tare) || 0;
        } catch (error) {
            console.error('Error:', error);
            return 0;
        }
    };

    // ================ OBTENCIÓN DE CUADRILLAS ================
    function fetchOptions(url) {
        return $.ajax({
          url: url, // La URL para obtener las opciones
          method: 'GET',
          dataType: 'json'
        }).fail(error => console.error('Error al obtener opciones:', error));
      }
    
    function updateFieldOptions(field, options, selectedValue) {
        field.empty(); // Limpiar las opciones existentes
        if (!field.prop('multiple')) {
            field.append(new Option('---------', '', true, false)); // Añadir opción por defecto
        }
        options.forEach(option => {
            field.append(new Option(option.name, option.id, false, option.id === selectedValue)); // Añadir cada opción
        });
        field.val(selectedValue); // Establecer el valor seleccionado
    }

    function handleProviderChange(providerField, harvestingCrewField, selectedHarvestingCrew = null) {
        const providerId = providerField.val(); 
        
        if (providerId) {
            fetchOptions(`/rest/v1/catalogs/harvesting-crew/?provider=${providerId}`)
            .then(harvestingCrews => {
                updateFieldOptions(harvestingCrewField, harvestingCrews, selectedHarvestingCrew); // Actualizar opciones
            })
            .catch(error => console.error('Error:', error));
        } else {
            // Si no se ha seleccionado un proveedor, limpiar las opciones del campo harvesting_crew
            updateFieldOptions(harvestingCrewField, [], null);
        }
    }

    // ================ ACTUALIZACIÓN DE CONTEO DE PALLETS ================
    const updatePalletCount = () => {
        // Solo contar pallets que no estén marcados para eliminación (usando el checkbox de pallet)
        const validPallets = $(PALLET_FORM_SELECTOR).filter((i, el) => {
            const $el = $(el);
            const $palletDelete = $el.find('input[name$="-DELETE"]').filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
            return !$palletDelete.prop('checked');
        }).length;
        palletReceivedField.val(validPallets).trigger('change');
    };

    // ================ CÁLCULO DE TARA DEL PALLET ================
    const calculatePalletTare = async ($palletForm) => {
        // Filtra el checkbox de eliminación del pallet (excluyendo los que pertenecen a un container)
        const $palletDeleteCheckbox = $palletForm
            .find('input[name$="-DELETE"]')
            .filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
        if ($palletDeleteCheckbox.prop('checked')) return;

        let totalTare = 0;
        let totalBoxes = 0;
        const containers = $palletForm.find(CONTAINER_FORM_SELECTOR);

        for (const container of containers) {
            const $container = $(container);
            const $deleteCheckbox = $container.find('input[name$="-DELETE"]');

            if ($deleteCheckbox.length && !$deleteCheckbox.data('observerAttached')) {
                const observer = new MutationObserver(mutations => {
                    mutations.forEach(mutation => {
                        if (mutation.attributeName === 'checked') {
                            console.log(`Cambio en container ${$container.attr('id')}: DELETE=${$deleteCheckbox.prop('checked')}`);
                            calculatePalletTare($palletForm);
                        }
                    });
                });
                observer.observe($deleteCheckbox[0], { attributes: true });
                $deleteCheckbox.data('observerAttached', true);
            }
            
            if ($deleteCheckbox.prop('checked')) continue;
            const harvestContainerId = $container.find('select[name$="-harvest_container"]').val();
            const quantity = parseFloat($container.find('input[name$="-quantity"]').val()) || 0;

            if (harvestContainerId) {
                const tare = await fetchContainerTare(harvestContainerId);
                totalTare += quantity * tare;
                totalBoxes += quantity;
            }
        }
        const truncatedTare = Math.trunc(totalTare * 1000) / 1000;
        $palletForm.find('input[name$="-container_tare"]').val(truncatedTare);
        $palletForm.find('input[name$="-total_boxes"]').val(totalBoxes);
        updateNetWeight($palletForm);
    };

    // ================ ACTUALIZACIÓN DE PESO NETO DEL PALLET ================
    const updateNetWeight = ($palletForm) => {
        const $palletDeleteCheckbox = $palletForm
            .find('input[name$="-DELETE"]')
            .filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
        if ($palletDeleteCheckbox.prop('checked')) return;

        const gross = parseFloat($palletForm.find('input[name$="-gross_weight"]').val()) || 0;
        const platform = parseFloat($palletForm.find('input[name$="-platform_tare"]').val()) || 0;
        const container = parseFloat($palletForm.find('input[name$="-container_tare"]').val()) || 0;
        
        const net = Math.trunc((gross - platform - container) * 1000) / 1000;
        $palletForm.find('input[name$="-net_weight"]').val(net);
        debouncedUpdatePackhouse();
    };

    // ================ ACTUALIZACIÓN TOTAL DEL PACKHOUSE ================
    const updatePackhouseWeight = () => {
        let total = 0;
        $(PALLET_FORM_SELECTOR).each(function() {
            const $pallet = $(this);
            const $palletDelete = $pallet.find('input[name$="-DELETE"]').filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
            if ($palletDelete.prop('checked')) return;
            const netWeight = parseFloat($pallet.find('input[name$="-net_weight"]').val()) || 0;
            total += netWeight;
        });
        const truncatedTotal = Math.trunc(total * 1000) / 1000;
        packhouseWeightResultField.val(truncatedTotal).trigger('change');
    };

    const debouncedUpdatePackhouse = debounce(updatePackhouseWeight, 300);

    // ================ INICIALIZACIÓN DE UN PALLET ================
    const initializePallet = (palletForm) => {
        const $pallet = $(palletForm);
        
        const providerField = $(palletForm).find('select[name$="-provider"]'); 
        const harvestingCrewField = $(palletForm).find('select[name$="-harvesting_crew"]');
        const selectedHarvestingCrew = harvestingCrewField.val();

        
        if (providerField.val()) {
            handleProviderChange(providerField, harvestingCrewField, selectedHarvestingCrew);
        } else {
            updateFieldOptions(harvestingCrewField, [], null);
        }

        // Manejar el cambio de proveedor en formularios existentes
        providerField.on('change', function() {
            handleProviderChange(providerField, harvestingCrewField, harvestingCrewField.val());
        });


        // --- Observer para detectar cambios en el checkbox DELETE del pallet ---
        const $palletDeleteCheckbox = $pallet
            .find('input[name$="-DELETE"]')
            .filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
        if ($palletDeleteCheckbox.length) {
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.attributeName === 'checked') {
                        console.log(`Pallet ${$pallet.attr('id')} - DELETE: ${$palletDeleteCheckbox.prop('checked')}`);
                        debouncedUpdatePackhouse();
                        updatePalletCount();
                    }
                });
            });
            observer.observe($palletDeleteCheckbox[0], { attributes: true });
        }
        
        if (!$pallet.data('childListObserverAttached')) {
            const childObserver = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.removedNodes && mutation.removedNodes.length) {
                        mutation.removedNodes.forEach(node => {
                            if ($(node).is(CONTAINER_FORM_SELECTOR)) {
                                console.log(`Container removido del pallet ${$pallet.attr('id')}`);
                                calculatePalletTare($pallet);
                            }
                        });
                    }
                });
            });
            childObserver.observe($pallet[0], { childList: true, subtree: true });
            $pallet.data('childListObserverAttached', true);
        }
        
        const debouncedCalculateTare = debounce(() => calculatePalletTare($pallet), 300);
        $pallet.off('input').on('input', 'input[name$="-gross_weight"], input[name$="-platform_tare"], input[name$="-quantity"]', debouncedCalculateTare);
        $pallet.off('change').on('change', 'select[name$="-harvest_container"]', debouncedCalculateTare);

        // Cálculo inicial al cargar el pallet
        calculatePalletTare($pallet);
        updatePalletCount();
    };

    // Inicializa todos los pallets existentes
    $(PALLET_FORM_SELECTOR).each((i, form) => initializePallet(form));

    // ================ MANEJO DE FORMSETS ================
    document.addEventListener('formset:added', (event) => {
        const formsetName = event.detail.formsetName;

        const providerField = $(formsetName).find('select[name$="-provider"]'); 
        const harvestingCrewField = $(formsetName).find('select[name$="-harvesting_crew"]');
        // Manejar el cambio de proveedor en el formulario agregado
        providerField.on('change', function() {
            handleProviderChange(providerField, harvestingCrewField);
        });

        // Actualizar las opciones del campo harvesting_crew cuando se agrega un nuevo formulario
        handleProviderChange(providerField, harvestingCrewField);
        if (formsetName === 'palletreceived_set') {
            initializePallet(event.target);
        } else if (formsetName === 'palletcontainer_set') {
            const $pallet = $(event.target).closest(PALLET_FORM_SELECTOR);
            debounce(() => calculatePalletTare($pallet), 300)();
        }
        updatePalletCount();
    });

    document.addEventListener('formset:removed', () => {
        debouncedUpdatePackhouse();
        updatePalletCount();
    });

    // ================ MANEJO DE BOTÓN ELIMINAR EN PALLETS  ================
    $(document).on('click', '.deletelink', function() {
        const $pallet = $(this).closest(PALLET_FORM_SELECTOR);
        setTimeout(() => {
            calculatePalletTare($pallet);
            updatePalletCount();
        }, 100);
    });

    // ================ MANEJO DE BOTÓN ELIMINAR EN CONTAINERS ================
    $(document).on('click', CONTAINER_FORM_SELECTOR + ' .deletelink', function() {
        const $pallet = $(this).closest(PALLET_FORM_SELECTOR);
        setTimeout(() => {
            calculatePalletTare($pallet);
        }, 100);
    });

    $(document).on('change', CONTAINER_FORM_SELECTOR + ' input[name$="-DELETE"]', function() {
        const $pallet = $(this).closest(PALLET_FORM_SELECTOR);
        calculatePalletTare($pallet);
    });
});
