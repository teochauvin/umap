import geopandas as gpd 
import osmnx as ox
import numpy as np 

class Network: 
    """ DOCME """

    def __init__(self, nodes:gpd.GeoDataFrame, edges:gpd.GeoDataFrame, vertices:dict, adj:dict, G): 
        self.G = G 
        self.vertices = vertices 
        self.adj = adj 
        self.edges = edges
        self.nodes = nodes 
        self.list_extremal_nodes:np.ndarray = [] 

        # Init 
        self.set_extremal_nodes()


    def __repr__(self):
        return f"{self.edges.columns}, {self.nodes.columns}"
    
    @classmethod
    def get_graph(cls, G): 
        """ Returns the pythonic graph. """

        nodes, edges = ox.graph_to_gdfs(G)

        adj = {}
        vertices = {}

        # Iterate over the edges and add (u, v) pairs to the dictionary
        for (u, v, key), row in edges.iterrows():
            adj.setdefault(u, []).append(v) 
            adj.setdefault(v, []).append(u) 

        for id,row in nodes.iterrows():
            vertices[id] = row["geometry"]

        return cls(nodes, edges, vertices, adj, G) 
    
    
    def set_extremal_nodes(self) -> None: 
        """ 
            Set the extremal nodes. 
            Extremal nodes are nodes that can be start or end points flows. 
        """

        extremal_node = [] 

        for (u,v_list) in self.adj.items(): 

            # The point 
            p = self.vertices[u]

            # Nodes that have only one neighbor 
            if len(v_list) <= 2: 
                extremal_node.append([p.x, p.y])


        self.list_extremal_nodes = np.asarray(extremal_node)