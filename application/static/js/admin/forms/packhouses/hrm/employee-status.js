document.addEventListener('DOMContentLoaded', function () {
    const $paidField = $('#id_is_paid'); 

    const $paymentPercentageField = $('#id_payment_percentage');

    function toggleFieldsBasedOnBoolean() {
        const $paidValue = $paidField.prop('checked'); 
    
        if ($paidValue) {
            $paymentPercentageField.closest('.form-group').fadeIn();
        } else {
            $paymentPercentageField.closest('.form-group').hide();
        }
    }
    
    toggleFieldsBasedOnBoolean();
    $paidField.change(toggleFieldsBasedOnBoolean);
});
