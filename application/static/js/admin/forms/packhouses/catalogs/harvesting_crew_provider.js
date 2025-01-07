document.addEventListener('DOMContentLoaded', function () {
  const isEnabledField = document.querySelector('#id_is_enabled');
  const vehicleTab = document.querySelector('a[href="#vehicles-tab"]').closest('.nav-item');

  let initialIsEnabledState = isEnabledField.checked;  // Guardar el estado inicial

  function toggleVehicleTab() {
      if (isEnabledField.checked) {
          vehicleTab.classList.remove('d-none');
          uncheckDeleteCheckboxes();
      } else {
          checkVehicleFormsBeforeDisabling();
      }
  }

  function checkVehicleFormsBeforeDisabling() {
      const vehicleForms = document.querySelectorAll('.dynamic-vehicle_set');

      if (vehicleForms.length > 0) {
          // Si hay formularios, preguntar con SweetAlert
          Swal.fire({
              title: '¿Estás seguro?',
              text: 'Si desactivas esta opción, se marcarán los vehículos vacíos para eliminar.',
              icon: 'warning',
              showCancelButton: true,
              confirmButtonText: 'Sí, desactivar',
              cancelButtonText: 'Cancelar',
              reverseButtons: false
          }).then((result) => {
              if (result.isConfirmed) {
                  vehicleTab.classList.add('d-none');
                  markEmptyVehicleFormsForDeletion();
                  checkAllDeleteCheckboxes();
                  initialIsEnabledState = false;  // Actualizar el estado
              } else {
                  isEnabledField.checked = true;  // Revertir el checkbox
              }
          });
      } else {
          vehicleTab.classList.add('d-none');
          checkAllDeleteCheckboxes();
          initialIsEnabledState = false;
      }
  }

  function markEmptyVehicleFormsForDeletion() {
      const vehicleForms = document.querySelectorAll('.dynamic-vehicle_set');

      vehicleForms.forEach(form => {
          const inputs = form.querySelectorAll('input[type="text"], input[type="number"], select');
          let isEmpty = true;

          inputs.forEach(input => {
              if (input.value.trim() !== '') {
                  isEmpty = false;
              }
          });

          if (isEmpty) {
              const deleteButton = form.querySelector('.inline-deletelink');
              if (deleteButton) {
                  deleteButton.click();  // Simular el clic en eliminar
              }
          }
      });
  }

  function checkAllDeleteCheckboxes() {
      const deleteCheckboxes = document.querySelectorAll('input[type="checkbox"][name$="-DELETE"]');
      deleteCheckboxes.forEach(checkbox => {
          checkbox.checked = true;
      });
  }

  function uncheckDeleteCheckboxes() {
      const deleteCheckboxes = document.querySelectorAll('input[type="checkbox"][name$="-DELETE"]');
      deleteCheckboxes.forEach(checkbox => {
          checkbox.checked = false;
      });
  }

  // Inicializar el estado al cargar la página
  toggleVehicleTab();

  // Escuchar cambios en el checkbox de is_enabled
  isEnabledField.addEventListener('change', function () {
      toggleVehicleTab();
  });
});
