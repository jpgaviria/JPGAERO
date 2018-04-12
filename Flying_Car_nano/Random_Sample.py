import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from shapely.geometry import Polygon, Point
from grid import create_grid
#import os
#%matplotlib inline 
plt.rcParams['figure.figsize'] = 12, 12
# This is the same obstacle data from the previous lesson.
filename = 'colliders.csv'
#os.chdir('C:\\Users\jpgaviri\iCloudDrive\Personal\Python\Flying_Car_nano')
data = np.loadtxt(filename, delimiter=',', dtype='Float64', skiprows=2)
print(data)
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
def collides(polygons, point):   
    # TODO: Determine whether the point collides
    # with any obstacles.
    collide = False
    for poly in polygons:
        if poly[0].contains(Point(point))and poly[1] >= point[2]:
            collide = True    
    return collide

if __name__ == "__main__":
    # coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
    # poly = Polygon(coords)
    # print(poly.area)
    # print(poly.length)
    # print(poly.bounds)

    # p1 = Point(0.5, 0.5)
    # p2 = Point(1.5, 1.5)
    # print(poly.contains(p1))
    # print(poly.contains(p2))

    polygons = extract_polygons(data)

    xmin = np.min(data[:, 0] - data[:, 3])
    xmax = np.max(data[:, 0] + data[:, 3])

    ymin = np.min(data[:, 1] - data[:, 4])
    ymax = np.max(data[:, 1] + data[:, 4])

    zmin = 0
    # Limit the z axis for the visualization
    zmax = 10

    print("X")
    print("min = {0}, max = {1}\n".format(xmin, xmax))

    print("Y")
    print("min = {0}, max = {1}\n".format(ymin, ymax))

    print("Z")
    print("min = {0}, max = {1}".format(zmin, zmax))

    num_samples = 100

    xvals = np.random.uniform(xmin, xmax, num_samples)
    yvals = np.random.uniform(ymin, ymax, num_samples)
    zvals = np.random.uniform(zmin, zmax, num_samples)

    samples = np.array(list(zip(xvals, yvals, zvals)))

    samples[:10]

    t0 = time.time()
    to_keep = []
    for point in samples:
        if not collides(polygons, point):
            to_keep.append(point)
    time_taken = time.time() - t0
    print("Time taken {0} seconds ...", time_taken)

    print(len(to_keep))

    grid = create_grid(data, zmax, 1)

    fig = plt.figure()

    plt.imshow(grid, cmap='Greys', origin='lower')

    nmin = np.min(data[:, 0])
    emin = np.min(data[:, 1])

    # draw points
    all_pts = np.array(to_keep)
    north_vals = all_pts[:,0]
    east_vals = all_pts[:,1]
    plt.scatter(east_vals - emin, north_vals - nmin, c='red')

    plt.ylabel('NORTH')
    plt.xlabel('EAST')

    plt.show()