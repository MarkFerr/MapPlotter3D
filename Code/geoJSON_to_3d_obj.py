import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, MultiPolygon
import numpy as np


# Specify the path to your GeoJSON file
file_path = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\taxi_zones\\taxi_zones.geojson'

# Load the GeoJSON file into a GeoDataFrame
gdf = gpd.read_file(file_path)


def create_obj_from_POLYGON(x,y,loc,locID, height):
    obj_file_path = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Objects\\3D\\' + loc + '_' + str(locID) + '.obj'
    z1 = np.zeros(len(x))
    z2 = np.ones(len(x)) * height
    
    vertex_offset = 0

    vertices1 = np.array(list(zip(x,y,z1)))
    vertices2 = np.array(list(zip(x,y,z2)))

    with open(obj_file_path, 'w') as obj_file:
        for vertex in vertices2:
            x, y, z = vertex
            obj_file.write(f"v {x} {y} {z}\n")

        for vertex in vertices1:
            x, y, z = vertex
            obj_file.write(f"v {x} {y} {z}\n")

        num_vertices = len(vertices2)
        face_line = " ".join(str(i + 1) for i in range(num_vertices))   #top Face
        obj_file.write(f"f {face_line}\n")

        vertex_offset += num_vertices
        face_line = " ".join(str(i + 1 + vertex_offset) for i in range(num_vertices))   #bottom Face
        #face_line = " ".join(str(i + 1) for i in range(num_vertices))   #top Face
        obj_file.write(f"f {face_line}\n")

        for i in range(1,num_vertices):
            face_line = "f " + str(i) + ' ' + str(i + vertex_offset) + ' ' + str(i + vertex_offset + 1)
            obj_file.write(f"{face_line}\n")
            face_line = "f " + str(i) + ' ' + str(i + vertex_offset + 1) + ' ' + str(i + 1)
            obj_file.write(f"{face_line}\n")
        return obj_file


def create_obj_from_polygon_part(x, y, loc, locID, height, index_offset):
    obj_file_path = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Objects\\3D\\' + loc + '_' + str(locID) + '.obj'
    z1 = np.zeros(len(x))
    z2 = np.ones(len(x)) * height

    vertex_offset = 0

    vertices1 = np.array(list(zip(x, y, z1)))
    vertices2 = np.array(list(zip(x, y, z2)))
    with open(obj_file_path, 'a') as obj_file:
        for vertex in vertices2:
            x, y, z = vertex
            obj_file.write(f"v {x} {y} {z}\n")

        for vertex in vertices1:
            x, y, z = vertex
            obj_file.write(f"v {x} {y} {z}\n")

        num_vertices = len(vertices2)
        face_line = " ".join(str(i + 1 + index_offset) for i in range(num_vertices))  # top Face
        #obj_file.write(f"f {face_line}\n")

        vertex_offset += num_vertices
        face_line = " ".join(str(i + 1 + vertex_offset + index_offset) for i in range(num_vertices))  # bottom Face
        # face_line = " ".join(str(i + 1) for i in range(num_vertices))   #top Face
        #obj_file.write(f"f {face_line}\n")

        for i in range(1, num_vertices):
            current_index = i + index_offset
            face_line = "f " + str(current_index) + ' ' + str(current_index + vertex_offset) + ' ' + str(current_index + vertex_offset + 1)
            obj_file.write(f"{face_line}\n")
            face_line = "f " + str(current_index) + ' ' + str(current_index + vertex_offset + 1) + ' ' + str(current_index + 1)
            obj_file.write(f"{face_line}\n")
        return obj_file

def create_obj_from_MULTIPOLYGON(v_list,loc,locID):
    obj_file_path = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Objects\\3D\\' + loc + '_' + str(locID) + '.obj'
    vertex_offset = 0
    with open(obj_file_path, 'w') as obj_file:
        for vertices in v_list:
            for vertex in vertices:
                x, y, z = vertex
                obj_file.write(f"v {x} {y} {z}\n")

            # Generate a face line based on the number of vertices in the current set
            num_vertices = len(vertices)
            face_line = " ".join(str(i + 1 + vertex_offset) for i in range(num_vertices))
            obj_file.write(f"f {face_line}\n")
            vertex_offset += num_vertices

for index, row in gdf.iterrows():
    location_id = row['LocationID']
    borough = row['borough']
    geometry = row['geometry']

    # Now you can work with the individual geometry and LocationID
    #print(f"LocationID: {location_id}")
    #print(f"Geometry: {geometry}\n")

    if geometry.geom_type == 'Polygon':
        x, y = geometry.exterior.xy
        #plt.plot(x, y, label=f'Polygon {index}')
        create_obj_from_POLYGON(x,y,borough,location_id, 10000)
    elif geometry.geom_type == 'MultiPolygon':
        vertices_list = []
        current_index_offset = 0
        for polygon_part in geometry.geoms:
            x, y = polygon_part.exterior.xy
            create_obj_from_polygon_part(x,y,borough,location_id, 10000, current_index_offset)
            current_index_offset += len(x)*2
            #plt.plot(x, y, label=f'Multipolygon {index}')
    #plt.title(str(location_id) + ' ' + borough)
    #figure = plt.figure(figsize=(8, 8))
    #plt.plot(geometry.xy[0], geometry.xy[1])
    #plt.show()
    #if location_id == 3:
    #    break




"""
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
            flattened_coordinates = [(x, y, 10000.0) for x, y in coordinates]

            # Extract interior coordinates from the polygon (holes)
            interior_coordinates = [list(interior.coords) for interior in polygon_part.interiors]

            # Flatten interior coordinates with z=0
            flattened_interiors = [[(x, y, 0.0) for x, y in interior] for interior in interior_coordinates]
            #z = np.zeros(len(x))
            #vertices = np.array(list(zip(x,y,z)))
            #vertices_list.append(vertices)
            vertices_list.append(flattened_coordinates)
            vertices_list.extend(flattened_interiors)
        create_obj_from_MULTIPOLYGON(vertices_list,borough,location_id)
"""