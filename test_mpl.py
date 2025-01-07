import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

# Create a sample GeoDataFrame (or load your own)
from shapely.geometry import Point

# Generate random data
num_points = 500
data = {
    "value": np.random.rand(num_points) * 100,  # Random values
    "geometry": [Point(x, y) for x, y in zip(np.random.rand(num_points) * 10, np.random.rand(num_points) * 10)],
}
gdf = gpd.GeoDataFrame(data)

# Initial filter value
initial_filter = 50

# Filter the GeoDataFrame
filtered_gdf = gdf[gdf["value"] <= initial_filter]

# Create a figure and axis
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)  # Leave space for the slider

# Plot the initial GeoDataFrame
base_plot = filtered_gdf.plot(ax=ax, markersize=10, color="blue", legend=True)

# Set axis limits
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_title("Filtered GeoDataFrame")

# Set up the slider
ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])  # [left, bottom, width, height]
value_slider = Slider(ax_slider, 'Max Value', 0, 100, valinit=initial_filter, valstep=1)

# Define the update function
def update(val):
    max_value = value_slider.val  # Get the slider value
    filtered_gdf = gdf[gdf["value"] <= max_value]  # Filter the GeoDataFrame
    
    # Clear the previous plot and replot
    ax.clear()
    filtered_gdf.plot(ax=ax, markersize=10, color="blue", legend=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_title(f"Filtered GeoDataFrame (Max Value: {max_value})")
    fig.canvas.draw_idle()  # Redraw the figure

# Connect the slider to the update function
value_slider.on_changed(update)

plt.show()
