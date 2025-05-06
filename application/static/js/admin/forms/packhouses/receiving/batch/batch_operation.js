document.addEventListener("DOMContentLoaded", function() {
    const reviewStatusField = $('#id_review_status');
    const operationalStatusField = $('#id_operational_status');
    const availableForProcessing = $('#id_is_available_for_processing');

    const initialReviewStatus = reviewStatusField.val();  
    const initialOperationalStatus = operationalStatusField.val();  
    const initialAvailableForProcessing = availableForProcessing.prop('checked');  
    const initialStatus = reviewStatusField.val();

    $(function() {
        const select2Container = operationalStatusField.next('.select2-container')
        const visibleSelection = select2Container.find('.select2-selection');
      
        operationalStatusField.on('select2:opening', e => e.preventDefault());
      
        visibleSelection.css({
          'pointer-events': 'none',
          'background-color':'#e9ecef',
          'border': 'none',
          'color': '#555'
        });
      });

    function disableAvailableForProcessing() {
        availableForProcessing.prop('disabled', true);
        availableForProcessing.prop('checked', false);
    }
    
    if (initialStatus !== 'pending') {
        reviewStatusField.find('option[value="pending"]').remove();
        reviewStatusField.trigger('change.select2');
    }
    setTimeout(function() {
        const initialStatus = reviewStatusField.val();
        if (initialStatus === 'pending') {
            disableAvailableForProcessing();
        }
    }, 50);

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
            availableForProcessing.prop('disabled', true).prop('checked', false);
            operationalStatusField.val('pending').trigger('change');
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