from umap import * 

import matplotlib.pyplot as plt


if __name__ == "__main__": 

    # reference point tls 
    name="tls"
    reference_point = MapPoint(
        lon=1.4432166595189688, 
        lat=43.5910143632871)
    
    # lyon 45.774792, 4.832051
    name = "lyon"
    reference_point = MapPoint(
        lon=4.832051, 
        lat=45.774792)
    
    # paris 48.862928, 2.329298
    """name = "paris"
    reference_point = MapPoint(
        lon=2.329298, 
        lat=48.862928)
    
    # 43.563971, 1.479148
    name = "enac"
    reference_point = MapPoint(
        lon=1.479148, 
        lat=43.563971)"""

    name = "eiffelTower"
    reference_point = MapPoint(
        lon=2.2941945479347217,
        lat=48.858234252317324
    )
    
    # Initialize map 
    umap = Map.init_from_request(reference_point, buffer_distance=1000.0, name=name, topography=True) 

    # Export map 
    umap.save()
    umap.save_geometry_as_json()

    # Load a file
    umap:Map = Map.load(name)

    # Build missions 
    # TODO: 1st version 
    plans = Plan.init_poisson_flow(K_uavs=100, flow=1.0, extremal_points=umap.road_network.list_extremal_nodes)

    # Visualize map 
    plot(umap)
