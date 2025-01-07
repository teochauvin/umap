import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

# Define the bounding box of the area (e.g., a rectangular region)
lat_min, lat_max = 40.5, 41.0  # Latitude range
lon_min, lon_max = -74.2, -73.7  # Longitude range

# Define the grid resolution (smaller step -> finer grid)
lat_step = 0.1
lon_step = 0.1

# Generate grid points
latitudes = np.arange(lat_min, lat_max, lat_step)
longitudes = np.arange(lon_min, lon_max, lon_step)

# Prepare a DataFrame to store results
wind_data = []

# Open-Meteo API base URL
base_url = "https://api.open-meteo.com/v1/forecast"

# Loop over all grid points
for lat in latitudes:
    for lon in longitudes:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "windspeed_10m,winddirection_10m",
            "timezone": "auto"
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Extract hourly wind data
            times = data["hourly"]["time"]
            windspeed = data["hourly"]["windspeed_10m"]
            winddirection = data["hourly"]["winddirection_10m"]
            
            # Store data for this point
            for t, ws, wd in zip(times, windspeed, winddirection):
                wind_data.append({"latitude": lat, "longitude": lon, "time": t, "windspeed": ws, "winddirection": wd})
        else:
            print(f"Failed for lat: {lat}, lon: {lon} - {response.status_code}")

# Convert to a DataFrame
wind_df = pd.DataFrame(wind_data)

specific_time = "2025-01-07T00:00"

# Filter the DataFrame for the specific time
filtered_df = wind_df[wind_df["time"] == specific_time]

# Convert wind direction to vector components
filtered_df["u"] = -filtered_df["windspeed"] * np.sin(np.radians(filtered_df["winddirection"]))
filtered_df["v"] = -filtered_df["windspeed"] * np.cos(np.radians(filtered_df["winddirection"]))

# Plot the wind data
plt.figure(figsize=(10, 8))
plt.quiver(
    filtered_df["longitude"],
    filtered_df["latitude"],
    filtered_df["u"],
    filtered_df["v"],
    filtered_df["windspeed"],  # Color by windspeed
    scale=50,                  # Adjust scale for arrow size
    cmap="viridis",            # Color map for windspeed
    width=0.005                # Arrow width
)

# Add colorbar
cbar = plt.colorbar(label="Wind Speed (m/s)")
cbar.set_label("Wind Speed (m/s)", fontsize=12)

# Customize the plot
plt.title(f"Wind Vector Field at {specific_time}", fontsize=16)
plt.xlabel("Longitude", fontsize=12)
plt.ylabel("Latitude", fontsize=12)
plt.grid(True)

# Show the plot
plt.show()
# Save to a CSV or GeoDataFrame for further use
wind_df.to_csv("wind_data_area.csv", index=False)
