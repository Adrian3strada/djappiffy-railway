from django.core.exceptions import ValidationError
import fiona
from django.core.files.base import ContentFile
from fiona.transform import transform_geom
from fiona.crs import from_epsg
from django.conf import settings
import os
from shapely.geometry import shape
from functools import wraps
from fiona.io import ZipMemoryFile
from django.core.files.storage import default_storage
from tempfile import mkstemp, NamedTemporaryFile
from fiona.io import MemoryFile
fiona.drvsupport.supported_drivers['KML'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'


def validate_geom_vector_file(value):
    try:
        file_content = value.read()
        file_extension = value.name.split('.')[-1].lower()

        if file_extension in ['gpkg', 'geojson']:
            with fiona.BytesCollection(file_content) as file:
                if file.schema['geometry'] not in ['Polygon', 'MultiPolygon']:
                    raise ValidationError("Geometría inválida")
        elif file_extension == 'zip':
            with fiona.io.ZipMemoryFile(file_content) as memfile:
                layers = memfile.listlayers()
                layer = memfile.open(layer=layers[0])
                if layer.schema['geometry'] not in ['Polygon', 'MultiPolygon']:
                    raise ValidationError("Geometría inválida")
        elif file_extension == 'kml':
            print("kml")
            with fiona.BytesCollection(file_content, driver='LIBKML') as file:
                print("file", file)
                if file.schema['geometry'] not in ['Polygon', 'MultiPolygon']:
                    raise ValidationError("Geometría inválida")
        elif file_extension == 'kmz':
            with ZipMemoryFile(file_content) as memfile:
                layers = memfile.listlayers()
                layer = memfile.open(layer=layers[0], driver='LIBKML')
                if layer.schema['geometry'] not in ['Polygon', 'MultiPolygon']:
                    raise ValidationError("Geometría inválida")
        else:
            raise ValidationError("El archivo no tiene formato válido")
    except Exception as e:
        try:
            if e.args and e.args[0] == "Geometría inválida":
                ex = "Geometría inválida"
            else:
                ex = "Formato inválido"
        except Exception as eee:
            ex = eee
        raise ValidationError(f"El archivo no es un archivo espacial válido: {ex}")


def to_multipolygon(instance):
    try:
        file_content = default_storage.open(instance.file.name).read()

        with fiona.BytesCollection(file_content) as src:
            schema = src.schema.copy()
            schema['geometry'] = 'MultiPolygon'

            with MemoryFile() as memfile:
                with memfile.open(
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

                generated_file = memfile.read()
                new_file_path = default_storage.get_available_name(instance.file.name)
                default_storage.save(new_file_path, ContentFile(generated_file))

                instance.file.name = new_file_path

    except fiona.errors.DriverError as e:
        raise ValidationError("Error al abrir el archivo con Fiona: {}".format(str(e)))
    except Exception as e:
        raise ValidationError("Error al procesar el archivo: {}".format(str(e)))


def to_polygon(instance):
    try:
        file_content = default_storage.open(instance.file.name).read()

        with fiona.BytesCollection(file_content) as src:
            schema = src.schema.copy()
            schema['geometry'] = 'Polygon'

            with MemoryFile() as memfile:
                with memfile.open(
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

                generated_file = memfile.read()
                new_file_path = default_storage.get_available_name(instance.file.name)
                default_storage.save(new_file_path, ContentFile(generated_file))

                print("polygon new_file_path", new_file_path)

                instance.file.name = new_file_path

    except fiona.errors.DriverError as e:
        raise ValidationError("to_polygon() fiona DriverError: {}".format(str(e)))
    except Exception as e:
        raise ValidationError("to_polygon() Error al procesar el archivo: {}".format(str(e)))


def fix_format(instance):
    try:
        # Leer el contenido del archivo original
        file_content = default_storage.open(instance.file.name).read()
        file_extension = instance.file.name.split('.')[-1].lower()

        # Verificar si el archivo es un ZIP
        if file_extension == 'zip':
            with ZipMemoryFile(file_content) as src:
                layers = src.listlayers()
                layer = src.open(layer=layers[0])

                with MemoryFile() as memfile:
                    with memfile.open(
                        driver="GPKG",
                        schema=layer.schema,
                        crs=layer.crs
                    ) as dst:
                        for feature in layer:
                            dst.write(feature)

                    generated_file = memfile.read()
                    new_file_path = default_storage.get_available_name(instance.file.name.replace('.zip', '.gpkg'))
                    default_storage.save(new_file_path, ContentFile(generated_file))

                    instance.file.name = new_file_path

        elif file_extension == 'kml':
            with fiona.BytesCollection(file_content, driver='LIBKML') as src:
                with MemoryFile() as memfile:
                    with memfile.open(
                        driver="GPKG",
                        schema=src.schema,
                        crs=src.crs
                    ) as dst:
                        for feature in src:
                            dst.write(feature)

                    generated_file = memfile.read()
                    new_file_path = default_storage.get_available_name(instance.file.name.replace('.kml', '.gpkg'))
                    default_storage.save(new_file_path, ContentFile(generated_file))

                    instance.file.name = new_file_path

        elif file_extension == 'kmz':
            with ZipMemoryFile(file_content) as src:
                layers = src.listlayers()
                layer = src.open(layer=layers[0], driver='LIBKML')

                with MemoryFile() as memfile:
                    with memfile.open(
                        driver="GPKG",
                        schema=layer.schema,
                        crs=layer.crs
                    ) as dst:
                        for feature in layer:
                            dst.write(feature)

                    generated_file = memfile.read()
                    new_file_path = default_storage.get_available_name(instance.file.name.replace('.kmz', '.gpkg'))
                    default_storage.save(new_file_path, ContentFile(generated_file))

                    instance.file.name = new_file_path

    except Exception as e:
        raise ValidationError(f"fix_format Error al procesar el formato: {str(e)}")


def fix_crs(instance):
    try:
        file_content = default_storage.open(instance.file.name).read()

        with fiona.BytesCollection(file_content) as src:
            crs_dst = from_epsg(settings.EUDR_DATA_FEATURES_SRID)

            with MemoryFile() as memfile:
                with memfile.open(
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

                generated_file = memfile.read()
                new_file_path = default_storage.get_available_name(instance.file.name)
                default_storage.save(new_file_path, ContentFile(generated_file))

                instance.file.name = new_file_path

    except fiona.errors.DriverError as e:
        raise ValidationError("fix_crs() fiona DriverError: {}".format(str(e)))
    except Exception as e:
        raise ValidationError("fix_crs() Error al procesar el archivo: {}".format(str(e)))


def get_geom_from_file(instance):
    try:
        file_content = default_storage.open(instance.file.name).read()

        with fiona.BytesCollection(file_content) as src:
            for feature in src:
                fiona_geometry = feature['geometry']
                shapely_geometry = shape(fiona_geometry)
                wkt_representation = shapely_geometry.wkt
                print("wkt_representation", wkt_representation)
                return wkt_representation
    except Exception as e:
        raise ValidationError("Error al leer archivo: {}".format(str(e)))


def uuid_file_path(instance, filename):
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('parcel_vector_files', filename)
    return file_path


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
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('verification_images/rgb_2020/', filename)
    return file_path


@set_year_path("2021")
def set_rgb_2021_image_path(instance, filename):
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('verification_images/rgb_2021/', filename)
    return file_path


def set_image_path(instance, filename, path):
    ext = filename.split('.')[-1]
    if not ext:
        raise ValidationError("El archivo debe tener extensión")
    filename = f"{instance.uuid}.{ext}"
    file_path = os.path.join('forestiffy', path, filename)
    return file_path

