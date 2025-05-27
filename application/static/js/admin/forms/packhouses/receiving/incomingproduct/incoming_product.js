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

    const statusField = $('#id_status');
    const initialStatus = statusField.val();
    const inQuarantinedField = $('#id_is_quarantined');

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

    if (initialStatus !== 'closed') {
        statusField.find('option[value="closed"]').remove();
        statusField.trigger('change.select2');
    }

    function updateFieldsBasedOnBatchStatus(status) {
        if (status === 'open') {
            enableField(inQuarantinedField);
        } else if (status === 'ready' || status === 'canceled' || status === 'closed') {
            disableField(inQuarantinedField);
            inQuarantinedField.prop('checked', false);
        }
    }

    updateFieldsBasedOnBatchStatus(initialStatus);

    statusField.on('change', function () {
        const newStatus = $(this).val();
        updateFieldsBasedOnBatchStatus(newStatus);
    });
});
