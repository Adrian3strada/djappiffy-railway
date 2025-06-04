 document.addEventListener("DOMContentLoaded", function() {

    document.querySelectorAll("td.original").forEach(row => {
        row.style.display = "none"; 
    });
    document.querySelectorAll("th.original").forEach(row => {
        row.style.display = "none";  
    });

    const statusField = $('#id_status');
    const availableForProcessingField = $('#id_is_available_for_processing');

    const initialStatus = statusField.val(); 

    function disableField(field) {
        field.prop("readonly", true);
        field.css({
            "pointer-events": "none",
            "outline": "none",
            "opacity": "0.3",
            "transform": "scale(1.1)",  
            "cursor": "not-allowed"
        });
    }

    function enableField(field) {
        field.prop("readonly", false);
        field.css({
            "pointer-events": "auto",
            "opacity": "1",
            "transform": "none",
            "cursor": "pointer"
        });
    }

    function updateFieldsBasedOnBatchStatus(status) {
        if (status == 'open'){
            availableForProcessingField.prop('checked', false);
            disableField(availableForProcessingField);
        }
        else if (status == 'ready'){
            enableField(availableForProcessingField);
        }
        else if (status == 'canceled' || status == 'closed'){
            disableField(availableForProcessingField);
            availableForProcessingField.prop('checked', false);
        }
    }

    updateFieldsBasedOnBatchStatus(initialStatus);

    statusField.on('change', function() {
        updateFieldsBasedOnBatchStatus(statusField.val())
    });

});