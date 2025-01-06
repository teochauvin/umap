import osmnx as ox
from shapely.geometry import Point, MultiPolygon, Polygon, box
import geopandas as gpd
import pandas as pd
import numpy as np
import math 
import requests
import rasterio 
from rasterio.warp import calculate_default_transform, reproject, Resampling

from .coordinates import MapPoint


# REQUESTS

def get_buildings_dataframe(
        reference_point:MapPoint, 
        buffer_distance:float=1000.0, 
        merge_distance:float = 5.0, 
        default_height:float = 15.0) -> gpd.GeoDataFrame: 
    """ Returns the raw dataframe of al buldings in the requested area. """

    lon, lat = reference_point.lon, reference_point.lat
    lat_min, lon_min = _meters_to_latlon(lat, lon, -buffer_distance)
    lat_max, lon_max = _meters_to_latlon(lat, lon, buffer_distance)
    area = box(lon_min, lat_min, lon_max, lat_max) 

    """point = Point(reference_point.lon, reference_point.lat)
    area = point.buffer(buffer_distance / 111320)""" # Approx. (see README.md : approx)

    # Retrieve buildings within the buffer
    buildings = ox.features_from_polygon(area, tags={"building": True})

    # Assign heights 
    merged_gdfs = assign_heights(buildings, default_height)

    # Convexify 
    merged_gdfs = convexify_polygons(merged_gdfs)

    # Merge nearby buildings
    merged_gdfs = merge_nearby_buildings(merged_gdfs, merge_distance)

    # Remove holes
    merged_gdfs = remove_holes_from_gdf(merged_gdfs)

    # Simpligy geometry 
    # Add the tolerance to the function parameters 
    # Find a better way to simplify polygons 
    merged_gdfs["geometry"] = merged_gdfs["geometry"].simplify(tolerance=1e-5, preserve_topology=True)

    print("Geometry data collected from Open Street Map.")

    return merged_gdfs 


def get_topography(
        reference_point:MapPoint, 
        buffer_distance:float = 1000.0,
        filename:str="default") -> tuple[np.ndarray, np.ndarray, np.ndarray]: 
    """
        Returns the topography (elevation) in a requested area around a reference point. \\
        One major issue is that the approximation made is not the same as OpenSM request. 
    """
    
    lat, lon = reference_point.lat, reference_point.lon
    
    # Change the approx. 
    lat_min, lon_min = _meters_to_latlon(lat, lon, -buffer_distance)
    lat_max, lon_max = _meters_to_latlon(lat, lon, buffer_distance)

    # Construct the OpenTopography API URL
    api_url = "https://portal.opentopography.org/API/globaldem"
    request_params = {
        'demtype': 'SRTMGL1',  
        'south':lat_min,
        'east':lon_max,
        'west':lon_min, 
        'north':lat_max,
        'outputFormat': 'GeoTIFF', 
        'API_Key': 'e38baccddfcc5990e87ec1257f880dbc' # REMOVE: this is my personnal API key 
    }

    # Make the request to OpenTopography
    response = requests.get(api_url, params=request_params)

    # Check if the request was successful 
    # (see Open Topography website and documentation)
    if response.status_code == 200:

        # Write down the file (not necessary I think)
        with open(f"save/topography_{filename}.tif", "wb") as f:
            f.write(response.content)

        print("Topograpy data collected from Open Topography.")

    else:
        print(f"Error: {response.status_code}, {response.text}")


    # Load the file 
    with rasterio.open(f"save/topography_{filename}.tif") as src:

        # Read the elevation data
        elevation = src.read(1)  # First band (elevation)
        transform = src.transform  # Affine transform for geographic coordinates

        # Mask invalid (no-data) values
        elevation = np.ma.masked_invalid(elevation)

        # Generate grid coordinates
        rows, cols = elevation.shape
        x = np.linspace(0, cols - 1, cols)
        y = np.linspace(0, rows - 1, rows)

        x, y = np.meshgrid(x, y)  # Create a 2D grid of x and y coordinates
        x, y = rasterio.transform.xy(transform, y, x, offset="center")

        x = np.array(x).reshape(rows, cols)  # Reshape x to match elevation shape
        y = np.array(y).reshape(rows, cols) 

    return x, y, elevation


def get_network(reference_point:MapPoint, buffer_distance:float):
    """ Returns the network of roads from OSM. """

    lon, lat = reference_point.lon, reference_point.lat
    lat_min, lon_min = _meters_to_latlon(lat, lon, -buffer_distance)
    lat_max, lon_max = _meters_to_latlon(lat, lon, buffer_distance)
    area = box(lon_min, lat_min, lon_max, lat_max) 

    # Get the graph 
    G = ox.graph_from_polygon(area, network_type="drive")

    return G


def get_water(reference_point:MapPoint, buffer_distance:float) -> gpd.GeoDataFrame: 
    """ Returns the water bodies informations. """

    lon, lat = reference_point.lon, reference_point.lat
    lat_min, lon_min = _meters_to_latlon(lat, lon, -buffer_distance)
    lat_max, lon_max = _meters_to_latlon(lat, lon, buffer_distance)
    area = box(lon_min, lat_min, lon_max, lat_max) 
    
    # Get water features
    water_bodies = ox.features_from_polygon(area, tags={"natural": "water", "waterway": True, "landuse": "reservoir"})
    
    # Filter polygons and multipolygons
    water_bodies = water_bodies[water_bodies.geom_type.isin(["Polygon", "MultiPolygon"])]
    water_bodies = water_bodies.reset_index(drop=True)

    # Intersection 
    area_gdf = gpd.GeoDataFrame(geometry=[area], crs=water_bodies.crs)
    water_in_area = gpd.overlay(water_bodies, area_gdf, how="intersection")

    return water_in_area


def load_topography(filename:str): 
    """ Load a .tif file. """ 

    # Load the file 
    with rasterio.open(f"save/topography_{filename}.tif") as src:

        # Read the elevation data
        elevation = src.read(1)  # First band (elevation)
        transform = src.transform  # Affine transform for geographic coordinates

        # Mask invalid (no-data) values
        elevation = np.ma.masked_invalid(elevation)

        # Generate grid coordinates
        rows, cols = elevation.shape
        x = np.linspace(0, cols - 1, cols)
        y = np.linspace(0, rows - 1, rows)

        x, y = np.meshgrid(x, y)  # Create a 2D grid of x and y coordinates
        x, y = rasterio.transform.xy(transform, y, x, offset="center")

        x = np.array(x).reshape(rows, cols)  # Reshape x to match elevation shape
        y = np.array(y).reshape(rows, cols) 

    return x, y, elevation


# MANAGE DATA 
def convexify_geometry(geom):
    """ 
        convexify_geometry relies on shapely library to create a convex instance of a polygon. \\ 
        For a Polygon, return its convex hull. Might not be completely optimal. \\
        For a MultiPolygon, apply convex hull to each individual Polygon. \\
        If it's not a Polygon or MultiPolygon, return it as is.
    """

    if isinstance(geom, Polygon):
        return geom.convex_hull
    elif isinstance(geom, MultiPolygon):
        convex_polygons = [polygon.convex_hull for polygon in geom.geoms]
        return MultiPolygon(convex_polygons)
    else: 
        return geom
    

def convexify_polygons(gdf):
    """ convexify_polygons apply the convexify_geometry on a set of polygons. """
    gdf["geometry"] = gdf["geometry"].apply(convexify_geometry)
    return gdf


def assign_heights(buildings_gdf, default_height=20): 
    """ 
        From the buidling_gdfs geo-dataframes, assign height data of each buidling. \\
        If the data is not available, assigns a default value. 
    """
    
    # The empty case 
    if buildings_gdf.empty:
        print("No buildings to merge.")
        return buildings_gdf
    
    # Determine the height column or assign default
    if "height" in buildings_gdf.columns:
        buildings_gdf.loc[:, "height"] = pd.to_numeric(buildings_gdf["height"], errors="coerce")
    elif "building:levels" in buildings_gdf.columns:
        buildings_gdf.loc[:, "height"] = pd.to_numeric(buildings_gdf["building:levels"], errors="coerce") * 3  # Approx. 3m per level
    else:
        buildings_gdf.loc[:, "height"] = default_height

    # Replace NaN values in height with the default value
    buildings_gdf["height"] = buildings_gdf["height"].fillna(default_height).infer_objects(copy=False)

    # Remove NaN values from 'height' column and group by height (should never happen) 
    buildings_gdf = buildings_gdf.dropna(subset=['height'])

    return buildings_gdf


def merge_nearby_buildings(buildings_gdf, merge_distance:float=5.0) -> gpd.GeoDataFrame:
    """
        merge_nearby_buidlings returns a new dataframe with merged buildings. \\ 
        Two buldings are merges if they are close enough and have the same height. \\
        Approx. meters to degrees (see: README.md : coordinate systems)
    """

    # The empty case 
    if buildings_gdf.empty:
        print("No buildings to merge.")
        return buildings_gdf

    # Convert merge_distance to degrees (approximation, suitable for small areas)
    distance_in_degrees = merge_distance / 111320  # Approx. meters to degrees

    # Reproject to a projected CRS for accurate buffering
    # Using EPSG:3395 (World Mercator)
    buildings_gdf = buildings_gdf.to_crs(epsg=3395)  

    # Store merged geometries in a list
    merged_geometries = []

    # Group by height
    for height, group in buildings_gdf.groupby('height'):

        # Buffer the geometries to merge nearby buildings
        buffered = group.geometry.buffer(distance_in_degrees)

        # Merge the buffered geometries using union_all() instead of unary_union
        merged_geometry = buffered.union_all()

        # Optional: Remove the buffer to restore original geometry sizes
        merged_geometry = merged_geometry.buffer(-distance_in_degrees)

        # Add the merged geometry to the list
        merged_geometries.append({
            'height': height,
            'geometry': merged_geometry
        })

    # Create a new GeoDataFrame with the merged geometries
    merged_gdf = gpd.GeoDataFrame(merged_geometries, geometry='geometry', crs=buildings_gdf.crs)

    # Reproject back to the original CRS if needed
    # Assuming original CRS is WGS84 (EPSG:4326)
    merged_gdf = merged_gdf.to_crs(epsg=4326)  

    return merged_gdf


def _remove_holes(geometry):
    """
        remove_holes returns a shapely geometry (Polygon, MultiPolygon) without holes. \\ 
        For polygons : keeps only the exterior ring.  \\ 
        For multi polygons : recreate each polygon without holes. \\ 
        Otherwise it returns the original geometry object. 
    """

    # The empty case 
    if geometry.is_empty:
        return geometry

    # Remove holes 
    if geometry.geom_type == "Polygon":
        return Polygon(geometry.exterior)
    elif geometry.geom_type == "MultiPolygon":
        return MultiPolygon([Polygon(p.exterior) for p in geometry.geoms])
    
    else:
        return geometry
    
def remove_holes_from_gdf(gdf:gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """ 
        remove_holes_from_gdf removes the holes of all polygons describred in a geo dataframe. \\ 
        It returns the modified dataframe. 
    """
    gdf["geometry"] = gdf["geometry"].apply(_remove_holes)
    return gdf


def _meters_to_latlon(lat:float, lon:float, distance_meters:float) -> tuple[float, float]: 
    """ The approximation made is to consider the Earth perfectly spherical. """

    # Earth radius in meters
    R = 6378137.0
    
    # Convert meters to degrees (approximation)
    # (see README.md : approximations)  
    lat_offset = distance_meters / R
    lon_offset = distance_meters / (R * math.cos(math.pi * lat / 180))

    # Calculate new lat/lon
    lat_new = lat + (lat_offset * 180 / math.pi)
    lon_new = lon + (lon_offset * 180 / math.pi)
    
    return lat_new, lon_new
