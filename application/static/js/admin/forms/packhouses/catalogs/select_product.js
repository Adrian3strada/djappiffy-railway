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
    const pestSelector = '.inline-group [name^="productpest_set-"][name$="-pest"]';
    const diseaseSelector = '.inline-group [name^="productdisease_set-"][name$="-disease"]';
    const processSelector = '.inline-group [name^="productfoodsafetyprocess_set-"][name$="-procedure"]';
    
    function updateAll() {
        updateSelectOptions(pestSelector);
        updateSelectOptions(diseaseSelector);
        updateSelectOptions(processSelector);
    }

    $(document).on('change', pestSelector, function () {
        updateAll();
    });
    $(document).on('change', diseaseSelector, function () {
        updateAll();
    });
    $(document).on('change', processSelector, function () {
        updateAll();
    });

    // Actualizamos al cargar la página
    updateAll();

    // Cuando se agrega una fila nueva, esperamos un breve retraso para asegurarnos que el DOM se ha actualizado
    document.addEventListener("click", function (event) {
        // Usamos closest para asegurarnos de capturar el click en el link de añadir fila (si es que la estructura cambia un poco)
        if (event.target.closest(".add-row a")) {
            // Si usamos un delay, el nuevo select ya estará presente en el DOM
            setTimeout(function () {
                updateAll();
            }, 100);
        }
        if (event.target.closest(".inline-deletelink") || 
        event.target.closest(".inline-related .delete") || 
        event.target.closest(".inline-related .remove")) {
            // Esperamos a que el DOM se actualice y se elimine el elemento
            setTimeout(function () {
                updateAll();
            }, 100);
        }
    });
});
