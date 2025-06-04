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
    
    const vehicleSelector = '.inline-group [name^="vehiclereview_set-"][name$="-vehicle"]';
 
    updateSelectOptions(vehicleSelector);


    $(document).on('change', function () {
        updateSelectOptions(vehicleSelector);
    });


    $(document).on('formset:removed', function (event, $inline) {
        updateSelectOptions(vehicleSelector);
    });
});
