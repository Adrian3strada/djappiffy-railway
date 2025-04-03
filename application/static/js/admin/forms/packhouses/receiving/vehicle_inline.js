document.addEventListener("DOMContentLoaded", function() {
    const VEHICLE_FORM_SELECTOR = 'div[id^="scheduleharvest-0-scheduleharvestvehicle_set-"]:not([id*="group"], [id*="empty"])';
    const CONTAINER_FORM_SELECTOR = "tbody.djn-inline-form[data-inline-model='gathering-scheduleharvestcontainervehicle']:not([id*='empty'])";

    // (Opcional) Ocultar botones de agregar/eliminar vehículo
    document.querySelectorAll("#scheduleharvest-0-scheduleharvestvehicle_set-group a.djn-add-handler.djn-model-gathering-scheduleharvestvehicle")
      .forEach(button => { button.style.display = "none"; });
    document.querySelectorAll("#scheduleharvest-0-scheduleharvestvehicle_set-group span.djn-delete-handler.djn-model-gathering-scheduleharvestvehicle")
      .forEach(element => { element.style.display = "none"; });

    // Función para actualizar missing_boxes en un contenedor
    function updateMissingBoxes(containerForm) {
        const $container = $(containerForm);
        // Si está marcado para eliminar, se fuerza missing_boxes a 0.
        if ($container.find("input[name$='-DELETE']").prop("checked")) {
            $container.find("input[name$='-missing_boxes']").first().val(0);
            console.log(`Container ${$container.attr("id")}: marcado para eliminar → missing_boxes=0`);
            return;
        }
        const quantity   = parseFloat($container.find("input[name$='-quantity']").first().val()) || 0;
        const fullBoxes  = parseFloat($container.find("input[name$='-full_boxes']").first().val()) || 0;
        const emptyBoxes = parseFloat($container.find("input[name$='-empty_boxes']").first().val()) || 0;
        const missingBoxes = quantity - fullBoxes - emptyBoxes;
        $container.find("input[name$='-missing_boxes']").first().val(missingBoxes);
        console.log(`Container ${$container.attr("id")}: quantity=${quantity}, full=${fullBoxes}, empty=${emptyBoxes} → missing=${missingBoxes}`);
    }

    // Inicializa un contenedor: agrega listeners para inputs y checkbox DELETE
    function initializeContainer(containerForm) {
        const $container = $(containerForm);
        updateMissingBoxes(containerForm);
  
        $container.on("input change", "input[name$='-quantity'], input[name$='-full_boxes'], input[name$='-empty_boxes']", function() {
            updateMissingBoxes(containerForm);
            updateGlobalTotals();
            // Actualiza el vehículo padre
            const $parentVehicle = $container.closest(VEHICLE_FORM_SELECTOR);
            if ($parentVehicle.length) {
                updateVehicleTotals($parentVehicle);
            }
        });
  
        $container.find("input[name$='-DELETE']").first().on("change", function() {
            console.log("Checkbox DELETE (inline) cambiado en contenedor:", $container.attr("id"), "Nuevo valor:", this.checked);
            updateMissingBoxes(containerForm);
            updateGlobalTotals();
            const $parentVehicle = $container.closest(VEHICLE_FORM_SELECTOR);
            if ($parentVehicle.length) {
                updateVehicleTotals($parentVehicle);
            }
        });
    }
  
    // Función para actualizar totales de un vehículo sumando sus contenedores
    function updateVehicleTotals(vehicleForm) {
        const $vehicle = $(vehicleForm);
        let vehicleQuantity = 0, vehicleFullBoxes = 0, vehicleEmptyBoxes = 0, vehicleMissingBoxes = 0;
  
        // Se suman solo si el vehículo tiene marcado "has_arrived"
        const $hasArrived = $vehicle.find("input[type='checkbox'][name$='-has_arrived']");
        if (!$hasArrived.prop("checked")) {
            console.log("Vehículo", $vehicle.attr("id"), "no está marcado como 'has_arrived'. Se omite.");
            return;
        }
  
        $vehicle.find(CONTAINER_FORM_SELECTOR).each(function(i, containerForm) {
            const $container = $(containerForm);
            if ($container.find("input[name$='-DELETE']").prop("checked")) return;
            vehicleQuantity   += parseFloat($container.find("input[name$='-quantity']").first().val()) || 0;
            vehicleFullBoxes  += parseFloat($container.find("input[name$='-full_boxes']").first().val()) || 0;
            vehicleEmptyBoxes += parseFloat($container.find("input[name$='-empty_boxes']").first().val()) || 0;
            vehicleMissingBoxes += parseFloat($container.find("input[name$='-missing_boxes']").first().val()) || 0;
        });
  
        console.log("Totales para vehículo", $vehicle.attr("id"), "→ quantity:", vehicleQuantity,
                    ", full_boxes:", vehicleFullBoxes,
                    ", empty_boxes:", vehicleEmptyBoxes,
                    ", missing_boxes:", vehicleMissingBoxes);
    }
  
    // Función para actualizar totales globales
    function updateGlobalTotals() {
        let globalQuantity = 0, globalFullBoxes = 0, globalEmptyBoxes = 0, globalMissingBoxes = 0;
  
        $(VEHICLE_FORM_SELECTOR).each(function(i, vehicleForm) {
            const $vehicle = $(vehicleForm);
            if ($vehicle.find("input[type='checkbox'][name$='-has_arrived']").prop("checked")) {
                $vehicle.find(CONTAINER_FORM_SELECTOR).each(function(j, containerForm) {
                    const $container = $(containerForm);
                    if ($container.find("input[name$='-DELETE']").prop("checked")) return;
                    globalQuantity   += parseFloat($container.find("input[name$='-quantity']").first().val()) || 0;
                    globalFullBoxes  += parseFloat($container.find("input[name$='-full_boxes']").first().val()) || 0;
                    globalEmptyBoxes += parseFloat($container.find("input[name$='-empty_boxes']").first().val()) || 0;
                    globalMissingBoxes += parseFloat($container.find("input[name$='-missing_boxes']").first().val()) || 0;
                });
            }
        });
  
        console.log("Totales Globales → quantity:", globalQuantity,
                    ", full_boxes:", globalFullBoxes,
                    ", empty_boxes:", globalEmptyBoxes,
                    ", missing_boxes:", globalMissingBoxes);
    }
  
    // Inicializa los contenedores existentes
    $(CONTAINER_FORM_SELECTOR).each(function(i, containerForm) {
        initializeContainer(containerForm);
    });
  
    // Inicializa cada formulario de vehículo y configura listeners para su checkbox "has_arrived" y para delegar en sus contenedores
    $(VEHICLE_FORM_SELECTOR).each(function(i, vehicleForm) {
        const $vehicle = $(vehicleForm);
  
        $vehicle.find("input[type='checkbox'][name$='-has_arrived']").on("change", function() {
            updateVehicleTotals(vehicleForm);
            updateGlobalTotals();
        });
  
        // Delegación para inputs dentro de los contenedores del vehículo
        $vehicle.on("input change", CONTAINER_FORM_SELECTOR + " input", function() {
            updateVehicleTotals(vehicleForm);
            updateGlobalTotals();
        });
  
        if ($vehicle.find("input[type='checkbox'][name$='-has_arrived']").prop("checked")) {
            updateVehicleTotals(vehicleForm);
        }
    });
  
    // Escucha el evento formset:added para nuevos contenedores
    document.addEventListener("formset:added", function(event) {
        const formsetName = event.detail.formsetName;
        if (formsetName.includes("scheduleharvestcontainervehicle_set")) {
            initializeContainer(event.target);
            updateGlobalTotals();
            const $parentVehicle = $(event.target).closest(VEHICLE_FORM_SELECTOR);
            if ($parentVehicle.length) {
                updateVehicleTotals($parentVehicle);
            }
        }
    });
  
    // Listener delegado para detectar clic en enlaces de eliminación ("Remove") dentro de contenedores
    $(document).on("click", CONTAINER_FORM_SELECTOR + " a.inline-deletelink, " + CONTAINER_FORM_SELECTOR + " a.djn-remove-handler", function() {
        const $container = $(this).closest(CONTAINER_FORM_SELECTOR);
        console.log("Se detectó clic en enlace de eliminación en contenedor:", $container.attr("id"));
        setTimeout(() => {
            updateMissingBoxes($container);
            updateGlobalTotals();
            const $parentVehicle = $container.closest(VEHICLE_FORM_SELECTOR);
            if ($parentVehicle.length) {
                updateVehicleTotals($parentVehicle);
            }
        }, 200);
    });
  
    // Listener delegado para detectar cambios en checkboxes DELETE específicos de contenedores
    $(document).on("change", CONTAINER_FORM_SELECTOR + " input[name$='-DELETE']", function() {
        const $container = $(this).closest(CONTAINER_FORM_SELECTOR);
        console.log("Se cambió el estado del checkbox DELETE en contenedor:", $container.attr("id"), "nuevo valor:", this.checked);
        setTimeout(() => {
            updateMissingBoxes($container);
            updateGlobalTotals();
            const $parentVehicle = $container.closest(VEHICLE_FORM_SELECTOR);
            if ($parentVehicle.length) {
                updateVehicleTotals($parentVehicle);
            }
        }, 200);
    });
});

  
  
// document.addEventListener(
//     "click",
//     function (e) {
//       // Buscamos, en la fase de captura, si se hizo clic sobre alguno de estos enlaces:
//       const deletionLink = e.target.closest("a.inline-deletelink, a.djn-remove-handler");
//       if (deletionLink) {
//         console.log("Se detectó clic en enlace de eliminación:", deletionLink);
//         // Buscamos el vehículo padre (según el mismo selector que usas para vehículos)
//         const parentVehicle = deletionLink.closest(
//           'div[id^="scheduleharvest-0-scheduleharvestvehicle_set-"]:not([id*="group"], [id*="empty"])'
//         );
//         if (parentVehicle) {
//           console.log("Vehículo padre encontrado:", parentVehicle.id);
//         } else {
//           console.log("No se encontró vehículo padre.");
//         }
//         // Esperamos un breve retardo para que el DOM se actualice (por ejemplo, Django marque para eliminar)
//         setTimeout(function () {
//           if (parentVehicle) {
//             updateVehicleTotals(parentVehicle);
//           }
//           updateGlobalTotals();
//         }, 200);
//       }
//     },
//     true // El tercer parámetro 'true' indica que el listener se engancha en la fase de captura
//   );
  