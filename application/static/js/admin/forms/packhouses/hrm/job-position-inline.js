document.addEventListener('DOMContentLoaded', () => {
    // Seleccionar el formulario inline
    const $inlineForm = $('[id*="employeejobposition-0"]');
    
    const paymentKindField = $inlineForm.find('select[name$="-payment_kind"]');
    const bankField = $inlineForm.find('select[name$="-bank"]');
    const bankAccountNumberField = $inlineForm.find('[name$="-bank_account_number"]');
    const clabeField = $inlineForm.find('[name$="-clabe"]');
    const swiftField = $inlineForm.find('[name$="-swift"]');
    
    function toggleFieldsBasedOnCategory() {
        const paymentKindValue = paymentKindField.val();
        const bankFieldContainer = bankField.parent().parent().parent();
        const bankAccountNumberFieldContainer = bankAccountNumberField.parent().parent();
        const clabeFieldContainer = clabeField.parent().parent();
        const swiftFieldContainer = swiftField.parent().parent();
        
    
        if (paymentKindValue === "bank_transfer" || paymentKindValue === "cheque") {
            bankFieldContainer.fadeIn();
            bankAccountNumberFieldContainer.fadeIn();
            clabeFieldContainer.fadeIn();
            swiftFieldContainer.fadeIn();
        } else{
            bankFieldContainer.hide();
            bankAccountNumberFieldContainer.hide();
            clabeFieldContainer.hide();
            swiftFieldContainer.hide();
        } 
      }
    
    toggleFieldsBasedOnCategory();

    paymentKindField.change(toggleFieldsBasedOnCategory);
});