document.addEventListener("DOMContentLoaded", function() {
    // Selectores: ajusta estos selectores según la estructura real del HTML generado por Django admin
    const SCHEDULEHARVEST_FORM_SELECTOR = 'div[id^="scheduleharvest-0"]';
    const VEHICLE_FORM_SELECTOR = SCHEDULEHARVEST_FORM_SELECTOR + ' div[id^="scheduleharvest-0-scheduleharvestvehicle_set-"]:not([id*="group"], [id*="empty"])';
    const CONTAINER_FORM_SELECTOR = "tbody.djn-inline-form[data-inline-model='gathering-scheduleharvestcontainervehicle']:not([id*='empty'])";

    const containersAssignedField = $('#id_containers_assigned');
    const fullContainersField = $('#id_full_containers_per_harvest');
    const emptyContainersField = $('#id_empty_containers');
    const missingContainersField = $('#id_missing_containers');

    // Ocultar botones de agregar/eliminar vehículo en el inline de ScheduleHarvest
    document.querySelectorAll(SCHEDULEHARVEST_FORM_SELECTOR + " #scheduleharvest-0-scheduleharvestvehicle_set-group a.djn-add-handler.djn-model-gathering-scheduleharvestvehicle")
        .forEach(button => { button.style.display = "none"; });
    document.querySelectorAll(SCHEDULEHARVEST_FORM_SELECTOR + " #scheduleharvest-0-scheduleharvestvehicle_set-group span.djn-delete-handler.djn-model-gathering-scheduleharvestvehicle")
        .forEach(element => { element.style.display = "none"; });

    // Función para actualizar missing_boxes en un contenedor
    function updateMissingBoxes(containerForm) {
        const $container = $(containerForm);
        const quantity = parseFloat($container.find("input[name$='-quantity']").val()) || 0;
        const fullBoxes = parseFloat($container.find("input[name$='-full_containers']").val()) || 0;
        const emptyBoxes = parseFloat($container.find("input[name$='-empty_containers']").val()) || 0;
        const missingBoxes = quantity - fullBoxes - emptyBoxes;
        $container.find("input[name$='-missing_containers']").val(missingBoxes);
    }

    // Inicializa un contenedor: agrega listeners para inputs y checkbox DELETE
    function initializeContainer(containerForm, aux) {
        const $container = $(containerForm);
        updateMissingBoxes(containerForm);
        if (aux === true){
            // hacer campos no editables pero que no cause conflicto al guardar los valores
            $container.find("select[name$='-harvest_container']").each(function() {
                const $select = $(this);
                const selectedValue = $select.val(); // Obtiene el valor seleccionado
                
                $select.prop("disabled", true);
                // Agrega un campo oculto con el mismo nombre y valor
                $("<input>")
                    .attr("type", "hidden")
                    .attr("name", $select.attr("name"))
                    .val(selectedValue)
                    .appendTo($container);
            });
            $container.find('input[name$="-quantity"]').each(function() {
                const $input = $(this);  
                $input.prop("readonly", true);  
                $input.css({
                    "pointer-events": "none", 
                    "background-color": "#e9ecef", 
                    "border": "none",  
                    "color": "#555"  
                });
            });
        }
        $container.on("input change", "input[name$='-quantity'], input[name$='-full_containers'], input[name$='-empty_containers']", function() {
            updateMissingBoxes(containerForm);
            updateGlobalTotals();
            // Actualiza el vehículo padre
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
            return;
        }
        $vehicle.find(CONTAINER_FORM_SELECTOR).each(function(i, containerForm) {
            const $container = $(containerForm);
            if ($container.find("input[name$='-DELETE']").prop("checked")) return;
            vehicleQuantity += parseFloat($container.find("input[name$='-quantity']").val()) || 0;
            vehicleFullBoxes += parseFloat($container.find("input[name$='-full_containers']").val()) || 0;
            vehicleEmptyBoxes += parseFloat($container.find("input[name$='-empty_containers']").val()) || 0;
            vehicleMissingBoxes += parseFloat($container.find("input[name$='-missing_containers']").val()) || 0;
        });
        
    }

    // Función para actualizar totales globales (en todos los vehículos)
    function updateGlobalTotals() {
        let globalQuantity = 0, globalFullContainers = 0, globalEmptyContainers = 0, globalMissingContainers = 0;
        $(VEHICLE_FORM_SELECTOR).each(function(i, vehicleForm) {
            const $vehicle = $(vehicleForm);
            if ($vehicle.find("input[type='checkbox'][name$='-has_arrived']").prop("checked")) {
                $vehicle.find(CONTAINER_FORM_SELECTOR).each(function(j, containerForm) {
                    const $container = $(containerForm);
                    if ($container.find("input[name$='-DELETE']").prop("checked")) return;
                    globalQuantity += parseFloat($container.find("input[name$='-quantity']").val()) || 0;
                    globalFullContainers += parseFloat($container.find("input[name$='-full_containers']").val()) || 0;
                    globalEmptyContainers += parseFloat($container.find("input[name$='-empty_containers']").val()) || 0;
                    globalMissingContainers += parseFloat($container.find("input[name$='-missing_containers']").val()) || 0;
                });
            }
            containersAssignedField.val(globalQuantity);
            fullContainersField.val(globalFullContainers);
            emptyContainersField.val(globalEmptyContainers);
            missingContainersField.val(globalMissingContainers);
        });
        
    }


    // Inicializa los contenedores existentes
    $(CONTAINER_FORM_SELECTOR).each(function(i, containerForm) {
        initializeContainer(containerForm, true);
    });


    // Inicializa cada formulario de vehículo y configura listeners para su checkbox "has_arrived"
    $(VEHICLE_FORM_SELECTOR).each(function(i, vehicleForm) {
        const $vehicle = $(vehicleForm);
        const hasArrivedField = $(vehicleForm).find('input[name$="-has_arrived"]');
        const guideNumberField = $(vehicleForm).find('input[name$="-guide_number"]');
        const stampVehicleNumberField = $(vehicleForm).find('input[name$="-stamp_vehicle_number"]');

        const guideNumberWrapper = guideNumberField.closest('.row');
        const stampVehicleWrapper = stampVehicleNumberField.closest('.row');

        // Buscar el siguiente .row después del campo guide_number para mensajes de error
        const guideNumberErrorRow = guideNumberWrapper.next('.row');
        const stampVehicleErrorRow = stampVehicleWrapper.next('.row');

        guideNumberWrapper.hide();
        stampVehicleWrapper.hide();

        if (hasArrivedField.prop('checked')) {
            guideNumberWrapper.show();
            stampVehicleWrapper.show();
        }    

        hasArrivedField.on('change', () => {
            const isChecked = hasArrivedField.prop('checked');
            if (isChecked === true) {
                guideNumberWrapper.fadeIn();
                stampVehicleWrapper.fadeIn();
                guideNumberErrorRow.fadeIn();
                stampVehicleErrorRow.fadeIn();
            } else {
                guideNumberWrapper.fadeOut();
                stampVehicleWrapper.fadeOut();
                guideNumberErrorRow.fadeOut();
                stampVehicleErrorRow.fadeOut();
            }
        });

        $vehicle.find("input[type='checkbox'][name$='-has_arrived']").on("change", function() {
            updateVehicleTotals(vehicleForm);
            updateGlobalTotals();
        });
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
            initializeContainer(event.target, null);
            updateGlobalTotals();
            const $parentVehicle = $(event.target).closest(VEHICLE_FORM_SELECTOR);
            if ($parentVehicle.length) {
                updateVehicleTotals($parentVehicle);
            }
        }
    });

    const globalObserver = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            // Si es cambio de atributo en un checkbox DELETE:
            if (
                mutation.type === "attributes" &&
                mutation.target.matches("input[name$='-DELETE']") &&
                !mutation.target.getAttribute("name").includes("crew")
              ) {
                const $container = $(mutation.target).closest(CONTAINER_FORM_SELECTOR);
                setTimeout(() => {
                  updateMissingBoxes($container);
                  updateGlobalTotals();
                  const $parentVehicle = $container.closest(VEHICLE_FORM_SELECTOR);
                  if ($parentVehicle.length) {
                    updateVehicleTotals($parentVehicle);
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
                            setTimeout(() => {
                                updateGlobalTotals();
                                // Recorre cada vehículo para actualizar
                                $(VEHICLE_FORM_SELECTOR).each(function(i, vehicleForm) {
                                    updateVehicleTotals(vehicleForm);
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
