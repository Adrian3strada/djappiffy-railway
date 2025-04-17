document.addEventListener("DOMContentLoaded", function () {
    function updateSelectOptions(selector) {
        const selects = document.querySelectorAll(selector);
        const selectedValues = new Set();

        // Recopilar valores seleccionados
        selects.forEach(select => {
            if (select.value) {
                selectedValues.add(select.value);
            }
        });

        // Guardar las opciones originales solo una vez
        selects.forEach(select => {
            if (!select.dataset.originalOptions) {
                const originalOptions = Array.from(select.options).map(option => {
                    return {
                        value: option.value,
                        text: option.text,
                    };
                });
                select.dataset.originalOptions = JSON.stringify(originalOptions);
            }
        });

        // Reconstruir opciones en cada select
        selects.forEach(select => {
            const originalOptions = JSON.parse(select.dataset.originalOptions);
            const currentValue = select.value;

            // Limpiar opciones actuales
            select.innerHTML = "";

            originalOptions.forEach(({ value, text }) => {
                // Mostrar si está vacía, no ha sido seleccionada o es la actual
                if (value === "" || !selectedValues.has(value) || value === currentValue) {
                    const option = document.createElement("option");
                    option.value = value;
                    option.textContent = text;
                    select.appendChild(option);
                }
            });

            // Restaurar valor
            select.value = currentValue;
        });
    }

    // Selectores para los dos tipos de selects
    const pestSelector = 'select[name*="samplepest_set"][name$="-product_pest"]';
    const diseaseSelector = 'select[name*="sampledisease_set"][name$="-product_disease"]';
    const physicalDamageSelector = 'select[name*="samplephysicaldamage_set"][name$="-product_physical_damage"]';
    const residueSelector = 'select[name*="sampleresidue_set"][name$="-product_residue"]';
 
    function updateAll() {
        updateSelectOptions(pestSelector);
        updateSelectOptions(diseaseSelector);
        updateSelectOptions(physicalDamageSelector);
        updateSelectOptions(residueSelector);
    }

    $(document).on('change', function () {
        updateAll();
    });


    $(document).on('formset:removed', function (event, $inline) {
        updateAll();
    });

    // Actualizamos al cargar la página
    updateAll();
});


