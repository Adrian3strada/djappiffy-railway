from django.core.exceptions import ValidationError
import fiona
from fiona.transform import transform_geom
from fiona.crs import from_epsg
from django.conf import settings
import shutil
import os
from shapely.geometry import shape
from functools import wraps


def validate_geom_vector_file(value):
    try:
        if value.name.split('.')[-1] in ['gpkg', 'geojson']:
            with fiona.open(value) as file:
                if file.schema['geometry'] not in ['Polygon', 'MultiPolygon']:
                    raise ValidationError("Geometría inválida")
        elif value.name.split('.')[-1] in ['zip']:
            with fiona.io.ZipMemoryFile(value) as memfile:
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
        with fiona.open(instance.file.path) as src:
            schema = src.schema.copy()
            schema['geometry'] = 'MultiPolygon'
            with fiona.open(
                instance.file.path + '-final',
                mode="w",
                driver=src.driver,
                schema=schema,
                crs=src.crs
            ) as dst:
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

        os.remove(instance.file.path)
        shutil.move(instance.file.path + '-final', instance.file.path)

    except fiona.errors.DriverError as e:
        raise ValidationError("Error al abrir el archivo con Fiona: {}".format(str(e)))
    except Exception as e:
        raise ValidationError("Error al procesar el archivo: {}".format(str(e)))


def to_polygon(instance):
    try:
        with fiona.open(instance.file.path) as src:
            schema = src.schema.copy()
            schema['geometry'] = 'Polygon'
            with fiona.open(
                instance.file.path + '-final',
                mode="w",
                driver=src.driver,
                schema=schema,
                crs=src.crs
            ) as dst:
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

        os.remove(instance.file.path)
        shutil.move(instance.file.path + '-final', instance.file.path)

    except fiona.errors.DriverError as e:
        raise ValidationError("Error al abrir el archivo con Fiona: {}".format(str(e)))
    except Exception as e:
        raise ValidationError("Error al procesar el archivo: {}".format(str(e)))


def fix_format(instance):
    try:
        print("instance.file.name", instance.file.name)
        print("instance.file.path", instance.file.path)
        print("instance.uuid", instance.uuid)
        if instance.file.name.split('.')[-1] == 'zip':
            print("zip")
            gpkg_path = instance.file.path.replace('.zip', '.gpkg')
            print("gpkg_path", gpkg_path)
            with fiona.io.ZipMemoryFile(instance.file) as src:
                layers = src.listlayers()
                layer = src.open(layer=layers[0])
                print("layer", layer)
                with fiona.open(
                    gpkg_path,
                    mode="w",
                    driver="GPKG",
                    schema=layer.schema,
                    crs=layer.crs
                ) as dst:
                    for feature in layer:
                        dst.write(feature)

                    instance.file = instance.file.path.replace('.zip', '.gpkg')
                    instance.file = os.path.join('parcel_vector_files', str(instance.uuid) + '.gpkg')
                    print("instance.file", instance.file)

                    instance.save_due_to_update_geom = True
                    instance.save()
    except Exception as e:
        raise ValidationError("fix_format Error al procesar el formato: {}".format(str(e)))


def fix_crs(instance):
    try:
        with fiona.open(instance.file.path) as src:
            crs_dst = from_epsg(settings.EUDR_DATA_FEATURES_SRID)

            with fiona.open(
                instance.file.path + '-final',
                mode="w",
                driver=src.driver,
                schema=src.schema.copy(),
                crs=crs_dst
            ) as dst:
                for feature in src:
                    geometry = feature['geometry']
                    reprojected_geometry = transform_geom(src.crs, crs_dst, geometry)
                    feature['geometry'] = reprojected_geometry
                    dst.write(feature)

        # Elimina el archivo original y renombra el archivo final
        os.remove(instance.file.path)
        shutil.move(instance.file.path + '-final', instance.file.path)
        instance.save_due_to_update_geom = True

    except fiona.errors.DriverError as e:
        raise ValidationError("fix_crs Error al abrir el archivo con Fiona: {}".format(str(e)))
    except Exception as e:
        raise ValidationError("fix_crs Error al procesar el archivo: {}".format(str(e)))


def get_geom_from_file(instance):
    try:
        with fiona.open(instance.file.path) as src:
            for feature in src:
                fiona_geometry = feature['geometry']
                shapely_geometry = shape(fiona_geometry)
                wkt_representation = shapely_geometry.wkt
                return wkt_representation
    except Exception:
        raise ValidationError("Error al leer archivo")


def uuid_file_path(instance, filename):
    """
    Returns the file path for the FileField upload_to parameter,
    using the UUID of the instance as the filename.
    """
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('parcel_vector_files', filename)
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
    Returns the file path for the FileField upload_to parameter using the UUID of the instance as the filename.
    :param instance:
    :param filename:
    :return: file_path
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
    Returns the file path for the FileField upload_to parameter using the UUID of the instance as the filename.
    :param instance:
    :param filename:
    :return: file_path
    """
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('verification_images/rgb_2021/', filename)
    return file_path


def set_image_path(instance, filename, path):
    """
    Returns the file path for the FileField upload_to parameter using the UUID of the instance as the filename.
    :param instance:
    :param filename:
    :param path:
    :return: file_path
    """
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join(f'forestiffy', path, filename)
    return file_path
