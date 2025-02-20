document.addEventListener('DOMContentLoaded', () => {
    // Seleccionar el formulario inline
    const $inlineForm = $('[id*="employeetaxandmedicalinformation-0"]');
    
    // Seleccionar campos
    const $hasDisabilityField = $inlineForm.find('input[type="checkbox"][name$="-has_disability"]');
    const $disabilityField = $inlineForm.find('[name$="-disability_details"]');
    const $hasIllnessField = $inlineForm.find('input[type="checkbox"][name$="-has_chronic_illness"]');
    const $illnessField = $inlineForm.find('[name$="-chronic_illness_details"]');
    const $insuranceField = $inlineForm.find('input[type="checkbox"][name$="-has_private_insurance"]');
    const $insuranceDetailsField = $inlineForm.find('textarea[name$="-private_insurance_details"].vLargeTextField');
    const $insuranceProviderField = $inlineForm.find('[name$="-medical_insurance_provider"]');
    const $insuranceNumberField = $inlineForm.find('[name$="-medical_insurance_number"]');
    const $insuranceStartDateField = $inlineForm.find('input[type="text"][name$="-medical_insurance_start_date"]');
    const $insuranceEndDateField = $inlineForm.find('input[type="text"][name$="-medical_insurance_end_date"]');
    

    function toggleFieldsBasedOnCategory() {
        const $disabilityContainer = $disabilityField.parent().parent();
        const $illnessContainer = $illnessField.parent().parent();
        const $illnessDetailsContainer = $insuranceDetailsField.parent().parent();
        const $insuranceProviderContainer = $insuranceProviderField.parent().parent();
        const $insuranceNumberContainer = $insuranceNumberField.parent().parent();
        const $insuranceStartDateContainer = $insuranceStartDateField.parent().parent().parent();
        const $insuranceEndDateContainer = $insuranceEndDateField.parent().parent().parent();

        if ($hasDisabilityField.is(':checked')) {
            $disabilityContainer.fadeIn();
        } else {
            $disabilityContainer.hide();
        }

        if ($hasIllnessField.is(':checked')) {
            $illnessContainer.fadeIn();
        } else {
            $illnessContainer.hide();
            
        }

        if ($insuranceField.is(':checked')) {
            $illnessDetailsContainer.fadeIn();
            $insuranceProviderContainer.hide();
            $insuranceNumberContainer.hide();
            $insuranceStartDateContainer.hide();
            $insuranceEndDateContainer.hide();

        } else {
            $illnessDetailsContainer.hide();
            $insuranceProviderContainer.fadeIn();
            $insuranceNumberContainer.fadeIn();
            $insuranceStartDateContainer.fadeIn();
            $insuranceEndDateContainer.fadeIn();
        }
    }

    toggleFieldsBasedOnCategory();

    
    $hasDisabilityField.on('change', toggleFieldsBasedOnCategory);
    $hasIllnessField.on('change', toggleFieldsBasedOnCategory);
    $insuranceField.on('change', toggleFieldsBasedOnCategory);
});