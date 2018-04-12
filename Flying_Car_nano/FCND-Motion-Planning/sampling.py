class Sampler(data):

    def __init__(data):
        #super().__init__(connection)

		_polygons = extract_polygons(data)
        _xmin = 0
		_xmax = 0
  
        _ymin = 0
        _ymax = 0
        
        _zmin = 0
        _zmax = 0

        # register all your callbacks here
        # self.register_callback(MsgID.LOCAL_POSITION, self.local_position_callback)
        # self.register_callback(MsgID.LOCAL_VELOCITY, self.velocity_callback)
        # self.register_callback(MsgID.STATE, self.state_callback)

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
def sample(num_samples):
	_xmin = np.min(data[:, 0] - data[:, 3])
	_xmax = np.max(data[:, 0] + data[:, 3])

	_ymin = np.min(data[:, 1] - data[:, 4])
	_ymax = np.max(data[:, 1] + data[:, 4])

	_zmin = 0
	_zmax = np.max(data[:, 2] + data[:, 5])
	print("X")
	print("min = {0}, max = {1}\n".format(_xmin, _xmax))

	print("Y")
	print("min = {0}, max = {1}\n".format(_ymin, _ymax))

	print("Z")
	print("min = {0}, max = {1}".format(_zmin, _zmax))
	 

	xvals = np.random.uniform(_xmin, _xmax, num_samples)
	yvals = np.random.uniform(_ymin, _ymax, num_samples)
	zvals = np.random.uniform(_zmin, _zmax, num_samples)

	samples = np.array(list(zip(xvals, yvals, zvals)))
	
	#t0 = time.time()
	Nodes = []
	for point in samples:
		if not collides(polygons, point):
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