
from .extract_functions import * 
from .building import Building
from .elevation import Elevation
from .network import Network

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
            name:str):
        
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


    @classmethod
    def init_from_request(cls, reference_point:MapPoint, buffer_distance:float=1000.0, name:str=""):
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

        # Get topography data from OT
        x_elevation,y_elevation, elevation = get_topography(reference_point, buffer_distance, filename=name) 

        # Road network
        edges, nodes, G = get_network(reference_point, buffer_distance)

        # The list of buidlings 
        for _, building in buildings_gdfs.iterrows():  # Iterate through rows of each GeoDataFrame
            # Create a Building object and append it to the list
            buildings.append(Building(building["geometry"], building["height"]))

        # Elevation 
        elevation = Elevation(x_elevation, y_elevation, elevation) 

        # Network 
        network = Network(edges, nodes, G)

        # Water bodies (special data)
        special_data["water"] = get_water(reference_point, buffer_distance)
  
        return cls(reference_point, buffer_distance, buildings_gdfs, buildings, elevation, network, special_data, name)


 
    @classmethod
    def load_from_file(cls, filename:str) -> None:
        """ Build a map from an existing one saved as a file. """ 
        pass 

    def export(self) -> None: 
        """ Save the map as a file. """
        
        # save GeoDataFrame
        buildings = self.buildings_gdfs['geometry'].apply(lambda x: x.wkt)
        edges = self.road_network.edges["geometry"].apply(lambda x: x.wkt) 
        nodes = self.road_network.nodes["geometry"].apply(lambda x: x.wkt) 

        buildings.to_hdf(f"save/{self.name}_geodataframes.h5", key='buildings', mode='w')
        edges.to_hdf(f"save/{self.name}_geodataframes.h5", key='edges')
        nodes.to_hdf(f"save/{self.name}_geodataframes.h5", key='nodes')

        for key, value in self.special_data.items(): 
            v = value["geometry"].apply(lambda x: x.wkt)
            v.to_hdf(f"save/{self.name}_geodataframes.h5", key=key) 


    
    




    def generate_flow(self): 
        pass 

    def _compute_distance_with_elevation(self): 
        pass 

    def _compute_distance_on_flat(self): 
        pass 

    def _compute_projection_error(self): 
        pass 

    

    