document.addEventListener('DOMContentLoaded', function () {
    const countryField = $('#id_country');      
    const countriesField = $('#id_countries');  
    const nameField = $('#id_name');            
    const aliasField = $('#id_alias');        

    if (!countryField.length) {
        return;
    }

    countryField.select2({
        placeholder: "Selecciona un país",
        allowClear: true,
        width: '100%'  
    });

    countryField.on('change', function () {
        const countryId = this.value;

        if (!countryId) {
            return;
        }

        fetch(`/rest/v1/cities/countries/${countryId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error();
                }
                return response.json();
            })
            .then(data => {
                const validId = $('#id_countries option').map((_, opt) => opt.value).get()[0];

                if (!validId) {
                    return;
                }

                if (countriesField.length) {
                    countriesField.empty(); 

                    const newOption = new Option(data.name, countryId, true, true);
                    countriesField.append(newOption);
                    countriesField.trigger('change');

                    if (countriesField.data('select2')) {
                        countriesField.select2('destroy').select2();
                    }
                }

                if (nameField.length) {
                    nameField.val(data.name || '');
                }

                if (aliasField.length) {
                    aliasField.val(data.code3 || '');
                }
            })
            .catch((error) => {
                console.error('Error fetching country data:', error);
            });
    });
});

