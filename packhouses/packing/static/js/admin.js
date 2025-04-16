document.addEventListener("DOMContentLoaded", function() { });


function submitNewLabels(id) {
    const input = document.getElementById("number_of_labels_" + id);
    if (input) {
        const quantity = parseInt(input.value, 10); 
        if (quantity < 1 || quantity > 1000 ) {  
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "Asegúrate de seleccionar entre 1 a 1000 etiquetas.",
                confirmButtonColor: "#2c3e50"
            });
            return;
        }
        const action = `/dadmin/product_packaging/packeremployee/generate_label/${id}/?quantity=${quantity}`;
        fetch(action, {
            method: "GET",
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("No new labels found or server error.");
            }
            return response.blob();
        })
        .then(data => {
            const url = window.URL.createObjectURL(data);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = "new_labels.pdf";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            location.reload();
        })
        .catch(error => {
            console.error("Error al recuperar las etiquetas nuevas", error);
            alert("Error al recuperar las etiquetas nuevas.");
        });
    } else {
        console.error("No inputs found for employee:", id);
    }
}

function submitPendingLabels(id) {
    const input = document.getElementById("pending_quantity_" + id);
    if (input) {
        const quantity = parseInt(input.value, 10); 
        if (quantity < 1) {  
            Swal.fire({
                icon: "error",
                text: "No hay etiquetas pendientes para este empacador.",
                confirmButtonColor: "#2c3e50"
            });
            return;
        }
        const action = `/dadmin/product_packaging/packeremployee/generate_pending_labels/${id}/`;
        fetch(action, {
            method: "GET",
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("No pending labels found or server error.");
            }
            return response.blob();
        })
        .then(data => {
            const url = window.URL.createObjectURL(data);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = "pending_labels";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            location.reload();
        })
        .catch(error => {
            console.error("Error trying to recover pending labels:", error);
        });
    } 
    else {
        console.error("No inputs found for employee:", id);
    }
}


function discardLabels(employeeId) {
    Swal.fire({
        title: "¿Estás seguro?",
        text: "¿Quieres descartar todas las etiquetas pendientes?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#2c3e50",
        confirmButtonText: "Si, descartar todas"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/dadmin/product_packaging/packeremployee/discard_labels/${employeeId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                if (data.status === "success") {
                    Swal.fire({
                        icon: "success",
                        title: "¡Etiquetas descartadas!",
                        text: `${data.deleted} etiquetas pendientes descartadas. `,
                        confirmButtonColor: "#2c3e50"
                    }).then(() => {
                        location.reload();
                    });
                } 
                else {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: data.message,
                        confirmButtonColor: "#2c3e50"
                    });
                }
            })
            .catch(error => {
                console.error("Error:", error);
                Swal.fire({
                    icon: "error",
                    title: "Request Failed",
                    text: "An error occurred while processing the request."
                });
            });
        }
    });
}

function getCSRFToken() {
    const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
    return csrfTokenElement ? csrfTokenElement.value : "";
}