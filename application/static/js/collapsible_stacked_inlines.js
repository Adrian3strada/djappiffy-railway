document.addEventListener('DOMContentLoaded', function () {
    const inlines = document.querySelectorAll('.inline-related');

    inlines.forEach(inline => {
        const header = inline.querySelector('h3');
        if (header) {
            header.style.cursor = 'pointer';  // Hace que el header sea clickeable
            const content = inline.querySelector('.form-row');

            // Inicialmente colapsado
            content.style.display = 'none';

            header.addEventListener('click', () => {
                if (content.style.display === 'none') {
                    content.style.display = '';
                } else {
                    content.style.display = 'none';
                }
            });
        }
    });
});
