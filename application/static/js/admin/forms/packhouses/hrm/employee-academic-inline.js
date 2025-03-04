document.addEventListener('DOMContentLoaded', () => {
    const $inlineForm = $('[id*="employeeacademicandworkinformation-0"]');
    const $academicStatusField = $inlineForm.find('select[name$="-academic_status"]');    
    const $degreeField = $inlineForm.find('[name$="-degree"]');
    const $professionalLicenseField = $inlineForm.find('[name$="-professional_license"]');
    const $institutionField = $inlineForm.find('[name$="-institution"]');
    const $graduationYearField = $inlineForm.find('[name$="-graduation_year"]');
    const $fieldStudyField = $inlineForm.find('[name$="-field_of_study"]');

    function toggleFieldsBasedOnCategory() {
        const $degreeFieldContainer = $degreeField.parents('div').eq(1);
        const $professionalLicenseFieldContainer = $professionalLicenseField.parents('div').eq(1);
        const $institutionFieldContainer = $institutionField.parents('div').eq(1);
        const $graduationYearFieldContainer = $graduationYearField.parents('div').eq(1);
        const $fieldStudyFieldContainer = $fieldStudyField.parents('div').eq(1);

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
