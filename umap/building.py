import numpy as np 
from shapely.geometry import Polygon, MultiPolygon

from .coordinates import MapPoint

class Building: 
    """ DOCME """

    def __init__(self, geometry:Polygon, height:float): 
        self.geometry = geometry 
        self.height = height
        self.area = self._compute_area()

    def xy(self) -> np.ndarray: 
        pass 
    
    def _compute_area(self) -> float: 
        """ Returns the area of a closed polygon. """ 
        return self.geometry.area
    


