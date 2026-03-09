#import Files
import os
import logging
import sys
from pathlib import Path

from mapplotter3d.io.data_reader import read_file
from mapplotter3d.validation.data_row_checks import check_missing_row_names
from mapplotter3d.geometry.mesh import build_meshes
from mapplotter3d.utils.mesh_plotter import generate_plot


#normalize Plot to:
norm = 10000

#height factor to calculate data
height_factor = 0

max_height = 0


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",    #
        handlers=[logging.StreamHandler(sys.stdout)],
    )

def main():

    data_path = os.path.join("Data", "Data", "municipality_test_data.csv")
    geojson_path = os.path.join("Data", "Zone_maps", "geoBoundaries-DEU-ADM3.geojson")
    plot_key = "population_test"

    #* set Logging
    setup_logging()
    logger = logging.getLogger(__name__)

    #* Dir Setup
    PROJECT_ROOT = Path(__file__).resolve().parents[3] # should point to MapPlotter3D dir
    #TMP_DIR = PROJECT_ROOT / "Data" / "tmp"
    OUT_DIR = PROJECT_ROOT / "Output"
    
    #* Load Data
    #TODO get Path from call
    logger.info("Loading data")
    data_path = "C:\\Users\\Mark\\VisualStudioProjects\\MapPlotter3D\\MapPlotter3D\\Data\\Data\\municipality_test_data.csv"#os.path.join("C:", "Users", "Mark", "VisualStudioProjects", "MapPlotter3D", "MapPlotter3D", "Data", "Data", "municipality_test_data.csv")
    df = read_file(data_path)
    df_reduced = df[["municipality", plot_key]]
   
    #* Load GeoJSON
    #TODO get Path from call
    logger.info("Loading map data")
    geojson_path = "C:\\Users\\Mark\\VisualStudioProjects\\MapPlotter3D\\MapPlotter3D\\Data\\Zone_maps\\geoBoundaries-DEU-ADM3.geojson"   #os.path.join("C:", "Users", "Mark", "VisualStudioProjects", "MapPlotter3D", "MapPlotter3D", "Data", "Zone_maps", "geoBoundaries-DEU-ADM3.geojson")
    geo_df, map_name = read_file(geojson_path)

    #* Check completeness
    check_missing_row_names(df_reduced, geo_df)

    #* Generate Objects
    map = build_meshes(geo_df, df, plot_key, map_name)

    #* Generate Plot
    generate_plot(map)

if __name__ == "__main__":
    main()