import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vedo import Plotter, Mesh, LegendBox, color_map
import matplotlib


logger = logging.getLogger(__name__)

class PlotPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.layout.addWidget(self.vtk_widget)

        # Persistent vedo plotter attached to the Qt VTK widget
        self.plt = Plotter(qt_widget=self.vtk_widget)

        self.actors = []    # vtkActor -> represents an actor in a rendered scene
        self.legend_box = None
        self._scene_initialized = False
        

    def set_map(self, map_res):

        # Remove old actors if present
        if self.actors:
            self.plt.remove(*self.actors)
            self.actors = []

        if self.legend_box is not None:
            self.plt.remove(self.legend_box)
            self.legend_box = None

        # Build new actors
        self.actors = []
        for mesh in map_res.map_objects:
            actor = Mesh(mesh.mesh)

            color = color_map(
                mesh.plot_value,
                matplotlib.colormaps["jet"],
                0,
                map_res.max_value,
            )

            actor.c(color).alpha(1.0).lw(0)
            actor.name = mesh.shape_name
            actor.info = (
                f"Shape_name: {mesh.shape_name}\n"
                f"Value: {mesh.value}\n"
                f"shape_id: {mesh.shape_id}"
            )
            self.actors.append(actor)

        self.legend_box = LegendBox()

        self.plt.add(self.actors)
        self.plt.add(self.legend_box)

        # Add hover legend once
        if not self._scene_initialized:
            self.plt.add_hover_legend(use_info=True)
            self._scene_initialized = True

        # First display: reset camera
        self.plt.show(resetcam=True, axes=1)

        # Later updates: just render
        self.plt.render()