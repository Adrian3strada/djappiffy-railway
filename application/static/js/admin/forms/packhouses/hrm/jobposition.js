document.addEventListener('DOMContentLoaded', function() {
    // Solo aplicar en la página de creación de JobPosition
    if (window.location.pathname.includes('/add/')) {
        const daysOfWeek = [
            gettext("Monday"), gettext("Tuesday"), gettext("Wednesday"),
            gettext("Thursday"), gettext("Friday"), gettext("Saturday"),
            gettext("Sunday")
        ];

        // Iterar sobre cada fila del inline
        document.querySelectorAll('.inline-related').forEach((row, index) => {
            if (index < daysOfWeek.length) {
                const dayInput = row.querySelector('input[name$="-day"]');
                if (dayInput) {
                    dayInput.value = daysOfWeek[index];  // Establecer valor del día
                    // Mostrar el día como texto en la interfaz
                    const dayDisplay = document.createElement('span');
                    dayDisplay.textContent = daysOfWeek[index];
                    dayDisplay.style.marginRight = '10px';
                    dayInput.closest('.form-row').prepend(dayDisplay);
                }
            }
        });
    }
});