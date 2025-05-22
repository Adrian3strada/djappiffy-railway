 document.addEventListener("DOMContentLoaded", function() {
    const statusField = $('#id_status');
    const inQuarantinedField = $('#id_is_quarantined');
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
            enableField(inQuarantinedField);
            availableForProcessingField.prop('checked', false);
            disableField(availableForProcessingField);
        }
        else if (status == 'ready'){
            disableField(inQuarantinedField);
            inQuarantinedField.prop('checked', false);
            enableField(availableForProcessingField);
        }
        else if (status == 'canceled' || status == 'closed'){
            disableField(inQuarantinedField);
            inQuarantinedField.prop('checked', false);
            disableField(availableForProcessingField);
            availableForProcessingField.prop('checked', false);
        }
    }

    updateFieldsBasedOnBatchStatus(initialStatus);

    statusField.on('change', function() {
        updateFieldsBasedOnBatchStatus(statusField.val())
    });

});