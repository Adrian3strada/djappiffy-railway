document.addEventListener("DOMContentLoaded", function () {
    function updateSelectOptions(selector) {
        const selects = Array.from(document.querySelectorAll(selector));
        const selectedValues = new Set(
            selects.map(select => select.value).filter(Boolean)
        );

        selects.forEach(select => {
            if (!select.dataset.originalOptions) {
                const options = Array.from(select.options).map(({ value, text }) => ({ value, text }));
                select.dataset.originalOptions = JSON.stringify(options);
            }
        });

        selects.forEach(select => {
            const originalOptions = JSON.parse(select.dataset.originalOptions);
            const currentValue = select.value;

            // Limpiar y reconstruir
            select.innerHTML = originalOptions
                .filter(({ value }) => value === "" || !selectedValues.has(value) || value === currentValue)
                .map(({ value, text }) => `<option value="${value}">${text}</option>`)
                .join("");

            select.value = currentValue;
        });
    }

    // Selectores para los dos tipos de selects
    const pestSelector = '.inline-group [name^="pestproductkind_set-"][name$="-pest"]';
    const diseaseSelector = '.inline-group [name^="diseaseproductkind_set-"][name$="-disease"]';
    
    updateSelectOptions(pestSelector);
    updateSelectOptions(diseaseSelector);

    $(document).on('change', pestSelector + ', ' + diseaseSelector, function () {
        if ($(this).is(pestSelector)) {
            updateSelectOptions(pestSelector);
        } else if ($(this).is(diseaseSelector)) {
            updateSelectOptions(diseaseSelector);
        }
    });

    document.addEventListener('formset:removed', (event) => {
        if (event.detail.formsetName === 'pestproductkind_set') {
            updateSelectOptions(pestSelector);
        } else if (event.detail.formsetName === 'diseaseproductkind_set') {
            updateSelectOptions(diseaseSelector);
        }
    });
});
