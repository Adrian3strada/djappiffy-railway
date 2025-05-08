document.addEventListener('DOMContentLoaded', function () {
    const countrySelect = document.getElementById('id_country');
    const countriesSelect = document.getElementById('id_countries');

    if (!countrySelect || !countriesSelect) return; // Evita errores si los elementos no existen

    function syncCountryToCountries() {
        const selectedCountryValue = countrySelect.value;

        // Deselecciona todas las opciones de countries
        for (const option of countriesSelect.options) {
            option.selected = false;
        }

        // Selecciona la opción en countries que coincida con country
        for (const option of countriesSelect.options) {
            if (option.value === selectedCountryValue) {
                option.selected = true;
                break;
            }
        }
    }

    // Sincroniza cuando se cambia el país
    countrySelect.addEventListener('change', syncCountryToCountries);

    // También sincroniza al cargar la página
    syncCountryToCountries();
});
