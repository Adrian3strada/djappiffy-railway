document.addEventListener('DOMContentLoaded', () => {
  const disableField = field => {
    field.readOnly = true;
    field.style.pointerEvents = 'none';
    field.style.backgroundColor = '#e9ecef';
    field.style.border = 'none';
    field.style.color = '#555';
  };

  function fetchOptions(url) {
      return $.ajax({ url, method: 'GET', dataType: 'json' })
               .fail(err => console.error('Error fetching options:', err));
    }

    function updateFieldOptions($field, options, selected) {
        $field.empty();
        if (!$field.prop('multiple')) {
            $field.append(new Option('---------', '', true, false));
        }
        options.forEach(o => {
            $field.append(new Option(o.name, o.id, false, o.id == selected));
        });
        $field.val(selected);
    }

  const fetchContainerTare = async id => {
    if (!id) return 0;
    try {
      const res = await $.ajax({
        url: `/rest/v1/catalogs/supply/${id}/`,
        method: 'GET',
        timeout: 5000
      });
      const tara = parseFloat(res.kg_tare) || 0;
      return tara;
    } catch (err) {
      return 0;
    }
  };

  const calculateNetWeight = $form => {
    const gross = parseFloat($form.find('input[name$="-gross_weight"]').val()) || 0;
    const platform = parseFloat($form.find('input[name$="-platform_tare"]').val()) || 0;
    const container = parseFloat($form.find('input[name$="-container_tare"]').val()) || 0;

    const net = Math.trunc((gross - platform - container) * 1000) / 1000;
    $form.find('input[name$="-net_weight"]').val(net);
  };

  async function calculateWeighingSetTare($form) {
    const id = $form.attr('id');
    let totalTare = 0;
    let totalContainers = 0;

    const $containers = $form.find('tbody[id*="weighingsetcontainer_set-"]:not([id*="empty"])');

    for (let i = 0; i < $containers.length; i++) {
      const $container = $($containers[i]);
      if ($container.find('input[name$="-DELETE"]').prop('checked')) continue;

      const containerId = $container.find('select[name$="-harvest_container"]').val();
      const quantity = parseFloat($container.find('input[name$="-quantity"]').val()) || 0;

      if (containerId) {
        const tare = await fetchContainerTare(containerId);
        totalTare += quantity * tare;
        totalContainers += quantity;
      }
    }

    const truncatedTare = Math.trunc(totalTare * 1000) / 1000;
    $form.find('input[name$="-container_tare"]').val(truncatedTare);
    $form.find('input[name$="-total_containers"]').val(totalContainers);

    calculateNetWeight($form);  
  }

  function initializeWeighingSet(form) {
    const $weighing_set = $(form);
    const $provider = $weighing_set.find('select[name$="-provider"]');
    const $crew = $weighing_set.find('select[name$="-harvesting_crew"]');
    const selelectCrew = $crew.val();

    $weighing_set.on('input', 'input[name$="-quantity"]', () => {
      calculateWeighingSetTare($weighing_set);
    });

    $weighing_set.on('change', 'select[name$="-harvest_container"]', () => {
      calculateWeighingSetTare($weighing_set);
    });

    $weighing_set.on('input', 'input[name$="-gross_weight"], input[name$="-platform_tare"]', () => {
      calculateNetWeight($weighing_set);
    });

    calculateWeighingSetTare($weighing_set);
  }

  document.addEventListener('formset:added', e => {
    const name = e.detail.formsetName;
    const $form = $(e.target);
    const id = $form.attr('id') || '';


    if (id.includes('__prefix__') || id.includes('-empty')) {
      return;
    }

    if (name.endsWith('weighingset_set')) {
      initializeWeighingSet(e.target);
    }

    if (name.endsWith('weighingsetcontainer_set')) {
      const $parent = $form.closest('div[id*="weighingset_set-"]');
      calculateWeighingSetTare($parent);
    }

    // Deshabilitar campos calculados
    $form.find('input[name$="-total_containers"], input[name$="-container_tare"], input[name$="-net_weight"]').each(function () {
      disableField(this);
    });
    document.addEventListener('formset:added', e => {
      $(e.target).find('input[name$="-total_containers"], input[name$="-container_tare"]').each(function() {
        disableField(this);
      });
    });
  });

  // Ocultar los <span> con checkbox deshabilitados
  document.querySelectorAll('span.delete input[type="checkbox"][disabled]')
    .forEach(checkbox => checkbox.closest('span.delete').style.display = 'none');

  document.querySelectorAll('table.djn-items').forEach(table => {
    let deleteColumnIndex = null;
    let totalCheckboxes = 0;
    let disabledCheckboxes = 0;

    table.querySelectorAll('td.delete.djn-model-receiving-weighingsetcontainer')
      .forEach(td => {
        const checkbox = td.querySelector('input[type="checkbox"]');
        if (!checkbox) return;
        
        // Obtener el índice de la celda dentro del <tr>
        const cellIndex = [...td.closest('tr').children].indexOf(td);
        if (deleteColumnIndex === null) {
          deleteColumnIndex = cellIndex;
        }
        
        totalCheckboxes++;
        if (checkbox.disabled) {
          td.style.display = 'none';
          disabledCheckboxes++;
        }
      });

    // Si todos los checkboxes de la tabla están deshabilitados, ocultar su título
    if (totalCheckboxes && totalCheckboxes === disabledCheckboxes && deleteColumnIndex !== null) {
      const headerCell = table.querySelector(`thead th:nth-child(${deleteColumnIndex + 1})`);
      if (headerCell) headerCell.style.display = 'none';
    }
  });

  // Guarda las opciones originales de cada select existente de WeighingSet
  function storeOriginalOptions() {
      const selects = document.querySelectorAll(
          'select[id^="id_weighingset_set-"]:not([id*="__prefix__"])[id$="-harvesting_crew"]'
      );
      selects.forEach(select => {
          if (!select.dataset.originalOptions) {
              select.dataset.originalOptions = select.innerHTML;
          }
      });
  }

  // Restaura las opciones originales en un elemento select
  function restoreOriginalOptions(select) {
      if (select.dataset.originalOptions) {
          select.innerHTML = select.dataset.originalOptions;
      }
  }

  // Reinicializa Select2 para un elemento select, asegurando que se conserve el valor actual
  function reinitializeSelect2(selectElement, currentValue) {
      const $select = $(selectElement);

      if ($select.data('select2')) {
          $select.select2('destroy');
      }

      if (!$select.find('option[value=""]').length) {
          $select.prepend(new Option("---------", "", false, false));
      }
      $select.val(currentValue);
      $select.select2();
  }


  // Obtiene los IDs de cuadrillas actualmente programadas (excluyendo las marcadas para eliminación)
  function getScheduledCrewIds() {
      const selector = 'select[id^="id_scheduleharvest-"][id*="-scheduleharvestharvestingcrew_set-"]:not([id*="__prefix__"])[id$="-harvesting_crew"]';
      const selects = document.querySelectorAll(selector);
      const crewIds = [];
      selects.forEach(select => {
          const row = select.closest('tr');
          const deleteCheckbox = row?.querySelector('input[type="checkbox"][id$="DELETE"]');
          if (deleteCheckbox?.checked) return;
          const val = select.value;
          if (val) crewIds.push(val.trim());
      });
      return crewIds;
  }

  // Filtra las opciones de un select de WeighingSet según las cuadrillas permitidas, limpiando la selección si ya no es válida
  function filterSelectOptions(selectElement, allowedCrewIds) {
      if (!selectElement) return;
      const $select = $(selectElement);

      const currentValue = $select.val();

      restoreOriginalOptions(selectElement);

      $select.find('option').each(function () {
          const $option = $(this);
          const val = $option.attr('value');
          if (val !== "" && !allowedCrewIds.includes(val)) {
              $option.remove();
          }
      });

      const isStillValid = currentValue && $select.find(`option[value="${currentValue}"]`).length > 0;
      if (!isStillValid) {
          $select.val("");
      } else {
          $select.val(currentValue);
      }
      reinitializeSelect2(selectElement, $select.val());
  }

  // Aplica el filtrado a todos los selects de cuadrillas en WeighingSet
  function applyFiltering() {
      storeOriginalOptions();
      const allowedCrewIds = getScheduledCrewIds();
      const allSelects = document.querySelectorAll(
          'select[id^="id_weighingset_set-"]:not([id*="__prefix__"])[id$="-harvesting_crew"]'
      );
      allSelects.forEach(select => {
          filterSelectOptions(select, allowedCrewIds);
      });
  }

  // Maneja la lógica al agregar nuevos formularios inline de WeighingSet
  document.addEventListener('formset:added', function (event) {
      const newForm = event.detail?.form || event.target;
      if (!newForm) {
          console.warn("⚠️ formset:added event contains no form");
          return;
      }
      const select = newForm.querySelector('select[name$="-harvesting_crew"]');
      if (select && !select.dataset.originalOptions) {
          select.dataset.originalOptions = select.innerHTML;
      }
      setTimeout(() => {
          applyFiltering();
      }, 100);
  });

  // Dispara el filtrado ante cualquier cambio relevante en los campos del formulario
  document.addEventListener('change', function (event) {
      const element = event.target;
      if (
          element.matches('input[type="checkbox"][id$="DELETE"]') ||
          element.matches('select[id*="-harvesting_crew"]') ||
          element.matches('select[id*="-provider"]')
      ) {
          setTimeout(applyFiltering, 100);
      }
  });

  // Observa cambios en el DOM de los inlines de cuadrillas y activa el filtrado
  const crewInlineContainer = document.querySelector('[id$="-scheduleharvestharvestingcrew_set-group"]');
  if (crewInlineContainer) {
      const crewObserver = new MutationObserver(mutations => {
          let shouldUpdate = false;
          for (const mutation of mutations) {
              if (
                  (mutation.type === 'childList' && (mutation.addedNodes.length || mutation.removedNodes.length)) ||
                  (mutation.type === 'attributes' && (mutation.target.matches('select') || mutation.target.matches('input[type="checkbox"]')))
              ) {
                  shouldUpdate = true;
                  break;
              }
          }
          if (shouldUpdate) {
              setTimeout(applyFiltering, 100);
          }
      });
      crewObserver.observe(crewInlineContainer, {
          childList: true,
          subtree: true,
          attributes: true,
          attributeFilter: ['value', 'checked']
      });
  }

  // Aplica el filtrado inicial al cargar la página
  window.addEventListener("load", () => {
      setTimeout(applyFiltering, 100);
  });

  });