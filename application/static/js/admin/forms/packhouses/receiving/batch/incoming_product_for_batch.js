document.addEventListener("DOMContentLoaded", function() {
    // Selecciona el contenedor del inline padre por su id
    const incomingProductForm = document.getElementById("incomingproduct_set-0");
    // Oculta las columnas de ID original
    document.querySelectorAll("td.original").forEach(row => {
        row.style.display = "none"; 
    });
    document.querySelectorAll("th.original").forEach(row => {
        row.style.display = "none";  
    });

    // Inlines anidados que debemos excluir
    const excludeSelectors = [
        '[id^="incomingproduct_set-0-weighingset_set"]',
        '[id^="incomingproduct_set-0-scheduleharvest-0-scheduleharvestharvestingcrew_set"]',
        '[id^="incomingproduct_set-0-scheduleharvest-0-scheduleharvestvehicle_set-0-scheduleharvestcontainervehicle_set"]'
    ];

    // Ocultar DELETE y labels solo si no están dentro de los inlines anidados
    incomingProductForm.querySelectorAll(`input[name$="-DELETE"]`).forEach(input => {
        let shouldExclude = false;
        excludeSelectors.forEach(selector => {
            if (input.closest(selector)) {
                shouldExclude = true;
            }
        });
        if (!shouldExclude) {
            // Oculta el checkbox
            input.style.display = "none";
            // Oculta su label asociada
            const label = incomingProductForm.querySelector(`label[for="${input.id}"]`);
            if (label) {
                label.style.display = "none";
            }
        }
    });

    const statusField = incomingProductForm.querySelector('select[name$="-status"]');
    const packhouseWeightResultField = incomingProductForm.querySelector('input[name$="-packhouse_weight_result"]');
    const totalWeighedSetsField = incomingProductForm.querySelector('input[name$="-total_weighed_sets"]');
    const containersAssignedField = incomingProductForm.querySelector('input[name$="-containers_assigned"]');
    const fullContainersPerHarvestField = incomingProductForm.querySelector('input[name$="-full_containers_per_harvest"]');
    const emptyContainersField = incomingProductForm.querySelector('input[name$="-empty_containers"]');
    const missingContainersField = incomingProductForm.querySelector('input[name$="-missing_containers"]');
    const averagePerContainerField = incomingProductForm.querySelector('input[name$="-average_per_container"]');
    const currentKgAvailableField = incomingProductForm.querySelector('input[name$="-current_kg_available"]');
    const totalWeighedSetContainmentsField = incomingProductForm.querySelector('input[name$="-total_weighed_set_containers"]');
    const missingFields = incomingProductForm.querySelectorAll(
        'input[type="number"]' +
        '[name^="incomingproduct_set-0-scheduleharvest-0-"]' +
        '[name$="-missing_containers"]'
      );

    // deshabilitar edición en campos, pero permitir que los valores se envíen
    function disableField(field) {
        if (!field) return;
            field.readOnly = true;
            field.style.pointerEvents = "none";
            field.style.backgroundColor = "#e9ecef";
            field.style.border = "none";
            field.style.color = "#555";
    }

    disableField(totalWeighedSetsField);
    disableField(packhouseWeightResultField);
    disableField(containersAssignedField);
    disableField(missingContainersField);
    disableField(fullContainersPerHarvestField);
    disableField(averagePerContainerField);
    disableField(currentKgAvailableField);
    disableField(emptyContainersField);
    disableField(totalWeighedSetContainmentsField)
    missingFields.forEach(disableField);

    const VEHICLE_INLINE_SELECTOR = 'div.djn-item[data-inline-model="gathering-scheduleharvestvehicle"]';

    // Devuelve todos los formularios de vehículo (excluyendo el “empty form”)
    function getAllVehicles() {
        return Array.from(incomingProductForm.querySelectorAll(VEHICLE_INLINE_SELECTOR))
            .filter(el => el.getAttribute('data-is-initial') === 'true');
    }

    // Vehiculos y Contenedores
    function countValidVehicles() {
        const vehicles = getAllVehicles();
        let valid = 0;
        vehicles.forEach(vehicle => {
            const hasArrived = vehicle.querySelector("input[name$='-has_arrived']");
            const del = vehicle.querySelector("input[name$='-DELETE']");
            if (hasArrived && hasArrived.checked && (!del || !del.checked)) {
                valid++;
            }
        });
        return valid;
    }

    function calculateContainerTotalsPerVehicle() {
        const vehicles = getAllVehicles();
        vehicles.forEach((vehicle, idx) => {
            const hasArrived = vehicle.querySelector("input[name$='-has_arrived']");
            const del = vehicle.querySelector("input[name$='-DELETE']");
            if (hasArrived && hasArrived.checked && (!del || !del.checked)) {
                const containerGroup = vehicle.querySelector('div.inline-group.djn-group[data-inline-formset*="containervehicle_set"]');
                if (containerGroup) {
                    // Usamos los formularios individuales (suponiendo elementos como tbody.djn-item)
                    const containerForms = Array.from(containerGroup.querySelectorAll("tbody.djn-item"));
                    let totalQuantity = 0,
                        totalFull = 0,
                        totalEmpty = 0,
                        totalMissing = 0;
                    containerForms.forEach(container => {
                        const quantityInput = container.querySelector("input[name$='quantity']");
                        const fullInput = container.querySelector("input[name$='full_containers']");
                        const emptyInput = container.querySelector("input[name$='empty_containers']");
                        const missingInput = container.querySelector("input[name$='missing_containers']");
                        const quantity = parseFloat(quantityInput ? quantityInput.value : 0) || 0;
                        const full = parseFloat(fullInput ? fullInput.value : 0) || 0;
                        const empty = parseFloat(emptyInput ? emptyInput.value : 0) || 0;
                        const missing = parseFloat(missingInput ? missingInput.value : 0) || 0;
                        totalQuantity += quantity;
                        totalFull += full;
                        totalEmpty += empty;
                        totalMissing += missing;
                    });
                } 
            }
        });
    }

    // Función para sumar globalmente los totales de todos los vehículos válidos.
    function calculateGlobalTotals() {
        const vehicles = getAllVehicles();
        let globalQuantity = 0,
            globalFull = 0,
            globalEmpty = 0,
            globalMissing = 0;
        vehicles.forEach(vehicle => {
            const hasArrived = vehicle.querySelector("input[name$='-has_arrived']");
            const del = vehicle.querySelector("input[name$='-DELETE']");
            if (hasArrived && hasArrived.checked && (!del || !del.checked)) {
                const containerGroup = vehicle.querySelector('div.inline-group.djn-group[data-inline-formset*="containervehicle_set"]');
                if (containerGroup) {
                    const containerForms = Array.from(containerGroup.querySelectorAll("tbody.djn-item"));
                    containerForms.forEach(container => {
                        const quantityInput = container.querySelector("input[name$='quantity']");
                        const fullInput = container.querySelector("input[name$='full_containers']");
                        const emptyInput = container.querySelector("input[name$='empty_containers']");
                        const missingInput = container.querySelector("input[name$='missing_containers']");
                        globalQuantity += parseFloat(quantityInput ? quantityInput.value : 0) || 0;
                        globalFull += parseFloat(fullInput ? fullInput.value : 0) || 0;
                        globalEmpty += parseFloat(emptyInput ? emptyInput.value : 0) || 0;
                        globalMissing += parseFloat(missingInput ? missingInput.value : 0) || 0;
                    });
                }
            }
        });
        containersAssignedField.value = globalQuantity;
        fullContainersPerHarvestField.value = globalFull;
        emptyContainersField.value = globalEmpty;
        missingContainersField.value = globalMissing;
    }
    
    countValidVehicles();
    calculateContainerTotalsPerVehicle();
    calculateGlobalTotals();

    function updateTotals(e) {
        if (e.target.matches("input[name$='-has_arrived'], input[name$='-DELETE'], input[type='number']")) {
            countValidVehicles();
            calculateContainerTotalsPerVehicle();
            calculateGlobalTotals();
        }
    }
    incomingProductForm.addEventListener("change", updateTotals);
    incomingProductForm.addEventListener("input", updateTotals);
    
});
