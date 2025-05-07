document.addEventListener("DOMContentLoaded", function() {
    /**
     * Funciona para cualquier nivel de inline anidado (nested inlines) y
     * sirve con cualquier modelo que utilice la misma convención de campos:
     *  - checkbox name$='-has_arrived'
     *  - campos guide_number y stamp_vehicle_number junto al mismo prefijo
     *  - contenedores como inline gathering-scheduleharvestcontainervehicle
     */

    // Selectores: inline directo o anidado
    const VEHICLE_FORM_SELECTOR = "div[id*='scheduleharvestvehicle_set-']:not([id*='group'], [id*='empty'])";
    const CONTAINER_FORM_SELECTOR = "tbody.djn-inline-form[data-inline-model='gathering-scheduleharvestcontainervehicle']:not([id*='empty'])";

    const containersAssignedField = $('#id_containers_assigned');
    const fullContainersField = $('#id_full_containers_per_harvest');
    const emptyContainersField = $('#id_empty_containers');
    const missingContainersField = $('#id_missing_containers');

    // 1) Ocultar botones de agregar/eliminar vehículo en cualquier nivel
    document.querySelectorAll(
        "a.djn-add-handler.djn-model-gathering-scheduleharvestvehicle,"
      + "span.djn-delete-handler.djn-model-gathering-scheduleharvestvehicle"
    ).forEach(el => {
        el.style.display = "none";
    });

    // 2) Mostrar/ocultar campos según checkbox has_arrived en cualquier inline
    $('input[name$="-has_arrived"]').each(function() {
        const $checkbox = $(this);
        const name = $checkbox.attr('name');
        const prefix = name.replace(/-has_arrived$/, '');
        const guideSelector = `input[name='${prefix}-guide_number']`;
        const stampSelector = `input[name='${prefix}-stamp_vehicle_number']`;
        const $guide = $(guideSelector).closest('.row.mb-3');
        const $stamp = $(stampSelector).closest('.row.mb-3');
        function toggleFields() {
            const checked = $checkbox.prop('checked');
            if (checked) {
                $guide.fadeIn();
                $stamp.fadeIn();
            } else {
                $guide.fadeOut();
                $stamp.fadeOut();
            }
        }
        toggleFields();
        $checkbox.on('change', () => {
            toggleFields();
            // Opcional: recalcular totales al cambiar visibilidad
            const $veh = $checkbox.closest(VEHICLE_FORM_SELECTOR);
            updateVehicleTotals($veh);
            updateGlobalTotals();
        });
    });
    
    const capacityCache = {};
    // Función para realizar una solicitud AJAX y obtener la capacidad de los contenedores
    function fetchContainerCapacity(containerId) {
        if (capacityCache.hasOwnProperty(containerId)) {
          return $.Deferred().resolve(capacityCache[containerId]).promise();
        }
        return $.ajax({
          url: `/rest/v1/catalogs/supply/`,
          method: 'GET',
          dataType: 'json',
          data: {
            id: containerId,    
            is_enabled: true
          }
        })
        .then(data => {
          capacityCache[containerId] = data;
          return data;
        })
        .fail(error => {
          console.error('Error al obtener la capacidad de los contenedores:', error);
          throw error;
        });
      }

    // Funcion de actualización de missing_containers
    function updateMissingBoxes(containerForm) {
        const $c = $(containerForm);
        const qty = parseFloat($c.find("input[name$='-quantity']").val()) || 0;
        const full = parseFloat($c.find("input[name$='-full_containers']").val()) || 0;
        const empty = parseFloat($c.find("input[name$='-empty_containers']").val()) || 0;
        const missing = qty - full - empty;
        $c.find("input[name$='-missing_containers']").val(missing);
    }

    // Configura contenedor para cálculos
    function initializeContainer(containerForm) {
        updateMissingBoxes(containerForm);
        $(containerForm).on("input change", "input[name$='-quantity'], input[name$='-full_containers'], input[name$='-empty_containers']", () => {
            updateMissingBoxes(containerForm);
            updateGlobalTotals();
            const $parent = $(containerForm).closest(VEHICLE_FORM_SELECTOR);
            updateVehicleTotals($parent);
        });
    }

    // Totales por vehículo
    function updateVehicleTotals($vehicle) {
        if (!$vehicle || !$vehicle.length) return;
        let qty=0, full=0, empty=0, miss=0;
        if (!$vehicle.find("input[name$='-has_arrived']").prop('checked')) {
            return;
        }
        $vehicle.find(CONTAINER_FORM_SELECTOR).each((_, cf) => {
            const $c = $(cf);
            if ($c.find("input[name$='-DELETE']").prop('checked')) return;
            qty += parseFloat($c.find("input[name$='-quantity']").val())||0;
            full += parseFloat($c.find("input[name$='-full_containers']").val())||0;
            empty += parseFloat($c.find("input[name$='-empty_containers']").val())||0;
            miss += parseFloat($c.find("input[name$='-missing_containers']").val())||0;
        });
    }

    // Totales globales
    function updateGlobalTotals() {
        let gQty = 0, gFull = 0, gEmpty = 0, gMiss = 0, sum = 0;
        const promises = [];
        
        // Recorrer todos los vehiculos sin importar si no han sido marcado como llegaron para saber el peso esperado
        $(VEHICLE_FORM_SELECTOR).each((_, vf) => {
          const $v = $(vf);
          $v.find(CONTAINER_FORM_SELECTOR).each((_, cf) => {
            const $c = $(cf);
            const Qty = parseInt($c.find("input[name$='-quantity']").val()) || 0;
            const id  = $c.find("select[name$='-harvest_container']").val();
            const p = fetchContainerCapacity(id).then(data => {
                const arr  = $.isArray(data) ? data : (data.results||[]);
                const cont = arr.find(item => String(item.id) === id);
                const w    = cont && cont.capacity!=null ? cont.capacity : 1;
                sum += w * Qty;
                })
                .fail(err => {
                console.error('Error fetching capacity for', id, err);
                sum += Qty; 
                });
        promises.push(p);
        $.when.apply($, promises).then(function() {
            const tr = Math.trunc(sum * 1000) / 1000;
            const [i, d = ''] = tr.toString().split('.');
            const val = i + '.' + (d + '000').slice(0, 3);
            
            $('input[id$="-weight_expected"]').each((_, input) => {
                const $f = $(input);
                $f.val(val);
              });

            });
        });  

          if (!$v.find("input[name$='-has_arrived']").prop("checked")) return;
          $v.find(CONTAINER_FORM_SELECTOR).each((_, cf) => {
            const $c = $(cf);
            if ($c.find("input[name$='-DELETE']").prop("checked")) return;
            const Qty = parseInt($c.find("input[name$='-quantity']").val()) || 0;
            gQty   += Qty;
            gFull  += parseFloat($c.find("input[name$='-full_containers']").val())  || 0;
            gEmpty += parseFloat($c.find("input[name$='-empty_containers']").val()) || 0;
            gMiss  += parseFloat($c.find("input[name$='-missing_containers']").val())|| 0;
            
          });
        });
        containersAssignedField.val(gQty);
        fullContainersField.val(gFull);
        emptyContainersField.val(gEmpty);
        missingContainersField.val(gMiss);
    }

    // Inicializar contenedores existentes
    $(CONTAINER_FORM_SELECTOR).each((_, cf) => initializeContainer(cf));

    // Nuevos contenedores
    document.addEventListener('formset:added', e => {
        if (e.detail.formsetName.includes('scheduleharvestcontainervehicle_set')) {
            initializeContainer(e.target);
            updateGlobalTotals();
            const $veh = $(e.target).closest(VEHICLE_FORM_SELECTOR);
            updateVehicleTotals($veh);
        }
    });

    // Observador para DELETE y remociones
    new MutationObserver(muts => muts.forEach(mut => {
        if (mut.type==='attributes' && mut.target.matches("input[name$='-DELETE']")) {
            const $c = $(mut.target).closest(CONTAINER_FORM_SELECTOR);
            setTimeout(() => { updateMissingBoxes($c); updateGlobalTotals(); updateVehicleTotals($c.closest(VEHICLE_FORM_SELECTOR)); },200);
        }
        if (mut.type==='childList' && mut.removedNodes.length) {
            Array.from(mut.removedNodes).forEach(node => {
                if (node.nodeType===1 && $(node).find('a.inline-deletelink').length) {
                    setTimeout(() => { updateGlobalTotals(); $(VEHICLE_FORM_SELECTOR).each((_, vf) => updateVehicleTotals($(vf))); },200);
                }
            });
        }
    })).observe(document.body, { attributes:true, childList:true, subtree:true });
});
