document.addEventListener('DOMContentLoaded', () => {
    const productField = $("#id_product");
    const clientField = $("#id_client");
    const orderItemsByField = $("#id_order_items_by")
    const pricingByField = $("#id_pricing_by")

    let productSizeOptions = [];
    let productPhenologyOptions = [];
    let marketClassOptions = [];
    let productPackagingOptions = [];

    let clientProperties = null;
    let productProperties = null;


    function updateFieldOptions(field, options) {
        if (field) {
            field.empty();
            if (!field.prop('multiple')) {
                field.append(new Option('---------', '', true, true));
            }
            options.forEach(option => {
                field.append(new Option(option.name, option.id, false, false));
            });
            field.trigger('change').select2();
        }
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
            fetchOptions(`${API_BASE_URL}/catalogs/product/${productField.val()}/`).then(
                (data) => {
                    productProperties = data;
                    console.log("productProperties", productProperties)
                    if (data.price_measure_unit_category_display) {
                        const priceLabel = $('label[for$="-unit_price"]');
                        priceLabel.text(`Price (${data.price_measure_unit_category_display})`);
                    }
                });
        } else {
            productProperties = null;
            const priceLabel = $('label[for$="-unit_price"]');
            priceLabel.text(`Price`);
        }
    }

    function updateProductOptions() {
        console.log("updateProductOptions")
        console.log("productField.val()", productField.val())
        console.log("clientProperties", clientProperties)
        if (productField.val() && clientProperties) {
            fetchOptions(`/rest/v1/catalogs/product-size/?product=${productField.val()}&market=${clientProperties.market}&is_enabled=1`)
                .then(data => {
                    productSizeOptions = data;
                }).then(() => {
                console.log("productSizeOptions", productSizeOptions)
            });
            fetchOptions(`/rest/v1/catalogs/product-phenology/?product=${productField.val()}&is_enabled=1`)
                .then(data => {
                    productPhenologyOptions = data;
                }).then(() => {
                console.log("productPhenologyOptions", productPhenologyOptions)
            });
            fetchOptions(`/rest/v1/catalogs/packaging/?product=${productField.val()}&is_enabled=1`)
                .then(data => {
                    productPackagingOptions = data;
                }).then(() => {
                console.log("productPackagingOptions", productPackagingOptions)
            });
        } else {
            productSizeOptions = [];
            productPhenologyOptions = [];
            productPackagingOptions = [];
        }
    }

    function getClientProperties() {
        if (clientField.val()) {
            fetchOptions(`/rest/v1/catalogs/client/${clientField.val()}/`)
                .then(data => {
                    clientProperties = data;
                    console.log("clientProperties", clientProperties)
                });
        } else {
            clientProperties = null;
        }
    }

    function updateMarketClassOptions() {
        if (clientProperties) {
            fetchOptions(`/rest/v1/catalogs/product-market-class/?market=${clientProperties.market}`)
                .then(data => {
                    marketClassOptions = data
                });
        } else {
            marketClassOptions = [];
        }
    }

    productField.on('change', () => {
        if (clientProperties) {
            getClientProperties();
            updateMarketClassOptions();
        }
        updateProductOptions();
    });

    clientField.on('change', () => {
        if (productField.val()) {
            updateProductOptions();
        }
        getClientProperties();
        updateMarketClassOptions();
    });

    document.addEventListener('formset:added', (event) => {
        if (event.detail.formsetName === 'orderitem_set') {
            alert(orderItemsByField.val())
            alert(pricingByField.val())
            const newForm = event.target;
            const productSizeField = $(newForm).find('select[name$="-product_size"]');
            const productPhenologyField = $(newForm).find('select[name$="-product_phenology"]');
            const marketClassField = $(newForm).find('select[name$="-market_class"]');
            const productPackagingField = $(newForm).find('select[name$="-product_packaging"]');

            updateFieldOptions(productSizeField, productSizeOptions);
            updateFieldOptions(productPhenologyField, productPhenologyOptions);
            updateFieldOptions(marketClassField, marketClassOptions);
            updateFieldOptions(productPackagingField, productPackagingOptions);
        }
    });

    if (clientField.val()) {
        // alert(clientField.val())
        getClientProperties();
        updateMarketClassOptions();
    }

    if (productField.val()) {
        setTimeout(() => {
            // alert(productField.val())
            updateProductOptions();
        }, 300);
    }

    setTimeout(() => {
        // const existingForms = $('div[id^="orderitem_set-"]');
        // se cambió la forma de obtener los elementos para que solo tome los que tienen un ID numérico (y evitar el group y el vacío)
        const existingForms = $('div[id^="orderitem_set-"]').filter((index, form) => {
            return /\d+$/.test(form.id);
        });

        existingForms.each((index, form) => {
            const productSizeField = $(form).find(`select[name$="${index}-product_size"]`);
            const productPhenologyField = $(form).find(`select[name$="${index}-product_phenology"]`);
            const marketClassField = $(form).find(`select[name$="${index}-market_class"]`);
            const productPackagingField = $(form).find(`select[name$="${index}-product_packaging"]`);

            updateFieldOptions(productSizeField, productSizeOptions);
            updateFieldOptions(productPhenologyField, productPhenologyOptions);
            updateFieldOptions(marketClassField, marketClassOptions);
            updateFieldOptions(productPackagingField, productPackagingOptions);
        });
    }, 2000);

});
