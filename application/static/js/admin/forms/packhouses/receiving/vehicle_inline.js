document.addEventListener("DOMContentLoaded", function() {
    // Selectores: ajusta estos selectores según la estructura real del HTML generado por Django admin
    const SCHEDULEHARVEST_FORM_SELECTOR = 'div[id^="scheduleharvest-0"]';
    const VEHICLE_FORM_SELECTOR = SCHEDULEHARVEST_FORM_SELECTOR + ' div[id^="scheduleharvest-0-scheduleharvestvehicle_set-"]:not([id*="group"], [id*="empty"])';
    const CONTAINER_FORM_SELECTOR = "tbody.djn-inline-form[data-inline-model='gathering-scheduleharvestcontainervehicle']:not([id*='empty'])";

    // (Opcional) Ocultar botones de agregar/eliminar vehículo en el inline de ScheduleHarvest
    document.querySelectorAll(SCHEDULEHARVEST_FORM_SELECTOR + " #scheduleharvest-0-scheduleharvestvehicle_set-group a.djn-add-handler.djn-model-gathering-scheduleharvestvehicle")
        .forEach(button => { button.style.display = "none"; });
    document.querySelectorAll(SCHEDULEHARVEST_FORM_SELECTOR + " #scheduleharvest-0-scheduleharvestvehicle_set-group span.djn-delete-handler.djn-model-gathering-scheduleharvestvehicle")
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
        const quantity = parseFloat($container.find("input[name$='-quantity']").first().val()) || 0;
        const fullBoxes = parseFloat($container.find("input[name$='-full_boxes']").first().val()) || 0;
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
            // Actualiza el inline padre (ScheduleHarvest)
            const $parentSchedule = $container.closest(SCHEDULEHARVEST_FORM_SELECTOR);
            if ($parentSchedule.length) {
                updateParentInlineTotals($parentSchedule);
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
            const $parentSchedule = $container.closest(SCHEDULEHARVEST_FORM_SELECTOR);
            if ($parentSchedule.length) {
                updateParentInlineTotals($parentSchedule);
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
            vehicleQuantity += parseFloat($container.find("input[name$='-quantity']").first().val()) || 0;
            vehicleFullBoxes += parseFloat($container.find("input[name$='-full_boxes']").first().val()) || 0;
            vehicleEmptyBoxes += parseFloat($container.find("input[name$='-empty_boxes']").first().val()) || 0;
            vehicleMissingBoxes += parseFloat($container.find("input[name$='-missing_boxes']").first().val()) || 0;
        });
        console.log("Totales para vehículo", $vehicle.attr("id"), "→ quantity:", vehicleQuantity, ", full_boxes:", vehicleFullBoxes, ", empty_boxes:", vehicleEmptyBoxes, ", missing_boxes:", vehicleMissingBoxes);
    }

    // Función para actualizar totales globales (en todos los vehículos)
    function updateGlobalTotals() {
        let globalQuantity = 0, globalFullBoxes = 0, globalEmptyBoxes = 0, globalMissingBoxes = 0;
        $(VEHICLE_FORM_SELECTOR).each(function(i, vehicleForm) {
            const $vehicle = $(vehicleForm);
            if ($vehicle.find("input[type='checkbox'][name$='-has_arrived']").prop("checked")) {
                $vehicle.find(CONTAINER_FORM_SELECTOR).each(function(j, containerForm) {
                    const $container = $(containerForm);
                    if ($container.find("input[name$='-DELETE']").prop("checked")) return;
                    globalQuantity += parseFloat($container.find("input[name$='-quantity']").first().val()) || 0;
                    globalFullBoxes += parseFloat($container.find("input[name$='-full_boxes']").first().val()) || 0;
                    globalEmptyBoxes += parseFloat($container.find("input[name$='-empty_boxes']").first().val()) || 0;
                    globalMissingBoxes += parseFloat($container.find("input[name$='-missing_boxes']").first().val()) || 0;
                });
            }
        });
        console.log("Totales Globales → quantity:", globalQuantity, ", full_boxes:", globalFullBoxes, ", empty_boxes:", globalEmptyBoxes, ", missing_boxes:", globalMissingBoxes);
    }

    // Función para actualizar totales en el inline padre (por ejemplo, ScheduleHarvest)
    function updateParentInlineTotals(scheduleForm) {
        let parentQuantity = 0, parentFullBoxes = 0, parentEmptyBoxes = 0, parentMissingBoxes = 0;
        $(scheduleForm).find(VEHICLE_FORM_SELECTOR).each(function(i, vehicleForm) {
            const $vehicle = $(vehicleForm);
            if ($vehicle.find("input[type='checkbox'][name$='-has_arrived']").prop("checked")) {
                $vehicle.find(CONTAINER_FORM_SELECTOR).each(function(j, containerForm) {
                    const $container = $(containerForm);
                    if ($container.find("input[name$='-DELETE']").prop("checked")) return;
                    parentQuantity += parseFloat($container.find("input[name$='-quantity']").first().val()) || 0;
                    parentFullBoxes += parseFloat($container.find("input[name$='-full_boxes']").first().val()) || 0;
                    parentEmptyBoxes += parseFloat($container.find("input[name$='-empty_boxes']").first().val()) || 0;
                    parentMissingBoxes += parseFloat($container.find("input[name$='-missing_boxes']").first().val()) || 0;
                });
            }
        });
        console.log("Totales del inline padre (ScheduleHarvest) → quantity:", parentQuantity, ", full_boxes:", parentFullBoxes, ", empty_boxes:", parentEmptyBoxes, ", missing_boxes:", parentMissingBoxes);
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
            const $parentSchedule = $vehicle.closest(SCHEDULEHARVEST_FORM_SELECTOR);
            if ($parentSchedule.length) {
                updateParentInlineTotals($parentSchedule);
            }
        });
        $vehicle.on("input change", CONTAINER_FORM_SELECTOR + " input", function() {
            updateVehicleTotals(vehicleForm);
            updateGlobalTotals();
            const $parentSchedule = $vehicle.closest(SCHEDULEHARVEST_FORM_SELECTOR);
            if ($parentSchedule.length) {
                updateParentInlineTotals($parentSchedule);
            }
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
            const $parentSchedule = $(event.target).closest(SCHEDULEHARVEST_FORM_SELECTOR);
            if ($parentSchedule.length) {
                updateParentInlineTotals($parentSchedule);
            }
        }
    });

    /* 
      --- MULTIOBSERVADOR GLOBAL PARA DETECTAR CAMBIOS EN ELEMENTOS DE LOS CONTENEDORES ---
      Se utiliza un MutationObserver para detectar:
         - Cambios en atributos (por ejemplo, cuando se marca/desmarca el checkbox DELETE).
         - Eliminación de nodos (cuando se remueve el contenedor vía enlace "Remove").
    */
    const globalObserver = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            // Si es cambio de atributo en un checkbox DELETE:
            if (mutation.type === "attributes" && mutation.target.matches("input[name$='-DELETE']")) {
                console.log("Mutation detectada en checkbox DELETE:", mutation.target);
                const $container = $(mutation.target).closest(CONTAINER_FORM_SELECTOR);
                // Se retrasa la actualización para dar tiempo a que se aplique el cambio
                setTimeout(() => {
                    updateMissingBoxes($container);
                    updateGlobalTotals();
                    const $parentVehicle = $container.closest(VEHICLE_FORM_SELECTOR);
                    if ($parentVehicle.length) {
                        updateVehicleTotals($parentVehicle);
                    }
                    const $parentSchedule = $container.closest(SCHEDULEHARVEST_FORM_SELECTOR);
                    if ($parentSchedule.length) {
                        updateParentInlineTotals($parentSchedule);
                    }
                }, 200);
            }
            // Si se detecta eliminación de nodos (childList) que contenga el enlace "Remove"
            if (mutation.type === "childList" && mutation.removedNodes.length > 0) {
                mutation.removedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const $node = $(node);
                        // Verifica si el nodo removido contiene un enlace con la clase del delete
                        if ($node.find("a.inline-deletelink.djn-remove-handler.djn-level-3").length) {
                            console.log("Nodo removido que contiene enlace de eliminación detectado.");
                            // Se actualizan totales globales y de vehículo/inline padre
                            setTimeout(() => {
                                updateGlobalTotals();
                                // Recorre cada vehículo para actualizar
                                $(VEHICLE_FORM_SELECTOR).each(function(i, vehicleForm) {
                                    updateVehicleTotals(vehicleForm);
                                });
                                $(SCHEDULEHARVEST_FORM_SELECTOR).each(function(i, scheduleForm) {
                                    updateParentInlineTotals(scheduleForm);
                                });
                            }, 200);
                        }
                    }
                });
            }
        });
    });

    // Observa cambios a nivel de documento para atributos y modificaciones en el árbol DOM
    globalObserver.observe(document.body, { attributes: true, childList: true, subtree: true });
});
