document.addEventListener("DOMContentLoaded", function () {
    console.log("llego 2");
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

    // Selectores para los dos tipos de selects
    const diseaseSelector = '.inline-group [name^="diseaseproductkind_set-"][name$="-disease"]';
    const pestSelector = '.inline-group [name^="pestproductkind_set-"][name$="-pest"]';
    const productPestSelector = '.inline-group [name^="productpest_set-"][name$="-pest"]';
    const productDiseaseSelector = '.inline-group [name^="productdisease_set-"][name$="-disease"]';
    const processSelector = '.inline-group [name^="productfoodsafetyprocess_set-"][name$="-procedure"]';
    
    // Ejecutar al cargar la página para ambos tipos de selects
    updateSelectOptions(diseaseSelector);
    updateSelectOptions(pestSelector);
    updateSelectOptions(productDiseaseSelector);
    updateSelectOptions(productPestSelector);
    updateSelectOptions(processSelector); 

    // Actualizar cuando cambia un select
    document.addEventListener("change", function (event) {
        if (event.target.matches('.inline-group select')) {
            // Determinar qué selector usar basado en el nombre del select que cambió
            if (event.target.matches(diseaseSelector)) {
                updateSelectOptions(diseaseSelector);
            } else if (event.target.matches(pestSelector)) {
                updateSelectOptions(pestSelector);
            } else if (event.target.matches(productDiseaseSelector)) {
                updateSelectOptions(productDiseaseSelector);
            } else if (event.target.matches(productPestSelector)) {
                updateSelectOptions(productPestSelector);
            } else if (event.target.matches(processSelector)) {
                updateSelectOptions(processSelector);
            }
        }
    });

    // Detectar cuando se agrega una nueva fila en el inline
    document.addEventListener("click", function (event) {
        if (event.target.matches(".add-row a")) {
            // Esperar a que Django agregue la fila y luego actualizar ambos tipos de selects
            setTimeout(() => {
                updateSelectOptions(diseaseSelector);
                updateSelectOptions(pestSelector);
                updateSelectOptions(productDiseaseSelector);
                updateSelectOptions(productPestSelector);
                updateSelectOptions(processSelector);
            }, 500);
        }
    });
});
