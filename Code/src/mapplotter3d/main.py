#import Files
import os
import logging
import sys

from mapplotter3d.io.data_reader import read_file
from validation.data_row_checks import check_missing_row_names


#normalize Plot to:
norm = 10000

#height factor to calculate data
height_factor = 0

max_height = 0


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(levelname)s | %(name)s | %(message)s",    #%(asctime)s | 
        handlers=[logging.StreamHandler(sys.stdout)],
    )

def create_obj_from_data(year, month, dataname, location=None):
    year_data = data_reader.y_pickle_files_dict[year]
    data = year_data['yellow_pickle_data_'+ str(year) + '_' + str(month) + '.pickle']
    #print(y_data_2023)
    if location is None:
        max_value = max(inner_dict[dataname] for inner_dict in data.values())
    else:   #this is for originID and destinationID
        location_data = data[location]
        data = location_data[dataname]
        max_value = max(data.values())
    global height_factor
    height_factor = max_value/norm

    for index, row in geoJSON_to_3d_obj.gdf.iterrows():
        location_id = row['LocationID']
        borough = row['borough']
        geometry = row['geometry']
        
        try:
            location_data = data[location_id]
            if location is None:
                height = location_data[dataname]/max_value * norm
            else:
                height = location_data/max_value * norm
            #if height > max_height:
            #    max_height = height
        except KeyError:
            height = 0

        #print(f"LocationID: {location_id}")
        #print(f"Geometry: {geometry}\n")

        if geometry.geom_type == 'Polygon':
            x, y = geometry.exterior.xy
            #plt.plot(x, y, label=f'Polygon {index}')
            geoJSON_to_3d_obj.create_obj_from_POLYGON(x,y,borough,location_id, height)
            #geoJSON_to_3d_obj.create_obj_from_POLYGON(x,y,borough,location_id, 10000)
        elif geometry.geom_type == 'MultiPolygon':
            vertices_list = []
            for polygon_part in geometry.geoms:
                #x, y = polygon_part.exterior.xy
                coordinates = list(polygon_part.exterior.coords)
                flattened_coordinates = [(x, y, 0.0) for x, y in coordinates]

                # Extract interior coordinates from the polygon (holes)
                interior_coordinates = [list(interior.coords) for interior in polygon_part.interiors]

                # Flatten interior coordinates with z=0
                flattened_interiors = [[(x, y, 0.0) for x, y in interior] for interior in interior_coordinates]
                #z = np.zeros(len(x))
                #vertices = np.array(list(zip(x,y,z)))
                #vertices_list.append(vertices)
                vertices_list.append(flattened_coordinates)
                vertices_list.extend(flattened_interiors)
            for polygon_part in geometry.geoms:
                #x, y = polygon_part.exterior.xy
                coordinates = list(polygon_part.exterior.coords)
                flattened_coordinates = [(x, y, height) for x, y in coordinates]

                # Extract interior coordinates from the polygon (holes)
                interior_coordinates = [list(interior.coords) for interior in polygon_part.interiors]

                # Flatten interior coordinates with z=0
                flattened_interiors = [[(x, y, 0.0) for x, y in interior] for interior in interior_coordinates]
                #z = np.zeros(len(x))
                #vertices = np.array(list(zip(x,y,z)))
                #vertices_list.append(vertices)
                vertices_list.append(flattened_coordinates)
                vertices_list.extend(flattened_interiors)
            geoJSON_to_3d_obj.create_obj_from_MULTIPOLYGON(vertices_list,borough,location_id)


def main():
    data_path = os.path.join("Data", "Data", "municipality_test_data.csv")
    geojson_path = os.path.join("Data", "Zone_maps", "geoBoundaries-DEU-ADM3.geojson")
    plot_key = "population_test"


    #* set Logging
    setup_logging()

    #* Load Data
    #TODO get Path from call
    data_path = "C:\\Users\\Mark\\VisualStudioProjects\\MapPlotter3D\\MapPlotter3D\\Data\\Data\\municipality_test_data.csv"#os.path.join("C:", "Users", "Mark", "VisualStudioProjects", "MapPlotter3D", "MapPlotter3D", "Data", "Data", "municipality_test_data.csv")
    df = read_file(data_path)

    #* Load GeoJSON
    #TODO get Path from call
    geojson_path = "C:\\Users\\Mark\\VisualStudioProjects\\MapPlotter3D\\MapPlotter3D\\Data\\Zone_maps\\geoBoundaries-DEU-ADM3.geojson"   #os.path.join("C:", "Users", "Mark", "VisualStudioProjects", "MapPlotter3D", "MapPlotter3D", "Data", "Zone_maps", "geoBoundaries-DEU-ADM3.geojson")
    geo_df = read_file(geojson_path)

    #* Check completeness
    check_missing_row_names(df, geo_df)

    #* Start plotting
    

    # global height_factor
    # data_reader.load()  #load all files from 2014 - 2023
    # year_to_inspect = 2014
    # month_to_inspect = 12
    # data_to_inspect = 'destinationID'
    # id_to_inspect = 3   # only needed, if data_to_inspect == destinationID or originID
    # create_obj_from_data(year_to_inspect, month_to_inspect, data_to_inspect, id_to_inspect)    #create .obj files from specific year, month, data to be inspected and if needed specific location that is to be looked at (for originID & destinationID)
    # #create_obj_from_data(2014,4,'total_trip_count',)    #create .obj files from specific year, month, data to be inspected and if needed specific location that is to be looked at (for originID & destinationID)
    # unit = ''   #Unit of data to be shown
    # #plot_objects.plot_saved_obj_vedo(norm, height_factor, unit, False,True , id_to_inspect)  #plot the .obj files with a normalized height, to "norm", add height factor to recreate value, add unit to show unit, add Arrows??, origin of arrows
    # plot_objects.plot_saved_obj_vedo(norm, height_factor, unit, False,True , id_to_inspect)

if __name__ == "__main__":
    main()