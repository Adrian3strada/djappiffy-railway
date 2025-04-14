function updateNumbersFor(prefix) {
    const tbodies = Array.from(document.querySelectorAll(`tbody[id*="${prefix}"]`))
        .filter((tbody) => !tbody.id.includes('empty'));

    let count = 1;

    tbodies.forEach((tbody) => {
        const rows = tbody.querySelectorAll('tr.djn-tr');

        rows.forEach((row) => {
            if (row.style.display === 'none') return;

            const numberCell = row.querySelector('.field-number p');
            if (numberCell) {
                numberCell.textContent = count++;
            }
        });
    });
}

function deferUpdateAll() {
    setTimeout(() => {
        updateNumbersFor('drymatter_set');
        updateNumbersFor('sampleweight_set');
        updateNumbersFor('internalinspection_set');
    }, 50);
}

document.addEventListener('DOMContentLoaded', function () {
    deferUpdateAll();

    ['nested:fieldAdded', 'formset:added'].forEach((evtName) => {
        document.body.addEventListener(evtName, function (event) {
            deferUpdateAll();
        });
    });

    document.addEventListener('click', function (e) {
        if (e.target && e.target.closest('.add-row')) {
            deferUpdateAll();
        }
    });

    document.body.addEventListener('change', function (e) {
        if (e.target.name && e.target.name.includes('-DELETE')) {
            deferUpdateAll();
        }
    });
});