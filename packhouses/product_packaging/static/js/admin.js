document.addEventListener("DOMContentLoaded", function() { });


function submitNewLabels(id) {
    const input = document.getElementById("number_of_labels_" + id);
    if (input) {
        const quantity = parseInt(input.value, 10); 
        if (quantity < 1 || quantity > 1000 ) {  
            alert("Asegúrate de seleccionar de 1 a 1000 etiquetas.");
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
            alert("No hay etiquetas pendientes para este empacador.");
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
    if (confirm("Are you sure you want to discard all pending labels?")) {
        fetch(`/dadmin/product_packaging/packeremployee/discard_labels/${employeeId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(`Deleted ${data.deleted} labels.`);
                location.reload();
            } else {
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => console.error("Error:", error));
    }
}

function getCSRFToken() {
    const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
    return csrfTokenElement ? csrfTokenElement.value : "";
}