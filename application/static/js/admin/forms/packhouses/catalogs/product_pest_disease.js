document.addEventListener('DOMContentLoaded', function () {
    const kindSelect = document.querySelector('select[name$="kind"]');

    if (!kindSelect) return;

    function populateSelects(selector, items, labelKey) {
        const selects = document.querySelectorAll(selector);

        selects.forEach(select => {
            const current = select.value;
            select.innerHTML = '<option value="">---------</option>';
            items.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = item[labelKey];
                select.appendChild(option);
            });
            select.value = current;

            const updatedOptions = Array.from(select.options).map(({ value, text }) => ({ value, text }));
            select.dataset.originalOptions = JSON.stringify(updatedOptions);
        });

        if (window.updateSelectOptions) {
            window.updateSelectOptions(selector);
        }
    }

    function updatePestDiseaseOptions(kindId) {
        console.log("update", kindId);

        // Pests
        fetch(`/rest/v1/catalogs/pest-kinds/?product_kind_id=${kindId}`)
            .then(res => res.json())
            .then(data => {
                const pests = data.results || [];
                populateSelects('.inline-group [name^="productpest_set-"][name$="-pest"]', pests, 'pest');
            });

        // Diseases
        fetch(`/rest/v1/catalogs/disease-kinds/?product_kind_id=${kindId}`)
            .then(res => res.json())
            .then(data => {
                const diseases = data.results || [];
                populateSelects('.inline-group [name^="productdisease_set-"][name$="-disease"]', diseases, 'disease');
            });
    }

    // Cambio de tipo
    $(document).on('change', kindSelect, function () {
        if (kindSelect.value) updatePestDiseaseOptions(kindSelect.value);
    });

});