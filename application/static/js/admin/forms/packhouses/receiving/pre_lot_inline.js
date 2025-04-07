document.addEventListener('DOMContentLoaded', () => {
    const packhouseWeightResultField = $('#id_packhouse_weight_result');
    const preLotField = $('#id_pre_lot_quantity');
    const preLotFullContainerField = $('#id_pre_lot_full_containers')

    // ================ CONSTANTES ================
    const PRE_LOT_FORM_SELECTOR = 'div[id^="prelot_set-"]:not([id*="group"], [id*="empty"])';
    const CONTAINER_FORM_SELECTOR = 'tbody[id*="-prelotcontainer_set-"]:not([id*="empty"])';

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

    // ================ ACTUALIZACIÓN DE CONTEO DE PRE-LOTES ================
    const updatePreLotCount = () => {
        // Solo contar pre-lotes que no estén marcados para eliminación (usando el checkbox de pre-lote)
        const validPreLots = $(PRE_LOT_FORM_SELECTOR).filter((i, el) => {
            const $el = $(el);
            const $preLotDelete = $el.find('input[name$="-DELETE"]').filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
            return !$preLotDelete.prop('checked');
        }).length;
        preLotField.val(validPreLots).trigger('change');
    };

    // ================ CÁLCULO DE TARA DEL PRE-LOTE ================
    const calculatePreLotTare = async ($preLotForm) => {
        // Filtra el checkbox de eliminación del pre-lote (excluyendo los que pertenecen a un container)
        const $preLotDeleteCheckbox = $preLotForm
            .find('input[name$="-DELETE"]')
            .filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
        if ($preLotDeleteCheckbox.prop('checked')) return;

        let totalTare = 0;
        let totalContainers = 0;
        const containers = $preLotForm.find(CONTAINER_FORM_SELECTOR);
        debouncedUpdateTotalContainers();

        for (const container of containers) {
            const $container = $(container);
            const $deleteCheckbox = $container.find('input[name$="-DELETE"]');

            if ($deleteCheckbox.length && !$deleteCheckbox.data('observerAttached')) {
                const observer = new MutationObserver(mutations => {
                    mutations.forEach(mutation => {
                        if (mutation.attributeName === 'checked') {
                            calculatePreLotTare($preLotForm);
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
                totalContainers += quantity;
                
            }
        }
        const truncatedTare = Math.trunc(totalTare * 1000) / 1000;
        $preLotForm.find('input[name$="-container_tare"]').val(truncatedTare);
        $preLotForm.find('input[name$="-total_containers"]').val(totalContainers);
        updateNetWeight($preLotForm);
    };

    // ================ ACTUALIZACIÓN DE PESO NETO DEL PRE-LOTE ================
    const updateNetWeight = ($preLotForm) => {
        const $preLotDeleteCheckbox = $preLotForm
            .find('input[name$="-DELETE"]')
            .filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
        if ($preLotDeleteCheckbox.prop('checked')) return;

        const gross = parseFloat($preLotForm.find('input[name$="-gross_weight"]').val()) || 0;
        const platform = parseFloat($preLotForm.find('input[name$="-platform_tare"]').val()) || 0;
        const container = parseFloat($preLotForm.find('input[name$="-container_tare"]').val()) || 0;
        
        const net = Math.trunc((gross - platform - container) * 1000) / 1000;
        $preLotForm.find('input[name$="-net_weight"]').val(net);
        debouncedUpdatePackhouse();
    };
    
    // ================ ACTUALIZACIÓN TOTAL DEL PACKHOUSE ================
    const updatePackhouseWeight = () => {
        let total = 0;
        $(PRE_LOT_FORM_SELECTOR).each(function() {
            const $preLot = $(this);
            const $preLotDelete = $preLot.find('input[name$="-DELETE"]').filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
            if ($preLotDelete.prop('checked')) return;
            const netWeight = parseFloat($preLot.find('input[name$="-net_weight"]').val()) || 0;
            total += netWeight;
        });
        const truncatedTotal = Math.trunc(total * 1000) / 1000;
        packhouseWeightResultField.val(truncatedTotal).trigger('change');
    };

    const debouncedUpdatePackhouse = debounce(updatePackhouseWeight, 300);


    // ================ ACTUALIZAR CONTENEDORES COMPLETOS ================
    const updateTotalFullContainers = () => {
        let total = 0;
        
        $(PRE_LOT_FORM_SELECTOR).each(function() {
            const $preLot = $(this);
            const $preLotDelete = $preLot.find('input[name$="-DELETE"]').filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
            
            // Si el pre-lote está marcado para eliminar, saltar
            if ($preLotDelete.prop('checked')) return;

            // Sumar contenedores de TODOS los containers no eliminados en este pre-lote
            $preLot.find(CONTAINER_FORM_SELECTOR).each(function() {
                const $container = $(this);
                const $deleteCheckbox = $container.find('input[name$="-DELETE"]');
                
                if (!$deleteCheckbox.prop('checked')) {
                    const quantity = parseFloat($container.find('input[name$="-quantity"]').val()) || 0;
                    total += quantity;
                }
            });
        });
        
        preLotFullContainerField.val(total);
    };

    const debouncedUpdateTotalContainers = debounce(updateTotalFullContainers, 300);


    // ================ INICIALIZACIÓN DE UN PRE-LOTE ================
    const initializePreLot = (preLoteForm) => {
        const $preLot = $(preLoteForm);
        
        const providerField = $(preLoteForm).find('select[name$="-provider"]'); 
        const harvestingCrewField = $(preLoteForm).find('select[name$="-harvesting_crew"]');
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


        // --- Observer para detectar cambios en el checkbox DELETE del pre-lote ---
        const $preLotDeleteCheckbox = $preLot
            .find('input[name$="-DELETE"]')
            .filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
        if ($preLotDeleteCheckbox.length) {
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.attributeName === 'checked') {
                        debouncedUpdatePackhouse();
                        updatePreLotCount();
                    }
                });
            });
            observer.observe($preLotDeleteCheckbox[0], { attributes: true });
        }
        
        if (!$preLot.data('childListObserverAttached')) {
            const childObserver = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.removedNodes && mutation.removedNodes.length) {
                        mutation.removedNodes.forEach(node => {
                            if ($(node).is(CONTAINER_FORM_SELECTOR)) {
                                calculatePreLotTare($preLot);
                            }
                        });
                    }
                });
            });
            childObserver.observe($preLot[0], { childList: true, subtree: true });
            $preLot.data('childListObserverAttached', true);
        }
        
        const debouncedCalculateTare = debounce(() => calculatePreLotTare($preLot), 300);
        $preLot.off('input').on('input', 'input[name$="-gross_weight"], input[name$="-platform_tare"], input[name$="-quantity"]', debouncedCalculateTare);
        $preLot.off('change').on('change', 'select[name$="-harvest_container"]', debouncedCalculateTare);

        // Cálculo inicial al cargar el pre-lote
        calculatePreLotTare($preLot);
        updatePreLotCount();
    };

    // Inicializa todos los pre-lote existentes
    $(PRE_LOT_FORM_SELECTOR).each((i, form) => initializePreLot(form));

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
        if (formsetName === 'prelot_set') {
            initializePreLot(event.target);
        } else if (formsetName === 'prelotcontainer_set') {
            const $preLot = $(event.target).closest(PRE_LOT_FORM_SELECTOR);
            debounce(() => calculatePreLotTare($preLot), 300)();
        }
        updatePreLotCount();
        debouncedUpdateTotalContainers();
    });

    document.addEventListener('formset:removed', () => {
        debouncedUpdatePackhouse();
        updatePreLotCount();
        debouncedUpdateTotalContainers();
    });

    // ================ MANEJO DE BOTÓN ELIMINAR EN PRE-LOTE  ================
    $(document).on('click', '.deletelink', function() {
        const $preLot = $(this).closest(PRE_LOT_FORM_SELECTOR);
        setTimeout(() => {
            calculatePreLotTare($preLot);
            updatePreLotCount();
        }, 100);
    });

    // ================ MANEJO DE BOTÓN ELIMINAR EN CONTAINERS ================
    $(document).on('click', CONTAINER_FORM_SELECTOR + ' .deletelink', function() {
        const $preLot = $(this).closest(PRE_LOT_FORM_SELECTOR);
        setTimeout(() => {
            calculatePreLotTare($preLot);
        }, 100);
    });

    $(document).on('change', CONTAINER_FORM_SELECTOR + ' input[name$="-DELETE"]', function() {
        const $preLot = $(this).closest(PRE_LOT_FORM_SELECTOR);
        calculatePreLotTare($preLot);
    });
});
