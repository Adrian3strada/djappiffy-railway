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

    function handleProviderChange($provider, $crew, selectedCrew = null) {
        const providerId = $provider.val();
        if (providerId) {
            fetchOptions(`/rest/v1/catalogs/harvesting-crew/?provider=${providerId}`)
                .then(crews => updateFieldOptions($crew, crews, selectedCrew));
        } else {
            updateFieldOptions($crew, [], null);
        }
    }

    const WEIGHING_SET_FORM_SELECTOR = 'div[id*="weighingset_set-"]:not([id*="group"],[id*="empty"])';

    function initializeWeighingSet(form) {
        const $weighing_set = $(form);
        const $provider = $weighing_set.find('select[name$="-provider"]');
        const $crew = $weighing_set.find('select[name$="-harvesting_crew"]');
        const selCrew = $crew.val();

        if ($provider.val()) handleProviderChange($provider, $crew, selCrew);
        else updateFieldOptions($crew, [], null);

        $provider.on('change', () => handleProviderChange($provider, $crew, $crew.val()));
    }

    // Aplicar a todos los formularios actuales
    $(WEIGHING_SET_FORM_SELECTOR).each((i, f) => initializeWeighingSet(f));

    // Aplicar solo deshabilitado visual a campos computados
    $('input[name$="-total_containers"], input[name$="-container_tare"], input[name$="-net_weight"]').each(function() {
        disableField(this);
    });

    document.addEventListener('formset:added', e => {
        if (e.detail.formsetName.endsWith('weighingset_set')) {
            initializeWeighingSet(e.target);
        }
        $(e.target).find('input[name$="-total_containers"], input[name$="-container_tare"], input[name$="-net_weight"]').each(function() {
            disableField(this);
        });
    });
});
