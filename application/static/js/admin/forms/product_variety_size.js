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

    function addMarketFieldEventListeners() {
        document.querySelectorAll('select[name^="productvarietysize_set-"][name$="-market"]').forEach(marketField => {
            marketField.removeEventListener('change', handleMarketChange); // Remove existing listener to avoid duplicates
            marketField.addEventListener('change', handleMarketChange);
            alert('Event listener added');
            console.log(marketField);
        });
    }

    function handleMarketChange(event) {
        updateMarketStandardProductSizeField(event.target);
    }

    // Initial call to add event listeners to existing fields
    addMarketFieldEventListeners();

    // Observe for new inlines being added
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                addMarketFieldEventListeners();
            }
        });
    });

    const inlineContainer = document.querySelector('#productvarietysize_set-group');
    if (inlineContainer) {
        observer.observe(inlineContainer, { childList: true });
    }
});
