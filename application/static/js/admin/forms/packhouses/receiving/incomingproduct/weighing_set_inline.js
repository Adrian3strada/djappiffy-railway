document.addEventListener('DOMContentLoaded', () => {
  /**
   * Combined script for:
   *  - Counting active weighing sets (direct & nested)
   *  - Calculating tare, net weight, and packhouse total
   *  for inline and nested WeighingSet forms in IncomingProduct/Batch.
   */
  const DEL_SEL = 'input[name^="incomingproduct_set-0-weighingset_set-"][name$="-DELETE"]';
  const CNT_SEL = 'div[id^="incomingproduct_set-0-weighingset_set-"]';
  const TOTAL_ID = 'id_incomingproduct_set-0-total_weighed_sets';
  const observed = new WeakSet();

  const debounce = (fn, wait = 300) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn(...args), wait);
    };
  };

  function recalcWeighingSets() {
    const allSets = Array.from(document.querySelectorAll(CNT_SEL))
      .filter(el => /^\d+$/.test(el.id.split('-').pop())); // exclude "-empty"

    const activeCount = allSets.reduce((sum, el) => {
      const cb = el.querySelector(DEL_SEL);
      return sum + ((cb && cb.checked) ? 0 : 1);
    }, 0);

    const fld = document.getElementById(TOTAL_ID);
    if (fld) {
      fld.value = activeCount;
      fld.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  function observeCheckbox(cb) {
    if (observed.has(cb)) return;
    const mo = new MutationObserver(muts => {
      muts.forEach(m => {
        if (m.attributeName === 'checked') debounce(recalcWeighingSets)();
      });
    });
    mo.observe(cb, { attributes: true });
    observed.add(cb);
  }

  // init count
  recalcWeighingSets();
  document.querySelectorAll(DEL_SEL).forEach(observeCheckbox);
  document.addEventListener('change', e => {
    if (e.target.matches(DEL_SEL)) debounce(recalcWeighingSets)();
  });
  document.addEventListener('formset:added', e => {
    if (e.detail.formsetName.includes('weighingset_set')) {
      const cb = e.target.querySelector(DEL_SEL);
      if (cb) observeCheckbox(cb);
      recalcWeighingSets();
    }
  });
  document.addEventListener('formset:removed', debounce(recalcWeighingSets));

  // ---------- 2) Tare / Net weight / Packhouse total ----------
  const $packhouseField = $('#id_packhouse_weight_result');
  const $weighedSetField = $('#id_total_weighed_sets').add('input[name$="-total_weighed_sets"]');
  const $weighedContainerField = $('#id_total_weighed_set_containers');

  const WEIGHING_SET_FORM_SELECTOR = 'div[id*="weighingset_set-"]:not([id*="group"],[id*="empty"])';
  const CONTAINER_FORM_SELECTOR = 'tbody[id*="weighingsetcontainer_set-"]:not([id*="empty"])';

  const disableField = field => {
    field.readOnly = true;
    field.style.pointerEvents = 'none';
    field.style.backgroundColor = '#e9ecef';
    field.style.border = 'none';
    field.style.color = '#555';
  };

  const fetchContainerTare = async id => {
    if (!id) return 0;
    try {
      const res = await $.ajax({
        url: `/rest/v1/catalogs/supply/${id}/`,
        method: 'GET',
        timeout: 5000
      });
      return parseFloat(res.kg_tare) || 0;
    } catch {
      return 0;
    }
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

  function handleProviderChange($prov, $crew, selectedCrew = null) {
    const provId = $prov.val();
    if (provId) {
      fetchOptions(`/rest/v1/catalogs/harvesting-crew/?provider=${provId}`)
        .then(crews => updateFieldOptions($crew, crews, selectedCrew));
    } else {
      updateFieldOptions($crew, [], null);
    }
  }

  const updateWeighedSetCount = () => {
    const count = $(WEIGHING_SET_FORM_SELECTOR)
      .filter((i, el) => {
        const $el = $(el);
        const $del = $el.find('input[name$="-DELETE"]').filter(function() {
          return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
        });
        return !$del.prop('checked');
      }).length;
    $weighedSetField.val(count).trigger('change');
  };

  const calculateWeighingSetTare = async $form => {
    const $delSet = $form.find('input[name$="-DELETE"]').filter(function() {
      return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
    });
    if ($delSet.prop('checked')) return;

    let totalTare = 0;
    let totalContainers = 0;
    const $containers = $form.find(CONTAINER_FORM_SELECTOR);
    debouncedUpdateTotalContainers();

    for (let i = 0; i < $containers.length; i++) {
      const $c = $($containers[i]);
      const $delC = $c.find('input[name$="-DELETE"]');
        const delElem = $delC.get(0);

        if (delElem && !$delC.data('obs')) {
        const mo = new MutationObserver(muts => {
            muts.forEach(m => m.attributeName === 'checked' && calculateWeighingSetTare($form));
        });
        mo.observe(delElem, { attributes: true });
        $delC.data('obs', true);
        }

      if ($delC.prop('checked')) continue;

      const cid = $c.find('select[name$="-harvest_container"]').val();
      const qty = parseFloat($c.find('input[name$="-quantity"]').val()) || 0;
      if (cid) {
        totalTare += qty * await fetchContainerTare(cid);
        totalContainers += qty;
      }
    }

    const tT = Math.trunc(totalTare * 1000) / 1000;
    $form.find('input[name$="-container_tare"]').val(tT);
    $form.find('input[name$="-total_containers"]').val(totalContainers);
    updateNetWeight($form);
  };

  const updateNetWeight = $form => {
    const $del = $form.find('input[name$="-DELETE"]').filter(function() {
      return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
    });
    if ($del.prop('checked')) return;

    const gross    = parseFloat($form.find('input[name$="-gross_weight"]').val()) || 0;
    const platform = parseFloat($form.find('input[name$="-platform_tare"]').val())   || 0;
    const container= parseFloat($form.find('input[name$="-container_tare"]').val())  || 0;
    const net = Math.trunc((gross - platform - container) * 1000) / 1000;
    $form.find('input[name$="-net_weight"]').val(net);
    debouncedUpdatePackhouse();
  };

  const updatePackhouseWeight = () => {
    let total = 0, prefix = null;
    $(WEIGHING_SET_FORM_SELECTOR).each(function() {
      const $ws = $(this);
      if (!prefix) {
        const m = this.id.match(/^(.*)-weighingset_set-\d+$/);
        if (m) prefix = m[1];
      }
      const $del = $ws.find('input[name$="-DELETE"]').filter(function() {
        return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
      });
      if ($del.prop('checked')) return;
      total += parseFloat($ws.find('input[name$="-net_weight"]').val()) || 0;
    });
    const truncated = Math.trunc(total * 1000) / 1000;
    if ($packhouseField.length) {
      $packhouseField.val(truncated).trigger('change');
    } else if (prefix) {
      const $pf = $(`input[name="${prefix}-packhouse_weight_result"]`);
      if ($pf.length) $pf.val(truncated).trigger('change');
    }
  };
  const debouncedUpdatePackhouse = debounce(updatePackhouseWeight, 300);
  const updateTotalFullContainers = () => {
    let total = 0;
    $(WEIGHING_SET_FORM_SELECTOR).each(function() {
      const $ws = $(this);
      const $del = $ws.find('input[name$="-DELETE"]').filter(function() {
        return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
      });
      if ($del.prop('checked')) return;
      $ws.find(CONTAINER_FORM_SELECTOR).each(function() {
        const $c = $(this);
        if (!$c.find('input[name$="-DELETE"]').prop('checked')) {
          total += parseFloat($c.find('input[name$="-quantity"]').val()) || 0;
        }
      });
    });
    $weighedContainerField.val(total);
  };
  const debouncedUpdateTotalContainers = debounce(updateTotalFullContainers, 300);

  function initializeWeighingSet(form) {
    const $ws = $(form);
    const $prov = $ws.find('select[name$="-provider"]');
    const $crew = $ws.find('select[name$="-harvesting_crew"]');
    const selCrew = $crew.val();

    if ($prov.val()) handleProviderChange($prov, $crew, selCrew);
    else updateFieldOptions($crew, [], null);
    $prov.on('change', () => handleProviderChange($prov, $crew, $crew.val()));

    // observe delete on weighing set
    const $delSet = $ws.find('input[name$="-DELETE"]').filter(function() {
      return $(this).closest(CONTAINER_FORM_SELECTOR).length === 0;
    });
    if ($delSet.length) {
      const mo = new MutationObserver(muts => muts.forEach(m => {
        if (m.attributeName==='checked') {
          debouncedUpdatePackhouse();
          updateWeighedSetCount();
        }
      }));
      mo.observe($delSet[0], { attributes: true });
    }

    // observe container removal
    if (!$ws.data('childObs')) {
      const childObs = new MutationObserver(muts => muts.forEach(m => {
        m.removedNodes && m.removedNodes.forEach(node => {
          if ($(node).is(CONTAINER_FORM_SELECTOR)) calculateWeighingSetTare($ws);
        });
      }));
      childObs.observe(form, { childList: true, subtree: true });
      $ws.data('childObs', true);
    }

    const debTare = debounce(() => calculateWeighingSetTare($ws), 300);
    $ws.off('input').on('input', 'input[name$="-gross_weight"], input[name$="-platform_tare"], input[name$="-quantity"]', debTare);
    $ws.off('change').on('change', 'select[name$="-harvest_container"]', debTare);

    // initial calc
    calculateWeighingSetTare($ws);
    updateWeighedSetCount();
  }

  // initialize existing weighing sets
  $(WEIGHING_SET_FORM_SELECTOR).each((i, f) => initializeWeighingSet(f));

  // handle dynamic formset additions/removals
  document.addEventListener('formset:added', e => {
    const name = e.detail.formsetName;
    if (name.endsWith('weighingset_set')) initializeWeighingSet(e.target);
    if (name.endsWith('weighingsetcontainer_set')) {
      const $ws = $(e.target).closest(WEIGHING_SET_FORM_SELECTOR);
      debounce(() => calculateWeighingSetTare($ws), 300)();
    }
    updateWeighedSetCount();
    debouncedUpdateTotalContainers();
    debouncedUpdatePackhouse();
  });
  document.addEventListener('formset:removed', () => {
    updateWeighedSetCount();
    debouncedUpdateTotalContainers();
    debouncedUpdatePackhouse();
  });

  // delete‑link buttons
  $(document).on('click', '.deletelink', function() {
    const $ws = $(this).closest(WEIGHING_SET_FORM_SELECTOR);
    setTimeout(() => {
      calculateWeighingSetTare($ws);
      updateWeighedSetCount();
    }, 100);
  });
  $(document).on('click', `${CONTAINER_FORM_SELECTOR} .deletelink`, function() {
    const $ws = $(this).closest(WEIGHING_SET_FORM_SELECTOR);
    setTimeout(() => calculateWeighingSetTare($ws), 100);
  });
  $(document).on('change', `${CONTAINER_FORM_SELECTOR} input[name$="-DELETE"]`, function() {
    const $ws = $(this).closest(WEIGHING_SET_FORM_SELECTOR);
    calculateWeighingSetTare($ws);
  });

  // disable computed fields
  $('input[name$="-total_containers"], input[name$="-container_tare"]').each(function() {
    disableField(this);
  });
  document.addEventListener('formset:added', e => {
    $(e.target).find('input[name$="-total_containers"], input[name$="-container_tare"]').each(function() {
      disableField(this);
    });
  });
});
