document.addEventListener('DOMContentLoaded', function () {
    const marketField = $('#id_market');
    const countryField = $('#id_country');
    const stateField = $('#id_state');
    const cityField = $('#id_city');

    function updateCountry() {
        const marketId = marketField.val();
        if (marketId) {
            fetch(`/rest/v1/catalogs/market/${marketId}/`)
                .then(response => response.json())
                .then(data => {
                    countryField.val(data.country).trigger('change');
                    updateState();
                });
        } else {
            countryField.val('').trigger('change');
            updateState();
        }
    }

    function updateState() {
        const countryId = countryField.val();
        if (countryId) {
            fetch(`/rest/v1/cities/region/?country=${countryId}`)
                .then(response => response.json())
                .then(data => {
                  console.log(data);
                    stateField.empty().append(new Option('---------', '', true, true));
                    data.forEach(state => {
                        const option = new Option(state.name, state.id, false, false);
                        stateField.append(option);
                    });
                    stateField.trigger('change');
                    updateCity();
                });
        } else {
            stateField.empty().append(new Option('---------', '', true, true)).trigger('change');
            updateCity();
        }
    }

    function updateCity() {
        const stateId = stateField.val();
        if (stateId) {
            fetch(`/rest/v1/cities/city/?region=${stateId}`)
                .then(response => response.json())
                .then(data => {
                  console.log(data);
                    cityField.empty().append(new Option('---------', '', true, true));
                    data.forEach(city => {
                        const option = new Option(city.name, city.id, false, false);
                        cityField.append(option);
                    });
                    cityField.trigger('change');
                });
        } else {
            cityField.empty().append(new Option('---------', '', true, true)).trigger('change');
        }
    }

    marketField.on('change', updateCountry);
    countryField.on('change', updateState);
    stateField.on('change', updateCity);

    // Inicializar select2 en los campos
    marketField.select2();
    countryField.select2();
    stateField.select2();
    cityField.select2();
});
