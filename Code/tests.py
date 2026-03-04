import os
import csv
import scipy
from vedo import tetmesh, Plotter, file_io, LegendBox, Spline, FlatArrow, show


start = (1,1,1)
end = (5,5,5)
start1 = (start[0] + 0.1, start[1], start[2])
start2 = (start[0] - 0.1, start[1], start[2])
center1 = ((start[0] + end[0] )/2 + 0.1, (start[1]+end[1])/2, start[2] + end[2])
center2 = ((center1[0] - 0.2 , center1[1], center1[2]))
end1 = (end[0] + 0.1, end[1], end[2])
end2 = (end[0] - 0.1, end[1], end[2])

curve1 = Spline([start1, center1, end1])
line1 = curve1.vertices.tolist()
curve2 = Spline([start2, center2, end2])
line2 = curve2.vertices.tolist()
farr = FlatArrow(line1, line2, tip_size=100, tip_width=133).c("pink5")

show(farr)