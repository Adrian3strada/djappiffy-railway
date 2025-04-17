document.addEventListener("DOMContentLoaded", function () {
    const pestSelector = '.inline-group [name^="internalinspection_set-"][name$="-product_pest"]';

    function initSelectWithDynamicFiltering($el) {
        $el.select2({
            width: 'style',
            allowClear: true,
            closeOnSelect: false,
            templateResult: function (data) {
                if (!data.id) return data.text;

                // Obtener los valores seleccionados en este mismo select
                const selected = $el.val() || [];

                // Ocultar del dropdown si ya está seleccionada (excepto la que estás editando ahora mismo)
                if (selected.includes(data.id)) {
                    return null;
                }

                return data.text;
            }
        });

        // Cuando cambie el select, forzamos el refresco del dropdown
        $el.on('change', function () {
            // Esto actualiza el renderizado para evitar que se repitan
            $el.select2('destroy');
            initSelectWithDynamicFiltering($el);
        });
    }

    function initAllSelects() {
        django.jQuery(pestSelector).each(function () {
            const $el = django.jQuery(this);
            if (!$el.hasClass('select2-hidden-accessible')) {
                initSelectWithDynamicFiltering($el);
            }
        });
    }

    // Inicializar al cargar
    initAllSelects();

    // Al agregar una nueva fila
    document.addEventListener("click", function (event) {
        if (event.target.closest(".add-row a")) {
            setTimeout(() => {
                initAllSelects();
            }, 100);
        }
    });
});