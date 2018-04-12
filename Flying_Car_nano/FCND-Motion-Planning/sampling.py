import numpy as np
from shapely.geometry import Polygon, Point, LineString

class Sampler():

    def __init__(self, data):
        #super().__init__(connection)

        self.data = data
        self._polygons = extract_polygons(data)
        self._xmin = 0
        self._xmax = 0
  
        self._ymin = 0
        self._ymax = 0
        
        self._zmin = 0
        self._zmax = 0


        #sample(num_samples)

        # register all your callbacks here
        # self.register_callback(MsgID.LOCAL_POSITION, self.local_position_callback)
        # self.register_callback(MsgID.LOCAL_VELOCITY, self.velocity_callback)
        # self.register_callback(MsgID.STATE, self.state_callback)

    def sample(self, num_samples):
        self._xmin = np.min(self.data[:, 0] - self.data[:, 3])
        self._xmax = np.max(self.data[:, 0] + self.data[:, 3])

        self._ymin = np.min(self.data[:, 1] - self.data[:, 4])
        self._ymax = np.max(self.data[:, 1] + self.data[:, 4])

        self._zmin = 0
        self._zmax = 10.0#np.max(self.data[:, 2] + self.data[:, 5])
        print("X")
        print("min = {0}, max = {1}\n".format(self._xmin, self._xmax))

        print("Y")
        print("min = {0}, max = {1}\n".format(self._ymin, self._ymax))

        print("Z")
        print("min = {0}, max = {1}".format(self._zmin, self._zmax))
        

        xvals = np.random.uniform(self._xmin, self._xmax, num_samples)
        yvals = np.random.uniform(self._ymin, self._ymax, num_samples)
        zvals = np.random.uniform(self._zmin, self._zmax, num_samples)

        samples = np.array(list(zip(xvals, yvals, zvals)))
        
        #t0 = time.time()
        Nodes = []
        for point in samples:
            if not collides(self._polygons, point):
                Nodes.append(point)
        #time_taken = time.time() - t0
        print(len(Nodes))
        
        return Nodes
def collides(polygons, point):   
    # TODO: Determine whether the point collides
    # with any obstacles.    
    for (p, height) in polygons:
        if p.contains(Point(point)) and height >= point[2]:
            return True
    return False 
def extract_polygons(data):

    polygons = []
    for i in range(data.shape[0]):
        north, east, alt, d_north, d_east, d_alt = data[i, :]

        # polygons.append(Polygon(coords))
        # TODO: Extract the 4 corners of the obstacle
        p1 = (north - d_north,east + d_east)
        p2 = (north + d_north,east + d_east)
        p3 = (north + d_north,east - d_east)
        p4 = (north - d_north,east - d_east)
        # NOTE: The order of the points matters since
        # `shapely` draws the sequentially from point to point.
        #
        # If the area of the polygon is 0 you've likely got a weird
        # order.
        corners = [p1,p2,p3,p4]
        
        # TODO: Compute the height of the polygon
        height = alt + d_alt

        # TODO: Once you've defined corners, define polygons
        p = Polygon(corners)
        polygons.append((p, height))

    return polygons 
