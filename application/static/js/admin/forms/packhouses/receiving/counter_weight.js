function updateNumbers() {
    const tbodies = Array.from(document.querySelectorAll('tbody[id*="sampleweight_set"]'))
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

// Se asegura de ejecutarse después de que todo esté renderizado
function deferUpdate() {
    setTimeout(updateNumbers, 50);
}

document.addEventListener('DOMContentLoaded', function () {
    deferUpdate();

    // Cuando se agregue una nueva fila via Nested Admin
    document.body.addEventListener('formset:added', function (event) {
        deferUpdate();
    });

    // Cuando se marque una fila para eliminar
    document.body.addEventListener('change', function (e) {
        if (e.target.name && e.target.name.includes('-DELETE')) {
            deferUpdate();
        }
    });
});