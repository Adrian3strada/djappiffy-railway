document.addEventListener("DOMContentLoaded", function () {
    function updateSelectOptions(selector) {
        const selects = Array.from(document.querySelectorAll(selector));
        const selectedValues = new Set(
            selects.map(select => select.value).filter(Boolean)
        );

        selects.forEach(select => {
            if (!select.dataset.originalOptions) {
                const options = Array.from(select.options).map(({ value, text }) => ({ value, text }));
                select.dataset.originalOptions = JSON.stringify(options);
            }
        });

        selects.forEach(select => {
            const originalOptions = JSON.parse(select.dataset.originalOptions);
            const currentValue = select.value;

            // Limpiar y reconstruir
            select.innerHTML = originalOptions
                .filter(({ value }) => value === "" || !selectedValues.has(value) || value === currentValue)
                .map(({ value, text }) => `<option value="${value}">${text}</option>`)
                .join("");

            select.value = currentValue;
        });
    }

    // Selectores para los dos tipos de selects
    const pestSelector = 'select[name*="samplepest_set"][name$="-product_pest"]';
    const diseaseSelector = 'select[name*="sampledisease_set"][name$="-product_disease"]';
    const physicalDamageSelector = 'select[name*="samplephysicaldamage_set"][name$="-product_physical_damage"]';
    const residueSelector = 'select[name*="sampleresidue_set"][name$="-product_residue"]';
    
    updateSelectOptions(pestSelector);
    updateSelectOptions(diseaseSelector);
    updateSelectOptions(physicalDamageSelector);
    updateSelectOptions(residueSelector);

    $(document).on('change', pestSelector + ', ' + diseaseSelector + ', ' + physicalDamageSelector + ', ' + residueSelector, function () {
        if ($(this).is(pestSelector)) {
            updateSelectOptions(pestSelector);
        } else if ($(this).is(diseaseSelector)) {
            updateSelectOptions(diseaseSelector);
        } else if ($(this).is(physicalDamageSelector)) {
            updateSelectOptions(physicalDamageSelector);
        } else if ($(this).is(residueSelector)) {
            updateSelectOptions(residueSelector);
        }
    });

    $(document).on('formset:removed', function (event, $inline) {
        if (event.detail.formsetName === 'samplecollection_set-0-samplepest_set') {
            updateSelectOptions(pestSelector);
        } else if (event.detail.formsetName === 'samplecollection_set-0-sampledisease_set') {
            updateSelectOptions(diseaseSelector);
        } else if (event.detail.formsetName === 'samplecollection_set-0-samplephysicaldamage_set') {
            updateSelectOptions(physicalDamageSelector);
        } else if (event.detail.formsetName === 'samplecollection_set-0-sampleresidue_set') {
            updateSelectOptions(residueSelector);
        }
    });
});

