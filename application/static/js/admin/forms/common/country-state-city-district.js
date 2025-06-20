// descomentar  consoles de depueración en desarrollo
// console.log('✅ Script country-state-city-district.js cargado');

const API_BASE_URL = '/rest/v1/cities';

function fetchOptions(url) {
  return $.ajax({
    url: url,
    method: 'GET',
    dataType: 'json'
  }).fail(error => console.error('❌ Fetch error:', error));
}

function updateFieldOptions($field, options) {
  const currentVal = $field.val();
  // const fieldId = $field.attr('id');
  // vconsole.log(`🧪 ${fieldId} => valor actual:`, currentVal || '<empty string>');

  $field.empty().append(new Option('---------', '', true, true));

  options.forEach(option => {
    const selected = currentVal && String(currentVal) === String(option.id);
    const newOption = new Option(option.name, option.id, selected, selected);
    $field.append(newOption);
  });

  if (currentVal) {
    $field.val(currentVal);
  }

  if ($field.hasClass('select2-hidden-accessible')) {
    $field.trigger('change.select2').trigger('input');
  } else {
    $field.trigger('change').trigger('input');
  }
}

function getFieldId(baseId, suffix) {
  return baseId.replace(/-country|-state|-city|-district/, `-${suffix}`);
}

function bindEventsToInline($country) {
  const baseId = $country.attr('id');
  // console.log('🔧 bindEventsToInline con ID base:', baseId);

  const ids = {
    state: getFieldId(baseId, 'state'),
    city: getFieldId(baseId, 'city'),
    district: getFieldId(baseId, 'district')
  };

  // console.log('🔍 Field IDs: ', ids);

  const $state = $(`#${ids.state}`);
  const $city = $(`#${ids.city}`);
  const $district = $(`#${ids.district}`);

  if (!$state.length || !$city.length || !$district.length) {
    // console.warn('⚠️ Campo no encontrado o undefined:', ids);
    return;
  }

  $country.off('change').on('change', function () {
    const countryId = $(this).val();
    // console.log('🌍 País seleccionado:', countryId);

    if (!countryId) {
      updateFieldOptions($state, []);
      updateFieldOptions($city, []);
      updateFieldOptions($district, []);
      return;
    }

    fetchOptions(`${API_BASE_URL}/region/?country=${countryId}`)
      .done(data => {
        updateFieldOptions($state, data);
        updateFieldOptions($city, []);
        updateFieldOptions($district, []);
      });
  });

  $state.off('change').on('change', function () {
    const stateId = $(this).val();
    // console.log('🗺️ Estado seleccionado:', stateId);

    if (!stateId) {
      updateFieldOptions($city, []);
      updateFieldOptions($district, []);
      return;
    }

    fetchOptions(`${API_BASE_URL}/subregion/?region=${stateId}`)
      .done(data => {
        updateFieldOptions($city, data);
        updateFieldOptions($district, []);
      });
  });

  $city.off('change').on('change', function () {
    const cityId = $(this).val();
    // console.log('🏙️ Ciudad seleccionada:', cityId);

    if (!cityId) {
      updateFieldOptions($district, []);
      return;
    }

    fetchOptions(`${API_BASE_URL}/city/?subregion=${cityId}`)
      .done(data => {
        updateFieldOptions($district, data);
      });
  });

  // Carga inicial para edición
  const countryId = $country.val();
  const stateId = $state.val();
  const cityId = $city.val();
  const districtId = $district.val();

  if (countryId) {
    fetchOptions(`${API_BASE_URL}/region/?country=${countryId}`)
      .done(data => updateFieldOptions($state, data));
  }

  if (stateId) {
    fetchOptions(`${API_BASE_URL}/subregion/?region=${stateId}`)
      .done(data => updateFieldOptions($city, data));
  }

  if (cityId) {
    fetchOptions(`${API_BASE_URL}/city/?subregion=${cityId}`)
      .done(data => updateFieldOptions($district, data));
  }
}

function initAllInlines() {
  // console.log('🔁 Inicializando todos los inlines existentes...');
  $('select[id$="-country"]').each(function () {
    bindEventsToInline($(this));
  });
}

function handleNewInline(event) {
  const $inline = $(event.target);
  const $country = $inline.find('select[id$="-country"]');
  if ($country.length) {
    // console.log('➕ Nuevo inline agregado, enlazando eventos...');
    bindEventsToInline($country);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAllInlines);
}
else {
  initAllInlines();
}

document.addEventListener('formset:added', handleNewInline);

// Log para verificar que los valores se mandan correctamente al guardar
// $(document).on('submit', 'form', function () {
// console.log('🧾 Enviando formulario. Valores actuales:');
//  $('select').each(function () {
//  console.log(this.id, '=>', $(this).val());
// });
// alert('¿Listo?');
// });
