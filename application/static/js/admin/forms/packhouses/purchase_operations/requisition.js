document.addEventListener("DOMContentLoaded", function () {

  // Función para obtener el token CSRF
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

  $(document).on("click", ".btn-ready-confirm", function (e) {
    var url = $(this).data("url");
    var message = $(this).data("message");
    var confirmText = $(this).data("confirm");
    var cancelText = $(this).data("cancel");

    var button = $(this);

    Swal.fire({
      html: message,
      icon: "question",
      showCancelButton: true,
      confirmButtonColor: "#4daf50",
      cancelButtonColor: "#d33",
      confirmButtonText: confirmText,
      cancelButtonText: cancelText,
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
              // Ocultar el botón
              button.hide();

              var row = button.closest("tr");
              var statusCell = row.find(".field-status");
              statusCell.text("Ready");

              Toastify({
                text: data.message,
                duration: 3000,
                close: true,
                gravity: "bottom",
                position: "right",
                backgroundColor: "#4caf50",
              }).showToast();
            } else {
              Toastify({
                text: data.message,
                duration: 3000,
                close: true,
                gravity: "bottom",
                position: "right",
                backgroundColor: "#f44336",
              }).showToast();
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            Toastify({
              text: "An error occurred while processing your request.",
              duration: 3000,
              close: true,
              gravity: "bottom",
              position: "right",
              backgroundColor: "#f44336",
            }).showToast();
          });
      }
    });
  });
});
