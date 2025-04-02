import base64
from io import BytesIO

def image_to_base64(image_io):
    """Convierte la imagen de BytesIO a un string base64."""
    return base64.b64encode(image_io.getvalue()).decode('utf-8')
