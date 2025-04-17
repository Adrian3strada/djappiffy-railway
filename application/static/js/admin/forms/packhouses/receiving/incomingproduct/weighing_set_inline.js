document.addEventListener('DOMContentLoaded', () => {
    const packhouseWeightResultField = $('#id_packhouse_weight_result');
    const weighedSetField = $('#id_total_weighed_sets');
    const weighedSetContainerField = $('#id_total_weighed_set_containers')

    // ================ CONSTANTES ================
    const WEIGHING_SET_FORM_SELECTOR = 'div[id^="weighingset_set-"]:not([id*="group"], [id*="empty"])';
    const CONTAINER_FORM_SELECTOR = 'tbody[id*="-weighingsetcontainer_set-"]:not([id*="empty"])';

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

    // ================ ACTUALIZACIÓN DE CONTEO DE WEIGHING SETS ================
    const updateWeighedSetCount = () => {
        // Solo contar weighing sets que no estén marcados para eliminación (usando el checkbox de weighing set)
        const validWeighedSets = $(WEIGHING_SET_FORM_SELECTOR).filter((i, el) => {
            const $el = $(el);
            const $weighingSetDelete = $el.find('input[name$="-DELETE"]').filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
            return !$weighingSetDelete.prop('checked');
        }).length;
        weighedSetField.val(validWeighedSets).trigger('change');
    };

    // ================ CÁLCULO DE TARA DEL WEIGHING SET ================
    const calculateWeighingSetTare = async ($weighingSetForm) => {
        // Filtra el checkbox de eliminación del weighing set (excluyendo los que pertenecen a un container)
        const $weighingSetDeleteCheckbox = $weighingSetForm
            .find('input[name$="-DELETE"]')
            .filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
        if ($weighingSetDeleteCheckbox.prop('checked')) return;

        let totalTare = 0;
        let totalContainers = 0;
        const containers = $weighingSetForm.find(CONTAINER_FORM_SELECTOR);
        debouncedUpdateTotalContainers();

        for (const container of containers) {
            const $container = $(container);
            const $deleteCheckbox = $container.find('input[name$="-DELETE"]');

            if ($deleteCheckbox.length && !$deleteCheckbox.data('observerAttached')) {
                const observer = new MutationObserver(mutations => {
                    mutations.forEach(mutation => {
                        if (mutation.attributeName === 'checked') {
                            calculateWeighingSetTare($weighingSetForm);
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
        $weighingSetForm.find('input[name$="-container_tare"]').val(truncatedTare);
        $weighingSetForm.find('input[name$="-total_containers"]').val(totalContainers);
        updateNetWeight($weighingSetForm);
    };

    // ================ ACTUALIZACIÓN DE PESO NETO DEL WEIGHING SET ================
    const updateNetWeight = ($weighingSetForm) => {
        const $weighingSetDeleteCheckbox = $weighingSetForm
            .find('input[name$="-DELETE"]')
            .filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
        if ($weighingSetDeleteCheckbox.prop('checked')) return;

        const gross = parseFloat($weighingSetForm.find('input[name$="-gross_weight"]').val()) || 0;
        const platform = parseFloat($weighingSetForm.find('input[name$="-platform_tare"]').val()) || 0;
        const container = parseFloat($weighingSetForm.find('input[name$="-container_tare"]').val()) || 0;
        
        const net = Math.trunc((gross - platform - container) * 1000) / 1000;
        $weighingSetForm.find('input[name$="-net_weight"]').val(net);
        debouncedUpdatePackhouse();
    };
    
    // ================ ACTUALIZACIÓN TOTAL DEL PACKHOUSE ================
    const updatePackhouseWeight = () => {
        let total = 0;
        $(WEIGHING_SET_FORM_SELECTOR).each(function() {
            const $weighingSet = $(this);
            const $weighingSetDelete = $weighingSet.find('input[name$="-DELETE"]').filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
            if ($weighingSetDelete.prop('checked')) return;
            const netWeight = parseFloat($weighingSet.find('input[name$="-net_weight"]').val()) || 0;
            total += netWeight;
        });
        const truncatedTotal = Math.trunc(total * 1000) / 1000;
        packhouseWeightResultField.val(truncatedTotal).trigger('change');
    };

    const debouncedUpdatePackhouse = debounce(updatePackhouseWeight, 300);


    // ================ ACTUALIZAR CONTENEDORES COMPLETOS ================
    const updateTotalFullContainers = () => {
        let total = 0;
        
        $(WEIGHING_SET_FORM_SELECTOR).each(function() {
            const $weighingSet = $(this);
            const $weighingSetDelete = $weighingSet.find('input[name$="-DELETE"]').filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
            
            // Si el weighing set está marcado para eliminar, saltar
            if ($weighingSetDelete.prop('checked')) return;

            // Sumar contenedores de TODOS los containers no eliminados en este weighing set
            $weighingSet.find(CONTAINER_FORM_SELECTOR).each(function() {
                const $container = $(this);
                const $deleteCheckbox = $container.find('input[name$="-DELETE"]');
                
                if (!$deleteCheckbox.prop('checked')) {
                    const quantity = parseFloat($container.find('input[name$="-quantity"]').val()) || 0;
                    total += quantity;
                }
            });
        });
        
        weighedSetContainerField.val(total);
    };

    const debouncedUpdateTotalContainers = debounce(updateTotalFullContainers, 300);


    // ================ INICIALIZACIÓN DE UN WEIGHING SET ================
    const initializeWeighingSet = (weighingSetForm) => {
        const $weighingSet = $(weighingSetForm);
        
        const providerField = $(weighingSetForm).find('select[name$="-provider"]'); 
        const harvestingCrewField = $(weighingSetForm).find('select[name$="-harvesting_crew"]');
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


        // --- Observer para detectar cambios en el checkbox DELETE del weighing set ---
        const $weighingSetDeleteCheckbox = $weighingSet
            .find('input[name$="-DELETE"]')
            .filter(function() {
                return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
            });
        if ($weighingSetDeleteCheckbox.length) {
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.attributeName === 'checked') {
                        debouncedUpdatePackhouse();
                        updateWeighedSetCount();
                    }
                });
            });
            observer.observe($weighingSetDeleteCheckbox[0], { attributes: true });
        }
        
        if (!$weighingSet.data('childListObserverAttached')) {
            const childObserver = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.removedNodes && mutation.removedNodes.length) {
                        mutation.removedNodes.forEach(node => {
                            if ($(node).is(CONTAINER_FORM_SELECTOR)) {
                                calculateWeighingSetTare($weighingSet);
                            }
                        });
                    }
                });
            });
            childObserver.observe($weighingSet[0], { childList: true, subtree: true });
            $weighingSet.data('childListObserverAttached', true);
        }
        
        const debouncedCalculateTare = debounce(() => calculateWeighingSetTare($weighingSet), 300);
        $weighingSet.off('input').on('input', 'input[name$="-gross_weight"], input[name$="-platform_tare"], input[name$="-quantity"]', debouncedCalculateTare);
        $weighingSet.off('change').on('change', 'select[name$="-harvest_container"]', debouncedCalculateTare);

        // Cálculo inicial al cargar el weighing set
        calculateWeighingSetTare($weighingSet);
        updateWeighedSetCount();
    };

    // Inicializa todos los weighing set existentes
    $(WEIGHING_SET_FORM_SELECTOR).each((i, form) => initializeWeighingSet(form));

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
        if (formsetName === 'weighingset_set') {
            initializeWeighingSet(event.target);
        } else if (formsetName === 'weighingsetcontainer_set') {
            const $weighingSet = $(event.target).closest(WEIGHING_SET_FORM_SELECTOR);
            debounce(() => calculateWeighingSetTare($weighingSet), 300)();
        }
        updateWeighedSetCount();
        debouncedUpdateTotalContainers();
    });

    document.addEventListener('formset:removed', () => {
        debouncedUpdatePackhouse();
        updateWeighedSetCount();
        debouncedUpdateTotalContainers();
    });

    // ================ MANEJO DE BOTÓN ELIMINAR EN WEIGHING SET  ================
    $(document).on('click', '.deletelink', function() {
        const $weighingSet = $(this).closest(WEIGHING_SET_FORM_SELECTOR);
        setTimeout(() => {
            calculateWeighingSetTare($weighingSet);
            updateWeighedSetCount();
        }, 100);
    });

    // ================ MANEJO DE BOTÓN ELIMINAR EN CONTAINERS ================
    $(document).on('click', CONTAINER_FORM_SELECTOR + ' .deletelink', function() {
        const $weighingSet = $(this).closest(WEIGHING_SET_FORM_SELECTOR);
        setTimeout(() => {
            calculateWeighingSetTare($weighingSet);
        }, 100);
    });

    $(document).on('change', CONTAINER_FORM_SELECTOR + ' input[name$="-DELETE"]', function() {
        const $weighingSet = $(this).closest(WEIGHING_SET_FORM_SELECTOR);
        calculateWeighingSetTare($weighingSet);
    });
});
