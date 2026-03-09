import pandas as pd
import geopandas as gpd
import os
import pickle
from datetime import datetime
import csv
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)



def read_geojson(path):
    
    filename = path.stem
    split_filename = filename.split("-")
    map_name = f"{split_filename[1]}-{split_filename[2]}"
    gdf = gpd.read_file(path)
    return gdf, map_name

READERS = {
    ".csv": pd.read_csv,
    ".pickle": pd.read_pickle,
    ".geojson": read_geojson #gpd.read_file,
}


def read_file(file: str, **kwargs) -> pd.DataFrame:
    path = Path(file)

    if not path.exists():
        raise FileNotFoundError(file)

    suffix = path.suffix.lower()
    logger.info("Found suffix '%s'", suffix)
    if suffix not in READERS:
        raise ValueError(f"Unsupported format: {suffix}")

    reader = READERS[suffix]
    return reader(path, **kwargs)




def print_first_row_of_first_file(folder_path):

    # Get a list of all files in the folder
    file_list = [file for file in os.listdir(folder_path) if file.endswith('.parquet')]

    # Read the .parquet file into a DataFrame
    df = pd.read_parquet(folder_path + '\\' + file_list[0])


    # Print the DataFrame
    #print(df)

    # Print the first 5 rows of the DataFrame
    #print(df.head())


    # Print all column names (headers)
    print(len(df.columns))
    print(df.columns)


    # Print the first row of data
    #first_row = df.iloc[1]
    #print(first_row)

def calculate_values_of_months_file(year):
    # Folder paths
    yellow_folder = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\drive_data\\Yellow\\' + str(year) + '\\'
    green_folder = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\drive_data\\Green\\' + str(year) + '\\'
    yellow_file_list = [file for file in os.listdir(yellow_folder) if file.endswith('.parquet')]
    green_file_list = [file for file in os.listdir(green_folder) if file.endswith('.parquet')]

    #yellow_pickle_filePath = str('C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\drive_data\\PickleData\\yellow_pickle_data_' + str(year) + '.pickle')
    yellow_pickle_filePath = str('C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\drive_data\\PickleData\\' + str(year) + '\\yellow_pickle_data_' + str(year) + '_')
    #green_pickle_filePath = str('C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\drive_data\\PickleData\\green_pickle_data_' + str(year) + '.pickle')
    green_pickle_filePath = str('C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\drive_data\\PickleData\\' + str(year) + '\\green_pickle_data_' + str(year) + '_')

    if not YELLOW_PU and not GREEN_PU:   # if not done already, read the yellow Pick up Data
        
        for yellow_file,green_file in zip(yellow_file_list,green_file_list):
            yellow_df = pd.read_parquet(yellow_folder + yellow_file)    #reads .parquet file to DataFrame of data of year of month
            
            yellow_first_row = yellow_df.iloc[1]
            y_date_object = yellow_first_row['tpep_dropoff_datetime']
            month = y_date_object.month
            print("Month: " + str(month))
            #initialize empty variables
            yellow_pickupData_list = {}    #init empty dictionary
            green_pickupData_list = {}
            yellow_total_trip_list = {}
            green_total_trip_list = {}
            #-----------------------------------------------Yellow Pick up
            print("Calculating Yellow Pick up...")
            puGroupDF = yellow_df.groupby('PULocationID')   #Group the file by the pick up location ID
            for group_name, group in puGroupDF:
                #print(group_name)
                total_trips = group.shape[0]
                tripcount_to_same_loc = 0
                tripcount_out_of_loc = 0
                try:
                    tripcount_to_same_loc = group['DOLocationID'].value_counts().xs(group_name)
                except KeyError as e:
                    tripcount_to_same_loc = 0

                try:    #Key 'airport_fee' from 2023 February: 'Airport_fee'
                    airportfee_mean = group['airport_fee'].mean()
                    airportfee_sum = group['airport_fee'].sum()
                except KeyError as e:
                    try:
                        airportfee_mean = group['Airport_fee'].mean()
                        airportfee_sum = group['Airport_fee'].sum()
                    except KeyError as e:
                        airportfee_mean = 0
                        airportfee_sum = 0

                #Create Dropoff list:
                dropoff_locations = group['DOLocationID']
                #dropoff_elements = dropoff_elements[dropoff_elements != group_name] #exclude this location
                unique_elements, counts = np.unique(dropoff_locations, return_counts=True)
                dropoff_counts = dict(zip(unique_elements, counts))

                tripcount_out_of_loc = total_trips - tripcount_to_same_loc
                taxi_data = {
                'LocationID': group_name,
                'PUvendorID': group['VendorID'].mode().iloc[0] if not group['VendorID'].mode().empty else None,
                'DOvendorID': 0,
                #'destinationID': group['DOLocationID'].mode().iloc[0] if not group['DOLocationID'].mode().empty else None,  #OLD! only one
                'destinationID': dropoff_counts,    # dict of dropofflocations with amount of dropoffs
                'originID': 0,
                'avg_pickup_datetime': group['tpep_pickup_datetime'].dt.time.iloc[0],
                'avg_dropof_datetime': '',
                'avg_leaving_passenger_count': group['passenger_count'].mean(),
                'avg_arriving_passenger_count': 0,
                'total_leaving_passenger_count': group['passenger_count'].sum(),
                'total_arriving_passenger_count': 0,
                'avg_leaving_trip_distance': group['trip_distance'].mean(),
                'avg_arriving_trip_distance': 0,
                'total_leaving_trip_distance': group['trip_distance'].sum(),
                'total_arriving_trip_distance': 0,
                'leaving_RateCodeID': group['RatecodeID'].mode().iloc[0] if not group['RatecodeID'].mode().empty else None,
                'arriving_RateCodeID': 0,
                'leaving_store_and_fwd_flag': group['store_and_fwd_flag'].mode().iloc[0] if not group['store_and_fwd_flag'].mode().empty else None,
                'arriving_store_and_fwd_flag': 0,
                'leaving_payment_type': group['payment_type'].mode().iloc[0] if not group['payment_type'].mode().empty else None,
                'arriving_payment_type': 0,
                'avg_leaving_fare_amount': group['fare_amount'].mean(),
                'avg_arriving_fare_amount': 0,
                'total_leaving_fare_amount': group['fare_amount'].sum(),
                'total_arriving_fare_amount': 0,
                'avg_leaving_extra': group['extra'].mean(),
                'avg_arriving_extra': 0,
                'total_leaving_extra': group['extra'].sum(),
                'total_arriving_extra': 0,
                'avg_leaving_mta_tax': group['mta_tax'].mean(),
                'avg_arriving_mta_tax': 0,
                'total_leaving_mta_tax': group['mta_tax'].sum(),
                'total_arriving_mta_tax': 0,
                'avg_leaving_tip_amount': group['tip_amount'].mean(),
                'avg_arriving_tip_amount': 0,
                'total_leaving_tip_amount': group['tip_amount'].sum(),
                'total_arriving_tip_amount': 0,
                'avg_leaving_tolls_amount': group['tolls_amount'].mean(),
                'avg_arriving_tolls_amount': 0,
                'total_leaving_tolls_amount': group['tolls_amount'].sum(),
                'total_arriving_tolls_amount': 0,
                'avg_leaving_improvement_surcharge': group['improvement_surcharge'].mean(),
                'avg_arriving_improvement_surcharge': 0,
                'total_leaving_improvement_surcharge': group['improvement_surcharge'].sum(),
                'total_arriving_improvement_surcharge': 0,
                'avg_leaving_total_amount': group['total_amount'].mean(),
                'avg_arriving_total_amount': 0,
                'total_leaving_total_amount': group['total_amount'].sum(),
                'total_arriving_total_amount': 0,
                'avg_leaving_congestion_surcharge': group['congestion_surcharge'].mean(),
                'avg_arriving_congestion_surcharge': 0,
                'total_leaving_congestion_surcharge': group['congestion_surcharge'].sum(),
                'total_arriving_congestion_surcharge': 0,
                'avg_leaving_airport_fee': airportfee_mean,
                'avg_arriving_airport_fee': 0,
                'total_leaving_airport_fee': airportfee_sum,
                'total_arriving_airport_fee': 0,
                'avg_leaving_ehail_fee': 0,
                'avg_arriving_ehail_fee': 0,
                'total_leaving_ehail_fee': 0,
                'total_arriving_ehail_fee': 0,
                'total_trip_count': total_trips,
                'trips_inside_Location': tripcount_to_same_loc,   
                'trips_outgoing_Location': tripcount_out_of_loc, 
                'trips_incoming_Location': 0
                }
                yellow_pickupData_list[group_name] = taxi_data
            #-----------------------------------------------Yellow Drop Off
            print("Calculating Yellow Drop off...")
            yellow_doGroupDF = yellow_df.groupby('DOLocationID')
            for group_name, group in yellow_doGroupDF:
                #print(group_name)
                total_trips = group.shape[0]
                tripcount_to_same_loc = 0
                tripcount_out_of_loc = 0
                try:
                    tripcount_to_same_loc = group['PULocationID'].value_counts().xs(group_name) #amount of 
                except KeyError as e:
                    tripcount_to_same_loc = 0
                tripcount_from_outside_of_loc = total_trips - tripcount_to_same_loc

                try:
                    yellow_PU_data = yellow_pickupData_list[group_name]
                    #data_available = True
                except KeyError as e:
                    #print("No data for this group yet...")
                    yellow_PU_data = empty_data
                    #data_available = False

                try:    #Key 'airport_fee' from 2023 February: 'Airport_fee'
                    airportfee_mean = group['airport_fee'].mean()
                    airportfee_sum = group['airport_fee'].sum()
                except KeyError as e:
                    try:
                        airportfee_mean = group['Airport_fee'].mean()
                        airportfee_sum = group['Airport_fee'].sum()
                    except KeyError as e:
                        airportfee_mean = 0
                        airportfee_sum = 0

                #Create Pickup list:
                pickup_locations = group['PULocationID']
                #dropoff_elements = dropoff_elements[dropoff_elements != group_name] #exclude this location
                unique_elements, counts = np.unique(pickup_locations, return_counts=True)
                pickup_counts = dict(zip(unique_elements, counts))

                update_data = {
                'DOvendorID': group['VendorID'].mode().iloc[0] if not group['VendorID'].mode().empty else None, 
                #'originID': group['PULocationID'].mode().iloc[0] if not group['PULocationID'].mode().empty else None,
                'originID': pickup_counts,
                'avg_dropof_datetime': group['tpep_dropoff_datetime'].dt.time.iloc[0],
                'avg_arriving_passenger_count': group['passenger_count'].mean(),
                'total_arriving_passenger_count': group['passenger_count'].sum(),
                'avg_arriving_trip_distance': group['trip_distance'].mean(),
                'total_arriving_trip_distance': group['trip_distance'].sum(),
                'arriving_RateCodeID': group['RatecodeID'].mode().iloc[0] if not group['RatecodeID'].mode().empty else None,
                'arriving_store_and_fwd_flag': group['store_and_fwd_flag'].mode().iloc[0] if not group['store_and_fwd_flag'].mode().empty else None,
                'arriving_payment_type': group['payment_type'].mode().iloc[0] if not group['payment_type'].mode().empty else None,
                'avg_arriving_fare_amount': group['fare_amount'].mean(),
                'total_arriving_fare_amount': group['fare_amount'].sum(),
                'avg_arriving_extra': group['extra'].mean(),
                'total_arriving_extra': group['extra'].sum(),
                'avg_arriving_mta_tax': group['mta_tax'].mean(),
                'total_arriving_mta_tax': group['mta_tax'].sum(),
                'avg_arriving_tip_amount': group['tip_amount'].mean(),
                'total_arriving_tip_amount': group['tip_amount'].sum(),
                'avg_arriving_tolls_amount': group['tolls_amount'].mean(),
                'total_arriving_tolls_amount': group['tolls_amount'].sum(),
                'avg_arriving_improvement_surcharge': group['improvement_surcharge'].mean(),
                'total_arriving_improvement_surcharge': group['improvement_surcharge'].sum(),
                'avg_arriving_total_amount': group['total_amount'].mean(),
                'total_arriving_total_amount': group['total_amount'].sum(),
                'avg_arriving_congestion_surcharge': group['congestion_surcharge'].mean(),
                'total_arriving_congestion_surcharge': group['congestion_surcharge'].sum(),
                'avg_arriving_airport_fee': airportfee_mean,
                'total_arriving_airport_fee': airportfee_sum,
                'total_trip_count': yellow_PU_data['total_trip_count'] + total_trips,   
                'trips_incoming_Location': tripcount_from_outside_of_loc
                }
                yellow_PU_data.update(update_data)
            
            #-----------------------------------------------Green Pick up
            print("Calculating Green Pick up...")    
            green_df = pd.read_parquet(green_folder + green_file)    #reads .parquet file to DataFrame of data of year of month
            green_puGroupDF = green_df.groupby('PULocationID')
            for group_name, group in green_puGroupDF:
                #print(group_name)
                total_trips = group.shape[0]
                tripcount_to_same_loc = 0
                tripcount_out_of_loc = 0
                try:
                    tripcount_to_same_loc = group['DOLocationID'].value_counts().xs(group_name)
                except KeyError as e:
                    tripcount_to_same_loc = 0

                #Create Dropoff list:
                dropoff_locations = group['DOLocationID']
                #dropoff_elements = dropoff_elements[dropoff_elements != group_name] #exclude this location
                unique_elements, counts = np.unique(dropoff_locations, return_counts=True)
                dropoff_counts = dict(zip(unique_elements, counts))

                tripcount_out_of_loc = total_trips - tripcount_to_same_loc
                green_data = {
                'LocationID': group_name,
                'PUvendorID': group['VendorID'].mode().iloc[0] if not group['VendorID'].mode().empty else None,
                'DOvendorID': 0,
                #'destinationID': group['DOLocationID'].mode().iloc[0] if not group['DOLocationID'].mode().empty else None,  
                'destinationID': dropoff_counts,    # dict of dropofflocations with amount of dropoffs
                'destination'
                'originID': 0,
                'avg_pickup_datetime': group['lpep_pickup_datetime'].dt.time.iloc[0],
                'avg_dropof_datetime': '',
                'avg_leaving_passenger_count': group['passenger_count'].mean(),
                'avg_arriving_passenger_count': 0,
                'total_leaving_passenger_count': group['passenger_count'].sum(),
                'total_arriving_passenger_count': 0,
                'avg_leaving_trip_distance': group['trip_distance'].mean(),
                'avg_arriving_trip_distance': 0,
                'total_leaving_trip_distance': group['trip_distance'].sum(),
                'total_arriving_trip_distance': 0,
                'leaving_RateCodeID': group['RatecodeID'].mode().iloc[0] if not group['RatecodeID'].mode().empty else None,
                'arriving_RateCodeID': 0,
                'leaving_store_and_fwd_flag': group['store_and_fwd_flag'].mode().iloc[0] if not group['store_and_fwd_flag'].mode().empty else None,
                'arriving_store_and_fwd_flag': 0,
                'leaving_payment_type': group['payment_type'].mode().iloc[0] if not group['payment_type'].mode().empty else None,
                'arriving_payment_type': 0,
                'avg_leaving_fare_amount': group['fare_amount'].mean(),
                'avg_arriving_fare_amount': 0,
                'total_leaving_fare_amount': group['fare_amount'].sum(),
                'total_arriving_fare_amount': 0,
                'avg_leaving_extra': group['extra'].mean(),
                'avg_arriving_extra': 0,
                'total_leaving_extra': group['extra'].sum(),
                'total_arriving_extra': 0,
                'avg_leaving_mta_tax': group['mta_tax'].mean(),
                'avg_arriving_mta_tax': 0,
                'total_leaving_mta_tax': group['mta_tax'].sum(),
                'total_arriving_mta_tax': 0,
                'avg_leaving_tip_amount': group['tip_amount'].mean(),
                'avg_arriving_tip_amount': 0,
                'total_leaving_tip_amount': group['tip_amount'].sum(),
                'total_arriving_tip_amount': 0,
                'avg_leaving_tolls_amount': group['tolls_amount'].mean(),
                'avg_arriving_tolls_amount': 0,
                'total_leaving_tolls_amount': group['tolls_amount'].sum(),
                'total_arriving_tolls_amount': 0,
                'avg_leaving_improvement_surcharge': group['improvement_surcharge'].mean(),
                'avg_arriving_improvement_surcharge': 0,
                'total_leaving_improvement_surcharge': group['improvement_surcharge'].sum(),
                'total_arriving_improvement_surcharge': 0,
                'avg_leaving_total_amount': group['total_amount'].mean(),
                'avg_arriving_total_amount': 0,
                'total_leaving_total_amount': group['total_amount'].sum(),
                'total_arriving_total_amount': 0,
                'avg_leaving_congestion_surcharge': group['congestion_surcharge'].mean(),
                'avg_arriving_congestion_surcharge': 0,
                'total_leaving_congestion_surcharge': group['congestion_surcharge'].sum(),
                'total_arriving_congestion_surcharge': 0,
                'avg_leaving_airport_fee': 0,
                'avg_arriving_airport_fee': 0,
                'total_leaving_airport_fee': 0,
                'total_arriving_airport_fee': 0,
                'avg_leaving_ehail_fee': group['ehail_fee'].mean(),
                'avg_arriving_ehail_fee': 0,
                'total_leaving_ehail_fee': group['ehail_fee'].sum(),
                'total_arriving_ehail_fee': 0,
                'total_trip_count': total_trips,
                'trips_inside_Location': tripcount_to_same_loc,   
                'trips_outgoing_Location': tripcount_out_of_loc,
                'trips_incoming_Location': 0
                }
                green_pickupData_list[group_name] = green_data
                    #TODO hier weiter

            #-----------------------------------------------Green Drop off
            print("Calculating Green Drop off...")
            green_doGroupDF = green_df.groupby('DOLocationID')
            for group_name, group in green_doGroupDF:
                #print(group_name)
                total_trips = group.shape[0]
                tripcount_to_same_loc = 0
                tripcount_out_of_loc = 0
                try:
                    tripcount_to_same_loc = group['PULocationID'].value_counts().xs(group_name) #amount of 
                except KeyError as e:
                    tripcount_to_same_loc = 0
                tripcount_from_outside_of_loc = total_trips - tripcount_to_same_loc

                try:
                    green_PU_data = green_pickupData_list[group_name]
                    #data_available = True
                except KeyError as e:
                    #print("No data for this group yet...")
                    green_PU_data = empty_data
                    #data_available = False

                #Create Pickup list:
                pickup_locations = group['PULocationID']
                #dropoff_elements = dropoff_elements[dropoff_elements != group_name] #exclude this location
                unique_elements, counts = np.unique(pickup_locations, return_counts=True)
                pickup_counts = dict(zip(unique_elements, counts))

                update_data = {
                'DOvendorID': group['VendorID'].mode().iloc[0] if not group['VendorID'].mode().empty else None,
                #'originID': group['PULocationID'].mode().iloc[0] if not group['PULocationID'].mode().empty else None,
                'originID': pickup_counts,
                'avg_dropof_datetime': group['lpep_dropoff_datetime'].dt.time.iloc[0],
                'avg_arriving_passenger_count': group['passenger_count'].mean(),
                'total_arriving_passenger_count': group['passenger_count'].sum(),
                'avg_arriving_trip_distance': group['trip_distance'].mean(),
                'total_arriving_trip_distance': group['trip_distance'].sum(),
                'arriving_RateCodeID': group['RatecodeID'].mode().iloc[0] if not group['RatecodeID'].mode().empty else None,
                'arriving_store_and_fwd_flag': group['store_and_fwd_flag'].mode().iloc[0] if not group['store_and_fwd_flag'].mode().empty else None,
                'arriving_payment_type': group['payment_type'].mode().iloc[0] if not group['payment_type'].mode().empty else None,
                'avg_arriving_fare_amount': group['fare_amount'].mean(),
                'total_arriving_fare_amount': group['fare_amount'].sum(),
                'avg_arriving_extra': group['extra'].mean(),
                'total_arriving_extra': group['extra'].sum(),
                'avg_arriving_mta_tax': group['mta_tax'].mean(),
                'total_arriving_mta_tax': group['mta_tax'].sum(),
                'avg_arriving_tip_amount': group['tip_amount'].mean(),
                'total_arriving_tip_amount': group['tip_amount'].sum(),
                'avg_arriving_tolls_amount': group['tolls_amount'].mean(),
                'total_arriving_tolls_amount': group['tolls_amount'].sum(),
                'avg_arriving_improvement_surcharge': group['improvement_surcharge'].mean(),
                'total_arriving_improvement_surcharge': group['improvement_surcharge'].sum(),
                'avg_arriving_total_amount': group['total_amount'].mean(),
                'total_arriving_total_amount': group['total_amount'].sum(),
                'avg_arriving_congestion_surcharge': group['congestion_surcharge'].mean(),
                'total_arriving_congestion_surcharge': group['congestion_surcharge'].sum(),
                'avg_arriving_ehail_fee': group['ehail_fee'].mean(),
                'total_arriving_ehail_fee': group['ehail_fee'].sum(),
                'total_trip_count': green_PU_data['total_trip_count'] + total_trips,   
                'trips_incoming_Location': tripcount_from_outside_of_loc
                }
                green_PU_data.update(update_data)
                green_pickupData_list[group_name] = green_PU_data
            
        #pickle_files_dict['pickle_data_' + str(year) + '.pickle'] = pickupData_list
        #TODO loop throug grouped YellowTaxiData grouped by DOLocation
        #TODO loop throug grouped GreenTaxiData grouped by DOLocation

        #for index, row in yellow_df.iterrows():
        #    y_date_object = row['tpep_dropoff_datetime']

        #TEST write the dictionary to pickle file:
            with open(yellow_pickle_filePath + str(month) + '.pickle' , 'wb') as file:
                pickle.dump(yellow_pickupData_list, file)    
            with open(green_pickle_filePath + str(month) + '.pickle' , 'wb') as file:
                pickle.dump(green_pickupData_list, file)

            create_cvs_from_pickle(yellow_pickupData_list, year, month, 'y')
            create_cvs_from_pickle(green_pickupData_list, year, month, 'g')

            y_pickle_files_dict[year] = yellow_pickupData_list
            g_pickle_files_dict[year] = green_pickupData_list


def create_cvs_from_pickle(pickle_dict, nom, nom2, type):
    folder_path = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\drive_data\\PickleData\\TestCSV\\' + str(nom) + '\\' + type + '_'
    print("Transforming to CSV-Files...")
    folder_path_test = folder_path + str(nom2) + '_Check.csv'
    with open(folder_path_test, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Key', 'Value'])
        
        for key, value in pickle_dict.items():
                for k, v in value.items():
                    writer.writerow([k, v])
    # for pickle, values in pickle_dict.items():
    #     folder_path_test = folder_path + str(pickle) + '_Check.csv'
    #     with open(folder_path_test, 'w', newline='') as file:
    #         writer = csv.writer(file)
            
    #         # Write header (optional)
    #         writer.writerow(['Key', 'Value'])
            
    #         #writer.writerow([pickle, values])
    #         # Write dictionary data
    #         for key, value in values.items():
    #             writer.writerow([key, value])
    #             #for k, v in value.items():
    #                 #writer.writerow([k, v])


def load_Pickle():
    folder_path_pickle = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\drive_data\\PickleData\\'
    y_pickle_files_dict.clear()
    for filename in os.listdir(folder_path_pickle):
        if filename.endswith(".pickle"):
            file_path = os.path.join(folder_path_pickle, filename)

        # Read the pickle file and store in the dictionary
            with open(file_path, 'rb') as file:
                y_pickle_files_dict[filename] = pickle.load(file)
        
def load_pickle_to_dict(y):
    pickle_folder_path = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\drive_data\\PickleData\\' + str(y) + '\\'
    y_pickle_dict = {}
    g_pickle_dict = {}
    for filename in os.listdir(pickle_folder_path):
        if filename.endswith(".pickle"):
            file_path = os.path.join(pickle_folder_path, filename)

        # Read the pickle file and store in the dictionary
            with open(file_path, 'rb') as file:
                if filename.startswith("green"):
                    g_pickle_dict[filename] = pickle.load(file)
                else:
                    y_pickle_dict[filename] = pickle.load(file)

    y_pickle_files_dict[y] = y_pickle_dict
    g_pickle_files_dict[y] = g_pickle_dict

g_pickle_files_dict = {}
y_pickle_files_dict = {}
years = list(range(2014,2024))
#years = [2014]



def load():
    #load_Pickle()
    y_pickle_files_dict.clear()
    g_pickle_files_dict.clear()

    for year in years:
        load_pickle_to_dict(year)

        
def read():

    y_pickle_files_dict.clear()
    g_pickle_files_dict.clear()

    for year in years:
        print(year)
        calculate_values_of_months_file(year)

## Testing:
#read()
