
from .extract_functions import * 
from .building import Building
from .elevation import Elevation
from .network import Network

import pickle
import uuid
import json

class Map: 
    """ DOCME """

    def __init__(
            self, 
            reference_point:MapPoint, 
            buffer_distance:float, 
            buildings_gdfs:gpd.GeoDataFrame, 
            original_gdfs:gpd.GeoDataFrame,
            buildings:list[Building], 
            elevation:Elevation, 
            network:Network, 
            special_data:dict[gpd.GeoDataFrame], 
            name:str, 
            topography:bool):
        
        # Infos 
        self.name=name 
        self.id_tag = str(uuid.uuid4())

        # Map coordinates 
        self.reference_point:MapPoint = reference_point 
        self.buffer_distance:float = buffer_distance

        # Map assets 
        self.buildings_gdfs:gpd.GeoDataFrame = buildings_gdfs
        self.raw_buildings_gdfs:gpd.GeoDataFrame = original_gdfs  
        self.inflated_buildings_gdfs:gpd.GeoDataFrame = buildings_gdfs

        self.buildings:list[Building] = buildings
        self.elevation:Elevation = elevation 
        self.road_network:Network = network 
        self.special_data:dict[gpd.GeoDataFrame] = special_data

        # Flags 
        self.topography = topography


    @classmethod
    def init_from_request(cls, reference_point:MapPoint, buffer_distance:float=1000.0, name:str="", topography:bool=False):
        """ 
            Send a request to the different APIs. \\ 
            Get buldings, roads, elevation, and all possible interesting data. \\ 
            Build the Map. 
        """

        # Init 
        buildings = []
        elevation = None
        network = None
        special_data = {} 

        # Get buildings from OSM
        buildings_gdfs, raw_gdfs = get_buildings_dataframe(reference_point, buffer_distance) 

        # Road network
        G = get_network(reference_point, buffer_distance)

        # The list of buidlings 
        for _, building in buildings_gdfs.iterrows():  
            # Iterate through rows of each GeoDataFrame
            # Create a Building object and append it to the list
            buildings.append(Building(building["geometry"], building["height"]))

        # Elevation 
        if topography: 
            # Get topography data from OT
            x_elevation,y_elevation, elevation = get_topography(reference_point, buffer_distance, filename=name) 
            elevation = Elevation(x_elevation, y_elevation, elevation) 
        else: 
            elevation = None

        # Network 
        network = Network.get_graph(G)

        # Water bodies (special data)
        special_data["water"] = get_water(reference_point, buffer_distance)
  
        return cls(reference_point, buffer_distance, buildings_gdfs, raw_gdfs, buildings, elevation, network, special_data, name, topography)

    @classmethod
    def load(cls, filename:str):
        """ Load and initialize a map object."""
        with open(f"save/mapobject_{filename}.pkl", 'rb') as f:
            return pickle.load(f)
        print("Map loaded.")

    # Binary serialization 
    def save(self) -> None: 
        """ Save the map as a file. """
        with open(f'save/mapobject_{self.name}.pkl', 'wb') as f:
            pickle.dump(self, f)
        print("Map saved.")


    
    def get_realtive_coordinates(self, lon:float, lat:float): 
        """ Returns relative coordinates (in meters) from the reference point. """

        def to_radians(degrees):
            return degrees * math.pi / 180

        #Get the reference point coordinates 
        ref_lat, ref_lon = self.reference_point.lat, self.reference_point.lon
        

        # Earth's radius in meters (assume it's a sphere)
        R = 6371000 

        lat1, lon1 = to_radians(ref_lat), to_radians(ref_lon)
        lat2, lon2 = to_radians(lat), to_radians(lon)

        # Compute the difference in coordinates (in radians)
        d_lat = lat1 - lat2
        d_lon = lon1 - lon2

        # Calculate the relative distances in meters
        x = d_lon * R * math.cos((lat1 + lat2) / 2)  # Longitude distance scaled by cosine of latitude
        y = d_lat * R  # Latitude distance scaled by Earth's radius
  
        return x,y


    def save_geometry_as_json(self): 
        """ Saves the map geometry in a json file. """

        # Path to the JSON file
        file_path = f"save/{self.name}.json"

        # Init data
        data = {
            "env_id": self.id_tag,
            "N_objects": len(self.buildings),
            "city": "default",
            "geometries" : []
        }

        # Write each building coordinates in a json file 
        for building in self.buildings:     
            
            # Get the polygon 
            polygon = building.geometry
            height = building.height

            
            
            # Extract the coordinates from the polygon 
            if isinstance(polygon, Polygon):
                # Process exterior coordinates of a Polygon

                # Initialize a dictionary to store x, y, z coordinates
                coordinates_dict = {"x": [], "y": []}

                for coord in polygon.exterior.coords:
                    x, y = coord  # Unpack the 3D coordinates
                    x_rel, y_rel = self.get_realtive_coordinates(x,y)

                    coordinates_dict["x"].append(x_rel)
                    coordinates_dict["y"].append(y_rel)

                # Add the geometry 
                data["geometries"].append((coordinates_dict, height))
            
            elif isinstance(polygon, MultiPolygon):
                # Process each Polygon in the MultiPolygon
                for p in polygon.geoms:

                    # Initialize a dictionary to store x, y, z coordinates
                    coordinates_dict = {"x": [], "y": []}

                    for coord in p.exterior.coords:
                        x, y = coord  # Unpack the 3D coordinates
                        x_rel, y_rel = self.get_realtive_coordinates(x,y)

                        coordinates_dict["x"].append(x_rel)
                        coordinates_dict["y"].append(y_rel)

                    # Add the geometry 
                    data["geometries"].append((coordinates_dict, height)) 

        # Open the file in write mode and write the JSON data
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        print("Geometry JSON file saved.")




    def update_merging_threshold(self, new_merge_thr:float) -> None: 
        """ 
            Update the geodataframe of building shapes regarding 
            a new merging threshold applied to the raw geodataframe data.
            NOTE: Take into account the buinding heights. --> move to extract functions ? 
        """

        self.buildings_gdfs = merge_nearby_buildings(self.raw_buildings_gdfs, new_merge_thr)
        self.buildings_gdfs = remove_holes_from_gdf(self.buildings_gdfs) 

    def compute_inflated_gfs(self, inflate:float):
        """ Modifies the inflated geodataframe. """

        # Reproject to a projected CRS 
        gdf_projected = self.raw_buildings_gdfs.to_crs(epsg=3395)

        # Now apply the buffer (inflating by 100 meters)
        gdf_projected['geometry'] = gdf_projected['geometry'].buffer(inflate)

        # If you need to bring the data back to its original geographic CRS
        gdf_projected = gdf_projected.to_crs(self.inflated_buildings_gdfs.crs)

        merged = gdf_projected.unary_union

        merged_gdf = gpd.GeoDataFrame({'geometry': [merged]})
        merged_gdf.crs = gdf_projected.crs 

        # Reproject back to the original CRS if needed
        # Assuming original CRS is WGS84 (EPSG:4326)
        self.inflated_buildings_gdfs = merged_gdf.to_crs(epsg=4326)  

        # remove holes 
        remove_holes_from_gdf(self.inflated_buildings_gdfs)

    def _compute_distance_with_elevation(self): 
        pass 

    def _compute_distance_on_flat(self): 
        pass 

    def _compute_projection_error(self): 
        pass 

    

    