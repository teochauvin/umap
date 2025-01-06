
from .extract_functions import * 
from .building import Building
from .elevation import Elevation
from .network import Network

import h5py
import pickle

class Map: 
    """ DOCME """

    def __init__(
            self, 
            reference_point:MapPoint, 
            buffer_distance:float, 
            buildings_gdfs:gpd.GeoDataFrame, 
            buildings:list[Building], 
            elevation:Elevation, 
            network:Network, 
            special_data:dict[gpd.GeoDataFrame], 
            name:str, 
            topography:bool):
        
        # Infos 
        self.name=name 

        # Map coordinates 
        self.reference_point:MapPoint = reference_point 
        self.buffer_distance:float = buffer_distance

        # Map assets 
        self.buildings_gdfs:gpd.GeoDataFrame = buildings_gdfs
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
        buildings_gdfs = get_buildings_dataframe(reference_point, buffer_distance) 

        # Road network
        G = get_network(reference_point, buffer_distance)

        # The list of buidlings 
        for _, building in buildings_gdfs.iterrows():  # Iterate through rows of each GeoDataFrame
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
  
        return cls(reference_point, buffer_distance, buildings_gdfs, buildings, elevation, network, special_data, name, topography)

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
    
    




    def generate_flow(self): 
        pass 

    def _compute_distance_with_elevation(self): 
        pass 

    def _compute_distance_on_flat(self): 
        pass 

    def _compute_projection_error(self): 
        pass 

    

    