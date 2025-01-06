
from .map import * 

from matplotlib import pyplot as plt 
from matplotlib.widgets import Slider, TextBox, Button


def plot(umap:Map): 
    
    # Get data 
    if umap.topography: 
        x_elevation, y_elevation, elevation = umap.elevation.xyz
        
    buildings_gdfs = umap.buildings_gdfs
    edges, nodes = umap.road_network.edges, umap.road_network.nodes
    extremal_nodes = umap.road_network.list_extremal_nodes
    special_data = umap.special_data

    # visualize
    fig, ax = plt.subplots(figsize=(12, 12))

    #  0  Create filled contour plot
    if umap.topography: 
        contours = plt.contourf(x_elevation, y_elevation, elevation, cmap="terrain", alpha=0.5, levels=20) 
        cbar = plt.colorbar(contours)
        cbar.set_label("Elevation (meters)") 

    #  1 PLot buildings 
    building_plot = buildings_gdfs.plot(
        ax=ax,
        column="height",
        cmap="viridis",
        legend=True,
        alpha=1.0,
        edgecolor="black")
                               
    #  2  Plot water 
    if "water" in special_data.keys(): 
        special_data["water"].plot(ax=ax, color="blue", alpha=1.0, label="Water Bodies")

    #  3  Plot road network (edges)
    edge_plot = edges.plot(ax=ax, linewidth=1.5, edgecolor="black", label="Roads")
    node_plot = nodes.plot(ax=ax, color="orange", markersize=4, label="Nodes")

    #  4  Plot extremal nodes
    extremal_plot = plt.scatter(extremal_nodes[:,0], extremal_nodes[:,1], s=10, color="red")


    # Add title and axis labels
    ax.set_title(f"map : {umap.name}", fontsize=16)
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)



    # Events
    visibility = {
        "topography":True,
        "buildings":True,
        "water":True,
        "road_network":True
    }

    # Button callback function
    def toggle_buildings_visibility(event):
        visibility['buildings'] = not visibility['buildings']
        collection = ax.collections[1] 
        collection.set_visible(visibility['buildings'])
        plt.draw() 

    def toggle_topography_visibility(event):
        visibility['topography'] = not visibility['topography']
        collection = ax.collections[0] 
        collection.set_visible(visibility['topography'])
        plt.draw() 

    def toggle_water_visibility(event):
        visibility['water'] = not visibility['water']
        collection = ax.collections[2] 
        collection.set_visible(visibility['water'])
        plt.draw()

    def toggle_road_network_visibility(event):
        visibility['road_network'] = not visibility['road_network']
        collections = ax.collections[3:5] 
        for collection in collections: 
            collection.set_visible(visibility['road_network'])
        plt.draw()


    # events 
    button_ax = plt.axes([0.05, 0.05, 0.100, 0.035])  # x, y, width, height
    button = Button(button_ax, 'Buildings')
    button.on_clicked(toggle_buildings_visibility)

    button_ax2 = plt.axes([0.05, 0.10, 0.100, 0.035]) 
    button2 = Button(button_ax2, 'Topography')
    button2.on_clicked(toggle_topography_visibility)

    button_ax3 = plt.axes([0.05, 0.15, 0.100, 0.035]) 
    button3 = Button(button_ax3, 'Water')
    button3.on_clicked(toggle_water_visibility)

    button_ax4 = plt.axes([0.20, 0.05, 0.100, 0.035]) 
    button4 = Button(button_ax4, 'Road Network')
    button4.on_clicked(toggle_road_network_visibility)

    # Show the plot
    plt.show()