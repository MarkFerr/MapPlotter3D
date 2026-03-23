from vedo import Plotter, LegendBox, Mesh, color_map
import matplotlib
import logging

#* set Logging
logger = logging.getLogger(__name__)


def generate_plot(map_res):
    logger.info("Generating 3D Plot")
    plt = Plotter()
    actors = []

    for mesh in map_res.map_objects:
        actor = Mesh(mesh.mesh)
        color = color_map(mesh.plot_value, matplotlib.colormaps["jet"],0, map_res.max_value)
        actor.c(color).alpha(1.0).lw(0)
        actor.name = mesh.shape_name
        actor.info = f"Shape_name: {mesh.shape_name}\nValue: {mesh.value}\nshape_id: {mesh.shape_id}"
        actors.append(actor)

    lBox = LegendBox()
    plt.add(actors)
    plt.add_hover_legend(use_info=True)
    plt.show(__doc__, axes=1)