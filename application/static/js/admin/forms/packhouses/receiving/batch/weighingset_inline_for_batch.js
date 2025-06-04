document.addEventListener('DOMContentLoaded', () => {
    
    function getScheduledCrewIds() {
    const selector = 'select[id^="id_incomingproduct-"][id*="scheduleharvestharvestingcrew_set-"][id$="-harvesting_crew"]:not([id*="__prefix__"])';
    const selects = document.querySelectorAll(selector);
    const crewIds = [];

    selects.forEach(select => {
        const row = select.closest('tr');
        const deleteCheckbox = row?.querySelector('input[type="checkbox"][id$="DELETE"]');
        if (deleteCheckbox?.checked) return;
        if (select.value) crewIds.push(select.value.trim());
    });

    return crewIds;
}

function restoreOriginalOptions(select) {
    if (select.dataset.originalOptions) {
        select.innerHTML = select.dataset.originalOptions;
    }
}

function reinitializeSelect2(selectElement, currentValue) {
    const $select = $(selectElement);
    if ($select.data('select2')) $select.select2('destroy');
    if (!$select.find('option[value=""]').length) {
        $select.prepend(new Option("---------", "", false, false));
    }
    $select.val(currentValue);
    $select.select2();
}

function filterWeighingSetOptions(allowedCrewIds) {
    const selector = 'select[id^="id_incomingproduct-"][id*="weighingset_set-"][id$="-harvesting_crew"]:not([id*="__prefix__"])';
    const selects = document.querySelectorAll(selector);

    selects.forEach(select => {
        const $select = $(select);
        const currentValue = $select.val();

        if (!select.dataset.originalOptions) {
            select.dataset.originalOptions = select.innerHTML;
        }

        restoreOriginalOptions(select);

        $select.find('option').each(function () {
            const val = this.value;
            if (val !== "" && !allowedCrewIds.includes(val)) {
                $(this).remove();
            }
        });

        const isValid = currentValue && $select.find(`option[value="${currentValue}"]`).length > 0;
        $select.val(isValid ? currentValue : "");
        reinitializeSelect2(select, $select.val());
    });
}

function applyFiltering() {
    const crewIds = getScheduledCrewIds();
    filterWeighingSetOptions(crewIds);
}

document.addEventListener('formset:added', () => {
    setTimeout(applyFiltering, 100);
});

document.addEventListener('change', function (e) {
    const el = e.target;
    if (
        el.matches('input[type="checkbox"][id$="DELETE"]') ||
        el.matches('select[id$="-harvesting_crew"]') ||
        el.matches('select[id$="-provider"]')
    ) {
        setTimeout(applyFiltering, 100);
    }
});

window.addEventListener('load', () => {
    setTimeout(applyFiltering, 100);

    // Observa los contenedores de cuadrillas para detectar cambios
    const crewGroups = document.querySelectorAll('[id$="-scheduleharvestharvestingcrew_set-group"]');
    crewGroups.forEach(group => {
        const observer = new MutationObserver(() => {
            setTimeout(applyFiltering, 100);
        });

        observer.observe(group, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['value', 'checked']
        });
    });
});

  });