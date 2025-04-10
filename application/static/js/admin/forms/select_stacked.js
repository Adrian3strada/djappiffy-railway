document.addEventListener("DOMContentLoaded", function () {
    // console.log("Stacked");

    // const selectors = {
    //     process: '[name^="transportreview_set-"][name$="-vehicle"]',
    // };
    
    // const originalOptions = {};
    
    // // Cache de las opciones originales para todos los selects
    // function cacheOriginalOptions() {
    //     for (const [key, selector] of Object.entries(selectors)) {
    //         const selects = document.querySelectorAll(selector);
    //         if (selects.length && !originalOptions[key]) {
    //             const options = Array.from(selects[0].options).map(opt => ({
    //                 value: opt.value,
    //                 text: opt.text,
    //             }));
    //             originalOptions[key] = options;
    //         }
    //     }
    //     console.log("originalOptions");
    //     console.log(originalOptions);
    // }
    
    // // Actualizar las opciones en todos los selects de acuerdo a lo que ya está seleccionado
    // function updateGroup(key, selector) {
    //     const selects = document.querySelectorAll(selector);
    //     const selectedValues = new Set();
    
    //     // Almacenar los valores seleccionados
    //     selects.forEach(select => {
    //         if (select.value) selectedValues.add(select.value);
    //         console.log(select.value);
    //     });
    
    //     // Para cada select, actualizar las opciones
    //     selects.forEach(select => {
    //         const currentValue = select.value;
    //         const options = originalOptions[key];
    //         select.innerHTML = "";
    
    //         options.forEach(({ value, text }) => {
    //             // Solo agregar opciones que no hayan sido seleccionadas
    //             if (!selectedValues.has(value) || value === currentValue || value === "") {
    //                 const option = document.createElement("option");
    //                 option.value = value;
    //                 option.text = text;
    //                 if (value === currentValue) option.selected = true;
    //                 select.appendChild(option);
    //             }
    //         });
    //     });
    // }
    
    // // Actualizar todos los selects
    // function updateAll() {
    //     cacheOriginalOptions();
    //     for (const [key, selector] of Object.entries(selectors)) {
    //         updateGroup(key, selector);
    //     }
    // }
    
    // // Inicializar las opciones al cargar la página
    // updateAll();
    
    // // Cuando cambie cualquier select
    // document.addEventListener("change", function (event) {
    //     if (event.target.tagName === "SELECT") {
    //         updateAll();
    //     }
    // });
    
    // // Cuando se agregue una nueva fila
    // document.addEventListener("click", function (event) {
    //     if (event.target.closest(".add-row a")) {
    //         setTimeout(updateAll, 500); // Asegurarse de que se agregue la nueva fila
    //     }
    // });
});
