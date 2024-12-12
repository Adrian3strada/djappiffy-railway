document.addEventListener('DOMContentLoaded', function () {
    const stateField = $('#id_state');
    const cityField = $('#id_city');

    if (stateField.length) {
        stateField.on('change', function () {
            const stateId = stateField.val();
            const url = `/rest/v1/cities/city/?region=${stateId}`;

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
});
