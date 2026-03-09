from dataclasses import dataclass
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import vtk
import numpy as np
import logging

from vedo import Mesh, show

logger = logging.getLogger(__name__)

@dataclass
class MeshResult:
    shape_id: int
    shape_name: str
    mesh: vtk.vtkPolyData
    top_indices:dict[str,np.ndarray]

    def __str__(self):
        n_points = self.mesh.GetNumberOfPoints() if self.mesh is not None else 0
        n_cells = self.mesh.GetNumberOfCells() if self.mesh is not None else 0
        n_top = len(self.top_indices) if self.top_indices is not None else 0

        return (
            f"MeshResult:\n"
            f"\tshape_id='{self.shape_id}', "
            f"\n\tshape_name='{self.shape_name}', "
            f"\n\tpoints={n_points}, "
            f"\n\tcells={n_cells}, "
            f"\n\ttop_idx_count={n_top}"
        )
    
    def set_height(self, new_height: float) -> None:
        polydata = self.mesh
        points = polydata.GetPoints()
        pts_np = vtk_to_numpy(points.GetData())

        pts_np[self.top_indices, 2] = new_height

        points.Modified()
        polydata.Modified()

def build_meshes(gdf, df, data_key) -> list[MeshResult]:
    logger.info("Building Meshes")

    meshes = []
    for row in gdf.itertuples(index=False):
        geom = row.geometry
        shape_id = row.shapeID
        shape_name = row.shapeName

        if isinstance(geom,Polygon):
            value = df.loc[df["municipality"] == shape_name, data_key].iloc[0]
            mesh = mesh_from_polygon(poly=geom, height=value, shape_id=shape_id, shape_name=shape_name)
        elif isinstance(geom, MultiPolygon):
            mesh = mesh_from_multipolygon(mp=geom, height=value, shape_id=shape_id, shape_name=shape_name)
        else:
            logger.info("Geometry type %s for %s not supported", type(geom), shape_name)
            continue

        if shape_name == "Rottweil":
            mesh.set_height(1)

        meshes.append(mesh)
        # plot_mesh(mesh.mesh)
    logger.info("Built %i meshes", len(meshes))
    return meshes
        
        # break


def mesh_from_polygon(shape_id: str, shape_name: str, poly: Polygon, height: float) -> MeshResult:
    #TODO make a function to generallize the height to normalize to, maybe average area?
    polydata = _extrude_polygon_to_polydata(poly, height=0.1)#height=height)

    pts = vtk_to_numpy(polydata.GetPoints().GetData())
    z = pts[:, 2]
    zmax = float(z.max())
    top_idx = np.flatnonzero(np.isclose(z, zmax))

    return MeshResult(shape_id=shape_id, shape_name=shape_name, mesh=polydata, top_indices=top_idx)


def mesh_from_multipolygon(mp: MultiPolygon, shape_id: str, shape_name: str, height: float) -> MeshResult:
    append = vtk.vtkAppendPolyData()
    for part in mp.geoms:
        pd = _extrude_polygon_to_polydata(part, height=0.1)#height)
        append.AddInputData(pd)
    append.Update()

    out = vtk.vtkPolyData()
    out.ShallowCopy(append.GetOutput())

    pts = vtk_to_numpy(out.GetPoints().GetData())
    z = pts[:, 2]
    zmax = float(z.max())
    top_idx = np.flatnonzero(np.isclose(z, zmax))

    return MeshResult(shape_id=shape_id, shape_name=shape_name, mesh=out, top_indices=top_idx)


def plot_mesh(polydata: vtk.vtkPolyData, title: str = "Mesh") -> None:

    print("Points:", polydata.GetNumberOfPoints())
    print("Cells:", polydata.GetNumberOfCells())
    print("Bounds:", polydata.GetBounds())

    actor = Mesh(polydata)
    actor.color("tomato")
    actor.linecolor("black")
    actor.linewidth(1)

    show(actor, axes=1, viewup="z", resetcam=True)


def _extrude_polygon_to_polydata(poly: Polygon, height: float) -> vtk.vtkPolyData:
    # exterior ring
    coords = np.asarray(poly.exterior.coords, dtype=float)

    # drop duplicate closing coordinate
    if len(coords) >= 2 and np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]

    n = len(coords)
    if n < 3:
        raise ValueError("Polygon exterior must have at least 3 unique points")

    points = vtk.vtkPoints()
    points.SetNumberOfPoints(n)
    for i, (x, y) in enumerate(coords[:, :2]):
        points.SetPoint(i, float(x), float(y), 0.0)

    polygon = vtk.vtkPolygon()
    polygon.GetPointIds().SetNumberOfIds(n)
    for i in range(n):
        polygon.GetPointIds().SetId(i, i)

    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polygon)

    poly2d = vtk.vtkPolyData()
    poly2d.SetPoints(points)
    poly2d.SetPolys(cells)

    tri = vtk.vtkTriangleFilter()
    tri.SetInputData(poly2d)
    tri.Update()

    extr = vtk.vtkLinearExtrusionFilter()
    extr.SetInputData(tri.GetOutput())
    extr.SetExtrusionTypeToVectorExtrusion()
    extr.SetVector(0.0, 0.0, 1.0)
    extr.SetScaleFactor(float(height))
    extr.SetCapping(True)
    extr.Update()

    out = vtk.vtkPolyData()
    out.ShallowCopy(extr.GetOutput())
    return out