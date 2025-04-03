document.addEventListener("DOMContentLoaded", function() {
    const VEHICLE_FORM_SELECTOR = 'div[id^="scheduleharvest-0-scheduleharvestvehicle_set-"]:not([id*="group"], [id*="empty"])';
    const CONTAINER_FORM_SELECTOR = "tbody.djn-inline-form[data-inline-model='gathering-scheduleharvestcontainervehicle']:not([id*='empty'])";
    document.querySelectorAll("#scheduleharvest-0-scheduleharvestvehicle_set-group a.djn-add-handler.djn-model-gathering-scheduleharvestvehicle")
    .forEach(button => {
        button.style.display = "none";
    });

    document.querySelectorAll("#scheduleharvest-0-scheduleharvestvehicle_set-group span.djn-delete-handler.djn-model-gathering-scheduleharvestvehicle")
    .forEach(element => {
        element.style.display = "none";
    });

    
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

    function initializeVehicle(vehicleForm) {
        const $vehicle = $(vehicleForm);
        // Buscar dentro de $vehicle el input checkbox cuyo nombre termine en "-has_arrived"
        const $vehicleArrived = $vehicle.find('input[type="checkbox"][name$="-has_arrived"]');
        
        // Si el checkbox está marcado, salimos sin imprimir nada
        if ($vehicleArrived.prop('checked')) {
          console.log("El vehículo con id", $vehicle.attr('id'), "ya tiene has_arrived marcado. Se omite.");
          return;
        }
        console.log("formulario", $vehicle);
      }
      

    // Inicializa todos los formularios de container existentes.
    $(CONTAINER_FORM_SELECTOR).each(function(index, containerForm) {
        initializeContainer(containerForm);
    });

    $(VEHICLE_FORM_SELECTOR).each(function(index, vehicleForm) {
        initializeVehicle(vehicleForm);
    });

    // Escucha el evento formset:added para inicializar nuevos formularios de container.
    document.addEventListener("formset:added", function(event) {
        const formsetName = event.detail.formsetName;
        if (formsetName.includes("scheduleharvestcontainervehicle_set")) {
            initializeContainer(event.target);
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
