document.addEventListener("DOMContentLoaded", () => {
  const categoryField = $("#id_category");
  const CrewChiefTab = document.querySelector('a[href="#crew-chiefs-tab"]');
  const allowedChiefProviderCategories = ["harvesting_provider"];
  const vehicleField = $("#id_vehicle_provider");

  let initialCategory = categoryField.val();
  let initialVehicle = vehicleField.val();

  const toggleCrewChiefTab = () => {
    const categoryId = categoryField.val();
    if (categoryId && allowedChiefProviderCategories.includes(categoryId)) {
      CrewChiefTab?.classList.remove("d-none");
      vehicleField.val(initialVehicle).select2().trigger('change');
      uncheckDeleteCheckboxes();
    } else {
      checkChiefFormsBeforeDisabling();
      vehicleField.val('').select2().trigger('change');
    }
  };

  const checkChiefFormsBeforeDisabling = () => {
    const chiefForms = document.querySelectorAll('.dynamic-crewchief_set');
    if (chiefForms.length > 0) {
      Swal.fire({
        title: '',
        text: 'Si cambias el tipo de proveedor, los jefes de cuadrilla serán removidos de este proveedor.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Cambiar tipo',
        cancelButtonText: 'Cancelar',
        reverseButtons: false
      }).then((result) => {
        if (result.isConfirmed) {
          CrewChiefTab?.classList.add('d-none');
          markEmptyChiefFormsForDeletion();
          checkAllDeleteCheckboxes();
        } else {
          categoryField.val(initialCategory).select2().trigger('change');
        }
      });
    } else {
      CrewChiefTab?.classList.add('d-none');
      checkAllDeleteCheckboxes();
    }
  };

  const markEmptyChiefFormsForDeletion = () => {
    document.querySelectorAll(".dynamic-crewchief_set").forEach(form => {
      const inputs = form.querySelectorAll('input[type="text"], input[type="number"], select');
      const isEmpty = Array.from(inputs).every(input => input.value.trim() === "");
      if (isEmpty) {
        form.querySelector(".inline-deletelink")?.click();
      }
    });
  };

  const checkAllDeleteCheckboxes = () => {
    document.querySelectorAll('input[type="checkbox"][name$="-DELETE"]').forEach(checkbox => {
      checkbox.checked = true;
    });
  };

  const uncheckDeleteCheckboxes = () => {
    document.querySelectorAll('input[type="checkbox"][name$="-DELETE"]').forEach(checkbox => {
      checkbox.checked = false;
    });
  };

  toggleCrewChiefTab();

  categoryField.on("change", toggleCrewChiefTab);

  vehicleField.on("change", () => {
    if (vehicleField.val().length > 0) {
      initialVehicle = vehicleField.val();
    }
  });
});
