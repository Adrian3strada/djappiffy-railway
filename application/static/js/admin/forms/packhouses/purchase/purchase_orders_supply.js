document.addEventListener('DOMContentLoaded', () => {

  // Función para actualizar las opciones disponibles en cada select
  function updateSupplyOptions() {
    // Obtener todos los selects de requisition_supply que no están marcados para borrar
    const selects = $('select[name$="-requisition_supply"]').filter(function() {
      const deleteCheckbox = $(this).closest('.inline-related').find('input[type="checkbox"][name$="-DELETE"]');
      return !(deleteCheckbox.length && deleteCheckbox.is(':checked'));
    });

    // Recolectar los valores seleccionados en los selects
    const selectedValues = selects
      .map(function() {
        return $(this).val();
      })
      .get()
      .filter(Boolean); // Filtrar valores nulos o vacíos

    // Actualizar las opciones de cada select
    selects.each(function() {
      const currentSelect = $(this);
      const currentValue = currentSelect.val();

      currentSelect.find('option').each(function() {
        const option = $(this);
        const optionVal = option.attr('value');

        // Deshabilitar la opción si ya está seleccionada en otro inline y no es la opción actual
        option.prop('disabled', optionVal && selectedValues.includes(optionVal) && optionVal !== currentValue);
      });
    });
  }
  // Actualiza el campo "quantity" cuando se selecciona un supply
  $(document).on('change', 'select[name$="-requisition_supply"]', function(){
    const selectedOption = $(this).find('option:selected');
    const dataQuantity = selectedOption.data('quantity');
    const dataComments = selectedOption.data('comments');

    const inlineForm = $(this).closest('.inline-related');
    const commentsField = inlineForm.find('div.field-comments > div.readonly');

    if (dataQuantity !== undefined) {
      const currentName = $(this).attr('name');
      const quantityFieldName = currentName.replace('requisition_supply', 'quantity');
      const quantityField = $('input[name="' + quantityFieldName + '"]');
      if (quantityField.length) {
        quantityField.val(dataQuantity);
      }
    }

    if (dataComments !== undefined && dataComments !== 'None') {
        if (commentsField.length) {
            commentsField.text(dataComments);
        } else {
            commentsField.text('');
        }
    } else {
      commentsField.text('');
    }

    updateSupplyOptions();
  });

  // Escuchar keyup en los inputs de cantidad y precio unitario
  $(document).on('keyup', 'input[name$="-quantity"], input[name$="-unit_price"]', function() {
    // Buscar el contenedor del inline actual
    var $inline = $(this).closest('.inline-related');

    // Obtener el valor de la cantidad y del precio unitario del inline actual
    var qty = parseFloat($inline.find('input[name$="-quantity"]').val());
    var unitPrice = parseFloat($inline.find('input[name$="-unit_price"]').val());

    // Si no se puede parsear, se establece 0
    if (isNaN(qty)) { qty = 0; }
    if (isNaN(unitPrice)) { unitPrice = 0; }

    // Calcular el total
    var total = qty * unitPrice;

    // Buscar el campo total ubicado dentro del contenedor .field-total_price)
    var $totalField = $inline.find('.field-total_price .readonly');

    // Actualizar el contenido: si el total es mayor que cero se muestra con dos decimales, de lo contrario un 0
    if (total > 0) {
      $totalField.text(total.toFixed(2));
    } else {
      $totalField.text('0');
    }
  });

  //  se hace clic en el botón de eliminar en el inline
  $(document).on('click', '.inline-deletelink', function(){
    setTimeout(updateSupplyOptions, 100);
  });

  //  el borrado se marca mediante el checkbox de borrar en el inline
  $(document).on('change', 'input[type="checkbox"][name$="-DELETE"]', function(){
    setTimeout(updateSupplyOptions, 100);
  });
  // Se actualiza las opciones al cargar la página (por si hay valores preseleccionados)
  updateSupplyOptions();
});
