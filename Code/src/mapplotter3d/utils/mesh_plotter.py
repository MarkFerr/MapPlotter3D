from vedo import Plotter, LegendBox, Mesh



def generate_plot(meshes):
    plt = Plotter()
    actors = []

    for mesh in meshes:
        actor = Mesh(mesh.mesh)
        #todo get color automatically from palette depending on the value
        actor.c("lightblue").alpha(1.0).lw(0)
        actor.name = mesh.shape_name
        actor.info = f"Shape_name: {mesh.shape_name}\nValue: {mesh.value}\nshape_id: {mesh.shape_id}"
        actors.append(actor)

    lBox = LegendBox()
    plt.add(actors)
    plt.add_hover_legend(use_info=True)
    plt.show(__doc__, axes=1)