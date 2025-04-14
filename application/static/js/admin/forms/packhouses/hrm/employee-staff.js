document.addEventListener('DOMContentLoaded', function () {
    const $staffField = $('#id_is_staff'); 

    const $staffUserField = $('#id_staff_username');

    function toggleFieldsBasedOnBoolean() {
        const $staffValue = $staffField.prop('checked'); 
    
        if ($staffValue) {
            $staffUserField.closest('.form-group').fadeIn();
        } else {
            $staffUserField.closest('.form-group').hide();
        }
    }
    
    toggleFieldsBasedOnBoolean();
    $staffField.change(toggleFieldsBasedOnBoolean);
});
