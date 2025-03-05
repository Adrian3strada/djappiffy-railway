document.addEventListener("DOMContentLoaded", function () {

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

  // Interceptar el clic en el botón de guardar
  const saveButton = document.querySelector('input[name="_save"]');
  if (saveButton) {
        saveButton.addEventListener('click', function (e) {
            e.preventDefault();

            const saveAndSendInput = $('input[name="save_and_send"]');
            const questionText = saveAndSendInput.data('question');
            const confirmText = saveAndSendInput.data('confirm');
            const denyText = saveAndSendInput.data('deny');
            const cancelText = saveAndSendInput.data('cancel');

            Swal.fire({
                icon: "question",
                text: questionText,
                showDenyButton: true,
                showCancelButton: true,
                confirmButtonText: confirmText,
                denyButtonText: denyText,
                confirmButtonColor: "#4daf50",
                denyButtonColor: "#162c58",
                cancelButtonColor: "#d33",
                cancelButtonText: cancelText,
            }).then((result) => {
                if (result.isConfirmed) {
                    document.querySelector('input[name="save_and_send"]').value = 'true';
                    document.querySelector('#purchaseorder_form').submit();
                } else if (result.isDenied) {
                    document.querySelector('input[name="save_and_send"]').value = 'false';
                    document.querySelector('#purchaseorder_form').submit();
                }
            });
        });
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
              window.location.reload();
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

  $(document).on("click", ".btn-open-confirm", function (e) {
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
              window.location.reload();
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
