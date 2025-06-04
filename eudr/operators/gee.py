from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.conf import settings
from django.views import View
import ee
import datetime
from django.utils import timezone
import httpx
from shapely.geometry import shape, Polygon as ShapelyPolygon, MultiPolygon as ShapelyMultiPolygon
from django.contrib.gis.geos import GEOSGeometry
import matplotlib.pyplot as plt


# Initialize the Earth Engine library


class DemoEarthEngineDataView(View):
    @staticmethod
    def get(request):
        today = timezone.now()
        bbox = [-102.4284588567301, 19.39364355991117, -102.40229546836717, 19.418225860404355]
        thumb_url = get_ndvi_image(bbox, None, today)
        return JsonResponse({'map_url': thumb_url})


def get_rgb_thumb_url(image, region, dimensions=2600):
    bands = ['B4', 'B3', 'B2']
    image_stats = image.reduceRegion(ee.Reducer.minMax(), region, scale=10)

    minRed = ee.Number(image_stats.get('B4_min'))
    maxRed = ee.Number(image_stats.get('B4_max'))
    minGreen = ee.Number(image_stats.get('B3_min'))
    maxGreen = ee.Number(image_stats.get('B3_max'))
    minBlue = ee.Number(image_stats.get('B2_min'))
    maxBlue = ee.Number(image_stats.get('B2_max'))

    minAdjusted = ee.List([minRed, minGreen, minBlue]).reduce(ee.Reducer.min())
    maxAdjusted = ee.List([maxRed, maxGreen, maxBlue]).reduce(ee.Reducer.max())

    if dimensions > 100:
        try:
            return image.visualize(min=minAdjusted, max=maxAdjusted, bands=bands).getThumbURL({
                'min': 1,
                'max': 100,
                'dimensions': dimensions,
                'region': region,
            })
        except Exception as e:
            print("Exception getThumbURL", e)
            return get_ndvi_thumb_url(image, region, dimensions - 200)
    else:
        raise ValidationError("Error al obtener la imagen de Earth Engine")


def get_ndvi_thumb_url(image, region, palette, dimensions=2600):
    image_stats = image.reduceRegion(ee.Reducer.minMax(), region, scale=10)
    min_value = image_stats.get('NDVI_min').getInfo()
    max_value = image_stats.get('NDVI_max').getInfo()

    if dimensions > 100:
        try:
            return image.visualize(min=min_value, max=max_value, palette=palette).getThumbURL({
                'min': 1,
                'max': 300,
                'dimensions': dimensions,
                'region': region,
            })
        except Exception as e:
            print("Exception getThumbURL", e)
            return get_ndvi_thumb_url(image, region, palette, dimensions - 200)
    else:
        raise ValidationError("Error al obtener la imagen de Earth Engine")


def vectorize_ndvi_difference_areas(ndvi_difference, threshold, geom, bbox):
    ee_geom = ee.Geometry.MultiPolygon(geom.coords)
    ee_region = ee.Geometry.Rectangle(*bbox)

    # Calculate degradation difference and connected components
    degradation_difference = ndvi_difference.lte(threshold)
    degradation_areas = degradation_difference.connectedComponents(ee.Kernel.plus(1), 256)
    clip_degradation_area = degradation_areas.clip(ee_region)

    # Vectorize the polygons
    vectorized_polygons = clip_degradation_area.reduceToVectors(
        geometryType='polygon',
        eightConnected=False,
        labelProperty='label',
        reducer=ee.Reducer.max(),
        scale=10
    )

    for i in vectorized_polygons.getInfo()['features']:
        print("vectorized_polygons", i['properties'])

    filtered_polygons = vectorized_polygons.filter(ee.Filter.gte('max', 1))

    # Clip the polygons to the specified geom with an error margin
    clipped_polygons = filtered_polygons.map(lambda feature: feature.intersection(ee_geom, ee.ErrorMargin(1)))

    # Convert clipping geometry to Shapely polygon
    clipping_geom = shape(ee_geom.getInfo())

    # Retrieve the features and convert them to Shapely geometries
    features = ee.FeatureCollection(clipped_polygons)
    features_list = features.getInfo()['features']
    geometries = []

    for feature in features_list:
        feat = shape(feature['geometry'])
        # print("feat", feat['properties'])
        if isinstance(feat, ShapelyPolygon):
            if not feat.equals(clipping_geom):
                geometries.append(feat)
        elif isinstance(feat, ShapelyMultiPolygon):
            print("multi_polygon", feat)
            if not feat.equals(clipping_geom):
                for polygon in feat.geoms:
                    geometries.append(polygon)
        else:
            print(f"Unsupported geometry type: {feature['geometry']['type']}")

    # Create a ShapelyMultiPolygon from the list of polygons
    if geometries:
        shapely_multipolygon = ShapelyMultiPolygon(geometries)
    else:
        shapely_multipolygon = None

    # Return the Well-Known Text (WKT) representation of the MultiPolygon
    return shapely_multipolygon.wkt if shapely_multipolygon else None


def get_rgb_image(bbox, multipolygon, date):
    past = date - datetime.timedelta(days=30)
    ee.Geometry.MultiPolygon(multipolygon)
    region = ee.Geometry.Rectangle(*bbox)
    bands = ['B4', 'B3', 'B2']

    collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(region) \
        .filterDate(past, date) \
        .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 12) \
        .sort('CLOUD_COVER', True)

    median_image = collection.median()
    image_clipped = median_image.clip(region)

    true_color_image = image_clipped.select(bands)

    thumb_url_ndvi = get_rgb_thumb_url(true_color_image, region)

    print("thumb_url_ndvi", thumb_url_ndvi)

    r = httpx.get(thumb_url_ndvi, timeout=600)
    if r.status_code != 200:
        raise ValidationError("Error al obtener la imagen de Earth Engine")

    print("r httpx", r)
    return r


def get_ndvi_image(bbox, multipolygon, date):
    past = date - datetime.timedelta(days=20)
    ee.Geometry.MultiPolygon(multipolygon)
    region = ee.Geometry.Rectangle(*bbox)
    palette = ['red', 'orange', 'yellow', 'green', 'darkgreen']

    collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(region) \
        .filterDate(past, date) \
        .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 12) \
        .sort('CLOUD_COVER', True)

    median_image = collection.median()
    image_clipped = median_image.clip(region)

    ndvi = image_clipped.normalizedDifference(['B8', 'B4']).rename('NDVI')

    thumb_url_ndvi = get_ndvi_thumb_url(ndvi, region, palette)
    print("thumb_url_ndvi", thumb_url_ndvi)

    r = httpx.get(thumb_url_ndvi, timeout=600)
    if r.status_code != 200:
        raise ValidationError("Error al obtener la imagen de Earth Engine")

    print("r httpx", r)
    return r


def plot_multipolygon(multipolygon, bbox):
    fig, ax = plt.subplots()
    if multipolygon:
        for polygon in multipolygon:
            x, y = zip(*polygon.coords[0])
            ax.fill(x, y, alpha=0.3, fc='red', ec='black')
    min_x, min_y, max_x, max_y = bbox
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax


def get_ndvi_difference_image(bbox, geom):
    base = settings.EUDR_START_DATE_BASE
    past_base = base - datetime.timedelta(days=20)
    today = timezone.now()
    past_today = today - datetime.timedelta(days=20)

    region = ee.Geometry.Rectangle(*bbox)
    palette = ['#d7191c ', '#fdae61', '#fcfbbf', '#43a2ca', '#0868ac']

    past_collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(region) \
        .filterDate(past_base, base) \
        .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 12) \
        .sort('CLOUD_COVER', True)

    past_median_image = past_collection.median()
    past_image_clipped = past_median_image.clip(region)
    past_ndvi = past_image_clipped.normalizedDifference(['B8', 'B4']).rename('PAST_NDVI')

    current_collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(region) \
        .filterDate(past_today, today) \
        .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 12) \
        .sort('CLOUD_COVER', True)

    current_median_image = current_collection.median()
    current_image_clipped = current_median_image.clip(region)
    current_ndvi = current_image_clipped.normalizedDifference(['B8', 'B4']).rename('CURRENT_NDVI')
    ndvi_difference = current_ndvi.subtract(past_ndvi).rename('NDVI')
    thumb_url_ndvi_difference = get_ndvi_thumb_url(ndvi_difference, region, palette)
    difference_vectors = vectorize_ndvi_difference_areas(ndvi_difference, -0.32, geom, bbox)

    r = httpx.get(thumb_url_ndvi_difference, timeout=600)

    if r.status_code != 200:
        raise ValidationError("Error al obtener la imagen de Earth Engine")

    return r, difference_vectors
