document.addEventListener("DOMContentLoaded", function () {

    function attachEventListener() {
        const currencyField = document.getElementById("id_source");
        const targetCurrencyField = document.getElementById("id_target");

        if (!currencyField || !targetCurrencyField) {
            return;
        }

        function disableSelectedCurrency() {
            const selectedCurrency = currencyField.value;

            Array.from(targetCurrencyField.options).forEach(option => {
                option.disabled = false;
            });

            if (selectedCurrency) {
                const targetOption = Array.from(targetCurrencyField.options).find(option => option.value === selectedCurrency);
                if (targetOption) {
                    targetOption.disabled = true;
                }
            }
        }

        currencyField.removeEventListener("change", disableSelectedCurrency);
        currencyField.addEventListener("change", disableSelectedCurrency);

        disableSelectedCurrency();
    }

    attachEventListener();

    const observer = new MutationObserver(() => {
        attachEventListener();
    });

    observer.observe(document.body, { childList: true, subtree: true });
});
