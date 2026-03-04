"""Taxi Data of New York"""
import os
import csv
import scipy
from vedo import TetMesh, Plotter, file_io, LegendBox, Spline, FlatArrow, show

def dict_from_csv(path):
     result = {}
     with open(path, 'r') as csvfile:
          reader = csv.reader(csvfile)
          for row in reader:
               key = row[0]
               values = row[1:]
               result[key] = values

     return result

colors = ["gray5","green5","teal5","blue5","purple5","indigo5","pink5","red5"]  #example colors

csv_lookup_path = "C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Data\\taxi+_zone_lookup.csv"

lookup_dict = dict_from_csv(csv_lookup_path)

def plot_saved_obj_vedo(height,factor, unit, arrows=False, arrow_origin=0):
     print("Plotting...")
     directory_path = 'C:\\Users\\Mark\\OneDrive\\Documents\\Uni\\Informatik_Master\\Semester_2\\Computergrafik und Informationsvisualisierung\\Seminar\\Objects\\3D'
     
     arrow_points = []
     area_colors = []
     area_color = "gray5"
     meshlist=[]
     seperator=[0, height/6, height/6 *2, height/6*3, height/6*4, height/6*5,height]
     for filename in os.listdir(directory_path):
            if filename.endswith('.obj'):
                file_path = os.path.join(directory_path, filename)
                id_digits = [char for char in filename if char.isdigit()]
                location_id = ''.join(id_digits)
                location_info = lookup_dict[location_id]
                mesh = file_io.read(file_path)
                h = mesh.bounds()[5] #get maximum Z-Height
                area_color = colors[getColor(seperator,h)]
                mesh.color(area_color)
                #create Arrows if needed
                if arrows:
                    if location_id == str(arrow_origin):
                         origin_point = ((mesh.bounds()[0] + mesh.bounds()[1]) / 2, (mesh.bounds()[2] + mesh.bounds()[3]) / 2, h)
                    elif h != 0:
                         point = ((mesh.bounds()[0] + mesh.bounds()[1]) / 2, (mesh.bounds()[2] + mesh.bounds()[3]) / 2, h)
                         arrow_points.append(point)
                         area_colors.append(area_color)
                          
                #triangulate mesh for perfect contours :)
                tri = mesh.triangulate()
                #Add info of mesh for "hover_legend"
                tri.info = "ID: " + location_id + "\nBorough: " + str(location_info[0]) + "\nZone: " + str(location_info[1]) + "\nValue: " + str(h*factor) + unit

                meshlist.append(tri)
                #meshlist.append(mesh)
     arrows = []
     for point,col in zip(arrow_points,area_colors):
          arrow = add_Arrows(origin_point, point,col)
          arrows.append(arrow)
     
     
     plt = Plotter()
     plt.add(arrows)
     lBox = LegendBox()
     print(type(plt))
     plt.add(meshlist)
     plt.add_hover_legend(use_info=True)
     plt.show(__doc__, axes=1)

def add_Arrows(start, end, color):
     arrow_width = 600
     arrow_height_ending = 400
     start1 = (start[0] + arrow_width/2, start[1], start[2])
     start2 = (start[0] - arrow_width/2, start[1], start[2])
     center1 = ((start[0] + end[0] )/2 + arrow_width/2, (start[1]+end[1])/2, start[2] + end[2])
     center2 = ((center1[0] - arrow_width , center1[1], center1[2]))
     end1 = (end[0] + arrow_width/2, end[1], end[2] + arrow_height_ending)
     end2 = (end[0] - arrow_width/2, end[1], end[2] + arrow_height_ending)

     curve1 = Spline([start1, center1, end1])
     line1 = curve1.vertices.tolist()
     curve2 = Spline([start2, center2, end2])
     line2 = curve2.vertices.tolist()
     farr = FlatArrow(line1, line2, tip_size=1, tip_width=1).c(color)
     #show(farr,__doc__, axes=1)
     return farr
     #curve = Spline([start,center,end], smooth=0.5, res=100)


def getColor(seq,height):
     match height:
          case _ if height >= seq[6]:
               return 7
          case _ if height > seq[5]:
               return 6
          case _ if height > seq[4]:
               return 5
          case _ if height > seq[3]:
               return 4
          case _ if height > seq[2]:
               return 3
          case _ if height > seq[1]:
               return 2
          case _ if height > seq[0]:
               return 1
          case _ if height <= seq[0]:
               return 0
     return 0 #as "default"

def dict_from_csv(path):
     result = {}
     with open(path, 'r') as csvfile:
          reader = csv.DictReader(csvfile)
          for row in reader:
               result.append(row)
     return result

#plot_saved_obj_vedo(10000, 1, '', True, 3)