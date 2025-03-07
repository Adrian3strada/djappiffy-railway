document.addEventListener('DOMContentLoaded', function () {
    const $harvestField = $('#id_harvest'); 
    const $harvestDateField = $('#id_harvest_date'); 
    const $categoryField = $('#id_category'); 
    const $productField = $('#id_product'); 
    const $marketField = $('#id_market'); 
    const $weightExpectedField = $('#id_weight_expected'); 
    const $orchardField = $('#id_orchard'); 
    const $orchardCertificationField = $('#id_orchard_certification'); 
    const $weighingScaleField = $('#id_weighing_scale'); 

    function toggleFieldsBasedOnChoice() {
        const harvestValue = $harvestField.val(); // Obtener la opción seleccionada

        if (harvestValue && harvestValue !== '') {
            // Mostrar los campos
            $harvestDateField.closest('.form-group').show();
            $categoryField.closest('.form-group').show();
            $productField.closest('.form-group').show();
            $marketField.closest('.form-group').show();
            $weightExpectedField.closest('.form-group').show();
            $orchardField.closest('.form-group').show();
            $orchardCertificationField.closest('.form-group').show();
            $weighingScaleField.closest('.form-group').show();

           
        } else {
            // Ocultar los campos si no hay selección
            $harvestDateField.closest('.form-group').hide();
            $categoryField.closest('.form-group').hide();
            $productField.closest('.form-group').hide();
            $marketField.closest('.form-group').hide();
            $weightExpectedField.closest('.form-group').hide();
            $orchardField.closest('.form-group').hide();
            $orchardCertificationField.closest('.form-group').hide();
            $weighingScaleField.closest('.form-group').hide();
        }
    }

    // Ejecutar al cargar la página
    toggleFieldsBasedOnChoice();

    // Agregar evento de cambio
    $harvestField.change(toggleFieldsBasedOnChoice);
});
