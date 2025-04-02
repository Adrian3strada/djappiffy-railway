document.addEventListener("DOMContentLoaded", function() { });

function submitForm(id) {
    console.log('Intentando enviar el formulario para el ID:', id);
    const form = document.getElementById("form_" + id);
    const input = document.getElementById("ticket_number_" + id);
    console.log('Formulario:', form);
    console.log('Input:', input);
    
    if (form && input) {
        const quantity = input.value;
        form.action = form.action.replace(/\d+\/$/, id + "/") + "?quantity=" + quantity;
        form.submit();
    } 
    else {
        console.error("No se encontró el formulario o el input para el ID:", id);
    }
}

// ************************************* WORKING
function submitFormPending(id) {
    console.log('Intentando enviar el formulario para etiquetas pendientes, ID:', id);

    // const form = document.getElementById("pending_form_" + id);
    const input = document.getElementById("pending_quantity_" + id);
    
    // console.log('Formulario encontrado:', form);
    console.log('Campo de entrada encontrado:', input);

    if (input) {
        const quantity = input.value;
        console.log('Cantidad de etiquetas pendientes:', quantity);

        if(quantity > 1){           //***************************************** 
            alert("No hay etiquetas pendientes para este empacador.")
            return
        }

        // Usamos reverse para generar la URL
        const action = form.action.replace(/\d+\/$/, id + "/") + "?quantity=" + quantity;
        
        fetch(action, {
            method: "GET",
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => response.blob()) // Recibimos el PDF
        .then(data => {
            const url = window.URL.createObjectURL(data);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = "pending_labels.pdf";  // Nombre del archivo de descarga
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);  // Limpiar el URL creado
        })
        .catch(error => {
            console.error("Error al generar las etiquetas pendientes:", error);
        });
    } else {
        console.error("No se encontró el input para el ID:", id, " en pending");
    }
}


// Función para obtener el token CSRF (por seguridad)
function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}