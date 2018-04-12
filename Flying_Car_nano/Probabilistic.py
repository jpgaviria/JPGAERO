from sklearn.neighbors import KDTree
import numpy as np
import networkx as nx
#import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, LineString
from queue import PriorityQueue
from grid import create_grid

plt.rcParams['figure.figsize'] = 8, 8
filename = 'colliders.csv'
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
def collides(polygon, point):   
    # TODO: Determine whether the point collides
    # with any obstacles.
    collide = False
    #for poly in polygons:
    if polygon[0].contains(Point(point))and polygon[1] >= point[2]:
        collide = True    
    return collide
def heuristic(n1, n2):
    # TODO: complete
    return 0
def a_star(graph, heuristic, start, goal):
    """Modified A* to work with NetworkX graphs."""
    
    # TODO: complete
    return []
def can_connect(node1, node2 ,polygons):
    # 2) write a method "can_connect()" that:
    # casts two points as a shapely LineString() object
    # tests for collision with a shapely Polygon() object
    # returns True if connection is possible, False otherwise
    possible = False
    n1 = np.array(node1)
    n2 = np.array(node2)
    line = LineString([n1[:2],n2[:2]])
    for poly in polygons:
        possible = False
        if not line.crosses(poly[0]):# and poly[1] >= min(n1[2], n2[2]):
            possible = True
        elif possible == False:
            break
    return possible
    
    # possible = True
    # for n in g.nodes:
    #     possible = True
    #     n1 = np.array(node)
    #     n2 = np.array(n)
    #     line = LineString([n1,n2])
    #     if line.length >0.0:
    #         for poly in polygons:    
    #             if line.crosses(poly[0]):
    #                 possible = False
    #                 break
    #         if possible:
    #             g.add_edge(tuple(n1),tuple(n2))
    # return possible, g
if __name__ == "__main__":
    # Generate some random 3-dimensional points
    #np.random.seed(0)
    #p#oints = np.random.random((20, 3))  # 10 points in 3 dimensions
    # Cast points into a KDTree data structure
    #tree = KDTree(points)              
    # Extract indices of 3 closest points
    # Note: need to cast search point as a list 
    # and return 0th element only to get back list of indices
    #idxs = tree.query([points[0]], k=3, return_distance=False)[0]              
    # indices of 3 closest neighbors (will vary due to random sample)
    #print(idxs)
    #print(points[idxs[0]])
    #print(points[idxs[1]])
    #print(nx.__version__)

    data = np.loadtxt(filename, delimiter=',', dtype='Float64', skiprows=2)
    print(data)
    #for i in range(data.shape[0]):
    #    north, east, alt, d_north, d_east, d_alt = data[i, :]

    # TODO: sample points randomly
    # then use KDTree to find nearest neighbor polygon
    # and test for collision
    print (data[:,:3])
    polygons = extract_polygons(data)

    xmin = np.min(data[:, 0] - data[:, 3])
    xmax = np.max(data[:, 0] + data[:, 3])

    ymin = np.min(data[:, 1] - data[:, 4])
    ymax = np.max(data[:, 1] + data[:, 4])

    zmin = 0
    # Limit the z axis for the visualization
    zmax = 10 #np.max(data[:, 2] + data[:, 5])

    num_samples = 300

    xvals = np.random.uniform(xmin, xmax, num_samples)
    yvals = np.random.uniform(ymin, ymax, num_samples)
    zvals = np.random.uniform(zmin, zmax, num_samples)

    zvalsMax = np.max(zvals)

    points = np.array(list(zip(xvals, yvals, zvals)))

    #points[:10]
    #for point in points:
    #    if not collides(polygons, point):
    #        to_keep.append(point)

    nodes = []
    #points = np.random.random((100, 3))  # 10 points in 3 dimensions
    tree = KDTree(data[:,:3])


    for p in points:
        idxs = tree.query([p], k=1, return_distance=False)[0]
        print(idxs) 
        if not collides(polygons[idxs[0]], p):
            nodes.append(p)   
    # idxs = tree.query([points[1]], k=3, return_distance=False)[0] 
    # print(idxs)
              
    # idxs = tree.query([points[0]], k=3, return_distance=False)[0]
    # TODO: connect nodes
    # Suggested method
        # 1) cast nodes into a graph called "g" using networkx
        # 2) write a method "can_connect()" that:
            # casts two points as a shapely LineString() object
            # tests for collision with a shapely Polygon() object
            # returns True if connection is possible, False otherwise
        # 3) write a method "create_graph()" that:
            # defines a networkx graph as g = Graph()
            # defines a tree = KDTree(nodes)
            # test for connectivity between each node and 
                # k of it's nearest neighbors
            # if nodes are connectable, add an edge to graph
        # Iterate through all candidate nodes!
    #1
    g = nx.Graph()
    for node in nodes:
        g.add_node((node[0],node[1]))
    #2,3
    tree2 = KDTree(nodes)
    for node in nodes:
        #po = [node[0],node[1]]
        index = tree2.query([node],k=3, return_distance=False)
        possible = can_connect(nodes[index[0][1]],nodes[index[0][2]],polygons)
        if possible:
            g.add_edge(tuple(nodes[index[0][1]]),tuple(nodes[index[0][2]]))

        
        

    grid = create_grid(data, zvalsMax, 1)

    fig = plt.figure()

    plt.imshow(grid, cmap='Greys', origin='lower')

    nmin = np.min(data[:, 0])
    emin = np.min(data[:, 1])

    # If you have a graph called "g" these plots should work
    # Draw edges
    for (n1, n2) in g.edges:
        plt.plot([n1[1] - emin, n2[1] - emin], [n1[0] - nmin, n2[0] - nmin], 'black' , alpha=0.5)

    # Draw all nodes connected or not in blue
    for n1 in nodes:#nodes:
        plt.scatter(n1[1] - emin, n1[0] - nmin, c='blue')
        
    # Draw connected nodes in red
    for n1 in g.nodes:
        plt.scatter(n1[1] - emin, n1[0] - nmin, c='red')
        


    plt.xlabel('NORTH')
    plt.ylabel('EAST')

    plt.show()

    fig = plt.figure()

    plt.imshow(grid, cmap='Greys', origin='lower')

    # Add code to visualize path here

    # # draw points
    # all_pts = np.array(to_keep)
    # north_vals = all_pts[:,0]
    # east_vals = all_pts[:,1]
    # plt.scatter(east_vals - emin, north_vals - nmin, c='red')


    plt.xlabel('NORTH')
    plt.ylabel('EAST')

    plt.show()