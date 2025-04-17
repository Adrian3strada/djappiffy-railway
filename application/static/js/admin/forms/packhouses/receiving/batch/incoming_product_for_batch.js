document.addEventListener("DOMContentLoaded", function() {
    // Selecciona el contenedor del inline padre por su id
    const incomingProductForm = document.getElementById("incomingproduct_set-0");
    if (!incomingProductForm) {
        console.warn("No se encontró el elemento con id 'incomingproduct_set-0'");
        return;
    }

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

});
