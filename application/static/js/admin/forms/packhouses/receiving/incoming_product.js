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
    
        const averagePerBox = fullBoxes > 0 ? (packhouseWeightResult / fullBoxes).toFixed(2) : 0;
        averageBoxField.val(averagePerBox);
    }

    fullBoxesField.on('input', function() {
        updateMissingBoxes();
        updateAveragePerBoxes(); 
    });
    emptyBoxesField.on('input', updateMissingBoxes);
    packhouseWeightResultField.on('input', updateAveragePerBoxes);
    packhouseWeightResultField.on('change', updateAveragePerBoxes);
    
    updateAveragePerBoxes();
});
