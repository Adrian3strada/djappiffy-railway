document.addEventListener('DOMContentLoaded', function () {

    function recalculatePercentage() {
        const sampleFields = document.querySelectorAll('input[name$="sample_residue"]');
        const percentageFields = Array.from(document.querySelectorAll('input[name*="samplecollection_set-0-sampleresidue_set-"]'))
        .filter(input => {
            return input.name.endsWith('-percentage') && /^samplecollection_set-\d+-sampleresidue_set-\d+-percentage$/.test(input.name);
        });
        // const percentageFields = Array.from(document.querySelectorAll('[id^="samplecollection_set-0-sampleresidue_set-"] .field-percentage p'));
        // console.log(percentageFields);

        const weightInputs = Array.from(document.querySelectorAll('input[name*="samplecollection_set-0-sampleweight_set-"]'))
            .filter(input => {
                return input.name.endsWith('-weight') && /^samplecollection_set-\d+-sampleweight_set-\d+-weight$/.test(input.name);
            });

        sampleFields.forEach((field, index) => {
            const sample = parseFloat(field.value); // Obtener el valor del campo
            if (!isNaN(sample && weightInputs.length > 0)) {
                // Calcular el porcentaje
                const percentage = sample / weightInputs.length;
                
                // Asignar el porcentaje al campo correspondiente de percentageFields
                if (percentageFields[index]) {
                    percentageFields[index].value = percentage.toFixed(2); // Asignar el valor al campo correspondiente
                    // percentageFields[index].textContent = percentage.toFixed(2); // Asignar el valor al campo correspondiente
                }
            }
        });
    }

    // Recalcular cuando se edita un campo sample_residue
    document.addEventListener('input', function (event) {
        if (event.target.matches('input[name$="sample_residue"]') || event.target.matches('input[name$="-weight"]')) {
            recalculatePercentage();
        }
    });

    // Observer para detectar cambios en el DOM (por si se agregan o eliminan inputs dinámicamente)
    const observer = new MutationObserver(mutations => {
        let shouldRecalculate = false;

        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    // Buscar cualquier input con nombre que termine en -weight dentro del nodo agregado
                    const weightInput = node.matches('input[name$="-weight"]') ?
                        node :
                        node.querySelector('input[name$="-weight"]');

                    if (weightInput) {
                        shouldRecalculate = true;
                    }
                }
            });

            mutation.removedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    const weightInput = node.matches('input[name$="-weight"]') ?
                        node :
                        node.querySelector('input[name$="-weight"]');

                    if (weightInput) {
                        shouldRecalculate = true;
                    }
                }
            });
        });

        if (shouldRecalculate) {
            recalculatePercentage();
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Llamar a la función inicial para establecer los porcentajes
    recalculatePercentage();
});