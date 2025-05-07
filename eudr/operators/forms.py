from django.contrib.gis.forms import OSMWidget

# Register your forms here.


class OLGoogleMapsSatelliteWidget(OSMWidget):
    template_name = "gis/ol-googlemaps-satellite.html"
