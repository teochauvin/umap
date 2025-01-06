from umap import * 

import matplotlib.pyplot as plt


# TEMPORARY DEBUG
if __name__ == "__main__": 

    # reference point tls 
    name="tls"
    reference_point = MapPoint(
        lon=1.4432166595189688, 
        lat=43.5910143632871)
    
    """# lyon 45.774792, 4.832051
    name = "lyon"
    reference_point = MapPoint(
        lon=4.832051, 
        lat=45.774792)
    
    # paris 48.862928, 2.329298
    name = "paris"
    reference_point = MapPoint(
        lon=2.329298, 
        lat=48.862928)
    
    43.563971, 1.479148
    name = "enac"
    reference_point = MapPoint(
        lon=1.479148, 
        lat=43.563971)
    
    48.858234252317324, 2.2941945479347217
    name = "eiffelTower"
    reference_point = MapPoint(
        lon=2.2941945479347217,
        lat=48.858234252317324
    )"""
    
    
    
    # Isnitialize map 
    umap = Map.init_from_request(reference_point, buffer_distance=1000.0, name=name) 

    # Export map 
    umap.save()

    # Load a file
    # new_umap = Map.load(name)

    # Get graph data
    # vertices, adj = umap.road_network.vertices, umap.road_network.adj

    # Visualize map 
    plot(umap)

    pass 