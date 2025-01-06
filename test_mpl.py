import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from shapely.geometry import Point

# Create some example GeoDataFrames
data1 = {'geometry': [Point(0, 0), Point(1, 1), Point(2, 2)]}
gdf1 = gpd.GeoDataFrame(data1, geometry='geometry')

data2 = {'geometry': [Point(3, 3), Point(4, 4), Point(5, 5)]}
gdf2 = gpd.GeoDataFrame(data2, geometry='geometry')

# Create the plot
fig, ax = plt.subplots()

# Plot the GeoDataFrames and store the plot objects as variables
gdf1_plot = gdf1.plot(ax=ax, color='blue', label='GeoDataFrame 1', zorder=1)
gdf2_plot = gdf2.plot(ax=ax, color='red', label='GeoDataFrame 2', zorder=2)

# Store the lines and points from the plot as objects
gdf1_objects = gdf1_plot.get_children()  # Stores points and lines for GeoDataFrame 1
gdf2_objects = gdf2_plot.get_children()  # Stores points and lines for GeoDataFrame 2

# Visibility dictionary to track which layers are visible
visibility = {
    'gdf1': True,
    'gdf2': True
}

# Adjust layout to accommodate buttons
plt.subplots_adjust(bottom=0.3)

# Button callback function to toggle visibility of GeoDataFrame 1
def toggle_gdf1(event):
    visibility['gdf1'] = not visibility['gdf1']  # Toggle visibility of gdf1
    for obj in gdf1_objects:
        obj.set_visible(visibility['gdf1'])
    plt.draw()

# Button callback function to toggle visibility of GeoDataFrame 2
def toggle_gdf2(event):
    visibility['gdf2'] = not visibility['gdf2']  # Toggle visibility of gdf2
    for obj in gdf2_objects:
        obj.set_visible(visibility['gdf2'])
    plt.draw()

# Create buttons to toggle visibility of the GeoDataFrames
button_ax1 = plt.axes([0.7, 0.05, 0.1, 0.075])  # Button 1: Toggle GeoDataFrame 1
button1 = Button(button_ax1, 'Toggle GDF 1')
button1.on_clicked(toggle_gdf1)

button_ax2 = plt.axes([0.7, 0.15, 0.1, 0.075])  # Button 2: Toggle GeoDataFrame 2
button2 = Button(button_ax2, 'Toggle GDF 2')
button2.on_clicked(toggle_gdf2)

# Show the plot
plt.show()
