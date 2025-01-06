import geopandas as gpd 

class Network: 
    """ DOCME """

    def __init__(self, edges:gpd.GeoDataFrame, nodes:gpd.GeoDataFrame, G): 
        self.edges = edges 
        self.nodes = nodes 
        self.G = G 

    # getters 