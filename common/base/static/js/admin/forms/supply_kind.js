document.addEventListener('DOMContentLoaded', function () {
  const categoryField = $('#id_category');
  const capacityUnitCategoryField = $('#id_capacity_unit_category');
  const usageDiscountUnitCategoryField = $('#id_usage_discount_unit_category');

  function updateCapacityUnitCategoryField() {
    console.log("updateCapacityUnitCategoryField", categoryField.val());
    const packagingContainerKinds = ['packaging_containment', 'packaging_separator', 'packaging_presentation'];
    if (categoryField.val()) {
      if (packagingContainerKinds.includes(categoryField.val())) {
             capacityUnitCategoryField.closest('.form-group').fadeIn();
          } else {
            capacityUnitCategoryField.val(null).trigger('change').select2();
            capacityUnitCategoryField.closest('.form-group').fadeOut();
      }
    } else {
      capacityUnitCategoryField.val(null).trigger('change').select2();
      capacityUnitCategoryField.closest('.form-group').fadeOut();
    }
  }

  categoryField.on('change', () => {
    updateCapacityUnitCategoryField();
  });

  capacityUnitCategoryField.closest('.form-group').hide()
  if (categoryField.val()) updateCapacityUnitCategoryField();

  [categoryField, capacityUnitCategoryField, usageDiscountUnitCategoryField].forEach(field => field.select2());
});
