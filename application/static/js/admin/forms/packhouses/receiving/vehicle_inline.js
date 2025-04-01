document.addEventListener("DOMContentLoaded", function() {
    const CONTAINER_FORM_SELECTOR = "tbody.djn-inline-form[data-inline-model='gathering-scheduleharvestcontainervehicle']:not([id*='empty'])";

    
    function updateMissingBoxes(containerForm) {
        const $container = $(containerForm);
       
        // const $delete = $container.find("input[name$='-DELETE']").first();
        // if ($delete.length && $delete.prop("checked")) return;

        const quantity = parseFloat($container.find("input[name$='-quantity']").val()) || 0;
        const fullBoxes = parseFloat($container.find("input[name$='-full_boxes']").val()) || 0;
        const emptyBoxes = parseFloat($container.find("input[name$='-empty_boxes']").val()) || 0;

        const missingBoxes = quantity - fullBoxes - emptyBoxes;

        // Actualiza el campo missing_boxes del formulario actual.
        $container.find("input[name$='-missing_boxes']").first().val(missingBoxes);
        console.log(`Container ${$container.attr("id")}: quantity=${quantity}, full_boxes=${fullBoxes}, empty_boxes=${emptyBoxes}, missing_boxes=${missingBoxes}`);
    }

    function initializeContainer(containerForm) {
        const $container = $(containerForm);
        // Cálculo inicial
        updateMissingBoxes(containerForm);

        // Actualiza el cálculo al cambiar los inputs que afectan el valor.
        $container.on("input change", "input[name$='-quantity'], input[name$='-full_boxes'], input[name$='-empty_boxes']", function() {
            updateMissingBoxes(containerForm);
        });

        // Actualiza el cálculo al cambiar el estado del checkbox DELETE.
        $container.find("input[name$='-DELETE']").first().on("change", function() {
            updateMissingBoxes(containerForm);
        });
    }

    // Inicializa todos los formularios de container existentes.
    $(CONTAINER_FORM_SELECTOR).each(function(index, containerForm) {
        initializeContainer(containerForm);
    });

    // Escucha el evento formset:added para inicializar nuevos formularios de container.
    document.addEventListener("formset:added", function(event) {
        const formsetName = event.detail.formsetName;
        if (formsetName.includes("scheduleharvestcontainervehicle_set")) {
            initializeContainer(event.target);
            console.log("Nuevo container inline añadido:", formsetName);
        }
    });

    // se actualiza el cálculo tras un breve retraso.
    $(document).on("click", CONTAINER_FORM_SELECTOR + " .deletelink", function() {
        const $container = $(this).closest(CONTAINER_FORM_SELECTOR);
        setTimeout(() => {
            updateMissingBoxes($container);
        }, 100);
    });
});
