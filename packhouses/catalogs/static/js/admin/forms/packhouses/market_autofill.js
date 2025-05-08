document.addEventListener('DOMContentLoaded', function() {
    // Obtener los elementos del formulario
    var countryField = document.querySelector('select[name="country"]');
    var countriesField = document.querySelector('select[name="countries"]');

    if (countryField && countriesField) {
        // Escuchar el cambio en el campo 'country'
        countryField.addEventListener('change', function() {
            var countryId = countryField.value;

            if (countryId) {
                // Realizar una solicitud AJAX para obtener los países relacionados
                fetch(`/dadmin/catalogs/market/${countryId}/get_countries/`)
                    .then(response => response.json())
                    .then(data => {
                        // Limpiar las opciones anteriores
                        countriesField.innerHTML = '';

                        // Agregar las nuevas opciones de países
                        data.countries.forEach(function(country) {
                            var option = document.createElement('option');
                            option.value = country.id;
                            option.text = country.name;
                            countriesField.appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error al obtener los países:', error));
            } else {
                // Si no se selecciona un país, limpiar el campo 'countries'
                countriesField.innerHTML = '';
            }
        });
    }
});
