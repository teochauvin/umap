from umap import * 

import matplotlib.pyplot as plt


# TEMPORARY DEBUG
if __name__ == "__main__": 

    # reference point tls 
    reference_point = MapPoint(
        lon=1.4432166595189688, 
        lat=43.5910143632871)
    
    # lyon 45.774792, 4.832051
    reference_point = MapPoint(
        lon=4.832051, 
        lat=45.774792)
    
    # paris 48.862928, 2.329298
    reference_point = MapPoint(
        lon=2.329298, 
        lat=48.862928)
    
    43.563971, 1.479148
    reference_point = MapPoint(
        lon=1.479148, 
        lat=43.563971)
    
    name="enac"
    
    # Isnitialize map 
    umap = Map.init_from_request(reference_point, buffer_distance=1000.0, name=name) 

    # Export map 
    umap.export()

    # Visualize map 
    plot(umap)

    pass 