from django.core.exceptions import ValidationError
import fiona
from fiona.transform import transform_geom
from fiona.crs import from_epsg
from django.conf import settings
import os
from shapely.geometry import shape
from functools import wraps
from fiona.io import ZipMemoryFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile


def validate_geom_vector_file(value):
    print("value", value)
    try:
        file_content = value.read()
        if value.name.split('.')[-1] in ['gpkg', 'geojson']:
            with fiona.BytesCollection(file_content) as file:
                if file.schema['geometry'] not in ['Polygon', 'MultiPolygon']:
                    raise ValidationError("Geometría inválida")
        elif value.name.split('.')[-1] in ['zip']:
            with fiona.io.ZipMemoryFile(file_content) as memfile:
                layers = memfile.listlayers()
                layer = memfile.open(layer=layers[0])
                if layer.schema['geometry'] not in ['Polygon', 'MultiPolygon']:
                    raise ValidationError("Geometría inválida")
        else:
            raise ValidationError("El archivo no tiene formato válido")
    except Exception as e:
        print("Exception", e)
        try:
            if e.args and e.args[0] == "Geometría inválida":
                ex = "Geometría inválida"
            else:
                ex = "Formato inválido"
        except Exception as ee:
            ex = ee
        print("ex", ex)
        raise ValidationError(f"El archivo no es un archivo espacial válido: {ex}")


def to_multipolygon(instance):
    try:
        # Leer el archivo desde el almacenamiento
        file_content = default_storage.open(instance.file.name).read()

        with fiona.BytesCollection(file_content) as src:
            schema = src.schema.copy()
            schema['geometry'] = 'MultiPolygon'
            with fiona.BytesCollection() as dst:
                dst.driver = src.driver
                dst.schema = schema
                dst.crs = src.crs

                single_feature = {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {
                        'type': 'MultiPolygon',
                        'coordinates': []
                    }
                }
                for index, feature in enumerate(src):
                    if index == 0:
                        single_feature['properties'] = feature['properties']
                    if feature['geometry']['type'] == 'Polygon':
                        single_feature['geometry']['coordinates'].append(feature['geometry']['coordinates'])
                    else:
                        raise ValidationError("Geometría inválida")
                if len(single_feature['geometry']['coordinates']) == 0:
                    raise ValidationError("No se encontraron polígonos")
                else:
                    dst.write(single_feature)

                # Leer el contenido del archivo en memoria
                new_file_content = dst.read()

                # Guardar el nuevo archivo en GCS
                new_file_name = os.path.join('parcel_vector_files', f"{instance.uuid}.gpkg")
                default_storage.save(new_file_name, ContentFile(new_file_content))

                # Actualizar la instancia
                instance.file.name = new_file_name
                instance.save_due_to_update_geom = True
                instance.save()

    except fiona.errors.DriverError as e:
        raise ValidationError("Error al abrir el archivo con Fiona: {}".format(str(e)))
    except Exception as e:
        raise ValidationError("Error al procesar el archivo: {}".format(str(e)))


def to_polygon(instance):
    try:
        # Leer el archivo desde el almacenamiento
        file_content = default_storage.open(instance.file.name).read()

        with fiona.BytesCollection(file_content) as src:
            schema = src.schema.copy()
            schema['geometry'] = 'Polygon'
            with fiona.BytesCollection() as dst:
                dst.driver = src.driver
                dst.schema = schema
                dst.crs = src.crs

                for feature in src:
                    if feature['geometry']['type'] == 'Polygon':
                        dst.write(feature)
                    elif feature['geometry']['type'] == 'MultiPolygon':
                        for coordinates in feature['geometry']['coordinates']:
                            dst.write({
                                'type': 'Feature',
                                'properties': feature['properties'],
                                'geometry': {
                                    'type': 'Polygon',
                                    'coordinates': coordinates
                                }
                            })
                    else:
                        raise ValidationError("Geometría inválida")

                # Leer el contenido del archivo en memoria
                new_file_content = dst.read()

                # Guardar el nuevo archivo en GCS
                new_file_name = os.path.join('parcel_vector_files', f"{instance.uuid}.gpkg")
                default_storage.save(new_file_name, ContentFile(new_file_content))

                # Actualizar la instancia
                instance.file.name = new_file_name
                instance.save_due_to_update_geom = True
                instance.save()

    except fiona.errors.DriverError as e:
        raise ValidationError("Error al abrir el archivo con Fiona: {}".format(str(e)))
    except Exception as e:
        raise ValidationError("Error al procesar el archivo: {}".format(str(e)))


def fix_format(instance):
    try:
        # Leer el archivo desde el almacenamiento
        # file_content = default_storage.open(instance.file.name).read()
        file_content = instance.file.read()

        if instance.file.name.split('.')[-1] == 'zip':
            with ZipMemoryFile(file_content) as src:
                layers = src.listlayers()
                layer = src.open(layer=layers[0])

                # Crear un nuevo archivo en memoria
                with fiona.open(
                        '/vsimem/temp.gpkg',
                        mode="w",
                        driver="GPKG",
                        schema=layer.schema,
                        crs=layer.crs
                ) as dst:
                    for feature in layer:
                        dst.write(feature)

                # Leer el contenido del archivo en memoria
                with open('/vsimem/temp.gpkg', 'rb') as temp_file:
                    new_file_content = temp_file.read()

                # Guardar el nuevo archivo en GCS
                new_file_name = os.path.join('parcel_vector_files', f"{instance.uuid}.gpkg")
                default_storage.save(new_file_name, ContentFile(new_file_content))

                # Actualizar la instancia
                instance.file.name = new_file_name
                instance.save_due_to_update_geom = True
                instance.save()
    except Exception as e:
        raise ValidationError("fix_format Error al procesar el formato: {}".format(str(e)))


import fiona
from fiona.transform import transform_geom
from fiona.crs import from_epsg
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from io import BytesIO


def fix_crs(instance):
    print("fix_crs")
    try:
        # Leer el archivo desde el almacenamiento
        file_content = default_storage.open(instance.file.name).read()

        with fiona.BytesCollection(file_content) as src:
            print("src", src)
            print("src driver", src.driver)
            print("src schema", src.schema)

            # Crear un archivo en memoria usando BytesIO
            with BytesIO() as memfile:
                with fiona.open(
                            memfile,
                            mode='w',
                            driver=src.driver,
                            schema=src.schema.copy(),
                            crs=from_epsg(settings.EUDR_DATA_FEATURES_SRID)
                        ) as dst:
                    print("dst", dst)

                    for feature in src:
                        print("feature", feature)
                        geometry = feature['geometry']
                        reprojected_geometry = transform_geom(src.crs, dst.crs, geometry)
                        feature['geometry'] = reprojected_geometry
                        dst.write(feature)

                # Obtener el contenido del archivo en memoria
                memfile.seek(0)
                new_file_content = memfile.read()

            # Guardar el nuevo archivo en GCS
            new_file_name = os.path.join('parcel_vector_files', f"{instance.uuid}.gpkg")
            default_storage.save(new_file_name, ContentFile(new_file_content))

            # Actualizar la instancia
            instance.file.name = new_file_name
            instance.save_due_to_update_geom = True
            instance.save()

    except fiona.errors.DriverError as e:
        raise ValidationError("fix_crs Error al abrir el archivo con Fiona: {}".format(str(e)))
    except Exception as e:
        raise ValidationError("fix_crs Error al procesar el archivo: {}".format(str(e)))


def get_geom_from_file(instance):
    try:
        # Leer el archivo desde el almacenamiento
        file_content = default_storage.open(instance.file.name).read()

        with fiona.BytesCollection(file_content) as src:
            for feature in src:
                fiona_geometry = feature['geometry']
                shapely_geometry = shape(fiona_geometry)
                wkt_representation = shapely_geometry.wkt
                return wkt_representation
    except Exception as e:
        raise ValidationError("Error al leer archivo: {}".format(str(e)))


def uuid_file_path(instance, filename):
    """
    Devuelve la ruta del archivo para el parámetro upload_to de FileField,
    usando el UUID de la instancia como nombre de archivo.
    """
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('parcel_vector_files', filename)
    print("file_path", file_path)
    return file_path


# .............................................................................

def set_year_path(path):
    def decorator(func):
        @wraps(func)
        def wrapper(instance, filename):
            ext = filename.split('.')[-1]
            if not ext:
                raise ValidationError("El archivo debe tener extensión")
            filename = f"{instance.uuid}.{ext}"
            file_path = os.path.join(f'verification_images/{path}/', filename)
            return file_path

        return wrapper

    return decorator


def set_rgb_2020_image_path(instance, filename):
    """
    Devuelve la ruta del archivo para el parámetro upload_to de FileField,
    usando el UUID de la instancia como nombre de archivo.
    """
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('verification_images/rgb_2020/', filename)
    return file_path


@set_year_path("2021")
def set_rgb_2021_image_path(instance, filename):
    """
    Devuelve la ruta del archivo para el parámetro upload_to de FileField,
    usando el UUID de la instancia como nombre de archivo.
    """
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('verification_images/rgb_2021/', filename)
    return file_path


def set_image_path(instance, filename, path):
    """
    Devuelve la ruta del archivo para el parámetro upload_to de FileField,
    usando el UUID de la instancia como nombre de archivo.
    """
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('forestiffy', path, filename)
    return file_path
