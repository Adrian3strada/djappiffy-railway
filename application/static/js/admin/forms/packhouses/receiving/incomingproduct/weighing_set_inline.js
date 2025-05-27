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

  const handleProviderChange = ($provider, $crew, selectedCrew = null) => {
    const providerId = $provider.val();

    if (providerId) {
      const url = `/rest/v1/catalogs/harvesting-crew/?provider=${providerId}`;
      fetchOptions(url).then(crews => {
        updateFieldOptions($crew, crews, selectedCrew);
      });
    } else {
      updateFieldOptions($crew, [], null);
    }
  };

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

    if ($provider.val()) {
      handleProviderChange($provider, $crew, selelectCrew);
    } else {
      updateFieldOptions($crew, [], null);
    }

    $provider.on('change', () => handleProviderChange($provider, $crew));

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

  });