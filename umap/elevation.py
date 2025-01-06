import numpy as np 

class Elevation: 
    """ DOCME """

    def __init__(self, x:np.ndarray, y:np.ndarray, elevation_data:np.ndarray): 
        self.elevation = elevation_data
        self.x = x 
        self.y = y 

    @property
    def xyz(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]: 
        return self.x, self.y, self.elevation 

    # Getters 