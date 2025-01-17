
from .map import * 

from matplotlib import pyplot as plt 
from matplotlib.widgets import Slider, TextBox, Button


def plot(umap:Map): 


    # Collection ids tracker 
    # initilized at 
    collection_ids = {
        "inflated_buildings" : 1,
        "buildings" : 2, 
        "topography" : 0, 
        "water" : 3, 
        "edges_road_network" : 4, 
        "nodes_road_network" : 5,
        "extremal_points" : 6, 
    }

    # Button Events
    visibility = {
        "topography":True,
        "buildings":True,
        "water":True,
        "road_network":True
    }
    
    # Get data 
    if umap.topography: 
        x_elevation, y_elevation, elevation = umap.elevation.xyz
        
    edges, nodes = umap.road_network.edges, umap.road_network.nodes
    extremal_nodes = umap.road_network.list_extremal_nodes
    special_data = umap.special_data

    # visualize
    fig, ax = plt.subplots(figsize=(12, 12))

    #  0  Create filled contour plot
    if umap.topography: 
        contours = plt.contourf(x_elevation, y_elevation, elevation, cmap="terrain", alpha=0.5, levels=20, zorder=collection_ids["topography"]) 
        cbar = plt.colorbar(contours, ax=ax)
        cbar.set_label("Elevation (meters)") 

    #  1  Inflated buildings
    inflated_building_plot = umap.inflated_buildings_gdfs.plot(
        ax=ax,
        alpha=0.4, 
        facecolor="purple",
        hatch="--",
        zorder=collection_ids["inflated_buildings"]
        )

    #  2 PLot buildings 
    building_plot = umap.buildings_gdfs.plot(
        ax=ax,
        column="height",
        cmap="viridis",
        legend=True,
        label="Buildings",
        edgecolor="black",
        zorder=collection_ids["buildings"])
                               
    #  3  Plot water 
    if "water" in special_data.keys(): 
        special_data["water"].plot(
            ax=ax, 
            color="blue", 
            alpha=1.0, 
            label="Water Bodies",
            zorder=collection_ids["water"])

    #  4-5  Plot road network (edges)
    edge_plot = edges.plot(
        ax=ax, 
        linewidth=1.5, 
        edgecolor="black", 
        label="Roads", 
        zorder=collection_ids["edges_road_network"])
    
    node_plot = nodes.plot(
        ax=ax, 
        color="orange", 
        markersize=4, 
        label="Nodes", 
        zorder=collection_ids["nodes_road_network"])

    #  6  Plot extremal nodes
    extremal_plot = plt.scatter(
        extremal_nodes[:,0], 
        extremal_nodes[:,1], 
        s=10, 
        color="red", 
        zorder=collection_ids["extremal_points"])

    # Add title and axis labels
    ax.set_title(f"map : {umap.name}", fontsize=16)
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)



    # Button callback function
    def toggle_buildings_visibility(event):
        visibility['buildings'] = not visibility['buildings']
        id_collection = collection_ids["buildings"]
        collection = ax.collections[id_collection] 
        collection.set_visible(visibility['buildings'])
        plt.draw() 

    def toggle_topography_visibility(event):
        visibility['topography'] = not visibility['topography']
        id_collection = collection_ids["topography"]
        collection = ax.collections[id_collection] 
        collection.set_visible(visibility['topography'])
        plt.draw() 

    def toggle_water_visibility(event):
        visibility['water'] = not visibility['water']
        id_collection = collection_ids["water"]
        collection = ax.collections[id_collection] 
        collection.set_visible(visibility['water'])
        plt.draw()

    def toggle_road_network_visibility(event):
        visibility['road_network'] = not visibility['road_network']
        ids = [collection_ids["nodes_road_network"], collection_ids["edges_road_network"], collection_ids["extremal_points"]]
        for id in ids: 
            collection = ax.collections[id] 
            collection.set_visible(visibility['road_network'])
        plt.draw()

    def save_button(event):
        umap.save()
        print("Map saved") 




    # connect buttons  
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

    button_ax5 = plt.axes([0.20, 0.10, 0.100, 0.035]) 
    button5 = Button(button_ax5, 'Save')
    button5.on_clicked(save_button)

    

    # Define the update function for the slider
    def merge_thr_update(val):

        # Update the buildings 
        umap.compute_inflated_gfs(float(val))

        # Remove previouse ones 
        ax.collections[collection_ids["inflated_buildings"]].remove() 

        # Update collections id tracker -- buildings goes to last position 
        for k,v in collection_ids.items(): 
            if v > collection_ids["inflated_buildings"]: 
                collection_ids[k] = v-1 
        collection_ids["inflated_buildings"] = len(collection_ids)-1
        
        # Plot new ones 
        inflated_building_plot = umap.inflated_buildings_gdfs.plot(
            ax=ax,
            alpha=0.4, 
            facecolor="purple",
            hatch="--",
            zorder=collection_ids["inflated_buildings"]
            )
        
        # Remove previouse ones 
        ax.collections[collection_ids["buildings"]].remove() 

        # Update collections id tracker -- buildings goes to last position 
        for k,v in collection_ids.items(): 
            if v > collection_ids["buildings"]: 
                collection_ids[k] = v-1 
        collection_ids["buildings"] = len(collection_ids)-1
        
        # Plot new ones 
        building_plot = umap.buildings_gdfs.plot(
            ax=ax,
            column="height",
            cmap="viridis",
            label="Buildings",
            edgecolor="black",
            zorder=collection_ids["buildings"])
        
        plt.draw()

    # Add a TextBox widget
    axbox = plt.axes([0.4, 0.05, 0.1, 0.025])  # Position: [left, bottom, width, height]
    text_box = TextBox(axbox, "inflate:", initial=str(0.0))
    text_box.on_submit(merge_thr_update)  # Connect the event handler

    # Show the plot
    plt.show()