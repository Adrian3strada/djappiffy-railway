document.addEventListener('DOMContentLoaded', function() {
    const geomField = document.getElementById('id_geom');
    if (geomField && !geomField.value) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                console.log("Centering map to", lat, lon);
                const view = geodjango_geom.map.getView();
                view.setCenter(ol.proj.fromLonLat([lon, lat]));
                view.setZoom(12);
            });
        }
    }
});
