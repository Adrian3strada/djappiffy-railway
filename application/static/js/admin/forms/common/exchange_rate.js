document.addEventListener("DOMContentLoaded", function () {

    function attachEventListener() {
        const currencyField = document.getElementById("id_currency");
        const targetCurrencyField = document.getElementById("id_target_currency");

        if (!currencyField || !targetCurrencyField) {
            return;
        }

        function disableSelectedCurrency() {
            const selectedCurrency = currencyField.value;

            // Habilita todas las opciones antes de deshabilitar una
            Array.from(targetCurrencyField.options).forEach(option => {
                option.disabled = false;
            });

            // Deshabilita la opción seleccionada en currency
            if (selectedCurrency) {
                const targetOption = Array.from(targetCurrencyField.options).find(option => option.value === selectedCurrency);
                if (targetOption) {
                    targetOption.disabled = true;
                }
            }
        }

        // Eliminar eventos duplicados
        currencyField.removeEventListener("change", disableSelectedCurrency);
        currencyField.addEventListener("change", disableSelectedCurrency);

        disableSelectedCurrency();
    }

    // Ejecutar al inicio
    attachEventListener();

    // **Usar MutationObserver para detectar cambios en el DOM**
    const observer = new MutationObserver(() => {
        attachEventListener();
    });

    observer.observe(document.body, { childList: true, subtree: true });
});
