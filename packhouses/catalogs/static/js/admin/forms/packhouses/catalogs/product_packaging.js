document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const marketsField = $('#id_markets');
  const packagingSupplyKindField = $('#id_packaging_supply_kind');
  const packagingSupplyField = $('#id_packaging_supply');
  const nameField = $('#id_name');

  let productProperties = null;
  let marketsCountries = [];

  const API_BASE_URL = '/rest/v1';

  function updateFieldOptions(field, options) {
    field.empty().append(new Option('---------', '', true, true));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, false, false));
    });
    field.trigger('change').select2();
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: 'GET',
      dataType: 'json'
    }).fail(error => console.error('Fetch error:', error));
  }

  function getProductProperties() {
    if (productField.val()) {
      fetchOptions(`/rest/v1/catalogs/product/${productField.val()}/`)
        .then(data => {
          productProperties = data;
          console.log("productProperties", productProperties)
          const maxProductAmountLabel = $('label[for="id_max_product_amount_per_package"]');
          console.log("maxProductAmountLabel", maxProductAmountLabel)
          if (data.price_measure_unit_category_display) {
            maxProductAmountLabel.text(`Max product ${data.price_measure_unit_category_display} per package`);
          } else {
            maxProductAmountLabel.text(`Max product amount per package`);
          }
        })
    } else {
      productProperties = null;
    }
  }

  function getMarketsCountries() {
    if (marketsField.val()) {
      let uniqueCountries = new Set();
      let fetchPromises = marketsField.val().map(marketId => {
        return fetchOptions(`/rest/v1/catalogs/market/${marketId}/`)
          .then(data => {
            data.countries.forEach(country => {
              uniqueCountries.add(country);
            });
          });
      });

      Promise.all(fetchPromises).then(() => {
        marketsCountries = Array.from(uniqueCountries);
        console.log("marketsCountries", marketsCountries);
      }).catch(error => console.error('Fetch error:', error));
    } else {
      marketsCountries = [];
    }
  }

  function updateSupply() {
    const packagingSupplyKindId = packagingSupplyKindField.val();
    if (packagingSupplyKindId) {
      fetchOptions(`${API_BASE_URL}/catalogs/supply/?kind=${packagingSupplyKindId}&is_enabled=1`)
        .then(data => {
          console.log("data", data);
          updateFieldOptions(packagingSupplyField, data);
        });
    } else {
      updateFieldOptions(packagingSupplyField, []);
    }
  }

  function updateName() {
    if (packagingSupplyKindField.val() && packagingSupplyField.val()) {
      const packagingSupplyKindName = packagingSupplyKindField.find('option:selected').text();
      const packagingSupplyName = packagingSupplyField.find('option:selected').text();
      nameField.val(`${packagingSupplyKindName} ${packagingSupplyName}`)
    } else {
      nameField.val('')
    }
  }

  productField.on('change', () => {
    getProductProperties()
  })

  marketsField.on('change', () => {
    // console.log("marketsField.val()", marketsField.val())
    getMarketsCountries()
  });

  packagingSupplyKindField.on('change', function () {
    updateSupply();
  });

  packagingSupplyField.on('change', function () {
    updateName();
  });

  [productField, marketsField, packagingSupplyKindField, packagingSupplyField].forEach(field => field.select2());
});
