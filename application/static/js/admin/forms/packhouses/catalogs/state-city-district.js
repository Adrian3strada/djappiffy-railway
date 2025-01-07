document.addEventListener('DOMContentLoaded', () => {
  const API_BASE_URL = '/rest/v1';
  const fields = {
    state: $('#id_state'),
    city: $('#id_city'),
    district: $('#id_district')
  };

  const updateFieldOptions = (field, options) => {
    field.empty().append($('<option>', { text: '---------', selected: true }));
    options.forEach(option => field.append($('<option>', { text: option.name, value: option.id })));
    field.trigger('change').select2();
  };

  const fetchOptions = url => $.getJSON(url).fail(error => console.error('Fetch error:', error));

  const updateCity = () => {
    const stateId = fields.state.val();
    const url = stateId ? `${API_BASE_URL}/cities/subregion/?region=${stateId}` : null;
    url ? fetchOptions(url).then(data => updateFieldOptions(fields.city, data)) : updateFieldOptions(fields.city, []);
  };

  const updateDistrict = () => {
    const cityId = fields.city.val();
    const url = cityId ? `${API_BASE_URL}/cities/city/?subregion=${cityId}` : null;
    url ? fetchOptions(url).then(data => updateFieldOptions(fields.district, data)) : updateFieldOptions(fields.district, []);
  };

  fields.state.on('change', updateCity);
  fields.city.on('change', updateDistrict);

  Object.values(fields).forEach(field => field.select2());
});
