document.addEventListener('DOMContentLoaded', function () {
    const $staffField = $('#id_is_staff'); 

    const $staffUserField = $('#id_staff_username');

    function toggleFieldsBasedOnBoolean() {
        const $staffValue = $staffField.prop('checked'); 
    
        if ($staffValue) {
            $staffUserField.parent().parent().parent().fadeIn();
        } else {
            $staffUserField.parent().parent().parent().hide();
        }
    }
    
    toggleFieldsBasedOnBoolean();
    $staffField.change(toggleFieldsBasedOnBoolean);
});
