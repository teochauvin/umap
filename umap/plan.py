import numpy as np 

class Plan: 

    def __init__(self, missions:np.ndarray, K_uavs:int, extremal_points:np.ndarray): 

        self.K_uavs = K_uavs 
        self.extremal_points = extremal_points 
        self.missions = missions 

    def __repr__(self) -> str:
        chaine = "" 
        for m in self.missions: 
            s,e,t = m
            chaine += f"start: {self.extremal_points[int(s)]}, end: {self.extremal_points[int(e)]} at time: {t}. \n"
        return chaine 


    @classmethod
    def init_poisson_flow(cls, K_uavs:int, flow:float, extremal_points:np.ndarray):
        """ 
            Initialize K random flows between randomly selected extremal points with Poisson generated 
            departure times. TODO: Have a specific lambda value for each mission path. 
        """

        # A mission is defined with a start point and an end point (extremal points indices) 
        # Each mission also has its own departure time following a Poisson distribution.
        # Each UAV has a mission. 
        N = extremal_points.shape[0]

        # Generate all possible pairs (i, j) where i != j
        all_pairs = np.array([(i, j) for i in range(N) for j in range(N) if i != j])

        # Select K random indices
        random_indices = np.random.choice(len(all_pairs), size=K_uavs, replace=False)
        mission_point_indices = all_pairs[random_indices]

        # Departure time 
        poisson_values = np.random.poisson(flow, K_uavs).astype(float)
        poisson_values = poisson_values.reshape(-1, 1)

        # TODO: add uncertainty on departure time 

        # Build missions         
        missions = np.hstack((mission_point_indices, poisson_values))

        # Create a plan
        return cls(missions, K_uavs, extremal_points) 
        


