document.addEventListener("DOMContentLoaded", function () {
    function updateSelectOptions() {
        let infestationSelects = document.querySelectorAll(
            '.inline-group [name^="infestationproductkind_set-"][name$="-infestation"]'
        );
        let selectedValues = new Set();

        // Recopilar valores seleccionados
        infestationSelects.forEach(select => {
            if (select.value) {
                selectedValues.add(select.value);
            }
        });

        // Actualizar las opciones de los selects
        infestationSelects.forEach(select => {
            let currentValue = select.value;
            let options = Array.from(select.options);

            // Guardar la opción seleccionada para que no desaparezca
            let selectedOption = options.find(option => option.value === currentValue);

            // Limpiar el select
            select.innerHTML = "";

            // Agregar solo las opciones que no están seleccionadas en otros selects
            options.forEach(option => {
                if (!selectedValues.has(option.value) || option === selectedOption || option.value === "") {
                    select.appendChild(option);
                }
            });
        });
    }

    // Ejecutar al cargar la página
    updateSelectOptions();

    // Actualizar cuando cambia un select
    document.addEventListener("change", function (event) {
        if (event.target.matches('.inline-group select')) {
            updateSelectOptions();
        }
    });

    // Detectar cuando se agrega una nueva fila en el inline
    document.addEventListener("click", function (event) {
        if (event.target.matches(".add-row a")) {
            setTimeout(updateSelectOptions, 500); // Esperar a que Django agregue la fila
        }
    });
});