document.addEventListener("DOMContentLoaded", function() { });


function submitForm(id) {
    console.log('Intentando enviar el formulario para ID:', id);

    const forms = document.querySelectorAll('form');
    console.log('Todos los formularios:', forms);
    
    const form = document.getElementById("form_" + id);
    const input = document.getElementById("ticket_number_" + id);
    
    console.log('Formulario encontrado:', form);  // 
    console.log('Campo de entrada encontrado:', input);  // 

    if (form && input) {
        console.log('Formulario encontrado para ID:', id);
        const quantity = input.value;
        console.log('Cantidad seleccionada:', quantity); 
        
        const action = form.action.replace(/\d+\/$/, id + "/") + "?quantity=" + quantity;

        console.log('Acción del formulario:', action);

        form.action = action;
        console.log('Nueva URL del formulario:', form.action);  
        form.submit();
    } else {
        console.error("No se encontró el formulario o el input para el ID:", id);
    }
}

