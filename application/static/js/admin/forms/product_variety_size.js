document.addEventListener('DOMContentLoaded', function() {
    function updateMarketStandardProductSizeField(marketField) {
        const marketId = marketField.value;
        const inlineIndex = marketField.name.match(/\d+/)[0];
        const marketStandardProductSizeField = document.querySelector(`select[name="productvarietysize_set-${inlineIndex}-market_standard_product_size"]`);

        if (marketId) {
            fetch(`/catalogs/market_standard_product_size/${marketId}/`)
                .then(response => response.json())
                .then(data => {
                    marketStandardProductSizeField.innerHTML = '';
                    data.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.id;
                        option.textContent = item.name;
                        marketStandardProductSizeField.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching market standard product sizes:', error);
                });
        } else {
            marketStandardProductSizeField.innerHTML = '';
        }
    }

    document.querySelectorAll('select[name^="productvarietysize_set-"][name$="-market"]').forEach(marketField => {
        marketField.addEventListener('change', function() {
            updateMarketStandardProductSizeField(marketField);
        });
    });

    // Add a new select element for MarketStandardProductSize
    document.querySelectorAll('.inline-related').forEach((inline, index) => {
        const marketField = inline.querySelector('select[name$="-market"]');
        if (marketField) {
            const marketStandardProductSizeField = document.createElement('select');
            marketStandardProductSizeField.name = `productvarietysize_set-${index}-market_standard_product_size`;
            marketStandardProductSizeField.classList.add('vSelectField');
            marketField.parentNode.insertBefore(marketStandardProductSizeField, marketField.nextSibling);
        }
    });
});
