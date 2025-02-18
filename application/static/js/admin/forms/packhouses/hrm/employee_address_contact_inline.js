document.addEventListener('DOMContentLoaded', () => {
    function updateFieldOptions(field, options) {
        field.empty(); 
        if (!field.prop('multiple')) {
            field.append(new Option('---------', '', true, true)); 
        }
        options.forEach(option => {
            field.append(new Option(option.name, option.id, false, false)); 
        });
    }

    function fetchOptions(url) {
        return $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json'
        }).fail(error => console.error('Fetch error:', error));
    }

    const $inlineForm = $('[id*="employeecontactinformation-0"]');

    if ($inlineForm.length) {
        const $countryField = $inlineForm.find('select[name$="-country"]');
        const $stateField = $inlineForm.find('select[name$="-state"]');
        const $cityField = $inlineForm.find('select[name$="-city"]');
        const $districtField = $inlineForm.find('select[name$="-district"]');

        const selectedState = $stateField.val();
        const selectedCity = $cityField.val();
        const selectedDistrict = $districtField.val();

        if ($countryField.val()) {
            fetchOptions(`/rest/v1/cities/region/?country=${$countryField.val()}`)
                .then(data => {
                    updateFieldOptions($stateField, data);
                    $stateField.val(selectedState).trigger('change');
                });
        }

        if ($stateField.val()) {
            fetchOptions(`/rest/v1/cities/subregion/?region=${$stateField.val()}`)
                .then(data => {
                    updateFieldOptions($cityField, data);
                    $cityField.val(selectedCity).trigger('change');
                });
        }

        if ($cityField.val()) {
            fetchOptions(`/rest/v1/cities/city/?subregion=${$cityField.val()}`)
                .then(data => {
                    updateFieldOptions($districtField, data);
                    $districtField.val(selectedDistrict).trigger('change');
                });
        }
        
        setTimeout(() => {
            $countryField.on('change', function () {
                const countryId = $(this).val();
                if (countryId) {
                    fetchOptions(`/rest/v1/cities/region/?country=${countryId}`)
                        .then(data => {
                            updateFieldOptions($stateField, data);
                        });
                } else {
                    updateFieldOptions($stateField, []);
                }
            });

            $stateField.on('change', function () {
                const stateId = $(this).val();
                if (stateId) {
                    fetchOptions(`/rest/v1/cities/subregion/?region=${stateId}`)
                        .then(data => {
                            updateFieldOptions($cityField, data);
                        });
                } else {
                    updateFieldOptions($cityField, []);
                }
            });

            $cityField.on('change', function () {
                const cityId = $(this).val();
                if (cityId) {
                    fetchOptions(`/rest/v1/cities/city/?subregion=${cityId}`)
                        .then(data => {
                            updateFieldOptions($districtField, data);
                        });
                } else {
                    updateFieldOptions($districtField, []);
                }
            });
        }, 200);
    }
});