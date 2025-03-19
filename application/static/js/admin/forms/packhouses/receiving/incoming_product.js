document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".djn-add-item .add-handler").forEach(button => {
        button.style.display = "none"; 
    });
    document.querySelectorAll("td.original").forEach(row => {
        row.style.display = "none"; 
    });
    document.querySelectorAll("th.original").forEach(row => {
        row.style.display = "none";  
    });
});

/*
document.addEventListener("DOMContentLoaded", function() {
    const API_BASE_URL = '/rest/v1';

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

    const harvestCuttingId = 
const vehicleId = 2;        
const stampNumberFromFrontend = "1122"; 
const url = `${API_BASE_URL}/gathering/harvest-cutting-vehicle/?harvest_cutting_id=${harvestCuttingId}&vehicle_id=${vehicleId}`;

const testEndpoint = (url) => {
    return fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
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


testEndpoint(url)
    .then(data => {
        console.log('Vehículo:', data);

        if (data && data.results && data.results.length > 0) {
            const vehicle = data.results[0]; 
            if (vehicle.stamp_number === stampNumberFromFrontend) {
                console.log('stamp_number coincide');
                
               
            } else {
                console.log('El stamp_number no coincide');
                alert('El número de sello no coincide.');
            }
        } else {
            console.log('No se encontró el vehículo');
        }
    })
    .catch(() => {
        alert('Hubo un error al verificar el vehículo. Intenta nuevamente.');
    });

});


*/