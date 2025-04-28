document.addEventListener('DOMContentLoaded', function () {

    // 1. Agregar data-average-type si no existe
    document.querySelectorAll('label').forEach(label => {
        const text = label.textContent.trim();
        if (text === 'Average Dry Matter:') {
            const container = label.closest('.row');
            if (container) {
                const valueDiv = container.querySelector('.col-md-7');
                if (valueDiv && !valueDiv.hasAttribute('data-average-type')) {
                    valueDiv.setAttribute('data-average-type', 'dry-matter');
                }
            }
        } else if (text === 'Average Internal Temperature:') {
            const container = label.closest('.row');
            if (container) {
                const valueDiv = container.querySelector('.col-md-7');
                if (valueDiv && !valueDiv.hasAttribute('data-average-type')) {
                    valueDiv.setAttribute('data-average-type', 'temperature');
                }
            }
        }
    });

    function recalculateAverage(select, outputSelector) {
        const inputs = Array.from(document.querySelectorAll(select));
        const valores = [];

        inputs.forEach(input => {
            const value = input.value.trim().replace(',', '.'); // convertir coma a punto
            const num = parseFloat(value);
            if (!isNaN(num)) {
                valores.push(num);
            }
        });

        if (valores.length > 0) {
            const suma = valores.reduce((acc, val) => acc + val, 0);
            const promedio = suma / valores.length;

            const output = document.querySelector(outputSelector);
            if (output) {
                output.textContent = promedio.toFixed(2).replace('.', ',');
            }
        }
    }

    // Selectores para los dos tipos de selects
    const temperature = '.inline-group [name^="internalinspection_set-"][name$="-internal_temperature"]';
    const dry_matter = '.inline-group [name^="drymatter_set-"][name$="-dry_matter"]';

    const temperature_average = '[data-average-type="temperature"]';
    const dry_matter_average = '[data-average-type="dry-matter"]';

    
    recalculateAverage(temperature, temperature_average);
    recalculateAverage(dry_matter, dry_matter_average);

    $(document).on('change', temperature + ', ' + dry_matter, function () {
        if ($(this).is(temperature)) {
            recalculateAverage(temperature, temperature_average);
        } else if ($(this).is(dry_matter)) {
            recalculateAverage(dry_matter, dry_matter_average);
        }
    });

    document.addEventListener('formset:removed', (event) => {
        if (event.detail.formsetName === 'internalinspection_set') {
            recalculateAverage(temperature, temperature_average);
        } else if (event.detail.formsetName === 'drymatter_set') {
            recalculateAverage(dry_matter, dry_matter_average);
        }
    });
});