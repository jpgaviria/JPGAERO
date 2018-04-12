# Make the relevant imports including Voronoi methods
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import os
from bresenham import bresenham
#%matplotlib inline 
plt.rcParams["figure.figsize"] = [12, 12]
# Read in the obstacle data
filename = 'colliders_med.csv'
os.chdir('C:\\Users\jpgaviri\iCloudDrive\Personal\Python\Flying_Car_nano')
data = np.loadtxt(filename, delimiter=',', dtype='Float64', skiprows=2)

# Here you'll modify the `create_grid()` method from a previous exercise
# In this new function you'll record obstacle centres and
# create a Voronoi graph around those points
def create_grid_and_edges(data, drone_altitude, safety_distance):
    """
    Returns a grid representation of a 2D configuration space
    along with Voronoi graph edges given obstacle data and the
    drone's altitude.
    """

    # minimum and maximum north coordinates
    north_min = np.floor(np.min(data[:, 0] - data[:, 3]))
    north_max = np.ceil(np.max(data[:, 0] + data[:, 3]))

    # minimum and maximum east coordinates
    east_min = np.floor(np.min(data[:, 1] - data[:, 4]))
    east_max = np.ceil(np.max(data[:, 1] + data[:, 4]))

    # given the minimum and maximum coordinates we can
    # calculate the size of the grid.
    north_size = int(np.ceil((north_max - north_min)))
    east_size = int(np.ceil((east_max - east_min)))

    # Initialize an empty grid
    grid = np.zeros((north_size, east_size))
    # Center offset for grid
    north_min_center = np.min(data[:, 0])
    east_min_center = np.min(data[:, 1])
    
    # Define a list to hold Voronoi points
    points = []
    # Populate the grid with obstacles
    for i in range(data.shape[0]):
        north, east, alt, d_north, d_east, d_alt = data[i, :]

        if alt + d_alt + safety_distance > drone_altitude:
            obstacle = [
                int(north - d_north - safety_distance - north_min_center),
                int(north + d_north + safety_distance - north_min_center),
                int(east - d_east - safety_distance - east_min_center),
                int(east + d_east + safety_distance - east_min_center),
            ]
            grid[obstacle[0]:obstacle[1], obstacle[2]:obstacle[3]] = 1
            
            # add center of obstacles to points list
            points.append([north - north_min, east - east_min])

    # TODO: create a voronoi graph based on
    # location of obstacle centres
    graph = Voronoi(points)
    #voronoi_plot_2d(graph)

    # TODO: check each edge from graph.ridge_vertices for collision
    edges = []
    for vpair in graph.ridge_vertices:
        if vpair[0] >= 0 and vpair[1] >= 0:
            v0 = graph.vertices[vpair[0]]
            v1 = graph.vertices[vpair[1]]
            # using python library
            # Note: you can run this for any (x1, y1, x2, y2)
            #line = (0, 0, 7, 5)

            cells = list(bresenham(int(v0[0]),int(v0[1]),int(v1[0]),int(v1[1])))
            print(cells)
            hit = False
            for c in cells:
                # First check if we're off the map
                if np.amin(c) < 0 or c[0] >= grid.shape[0] or c[1] >= grid.shape[1]:
                    hit = True
                    break
                # Next check if we're in collision
                if grid[c[0], c[1]] == 1:
                    hit = True
                    break
            # If the edge does not hit on obstacle
            # add it to the list
            if hit == False:
                hit = hit
                # array to tuple for future graph creation step)
                v0 = (v0[0], v0[1])
                v1 = (v1[0], v1[1])
                edges.append((v0, v1))

            # if v0[0] >= east_min and v0[0] < east_max and v1[0] >= north_min and v1[0] < north_max:
            #     if grid[int(v0[0]),int(v0[1])] !=1 and grid[int(v1[0]),int(v1[1])] !=1:
            #         #edges.append([v0,v1])
            #         edges.append([v0[0],v0[1]])
            #         edges.append([v1[0],v1[1]])
            # Draw a line from v0 to v1.
            # lt.plot([v0[0], v1[0]], [v0[1], v1[1]], 'k', linewidth=2)
    return grid, edges
if __name__ == "__main__":
    # Recreate the figure above for a new set of random points
    #points = np.random.randint(50, size=(50, 2))
    #points = np.array([[1,5],[6,2],[10,10],[15,5]])
    #points = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2],[2, 0], [2, 1], [2, 2]])
    points = np.array([[0, 0], [0, 1], [0, 2],
                   [1, 0], [1, 1], [1, 2],
                   [2, 0], [2, 1], [2, 2]])
    graph = Voronoi(points)
    for vpair in graph.ridge_vertices:
        if vpair[0] >= 0 and vpair[1] >= 0:
            v0 = graph.vertices[vpair[0]]
            v1 = graph.vertices[vpair[1]]
            # Draw a line from v0 to v1.
            plt.plot([v0[0], v1[0]], [v0[1], v1[1]], 'k', linewidth=2)
    #voronoi_plot_2d(graph)
    #plt.show()

    # Define a flying altitude (feel free to change this)
    drone_altitude = 100
    safety_distance = 3
    grid, edges = create_grid_and_edges(data, drone_altitude, safety_distance)
    print('Found %5d edges' % len(edges))

    # equivalent to
    # plt.imshow(np.flip(grid, 0))
    # Plot it up!
    plt.imshow(grid, origin='lower', cmap='Greys') 

    #Stepping through each edge
    for e in edges:
        p1 = e[0]
        p2 = e[1]
        plt.plot([p1[1], p2[1]], [p1[0], p2[0]], 'b-')

    plt.xlabel('EAST')
    plt.ylabel('NORTH')
    plt.show()