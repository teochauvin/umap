
from .map import * 

from matplotlib import pyplot as plt 
from matplotlib.widgets import Slider, TextBox


def plot(umap:Map): 
    
    # Get data 
    if umap.topography: 
        x_elevation, y_elevation, elevation = umap.elevation.xyz
        
    buildings_gdfs = umap.buildings_gdfs
    edges, nodes = umap.road_network.edges, umap.road_network.nodes
    special_data = umap.special_data

    # visualize
    fig, ax = plt.subplots(figsize=(15, 15))

    # Create filled contour plot
    if umap.topography: 
        contours = plt.contourf(x_elevation, y_elevation, elevation, cmap="terrain", alpha=0.5, levels=20)  

    # Plot water 
    if "water" in special_data.keys(): 
        special_data["water"].plot(ax=ax, color="blue", alpha=1.0, label="Water Bodies")

    # PLot buildings 
    buildings_gdfs.plot(
        ax=ax,
        column="height",
        cmap="viridis",
        legend=True,
        alpha=1.0,
        edgecolor="black"
    )

    # Plot road network (edges)
    edges.plot(ax=ax, linewidth=1.5, edgecolor="black", label="Roads")
    nodes.plot(ax=ax, color="red", markersize=4, label="Nodes")

    # Add colorbar
    if umap.topography: 
        cbar = plt.colorbar(contours)
        cbar.set_label("Elevation (meters)")

    # Add title and axis labels
    ax.set_title("debug", fontsize=16)
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)

    # Show the plot
    plt.show()