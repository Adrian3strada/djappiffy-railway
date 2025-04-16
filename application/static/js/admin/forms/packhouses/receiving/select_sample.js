document.addEventListener("DOMContentLoaded", function () {
    function updateSelectOptions(selector) {
        let selects = document.querySelectorAll(selector);
        let selectedValues = new Set();

        // Recopilar valores seleccionados
        selects.forEach(select => {
            if (select.value) {
                selectedValues.add(select.value);
            }
        });

        // Actualizar las opciones de los selects
        selects.forEach(select => {
            let currentValue = select.value;
            let options = Array.from(select.options);

            let selectedOption = options.find(option => option.value === currentValue);

            // Limpiar el select
            select.innerHTML = "";

            // Agregar solo las opciones permitidas
            options.forEach(option => {
                if (!selectedValues.has(option.value) || option === selectedOption || option.value === "") {
                    select.appendChild(option);
                }
            });

            // Refrescar Select2 para que se actualice visualmente
            if ($(select).data('select2')) {
                $(select).trigger('change.select2');
            }
        });
    }

    const pestSelector = 'select[name$="-product_pest"]';
    const diseaseSelector = 'select[name$="-product_disease"]';
    const physicalDamageSelector = 'select[name$="-product_physical_damage"]';
    const residueSelector = 'select[name$="-product_residue"]';

    updateSelectOptions(pestSelector);
    updateSelectOptions(diseaseSelector);
    updateSelectOptions(physicalDamageSelector);
    updateSelectOptions(residueSelector);

    // Detectar cambios manuales
    document.addEventListener("change", function (event) {
        if (event.target.matches(pestSelector)) {
            updateSelectOptions(pestSelector);
        } else if (event.target.matches(diseaseSelector)) {
            updateSelectOptions(diseaseSelector);
        } else if (event.target.matches(physicalDamageSelector)) {
            updateSelectOptions(physicalDamageSelector);
        } else if (event.target.matches(residueSelector)) {
            updateSelectOptions(residueSelector);
        }
    });

    // Detectar cuando nested_admin agrega una fila
    document.addEventListener("formset:added", function (event) {
        setTimeout(() => {
            updateSelectOptions(pestSelector);
            updateSelectOptions(diseaseSelector);
            updateSelectOptions(physicalDamageSelector);
            updateSelectOptions(residueSelector);
        }, 100);
    });
});

