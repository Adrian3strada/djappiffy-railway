document.addEventListener('DOMContentLoaded', function () {

    const fieldTypes = [
        { name: 'sample_pest', setName: 'samplepest_set' },
        { name: 'sample_disease', setName: 'sampledisease_set' },
        { name: 'sample_physical_damage', setName: 'samplephysicaldamage_set' },
        { name: 'sample_residue', setName: 'sampleresidue_set' }
    ];

    function recalculatePercentage() {
        fieldTypes.forEach(({ name: fieldType, setName }) => {
            const sampleFields = Array.from(document.querySelectorAll(`input[name$="${fieldType}"]`));

            const percentageFields = Array.from(document.querySelectorAll('input'))
                .filter(input =>
                    input.name.includes(setName) &&
                    input.name.endsWith('-percentage') &&
                    new RegExp(`^samplecollection_set-\\d+-${setName}-\\d+-percentage$`).test(input.name)
                );

            const weightInputs = Array.from(document.querySelectorAll('input'))
                .filter(input =>
                    input.name.includes('sampleweight_set') &&
                    input.name.endsWith('-weight') &&
                    /^samplecollection_set-\d+-sampleweight_set-\d+-weight$/.test(input.name)
                );

            sampleFields.forEach((field, index) => {
                const sample = parseFloat(field.value);
                if (!isNaN(sample) && weightInputs.length > 0) {
                    const percentage = sample / weightInputs.length;
                    if (percentageFields[index]) {
                        percentageFields[index].value = percentage.toFixed(2);
                    }
                }
            });
        });
    }

    document.addEventListener('input', function (event) {
        const isSampleField = fieldTypes.some(({ name }) => event.target.name.endsWith(name));
        if (isSampleField || event.target.name.endsWith('-weight')) {
            recalculatePercentage();
        }
    });

    const observer = new MutationObserver(mutations => {
        let shouldRecalculate = false;

        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    const input = node.matches('input') ? node : node.querySelector('input');
                    if (input && (
                        fieldTypes.some(({ name }) => input.name.endsWith(name)) ||
                        input.name.endsWith('-weight')
                    )) {
                        shouldRecalculate = true;
                    }
                }
            });

            mutation.removedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    const input = node.matches('input') ? node : node.querySelector('input');
                    if (input && (
                        fieldTypes.some(({ name }) => input.name.endsWith(name)) ||
                        input.name.endsWith('-weight')
                    )) {
                        shouldRecalculate = true;
                    }
                }
            });
        });

        if (shouldRecalculate) {
            recalculatePercentage();
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    recalculatePercentage();
});