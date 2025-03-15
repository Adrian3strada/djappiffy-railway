document.addEventListener("DOMContentLoaded", function() {
    const API_BASE_URL = '/rest/v1';

    document.querySelectorAll(".djn-add-item .add-handler").forEach(button => {
        button.style.display = "none"; 
    });
    document.querySelectorAll("td.original").forEach(row => {
        row.style.display = "none"; 
    });
    document.querySelectorAll("th.original").forEach(row => {
        row.style.display = "none";  
    });

    const vehicleRows = document.querySelectorAll('tbody[id^="scheduleharvest_set-0-scheduleharvestvehicle_set-"]');

    document.querySelectorAll('div[id^="scheduleharvest_set-"]').forEach(harvestInline => {
        const harvestId = harvestInline.querySelector('input[name$="-id"]').value;
        console.log("Harvest ID:", harvestId);
      });

    vehicleRows.forEach(row => {
    // Obtener datos del vehículo
    const provider = row.querySelector('.field-provider a').innerText;
    const vehicle = row.querySelector('.field-vehicle a').innerText;
    const stampNumber = row.querySelector('input[name$="-stamp_vehicle_number"]').value;
    const vehicleId = row.querySelector('input[name$="-id"]').value;

    // Obtener el índice del registro (último número del ID)
    const index = row.id.split('-').pop();

    console.log(`Vehículo ${index}:`, {
        provider,
        vehicle,
        stampNumber,
        vehicleId
    });
    });

    const testEndpoint = (url, options = {}) => {
        return fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            // 'Authorization': 'Bearer TU_TOKEN' // Agrega si necesitas autenticación
          },
          ...options
        })
        .then(response => {
          if (!response.ok) throw new Error(`Error ${response.status}`);
          return response.json();
        })
        .catch(error => {
          console.error('Falló el endpoint:', url, error);
          throw error;
        });
      };
      
      // Ejemplo de uso:
      testEndpoint(`${API_BASE_URL}/gathering/harvest-cutting-vehicle=1`)
        .then(data => {
          console.log('Vehículos:', data);
          // Actualizar UI aquí
        })
        .catch(() => {
          console.log('Mostrar error al usuario');
        });



});


