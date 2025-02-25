document.addEventListener('DOMContentLoaded', () => {
    // Seleccionar el formulario inline
    const $inlineForm = $('[id*="employeejobposition-0"]');
    
    const $paymentKindField = $inlineForm.find('select[name$="-payment_kind"]');
    const $bankField = $inlineForm.find('select[name$="-bank"]');
    const $bankAccountNumberField = $inlineForm.find('[name$="-bank_account_number"]');
    const $clabeField = $inlineForm.find('[name$="-clabe"]');
    const $swiftField = $inlineForm.find('[name$="-swift"]');

    const $paymentPerHourField = $inlineForm.find('input[name$="-payment_per_hour"]');
    const $workHoursPerDayField = $inlineForm.find('input[name$="-work_hours_per_day"]');
    const $paymentPerDayField = $inlineForm.find('input[name$="-payment_per_day"]');

    function toggleFieldsBasedOnCategory() {
        const $paymentKindValue = $paymentKindField.val();
        const $bankFieldContainer = $bankField.parent().parent().parent();
        const $bankAccountNumberFieldContainer = $bankAccountNumberField.parent().parent();
        const $clabeFieldContainer = $clabeField.parent().parent();
        const $swiftFieldContainer = $swiftField.parent().parent();
    
        if ($paymentKindValue === "bank_transfer" || $paymentKindValue === "cheque") {
            $bankFieldContainer.fadeIn();
            $bankAccountNumberFieldContainer.fadeIn();
            $clabeFieldContainer.fadeIn();
            $swiftFieldContainer.fadeIn();
        } else{
            $bankFieldContainer.hide();
            $bankAccountNumberFieldContainer.hide();
            $clabeFieldContainer.hide();
            $swiftFieldContainer.hide();
        } 
      }
    
    toggleFieldsBasedOnCategory();

    $paymentKindField.change(toggleFieldsBasedOnCategory);

    function dailyPayment() {
        // Obtener los valores de los campos
        const paymentPerHour = parseFloat($paymentPerHourField.val()) || 0; // Si no hay valor, usar 0
        const workHoursPerDay = parseFloat($workHoursPerDayField.val()) || 0; // Si no hay valor, usar 0

        // Calcular el pago diario
        const paymentPerDay = paymentPerHour * workHoursPerDay;

        // Actualizar el campo de pago diario
        $paymentPerDayField.val(paymentPerDay.toFixed(2)); // Redondear a 4 decimales
    }

    // Escuchar cambios en los campos de pago por hora y horas trabajadas por día
    $paymentPerHourField.on('input', dailyPayment);
    $workHoursPerDayField.on('input', dailyPayment);

    // Llamar a la función inicialmente para calcular el pago diario si ya hay valores
    dailyPayment();
});