document.addEventListener('DOMContentLoaded', function () {
  const productField = $('#id_product');
  const marketsField = $('#id_markets');
  const packagingSupplyKindField = $('#id_packaging_supply_kind');
  const productStandardPackagingField = $('#id_product_standard_packaging');
  const packagingSupplyField = $('#id_packaging_supply');

  const API_BASE_URL = '/rest/v1';

  function updateFieldOptions(field, options, selectedValue = null) {
    console.log("updateFieldOptions", field, options, selectedValue);
    field.empty().append(new Option('---------', '', !selectedValue, !selectedValue));
    options.forEach(option => {
      field.append(new Option(option.name, option.id, selectedValue === option.id, selectedValue === option.id));
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
          let maxProductAmountLabel = maxProductAmountLabel
          const originalText = maxProductAmountLabel.contents().filter(function () {
            return this.nodeType === 3;
          }).text().trim();

          if (data.price_measure_unit_category_display) {
            const newText = originalText.replace('amount', data.price_measure_unit_category_display);
            maxProductAmountLabel.contents().filter(function () {
              return this.nodeType === 3;
            }).first().replaceWith(newText + ' ');
          }
        })
    } else {
      productProperties = null;
    }
  }

  function getMarketsCountries() {
    return new Promise((resolve, reject) => {
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
          resolve(marketsCountries);
        }).catch(error => {
          console.error('Fetch error:', error);
          reject(error);
        });
      } else {
        marketsCountries = [];
        resolve(marketsCountries);
      }
    });
  }

  function updateProductStandardPackaging() {
    const packagingSupplyKindId = packagingSupplyKindField.val();
    if (packagingSupplyKindId && marketsCountries.length) {
      const countries = marketsCountries.join(',');
      fetchOptions(`${API_BASE_URL}/base/product-standard-packaging/?supply_kind=${packagingSupplyKindId}&standard__country__in=${countries}&is_enabled=1`)
        .then(data => {
          updateFieldOptions(productStandardPackagingField, data);
          updateName();
        })
    } else {
      updateFieldOptions(productStandardPackagingField, []);
      updateName();
    }
  }


  function getproductStandardPackagingFieldProperties() {
    return new Promise((resolve, reject) => {
      if (productStandardPackagingField.val()) {
        fetchOptions(`/rest/v1/base/product-standard-packaging/${productStandardPackagingField.val()}/`)
          .then(data => {
            productStandardPackagingProperties = data;
            resolve(data);
          })
          .catch(error => {
            console.error('Fetch error:', error);
            reject(error);
          });
      } else {
        productStandardPackagingProperties = null;
        resolve(null);
      }
    });
  }


  [productField, marketsField, packagingSupplyKindField, productStandardPackagingField, packagingSupplyField].forEach(field => field.select2());
});
