document.addEventListener('DOMContentLoaded', () => {
    // Seleccionar el formulario inline
    const $inlineForm = $('[id*="employeeacademicandworkinformation-0"]');
    const $academicStatusField = $inlineForm.find('select[name$="-academic_status"]');    
    const $degreeField = $inlineForm.find('[name$="-degree"]');
    const $professionalLicenseField = $inlineForm.find('[name$="-professional_license"]');
    const $institutionField = $inlineForm.find('[name$="-institution"]');
    const $graduationYearField = $inlineForm.find('[name$="-graduation_year"]');
    const $fieldStudyField = $inlineForm.find('[name$="-field_of_study"]');

    function toggleFieldsBasedOnCategory() {    
        const $degreeFieldContainer = $degreeField.parent().parent();
        const $professionalLicenseFieldContainer = $professionalLicenseField.parent().parent();
        const $institutionFieldContainer = $institutionField.parent().parent();
        const $graduationYearFieldContainer = $graduationYearField.parent().parent().parent();
        const $fieldStudyFieldContainer = $fieldStudyField.parent().parent();

        if ($academicStatusField.val() === "basic_education" || $academicStatusField.val() === "none") {
            $degreeFieldContainer.hide();
            $professionalLicenseFieldContainer.hide();
            $institutionFieldContainer.hide();
            $graduationYearFieldContainer.hide();
            $fieldStudyFieldContainer.hide();
        } else if ($academicStatusField.val() === "upper_secondary_education") {
            $degreeFieldContainer.hide();
            $professionalLicenseFieldContainer.hide();
            $institutionFieldContainer.hide();
            $graduationYearFieldContainer.fadeIn();
            $fieldStudyFieldContainer.fadeIn();
        } else if ($academicStatusField.val() === "higher_education") {
            $degreeFieldContainer.fadeIn();
            $professionalLicenseFieldContainer.fadeIn();
            $institutionFieldContainer.fadeIn();
            $graduationYearFieldContainer.fadeIn();
            $fieldStudyFieldContainer.fadeIn();
        }
    }
    
    toggleFieldsBasedOnCategory();
    $academicStatusField.change(toggleFieldsBasedOnCategory);

});