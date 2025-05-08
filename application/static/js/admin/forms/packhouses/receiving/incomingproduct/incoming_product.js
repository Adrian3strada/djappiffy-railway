document.addEventListener("DOMContentLoaded", function() {
    /* document.querySelectorAll("#scheduleharvest-0 .djn-add-item .add-handler").forEach(button => {
        button.style.display = "none"; 
    });
    */
    document.querySelectorAll("td.original").forEach(row => {
        row.style.display = "none"; 
    });
    document.querySelectorAll("th.original").forEach(row => {
        row.style.display = "none";  
    });

    const totalWeighingSetsField = $('#id_total_weighed_sets');
    const packhouseWeightResultField = $('#id_packhouse_weight_result');
    const containersAssignedField = $('#id_containers_assigned');
    const fullContainersField = $('#id_full_containers_per_harvest');
    const emptyContainersField = $('#id_empty_containers');
    const missingContainersField = $('#id_missing_containers');
    const averageContainersField = $('#id_average_per_container');
    const currentKgField = $('#id_current_kg_available');
    const missingVehicleContainerField = $('input[name$="-missing_containers"]');
    const totaWeighedSetContainersField = $('#id_total_weighed_set_containers');
    const statusField = $('#id_status');
    const initialStatus = statusField.val();

    // deshabilitar edición en campos, pero permitir que los valores se envíen
    function disableField(field) {
        field.prop("readonly", true);
        field.css({
            "pointer-events": "none",
            "background-color": "#e9ecef",
            "border": "none",
            "color": "#555"
        });
    }

    disableField(currentKgField);
    disableField(totalWeighingSetsField);
    disableField(packhouseWeightResultField);
    disableField(containersAssignedField);
    disableField(missingContainersField);
    disableField(averageContainersField);
    disableField(fullContainersField);
    disableField(emptyContainersField);
    disableField(missingVehicleContainerField);
    disableField(totaWeighedSetContainersField);

    
    if (initialStatus !== 'pending') {
        statusField.find('option[value="pending"]').remove();
        statusField.trigger('change.select2');
    }

    // Función para actualizar missingBoxes
    function updateMissingContainers() {
        const boxesAssigned = parseFloat(containersAssignedField.val());
        const fullBoxes = parseFloat(fullContainersField.val());
        const emptyBoxes = parseFloat(emptyContainersField.val());

        const missingBoxes = boxesAssigned - fullBoxes - emptyBoxes;
        missingContainersField.val(missingBoxes);
    }

    // Función para actualizar averageBox
    function updateAveragePerContainers() {
        const packhouseWeightResult = parseFloat(packhouseWeightResultField.val());
        const fullBoxes = parseFloat(totaWeighedSetContainersField.val());
    
        const averagePerBox = fullBoxes > 0 
            ? Math.floor((packhouseWeightResult / fullBoxes) * 1000) / 1000 
            : 0;
            
        averageContainersField.val(averagePerBox);
    }

    // Función para actualizar kilos disponibles
    function updateCurrentKg() {
        const packhouseWeightResult = parseFloat(packhouseWeightResultField.val());
        currentKgField.val(packhouseWeightResult);
    }

    fullContainersField.on('input', function() {
        updateMissingContainers();
        updateAveragePerContainers(); 
    });
    emptyContainersField.on('input', updateMissingContainers);
    packhouseWeightResultField.on('input change', function() {
        updateAveragePerContainers();
        updateCurrentKg();
    });
    
    updateMissingContainers();
    updateAveragePerContainers();
    updateCurrentKg()
    
    document.querySelectorAll('input[name="_save"], input[name="_continue"]').forEach(button => {
        button.addEventListener('click', function(e) {
            updateMissingContainers();
            updateAveragePerContainers();
            updateCurrentKg(); 
        });
    });

    const form = document.querySelector('form');
    if (form) {
        document.querySelectorAll('input[name="_save"], input[name="_continue"]').forEach(button => {
            button.addEventListener('click', function(e) {
                updateMissingContainers();
                updateAveragePerContainers();
                updateCurrentKg();
                
                const publicWeight = parseFloat($('#id_public_weight_result').val().replace(',', '.')) || 0;
                const packhouseWeight = parseFloat($('#id_packhouse_weight_result').val().replace(',', '.')) || 0;
                const threshold = publicWeight * 0.015; 
                const diff = publicWeight - packhouseWeight; 
                const status = $('#id_status').val();
                console.log("El status: ", status)

                if (publicWeight > packhouseWeight && diff >= threshold && status === "accepted") {
                    e.preventDefault();
                    const diffPerc = (diff / publicWeight) * 100; 
                    Swal.fire({
                        title: 'Significant Difference!',
                        text: `The difference is ${diffPerc.toFixed(2)}%, are you sure you want to proceed?`,
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonText: 'Yes',
                        cancelButtonText: 'No'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            e.target.closest('form').submit();
                        }
                    });                    
                }
            });
        });
    }

});
