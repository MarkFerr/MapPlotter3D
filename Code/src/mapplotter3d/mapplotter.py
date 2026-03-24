import os
import logging
from vedo import Plotter, LegendBox, Mesh, color_map
import matplotlib
from pathlib import Path

from mapplotter3d.io.data_reader import read_file
from mapplotter3d.validation.data_row_checks import check_missing_row_names
from mapplotter3d.geometry.mesh import build_meshes
from mapplotter3d.utils.mesh_plotter import generate_plot
from mapplotter3d.geo_info.geo_json_finder import find_fitting_geoJSON
from mapplotter3d.io.downloader import download_geojson_temp

#* set Logging
logger = logging.getLogger(__name__)


def run_mapplotter(data_path, loc_column, plot_key):
    

    #* Dir Setup
    PROJECT_ROOT = Path(__file__).resolve().parents[3] # should point to MapPlotter3D dir
    #TMP_DIR = PROJECT_ROOT / "Data" / "tmp"
    OUT_DIR = PROJECT_ROOT / "Output"
    
    #* Load Data
    logger.info("Loading data")
    df = read_file(data_path)
    logger.info(f"DataFrame found with keys: {df.keys()}")
    df_reduced = df[[loc_column, plot_key]]

   
    #* Load GeoJSON
    geoJSON_metadata = find_fitting_geoJSON(df_reduced[loc_column])

    if geoJSON_metadata["id"] == "WORLD-ADM0-GEOBOUNDARIES":
        logger.info("Loading Worldmap")
        geo_df = read_file("Code\\src\\mapplotter3d\\geo_info\\geoBoundariesCGAZ_ADM0.geojson")
    else:
        geojson_path = download_geojson_temp(geoJSON_metadata["geojsonUrl"])
        # geojson_path = "C:\\Users\\Mark\\VisualStudioProjects\\MapPlotter3D\\MapPlotter3D\\Data\\Zone_maps\\ADM2to5\\geoBoundaries-DEU-ADM3.geojson"   #os.path.join("C:", "Users", "Mark", "VisualStudioProjects", "MapPlotter3D", "MapPlotter3D", "Data", "Zone_maps", "geoBoundaries-DEU-ADM3.geojson")
        geo_df = read_file(geojson_path)

    # #* Check completeness
    # check_missing_row_names(df_reduced, geo_df)

    #* Generate Objects
    map = build_meshes(geo_df, df, loc_column, plot_key, missing_rows=geoJSON_metadata["missing"])

    #* Generate Plot
    generate_plot(map)


def get_mapplott(df, loc_col, val_col, label_col):
    logger.info(f"DataFrame found with keys: {df.keys()}")
    df_reduced = df[[loc_col, val_col]]

    geoJSON_metadata = find_fitting_geoJSON(df_reduced[loc_col])

    if geoJSON_metadata["id"] == "WORLD-ADM0-GEOBOUNDARIES":
        logger.info("Loading Worldmap")
        geo_df = read_file("Code\\src\\mapplotter3d\\geo_info\\geoBoundariesCGAZ_ADM0.geojson")
    else:
        geojson_path = download_geojson_temp(geoJSON_metadata["geojsonUrl"])
        geo_df = read_file(geojson_path)

    map_res = build_meshes(
        geo_df,
        df,
        loc_col,
        val_col,
        missing_rows=geoJSON_metadata["missing"],
    )

    return map_res


def build_vedo_actors(map_res):
    actors = []

    for mesh in map_res.map_objects:
        actor = Mesh(mesh.mesh)
        color = color_map(
            mesh.plot_value,
            matplotlib.colormaps["jet"],
            0,
            map_res.max_value,
        )
        actor.c(color).alpha(1.0).lw(0)
        actor.name = mesh.shape_name
        actor.info = (
            f"Shape_name: {mesh.shape_name}\n"
            f"Value: {mesh.value}\n"
            f"shape_id: {mesh.shape_id}"
        )
        actors.append(actor)

    return actors