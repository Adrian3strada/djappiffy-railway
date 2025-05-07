document.addEventListener('DOMContentLoaded', function () {
    const countrySelect = document.querySelector('#id_country');
    const nameInput = document.querySelector('#id_name');
    const aliasInput = document.querySelector('#id_alias');

    if (!countrySelect) return;

    // Simula el evento 'change' si ya hay un país seleccionado
    if (countrySelect.value) {
        countrySelect.dispatchEvent(new Event('change'));
    }

    countrySelect.addEventListener('change', function () {
        const countryId = this.value;
        if (!countryId) return;

        fetch(`/rest/v1/cities/countries/${countryId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.name && nameInput) nameInput.value = data.name;
                if (data.code3 && aliasInput) aliasInput.value = data.code3;
            })
            .catch(error => {
                console.error("Error fetching country data:", error);
            });
    });
});
