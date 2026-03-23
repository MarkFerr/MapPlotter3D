import geopandas
import json
import logging


#* set Logging
logger = logging.getLogger(__name__)

def _load_geo_metadata(filepath:str = "Code/src/mapplotter3d/geo_info/geo_layers copy.json") -> dict:
    logger.info("Loading Geo-Metadata")
    with open(filepath, encoding="utf-8") as json_data:
        data = json.load(json_data)
        json_data.close()
        return data


def find_fitting_geoJSON(shapenames) -> dict:
    data_set = set(shapenames)

    geoJSON_data = _load_geo_metadata()

    best_geoJSON_id = None
    best_match_count = 0
    best_missing_shapes = None
    best_geojsonUrl = None

    logger.info("Starting search for best geoJSON")
    for d in geoJSON_data:
        shapes = set(d.get("shapeNames", []))

        matches = len(data_set & shapes)
        missing = data_set - shapes

        # perfect coverage → stop searching
        if matches == len(data_set):
            best_match_count = matches
            best_geoJSON_id = d["id"]
            best_missing_shapes = set()
            best_geojsonUrl = d["geojsonUrl"]
            break

        if matches > best_match_count:
            best_match_count = matches
            best_geoJSON_id = d["id"]
            best_missing_shapes = missing
            best_geojsonUrl = d["geojsonUrl"]
    result = {
        "id": best_geoJSON_id,
        "matching_count": best_match_count,
        "missing": best_missing_shapes,
        "geojsonUrl": best_geojsonUrl
        }
    logger.info(f"Best match found: {result}")
    return result
    