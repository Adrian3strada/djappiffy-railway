document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll("#scheduleharvest-0 .djn-add-item .add-handler").forEach(button => {
        button.style.display = "none"; 
    });
    document.querySelectorAll("td.original").forEach(row => {
        row.style.display = "none"; 
    });
    document.querySelectorAll("th.original").forEach(row => {
        row.style.display = "none";  
    });

    const palletsReceivedField = $('#id_pallets_received');
    const packhouseWeightResultField = $('#id_packhouse_weight_result');
    const boxesAssignedField = $('#id_boxes_assigned');
    const fullBoxesField = $('#id_full_boxes');
    const emptyBoxesField = $('#id_empty_boxes');
    const missingBoxesField = $('#id_missing_boxes');
    const averageBoxField = $('#id_average_per_box');
    const currentKgField = $('#id_current_kg_available');
    const containerTare= $('input[name$="-container_tare"]');
    const totalBoxes= $('input[name$="-total_boxes"]');

    // deshabilitar edición en campos, pero permitir que los valores se envíen
    function makeFieldReadonly(field) {
        field.prop("readonly", true);
        field.css({
            "pointer-events": "none",
            "background-color": "#e9ecef"
        });
    }

    makeFieldReadonly(currentKgField);
    makeFieldReadonly(palletsReceivedField);
    makeFieldReadonly(packhouseWeightResultField);
    makeFieldReadonly(boxesAssignedField);
    makeFieldReadonly(missingBoxesField);
    makeFieldReadonly(averageBoxField);
    makeFieldReadonly(containerTare);
    makeFieldReadonly(totalBoxes);

    // Función para actualizar missingBoxes
    function updateMissingBoxes() {
        const boxesAssigned = parseFloat(boxesAssignedField.val());
        const fullBoxes = parseFloat(fullBoxesField.val());
        const emptyBoxes = parseFloat(emptyBoxesField.val());

        const missingBoxes = boxesAssigned - fullBoxes - emptyBoxes;
        missingBoxesField.val(missingBoxes);
    }

    // Función para actualizar averageBox
    function updateAveragePerBoxes() {
        const packhouseWeightResult = parseFloat(packhouseWeightResultField.val());
        const fullBoxes = parseFloat(fullBoxesField.val());
    
        const averagePerBox = fullBoxes > 0 
            ? Math.floor((packhouseWeightResult / fullBoxes) * 1000) / 1000 
            : 0;
            
        averageBoxField.val(averagePerBox);
    }

    // Función para actualizar kilos disponibles
    function updateCurrentKg() {
        const packhouseWeightResult = parseFloat(packhouseWeightResultField.val());
        currentKgField.val(packhouseWeightResult);
    }


    fullBoxesField.on('input', function() {
        updateMissingBoxes();
        updateAveragePerBoxes(); 
    });
    emptyBoxesField.on('input', updateMissingBoxes);
    packhouseWeightResultField.on('input change', function() {
        updateAveragePerBoxes();
        updateCurrentKg();
    });
    
    updateMissingBoxes();
    updateAveragePerBoxes();
    updateCurrentKg()
    
});
