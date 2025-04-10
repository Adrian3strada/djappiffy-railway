document.addEventListener('DOMContentLoaded', function () {
    console.log("LLego2")

    // const updatePercentage = () => {
        // const sampleResidueFields = document.querySelectorAll('input[name$="sample_residue"]');
        // const percentageFields = document.querySelectorAll('input[name$="percentage"]');
        // const weightInputs = Array.from(document.querySelectorAll('input[name*="samplecollection_set-0-sampleweight_set-"]'))
        // .filter(input => {
        //     // Expresión regular para verificar que el nombre tiene un número en medio
        //     return input.name.endsWith('-weight') && /^samplecollection_set-\d+-sampleweight_set-\d+-weight$/.test(input.name);
        //   });

        // // Recorrer todos los valores de sample_residue
        // sampleResidueFields.forEach(field => {
        //     const sampleResidue = parseFloat(field.value);  // Obtener el valor del campo

        //     // Verificar si el valor es un número válido
        //     if (!isNaN(sampleResidue)) {
        //         // Calcular el porcentaje
        //         const percentage = sampleResidue / weightInputs.length;
        //         console.log("Calcula", percentage);
        //     }
        // });

        // // Mostrar el arreglo con los porcentajes calculados (opcional)
        // console.log('Porcentajes calculados:', percentages);
        // console.log(totalSamples);

        // if (!samplesWithResidueInput || !percentageInput || weightInputs.length === 0) return;

        // const samplesWithResidue = parseFloat(samplesWithResidueInput.value.replace(',', '.')) || 0;
        // const totalSamples = Array.from(weightInputs).filter(input => input.closest('tr').style.display !== 'none').length;

        // if (totalSamples > 0) {
        //     const percentage = (samplesWithResidue / totalSamples) * 100;
        //     percentageInput.value = percentage.toFixed(2).replace('.', ',');
        // } else {
        //     percentageInput.value = '0,00';
        // }
    // };

    // // Detectar cambios en el input de Samples With Residue
    // document.querySelector('input[name$="samples_with_residue"]')?.addEventListener('input', updatePercentage);

    // // Detectar cambios en los inputs de peso (por si se agregan nuevos)
    // const observer = new MutationObserver(updatePercentage);
    // observer.observe(document.body, { childList: true, subtree: true });

    // // Detectar cambios en los pesos existentes
    // document.addEventListener('input', function (e) {
    //     if (e.target.name && e.target.name.includes('sampleweight_set') && e.target.name.endsWith('-weight')) {
    //         updatePercentage();
    //     }
    // });

    // updatePercentage();
    // Función para recalcular los porcentajes
function recalculatePercentage() {
    const sampleResidueFields = document.querySelectorAll('input[name$="sample_residue"]');
    const percentageFields = document.querySelectorAll('input[name$="percentage"]');
    const weightInputs = Array.from(document.querySelectorAll('input[name*="samplecollection_set-0-sampleweight_set-"]'))
        .filter(input => {
            return input.name.endsWith('-weight') && /^samplecollection_set-\d+-sampleweight_set-\d+-weight$/.test(input.name);
        });

    sampleResidueFields.forEach((field, index) => {
        const sampleResidue = parseFloat(field.value); // Obtener el valor del campo
        if (!isNaN(sampleResidue)) {
            // Calcular el porcentaje
            const percentage = sampleResidue / weightInputs.length;
            console.log("Calcula1", percentage);
            
            // Asignar el porcentaje al campo correspondiente de percentageFields
            if (percentageFields[index]) {
                percentageFields[index].value = percentage.toFixed(2); // Asignar el valor al campo correspondiente
                console.log("Calcula2", percentageFields[index].value);
                console.log("Calcula2", percentageFields[index]);
            }
        }
    });
}

// Llamar a la función inicial para establecer los porcentajes
recalculatePercentage();

// Escuchar cambios en los campos sample_residue
sampleResidueFields.forEach(field => {
    field.addEventListener('input', recalculatePercentage);
});
});