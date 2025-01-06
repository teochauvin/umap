import geopandas as gpd 
import osmnx as ox

class Network: 
    """ DOCME """

    def __init__(self, nodes:gpd.GeoDataFrame, edges:gpd.GeoDataFrame, vertices:dict, adj:dict, G): 
        self.G = G 
        self.vertices = vertices 
        self.adj = adj 
        self.edges = edges
        self.nodes = nodes 

    def __repr__(self):
        return f"{self.edges.columns}, {self.nodes.columns}"
    
    @classmethod
    def get_graph(cls, G): 
        """ Returns the pythonic graph. """

        nodes, edges = ox.graph_to_gdfs(G)
        print(nodes)
        #u, v, key = edges.index.get_level_values('u'), edges.index.get_level_values('v'), edges.index.get_level_values('key')

        adj = {}
        vertices = {}

        # Iterate over the edges and add (u, v) pairs to the dictionary
        for (u, v, key), row in edges.iterrows():
            adj.setdefault(u, []).append(v) 

        for id,row in edges.iterrows():
            vertices.setdefault(id, []).append(row["geometry"].wkt)

        return cls(nodes, edges, vertices, adj, G) 
    
    # getters 