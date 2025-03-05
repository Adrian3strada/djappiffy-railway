document.addEventListener('DOMContentLoaded', function() {

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

    const purchaseOrderSelect = document.querySelector('#id_purchase_order');
    if (!purchaseOrderSelect) {
        console.error('El elemento #id_purchase_order no fue encontrado en el DOM.');
    }

    let purchaseOrderField = document.querySelector('.field-purchase_order .readonly');
    if (purchaseOrderField) {
            // Seleccionar todos los inlines y ocultar el campo purchase_order_supply
            let inlineGroups = document.querySelectorAll('.inline-related');

            inlineGroups.forEach(function (inline) {
                let purchaseOrderSupplyFields = inline.querySelectorAll('.field-purchase_order_supply');

                purchaseOrderSupplyFields.forEach(function (field) {
                    field.style.display = 'none';  // Ocultar con CSS
                });
            });
    }

    if($(".add-row")) {
      setTimeout(() => {
            $(".add-row").hide();
            }, 300);
    }

    $(document).on('change.select2', '#id_purchase_order', function() {
        const purchaseOrderId = purchaseOrderSelect.value;
        if (purchaseOrderId) {
            fetch(`/rest/v1/storehouse/purchase-order-supplies/?purchase_order=${purchaseOrderId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Error en la solicitud: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    const inlineFormContainer = document.querySelector('#storehouseentrysupply_set-group .card-body');
                    if (!inlineFormContainer) {
                        console.error('El contenedor no fue encontrado en el DOM.');
                        return;
                    }

                    const totalFormsInput = document.querySelector('#id_storehouseentrysupply_set-TOTAL_FORMS');
                    if (!totalFormsInput) {
                        console.error('El campo TOTAL_FORMS no fue encontrado en el DOM.');
                        return;
                    }

                    inlineFormContainer.querySelectorAll('.dynamic-inline-form').forEach(form => form.remove());
                    let totalForms = 0;
                    totalFormsInput.value = totalForms;

                    const emptyForm = document.querySelector('#storehouseentrysupply_set-empty');
                    if (!emptyForm) {
                        console.error('El formulario vacío no fue encontrado en el DOM.');
                        return;
                    }

                    data.forEach(supply => {
                        const newInlineForm = emptyForm.cloneNode(true);
                        newInlineForm.classList.add('dynamic-inline-form');
                        const formIndex = totalForms;
                        newInlineForm.innerHTML = newInlineForm.innerHTML.replace(/__prefix__/g, formIndex);

                        const purchaseOrderSupplySelect = newInlineForm.querySelector('select[name$="-purchase_order_supply"]');
                        if (purchaseOrderSupplySelect) {
                            purchaseOrderSupplySelect.innerHTML = '';
                            supply.purchase_order_supply_options.forEach(optionData => {
                                const option = document.createElement('option');
                                option.value = optionData.id;
                                option.textContent = optionData.name;
                                if (optionData.id === supply.id) {
                                    option.selected = true;
                                }
                                purchaseOrderSupplySelect.appendChild(option);
                            });
                            purchaseOrderSupplySelect.classList.add('disabled-field');
                        }

                        const receivedQuantityInput = newInlineForm.querySelector('input[name$="-received_quantity"]');
                        if (receivedQuantityInput) {
                            receivedQuantityInput.value = 0;
                        }

                        const expectedQuantityInput = newInlineForm.querySelector(`input[name$="-expected_quantity"]`);
                        if (expectedQuantityInput) {
                            expectedQuantityInput.value = supply.quantity;
                            expectedQuantityInput.classList.add('disabled-field');
                        }

                        newInlineForm.classList.remove('empty-form', 'last-related');
                        inlineFormContainer.insertBefore(newInlineForm, emptyForm);
                        totalForms += 1;
                    });

                    totalFormsInput.value = totalForms;
                    //Botón para devolver a Purchase
                    let targetDiv = document.getElementById("storehouse-entry-supplies-tab");

                    if (targetDiv) {
                      let existingContainer = targetDiv.querySelector(".storehouse-button-container");

                      if (!existingContainer) {
                          // Crear un div contenedor
                          let container = document.createElement("div");
                          container.classList.add("storehouse-button-container");

                          // Crear el botón
                          let button = document.createElement("a");
                          button.href = "javascript:void(0);";
                          button.innerText = "Devolver a Purchase";
                          button.classList.add("btn", "btn-info", "storehouse-button");
                          button.id = "return-to-purchase-btn";

                          // Agregar botón al contenedor
                          container.appendChild(button);

                          // Insertar el contenedor dentro del targetDiv
                          targetDiv.insertAdjacentElement("afterbegin", container);
                      }
                  }

                })
                .catch(error => {
                    console.error('Error al obtener los datos:', error);
                });

            const tabLink = document.querySelector('a.nav-link[data-toggle="pill"][href="#storehouse-entry-supplies-tab"]');
            if (tabLink) {
                tabLink.click();
            }
        }
    });

    $(document).on('click', '#return-to-purchase-btn', function(e) {
        e.preventDefault();

        const purchaseOrderId = purchaseOrderSelect.value;

        if (!purchaseOrderId) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "No purchase order selected.",
                confirmButtonColor: "#f44336",
                confirmButtonText: "OK",
            });
            return;
        }

        const url = `/dadmin/purchase/set_purchase_order_supply_open/${purchaseOrderId}/`;

        Swal.fire({
            icon: "question",
            text: "¿Está seguro que desea devolver a Purchase?",
            showCancelButton: true,
            confirmButtonText: "Sí, devolver",
            cancelButtonText: "Cancelar",
            confirmButtonColor: "#4daf50",
            cancelButtonColor: "#d33",
            allowOutsideClick: false,
            allowEscapeKey: false,
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Content-Type": "application/json",
                    },
                })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        Swal.fire({
                            icon: "success",
                            title: data.title,
                            text: data.message,
                            confirmButtonColor: "#4daf50",
                            confirmButtonText: data.button,
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                        }).then(() => {
                            window.location.href = window.location.pathname + "#general-tab";
                            window.location.reload();
                        });
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: data.message,
                            confirmButtonColor: "#f44336",
                            confirmButtonText: "OK",
                        });
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: "An error occurred while processing your request.",
                        confirmButtonColor: "#f44336",
                        confirmButtonText: "OK",
                    });
                });
            }
        });
    });

});
