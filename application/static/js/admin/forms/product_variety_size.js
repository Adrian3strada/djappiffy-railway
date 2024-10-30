document.addEventListener('DOMContentLoaded', function() {
    const marketField = document.getElementById('id_market');
    const marketStandardSizeField = document.getElementById('id_market_standard_size');

    if (marketField) {
        const updateMarketStandardSizes = function() {
            const marketId = marketField.value;
            const url = `/rest/v1/catalogs/market_standard_product_size/?market=${marketId}&is_enabled=1`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    marketStandardSizeField.innerHTML = '';
                    const emptyOption = new Option('---------', '', true, true);
                    marketStandardSizeField.appendChild(emptyOption);
                    data.forEach(item => {
                        const option = new Option(item.name, item.id, false, false);
                        marketStandardSizeField.appendChild(option);
                    });
                });
        };

        // Inicializar select2
        $(marketField).select2();
        $(marketStandardSizeField).select2();

        // Actualizar al cargar la página si hay un valor seleccionado
        if (!marketField.value) {
            updateMarketStandardSizes();
        }

        // Actualizar al cambiar el valor del campo market
        $(marketField).on('select2:select', updateMarketStandardSizes);

        // Actualizar los campos name y alias al seleccionar un size
        $(marketStandardSizeField).on('select2:select', function(e) {
            const selectedText = e.params.data.text;
            const nameField = document.querySelector('input[name="name"]');
            const aliasField = document.querySelector('input[name="alias"]');

            if (nameField) {
                nameField.value = selectedText;
            }

            if (aliasField) {
                aliasField.value = transformTextForAlias(selectedText);
            }
        });
    }

    // Función para transformar el texto para el campo alias
    function transformTextForAlias(text) {
        const accentsMap = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'
        };
        return text
            .replace(/[áéíóúÁÉÍÓÚ]/g, match => accentsMap[match])
            .replace(/[^a-zA-Z0-9]/g, '');
    }
});
