from dataclasses import dataclass
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import vtk
import numpy as np
import logging

from vedo import Mesh, show


from mapplotter3d.utils.normalization import get_normalization, normalize_df

logger = logging.getLogger(__name__)


@dataclass
class MeshResult:
    shape_id: int
    shape_name: str
    value: float
    plot_value: float
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


@dataclass
class MapResult:
    max_value: float
    map_name: str
    map_objects: list[MeshResult]


def build_meshes(gdf, df, loc_key, data_key, map_name="", missing_rows=None) -> list[MeshResult]:
    logger.info("Building Meshes")

    #* Get value to Normalize to
    max_height = get_normalization(gdf)

    normalized_df = normalize_df(df, max_height)

    meshes = []
    for _, row in normalized_df.iterrows():
        if missing_rows and row[loc_key] in missing_rows:
            logger.info("Skipping plot for %s", row[loc_key])
            continue
        
        logger.info("Building Mesh for %s", row[loc_key])

        gdf_row = gdf[gdf["shapeName"] == row[loc_key]].iloc[0]
        geom = gdf_row.geometry
        if "shapeID" in gdf_row.keys():
            shape_id = gdf_row.shapeID
        else:
            shape_id = None
        shape_name = gdf_row.shapeName

        value = df.loc[df[loc_key] == row[loc_key], data_key].iloc[0]
        normalized_value = row[data_key]    #normalized_df.loc[normalized_df[loc_key] == shape_name, data_key].iloc[0]

        if isinstance(geom,Polygon):
            logger.info("Is simple Polygon")
            mesh, top_idx = mesh_from_polygon(poly=geom, height=normalized_value)
        elif isinstance(geom, MultiPolygon):
            logger.info("Is MultiPolygon")
            mesh, top_idx = mesh_from_multipolygon(mp=geom, height=normalized_value)
        else:
            logger.info("Geometry type %s for %s not supported", type(geom), shape_name)
            continue
        mesh_res = MeshResult(shape_id=shape_id, shape_name=shape_name, value=value, plot_value=normalized_value, mesh=mesh, top_indices=top_idx)

        meshes.append(mesh_res)
        # plot_mesh(mesh.mesh)
    logger.info("Built %i meshes", len(meshes))
    map_res = MapResult(max_value=max_height, map_name=map_name, map_objects=meshes)
    return map_res
        
        # break


def mesh_from_polygon(poly: Polygon, height: float) -> MeshResult:
    polydata = _extrude_polygon_to_polydata(poly, height=height)

    pts = vtk_to_numpy(polydata.GetPoints().GetData())
    z = pts[:, 2]
    zmax = float(z.max())
    top_idx = np.flatnonzero(np.isclose(z, zmax))

    return polydata, top_idx #MeshResult(shape_id=shape_id, shape_name=shape_name, mesh=polydata, top_indices=top_idx)


def mesh_from_multipolygon(mp: MultiPolygon, height: float) -> MeshResult:
    multi_poly = vtk.vtkAppendPolyData()
    for poly in mp.geoms:
        pd = _extrude_polygon_to_polydata(poly, height=height)
        multi_poly.AddInputData(pd)
    multi_poly.Update()

    mesh = vtk.vtkPolyData()
    mesh.ShallowCopy(multi_poly.GetOutput())

    pts = vtk_to_numpy(mesh.GetPoints().GetData())
    z = pts[:, 2]
    zmax = float(z.max())
    top_idx = np.flatnonzero(np.isclose(z, zmax))

    return mesh, top_idx


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
    # Clean invalid polygons if needed
    if not poly.is_valid:
        logger.info("Attempting to clean Polygon")
        poly = poly.buffer(0)

    if poly.is_empty:
        raise ValueError("Polygon is empty after cleaning")

    # If cleaning produced a MultiPolygon, keep the largest piece here
    if isinstance(poly, MultiPolygon):
        logger.info("Cleaning created Multipolygon. Keeping largest Polygon")
        poly = max(poly.geoms, key=lambda g: g.area)

    # Exterior ring
    coords = np.asarray(poly.exterior.coords, dtype=float)
    if len(coords) >= 2 and np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]

    n = len(coords)
    if n < 3:
        raise ValueError("Polygon exterior must have at least 3 unique points")

    points = vtk.vtkPoints()
    for x, y in coords[:, :2]:
        points.InsertNextPoint(float(x), float(y), 0.0)

    # Build a closed polyline contour, not a vtkPolygon cell
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(n + 1)
    for i in range(n):
        lines.InsertCellPoint(i)
    lines.InsertCellPoint(0)  # close loop

    contour = vtk.vtkPolyData()
    contour.SetPoints(points)
    contour.SetLines(lines)

    # Robust triangulation for concave contours
    triangulator = vtk.vtkContourTriangulator()
    triangulator.SetInputData(contour)
    triangulator.Update()

    triangulated = vtk.vtkPolyData()
    triangulated.ShallowCopy(triangulator.GetOutput())

    extr = vtk.vtkLinearExtrusionFilter()
    extr.SetInputData(triangulated)
    extr.SetExtrusionTypeToVectorExtrusion()
    extr.SetVector(0.0, 0.0, 1.0)
    extr.SetScaleFactor(float(height))
    extr.SetCapping(True)
    extr.Update()

    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(extr.GetOutput())
    clean.Update()

    out = vtk.vtkPolyData()
    out.ShallowCopy(clean.GetOutput())
    return out