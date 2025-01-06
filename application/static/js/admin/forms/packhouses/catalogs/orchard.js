document.addEventListener('DOMContentLoaded', function () {
    const stateField = $('#id_state');
    const cityField = $('#id_city');
    const districtField = $('#id_district');

    if (stateField.length) {
        stateField.on('change', function () {
            const stateId = stateField.val();
            const url = `/rest/v1/cities/subregion/?region=${stateId}`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    cityField.empty();
                    cityField.append(new Option('---------', '', true, true));
                    data.forEach(city => {
                        const option = new Option(city.name, city.id, false, false);
                        cityField.append(option);
                    });
                    cityField.trigger('change'); // Notify select2 of changes
                });
        });
    }

    if (cityField.length) {
        cityField.on('change', function () {
            const cityId = cityField.val();
            const url = `/rest/v1/cities/city/?subregion=${cityId}`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    districtField.empty();
                    districtField.append(new Option('---------', '', true, true));
                    data.forEach(district => {
                        const option = new Option(district.name, district.id, false, false);
                        districtField.append(option);
                    });
                    districtField.trigger('change'); // Notify select2 of changes
                });
        });
    }
});
