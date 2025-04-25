document.addEventListener('DOMContentLoaded', function () {
    const fieldSuffixes = ['sample_pest', 'sample_disease', 'sample_physical_damage', 'sample_residue'];

    function getValidWeightInputs() {
        return Array.from(document.querySelectorAll('input'))
            .filter(input =>
                input.name.includes('sampleweight_set') &&
                input.name.endsWith('-weight') &&
                /^samplecollection_set-\d+-sampleweight_set-\d+-weight$/.test(input.name)
            );
    }

    function recalculatePercentage() {
        const weightInputs = getValidWeightInputs();
        const totalWeights = weightInputs.length;

        const tbodies = Array.from(document.querySelectorAll('tbody[id^="samplecollection_set-"]'));

        tbodies.forEach(tbody => {
            const sampleInput = fieldSuffixes
                .map(suffix => tbody.querySelector(`input[name$="${suffix}"]`))
                .find(Boolean);

            const percentageDisplay = tbody.querySelector('td.field-percentage p');

            if (sampleInput && percentageDisplay && totalWeights > 0) {
                const sampleValue = parseFloat(sampleInput.value.replace(',', '.'));
                if (!isNaN(sampleValue)) {
                    const percentage = (sampleValue / totalWeights) * 100;
                    percentageDisplay.textContent = `${percentage.toFixed(2).replace('.', ',')} %`;
                }
            }
        });
    }

    function isRelevantInput(name) {
        return fieldSuffixes.some(suffix => name.endsWith(suffix)) || name.endsWith('-weight');
    }

    document.addEventListener('input', function (event) {
        if (isRelevantInput(event.target.name)) {
            recalculatePercentage();
        }
    });

    const observer = new MutationObserver(mutations => {

        mutations.forEach(({ addedNodes, removedNodes }) => {
            [...addedNodes, ...removedNodes].forEach(node => {
                if (node.nodeType === 1) {
                    const inputs = node.matches('input')
                        ? [node]
                        : Array.from(node.querySelectorAll('input'));

                    if (inputs.some(input => isRelevantInput(input.name))) {
                        recalculatePercentage();
                    }
                }
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    recalculatePercentage();
});