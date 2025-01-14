$(document).ready(function () {
 const categoryField = $("#id_category");
  const gathererField = $(".field-gatherer");
  const maquiladoraField = $(".field-maquiladora");
  const productField = $("#id_product");
  const varietyField = $("#id_product_variety");
  const initialVarietyValue = varietyField.val();
  const seasonField = $("#id_product_season_kind");
  const initialSeasonValue = seasonField.val();
  const harvestSizeField = $("#id_product_harvest_size_kind");
  const initialHarvestSizeValue = harvestSizeField.val();
  const orchardField = $("#id_orchard");
  const initialOrchardSizeValue = orchardField.val();

  const API_BASE_URL = "/rest/v1";

  function updateFieldOptions(field, options) {
    field.empty().append(new Option("---------", "", true, true));
    options.forEach((option) => {
      if(field === orchardField){
        field.append(new Option(option.code+' - '+option.name, option.id, false, false));
      }else{
        field.append(new Option(option.name, option.id, false, false));
      }
    });
    field.trigger("change").select2();
  }

  function fetchOptions(url) {
    return $.ajax({
      url: url,
      method: "GET",
      dataType: "json",
    }).fail((error) => console.error("Fetch error:", error));
  }

  function updateVarietyField() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_variety/?product=${productId}&is_enabled=true`)
        .then((data) => {
          updateFieldOptions(varietyField, data);
          if (initialVarietyValue) {
            varietyField.val(initialVarietyValue).trigger("change");
          }
        });
    } else {
      updateFieldOptions(varietyField, []);
    }
  }

  function updateSeasonField() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_season_kind/?product=${productId}&is_enabled=true`)
        .then((data) => {
          updateFieldOptions(seasonField, data);
          if (initialSeasonValue) {
            seasonField.val(initialSeasonValue).trigger("change");
          }
        });
    } else {
      updateFieldOptions(seasonField, []);
    }
  }

  function updateHarvestSizeField() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/product_harvest_size_kind/?product=${productId}&is_enabled=true`)
        .then((data) => {
          updateFieldOptions(harvestSizeField, data);
          if (initialHarvestSizeValue) {
            harvestSizeField.val(initialHarvestSizeValue).trigger("change");
          }
        });
    } else {
      updateFieldOptions(harvestSizeField, []);
    }
  }

  function toggleFieldsBasedOnCategory() {
    const categoryValue = categoryField.val();

    if (categoryValue === "gathering") {
      gathererField.fadeIn();
      $("#id_maquiladora").val('').trigger('change');
      maquiladoraField.hide();
    } else if (categoryValue === "maquila") {
      gathererField.hide();
      $("#id_gatherer").val('').trigger('change');
      maquiladoraField.fadeIn();
    } else {
      $("#id_gatherer").val('').trigger('change');
      $("#id_maquiladora").val('').trigger('change');
      gathererField.hide();
      maquiladoraField.hide();
    }
  }

  function updateOrchardField() {
    const productId = productField.val();
    if (productId) {
      fetchOptions(`${API_BASE_URL}/catalogs/orchard/?product=${productId}&is_enabled=true`)
        .then((data) => {
          updateFieldOptions(orchardField, data);
          if (initialOrchardSizeValue) {
            orchardField.val(initialOrchardSizeValue).trigger("change");
          }
        });
    } else {
      updateFieldOptions(orchardField, []);
    }
  }

  // Oculta ambos campos al inicio
  gathererField.hide();
  maquiladoraField.hide();

  // Llama a la función cuando carga la página para calcular valores iniciales
  toggleFieldsBasedOnCategory();

  productField.on("change", function () {
    setTimeout(function () {
        updateVarietyField();
        updateSeasonField();
        updateHarvestSizeField();
        updateOrchardField();
    }, 300);
});


  // Llama a la función cuando el campo de categoría cambia
  categoryField.change(toggleFieldsBasedOnCategory);


  if (initialVarietyValue) {
    varietyField.val(initialVarietyValue).trigger("change");
  }

  updateVarietyField();
  updateSeasonField();
  updateHarvestSizeField();
  updateOrchardField();

});
