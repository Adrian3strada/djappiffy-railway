document.addEventListener("DOMContentLoaded", function () {
    const incomingProductForm = document.getElementById("incomingproduct-0");
    if (!incomingProductForm) return;

    // Campos que vamos a usar
    const packhouseWeightResultField = incomingProductForm.querySelector('input[name$="-packhouse_weight_result"]');
    const totalWeighedSetsField = incomingProductForm.querySelector('input[name$="-total_weighed_sets"]');
    const containersAssignedField = incomingProductForm.querySelector('input[name$="-containers_assigned"]');
    const fullContainersPerHarvestField = incomingProductForm.querySelector('input[name$="-full_containers_per_harvest"]');
    const emptyContainersField = incomingProductForm.querySelector('input[name$="-empty_containers"]');
    const missingContainersField = incomingProductForm.querySelector('input[name$="-missing_containers"]');
    const averagePerContainerField = incomingProductForm.querySelector('input[name$="-average_per_container"]');
    const totalWeighedSetContainmentsField = incomingProductForm.querySelector('input[name$="-total_weighed_set_containers"]');

    const missingFields = incomingProductForm.querySelectorAll(
        'input[type="number"]' +
        '[name^="incomingproduct-0-scheduleharvest-0-"]' +
        '[name$="-missing_containers"]'
    );

    // Deshabilitar campos calculados
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
    disableField(emptyContainersField);
    disableField(totalWeighedSetContainmentsField);
    missingFields.forEach(disableField);

    // Actualiza la suma de quantity de los contenedores pesados (weighingsetcontainer_set)
    function updateTotalWeighedSetContainments() {
        let total = 0;
        const quantityInputs = incomingProductForm.querySelectorAll(
            'input[name^="incomingproduct-0-weighingset_set-"]' +
            '[name*="-weighingsetcontainer_set-"]' +
            '[name$="-quantity"]'
        );

        quantityInputs.forEach(input => {
            const tr = input.closest('tr');
            const deleteCheckbox = tr?.querySelector(
                'input[type="checkbox"][name$="-DELETE"]'
            );
            const isMarkedForDeletion = deleteCheckbox?.checked;

            if (!isMarkedForDeletion) {
                total += parseInt(input.value || 0, 10);
            }
        });

        totalWeighedSetContainmentsField.value = total;
        updateAveragePerContainer();
    }

    // Calcula el promedio por contenedor
    function updateAveragePerContainer() {
        const total = parseFloat(totalWeighedSetContainmentsField?.value) || 0;
        const weight = parseFloat(packhouseWeightResultField?.value) || 0;
        const average = total > 0 ? Math.floor((weight / total) * 1000) / 1000 : 0;
        averagePerContainerField.value = average;
    }

    // Agrega listeners a los contenedores
    function attachListeners() {
        const inputs = incomingProductForm.querySelectorAll(
            'input[name^="incomingproduct-0-weighingset_set-"]' +
            '[name*="-weighingsetcontainer_set-"]' +
            '[name$="-quantity"], ' +
            'input[name^="incomingproduct-0-weighingset_set-"]' +
            '[name*="-weighingsetcontainer_set-"]' +
            '[name$="-DELETE"]'
        );

        inputs.forEach(input => {
            input.removeEventListener("input", updateTotalWeighedSetContainments);
            input.removeEventListener("change", updateTotalWeighedSetContainments);
            input.addEventListener("input", updateTotalWeighedSetContainments);
            input.addEventListener("change", updateTotalWeighedSetContainments);
        });
    }

    // 👁️ Observador para detectar nuevos contenedores
    const observer = new MutationObserver(() => {
        attachListeners();
        updateTotalWeighedSetContainments();
    });

    observer.observe(incomingProductForm, { childList: true, subtree: true });

    // Si cambia el resultado del peso (packhouse), recalcular promedio
    if (packhouseWeightResultField) {
        packhouseWeightResultField.addEventListener("input", updateAveragePerContainer);
        packhouseWeightResultField.addEventListener("change", updateAveragePerContainer);
    }

    attachListeners();
    updateTotalWeighedSetContainments();
});
