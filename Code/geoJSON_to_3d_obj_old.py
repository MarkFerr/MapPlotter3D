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

            #plt.plot(x, y, label=f'Multipolygon {index}')
    #plt.title(str(location_id) + ' ' + borough)
    #figure = plt.figure(figsize=(8, 8))
    #plt.plot(geometry.xy[0], geometry.xy[1])
    #plt.show()
    #if location_id == 3:
    #    break
def is_concave(vertices):
    def cross_product(p1, p2, p3):
        return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

    n = len(vertices)
    for i in range(n):
        p1, p2, p3 = vertices[i], vertices[(i + 1) % n], vertices[(i + 2) % n]
        result = cross_product(p1, p2, p3)
        if result < 0:
            return True  # Concave
    return False  # Convex
