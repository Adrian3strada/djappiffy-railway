import requests
import json
import geojson

def fetch_all_data(url, params=None):
    if params is None:
        params = {}
    params['f'] = 'json'
    params['resultOffset'] = 0
    all_data = []
    while True:
        print(f'Fetching data from {params["resultOffset"]}')
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        all_data.extend(data.get('features', []))
        if 'exceededTransferLimit' in data and data['exceededTransferLimit']:
            params['resultOffset'] += params['resultRecordCount']
        else:
            break
    return all_data

def convert_to_geojson_geometry(geometry):
    if 'x' in geometry and 'y' in geometry:
        return geojson.Point((geometry['x'], geometry['y']))
    elif 'rings' in geometry:
        return geojson.Polygon(geometry['rings'])
    elif 'paths' in geometry:
        return geojson.LineString(geometry['paths'][0])
    else:
        raise ValueError(f"Unsupported geometry type: {geometry}")

def save_to_geojson(data, filename):
    features = []
    for feature in data:
        geometry = convert_to_geojson_geometry(feature['geometry'])
        properties = feature['attributes']
        features.append(geojson.Feature(geometry=geometry, properties=properties))
    feature_collection = geojson.FeatureCollection(features)
    with open(filename, 'w') as f:
        geojson.dump(feature_collection, f)

if __name__ == "__main__":
    url = 'https://services.arcgis.com/azYCYQPfHWnM02Go/arcgis/rest/services/Fincas_11082024/FeatureServer/0/query'
    params = {
        'where': '1=1',
        'outFields': '*',
        'resultRecordCount': 1000
    }
    all_data = fetch_all_data(url, params)
    save_to_geojson(all_data, 'all_data.geojson')
