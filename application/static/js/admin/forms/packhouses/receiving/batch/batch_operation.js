document.addEventListener("DOMContentLoaded", function() {
    const reviewStatusField = $('#id_review_status');
    const operationalStatusField = $('#id_operational_status');
    const availableForProcessing = $('#id_is_available_for_processing');

    const initialReviewStatus = reviewStatusField.val();  
    const initialOperationalStatus = operationalStatusField.val();  
    const initialAvailableForProcessing = availableForProcessing.prop('checked');  
    const initialStatus = reviewStatusField.val();
    
    
    if (initialStatus !== 'pending') {
        reviewStatusField.find('option[value="pending"]').remove();
        reviewStatusField.trigger('change.select2');
    }
    if (initialStatus === 'pending') {
        operationalStatusField.prop('disabled', true);
        availableForProcessing.prop('disabled', true);
    }

    function updateFieldsBasedOnReviewStatus() {
        const reviewStatus = reviewStatusField.val();
        console.log('Valor actual de review_status:', reviewStatus);

        if (reviewStatus === 'accepted') {
            availableForProcessing.prop('disabled', false);
            operationalStatusField.val('in_operation').trigger('change');
        }
        
        if (reviewStatus === 'pending') {
            availableForProcessing.prop('disabled', false);
            operationalStatusField.val('pending').trigger('change');
        }

        if (reviewStatus === 'rejected' || reviewStatus === 'quarantine') {
            availableForProcessing.prop('disabled', true);
            operationalStatusField.val('pending').trigger('change');
            operationalStatusField.prop('disabled', true);
            availableForProcessing.prop('checked', false);
        }
    }
    function updateFieldsBasedOnOperationalStatus(){
        const operationalStatus = operationalStatusField.val()
        console.log('Valor actual de operational status:', operationalStatus);
    }
    
    updateFieldsBasedOnReviewStatus();
    updateFieldsBasedOnOperationalStatus();


    reviewStatusField.on('change', function() {
        updateFieldsBasedOnReviewStatus();
    });

    operationalStatusField.on('change', function() {
        updateFieldsBasedOnOperationalStatus();
    });
});