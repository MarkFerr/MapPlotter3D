from dataclasses import dataclass
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
import vtk
import numpy as np
import logging

logger = logging.getLogger(__name__)

@dataclass
class MeshResult:
    shape_id: int
    shape_name: str
    mesh: vtk.vtkPolyData
    top_indices:dict[str,np.ndarray]

def build_meshes(gdf, df, data_key) -> list[MeshResult]:
    for row in gdf.itertuples(index=False):
        geom = row.geometry
        shape_id = row.shapeID
        shape_name = row.shapeName
        if isinstance(geom,Polygon):
            value = df.loc[df["municipality"] == shape_name, data_key].iloc[0]
            print(value)
            mesh = mesh_from_polygon(geom, value, shape_id, shape_name)
        elif isinstance(geom, MultiPolygon):
            mesh = mesh_from_multipolygon(geom, shape_id, shape_name)
        else:
            logger.info("Geometry type %s for %s not supported", type(geom), shape_name)
            continue
        
        break

def mesh_from_polygon(data) -> MeshResult:
    