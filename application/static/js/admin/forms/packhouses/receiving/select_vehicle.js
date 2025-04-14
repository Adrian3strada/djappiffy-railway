document.addEventListener("DOMContentLoaded", function () {
    function updateSelectOptions(selector) {
        let selects = document.querySelectorAll(selector);
        let selectedValues = new Set();

        selects.forEach(select => {
            if (select.value) {
                selectedValues.add(select.value);
            }
        });

        selects.forEach(select => {
            let currentValue = select.value;
            let options = Array.from(select.options);
            let selectedOption = options.find(option => option.value === currentValue);
            select.innerHTML = "";

            options.forEach(option => {
                if (!selectedValues.has(option.value) || option === selectedOption || option.value === "") {
                    select.appendChild(option);
                }
            });
        });
    }

    const vehicleSelector = '.inline-group [name^="vehiclereview_set-"][name$="-vehicle"]';

    // Inicial al cargar
    updateSelectOptions(vehicleSelector);

    // Al cambiar un select
    document.addEventListener("change", function (event) {
        if (event.target.matches(vehicleSelector)) {
            updateSelectOptions(vehicleSelector);
        }
    });

    // ✅ Escuchar evento de nested-admin
    document.addEventListener("formset:added", function (event) {
        // Verifica que el inline agregado sea uno que contiene los selects que quieres actualizar
        setTimeout(() => {
            updateSelectOptions(vehicleSelector);
        }, 100); // puedes ajustar este tiempo si es necesario
    });
});

