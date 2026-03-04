#import Files
import geoJSON_to_3d_obj
import data_reader
import plot_objects

#normalize Plot to:
norm = 10000

#height factor to calculate data
height_factor = 0

data_names = ['LocationID', 'PUvendorID', 'DOvendorID', 'destinationID', 'originID', 
              'avg_pickup_datetime','avg_dropof_datetime', 
              'avg_leaving_passenger_count', 'avg_arriving_passenger_count', 'total_leaving_passenger_count', 'total_arriving_passenger_count', 
              'avg_leaving_trip_distance', 'avg_arriving_trip_distance', 'total_leaving_trip_distance', 'total_arriving_trip_distance', 
              'leaving_RateCodeID', 'arriving_RateCodeID', 'leaving_store_and_fwd_flag', 'arriving_store_and_fwd_flag', 
              'leaving_payment_type', 'arriving_payment_type', 
              'avg_leaving_fare_amount', 'avg_arriving_fare_amount', 'total_leaving_fare_amount', 'total_arriving_fare_amount', 
              'avg_leaving_extra', 'avg_arriving_extra', 'total_leaving_extra', 'total_arriving_extra', 
              'avg_leaving_mta_tax', 'avg_arriving_mta_tax', 'total_leaving_mta_tax', 'total_arriving_mta_tax', 
              'avg_leaving_tip_amount', 'avg_arriving_tip_amount', 'total_leaving_tip_amount', 'total_arriving_tip_amount', 
              'avg_leaving_tolls_amount', 'avg_arriving_tolls_amount', 'total_leaving_tolls_amount', 'total_arriving_tolls_amount', 
              'avg_leaving_improvement_surcharge', 'avg_arriving_improvement_surcharge', 'total_leaving_improvement_surcharge', 'total_arriving_improvement_surcharge', 
              'avg_leaving_total_amount', 'avg_arriving_total_amount', 'total_leaving_total_amount', 'total_arriving_total_amount', 
              'avg_leaving_congestion_surcharge', 'avg_arriving_congestion_surcharge', 'total_leaving_congestion_surcharge', 'total_arriving_congestion_surcharge', 
              'avg_leaving_airport_fee', 'avg_arriving_airport_fee', 'total_leaving_airport_fee', 'total_arriving_airport_fee', 
              'avg_leaving_ehail_fee', 'avg_arriving_ehail_fee', 'total_leaving_ehail_fee', 'total_arriving_ehail_fee', 
              'total_trip_count', 'trips_inside_Location', 'trips_outgoing_Location', 'trips_incoming_Location']

max_height = 0


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
    global height_factor
    data_reader.load()  #load all files from 2014 - 2023
    year_to_inspect = 2014
    month_to_inspect = 12
    data_to_inspect = 'destinationID'
    id_to_inspect = 3   # only needed, if data_to_inspect == destinationID or originID
    create_obj_from_data(year_to_inspect, month_to_inspect, data_to_inspect, id_to_inspect)    #create .obj files from specific year, month, data to be inspected and if needed specific location that is to be looked at (for originID & destinationID)
    #create_obj_from_data(2014,4,'total_trip_count',)    #create .obj files from specific year, month, data to be inspected and if needed specific location that is to be looked at (for originID & destinationID)
    unit = ''   #Unit of data to be shown
    #plot_objects.plot_saved_obj_vedo(norm, height_factor, unit, False,True , id_to_inspect)  #plot the .obj files with a normalized height, to "norm", add height factor to recreate value, add unit to show unit, add Arrows??, origin of arrows
    plot_objects.plot_saved_obj_vedo(norm, height_factor, unit, False,True , id_to_inspect)

if __name__ == "__main__":
    main()