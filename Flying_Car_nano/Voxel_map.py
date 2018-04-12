import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
# %matplotlib inline
plt.rcParams['figure.figsize'] = 16, 16
# This is the same obstacle data from the previous lesson.
filename = 'colliders_med.csv'
os.chdir('C:\\Users\jpgaviri\iCloudDrive\Personal\Python\Flying_Car_nano')
data = np.loadtxt(filename, delimiter=',', dtype='Float64', skiprows=2)
print(data)
#safety_distance = 3
def create_voxmap(data, voxel_size=5):
    """
    Returns a grid representation of a 3D configuration space
    based on given obstacle data.
    
    The `voxel_size` argument sets the resolution of the voxel map. 
    """

    # minimum and maximum north coordinates
    north_min = np.floor(np.amin(data[:, 0] - data[:, 3]))
    north_max = np.ceil(np.amax(data[:, 0] + data[:, 3]))

    # minimum and maximum east coordinates
    east_min = np.floor(np.amin(data[:, 1] - data[:, 4]))
    east_max = np.ceil(np.amax(data[:, 1] + data[:, 4]))

    alt_max = np.ceil(np.amax(data[:, 2] + data[:, 5]))
    
    # given the minimum and maximum coordinates we can
    # calculate the size of the grid.
    north_size = int(np.ceil((north_max - north_min))) // voxel_size
    east_size = int(np.ceil((east_max - east_min))) // voxel_size
    alt_size = int(alt_max) // voxel_size

    voxmap = np.zeros((north_size, east_size, alt_size), dtype=np.bool)
    # Center offset for grid
    #north_min_center = np.min(data[:, 0])
    #east_min_center = np.min(data[:, 1])
    for i in range(data.shape[0]):
        north, east, alt, d_north, d_east, d_alt = data[i, :]
        #rebaseline coordinates to be on the grid position that starts at 0
        # north = north + abs(north_min_center)
        # east = east + abs(east_min_center)
        # print(north, east, alt, d_north, d_east, d_alt)
        # initposSouth = int(north - d_north)
        # initposWest = int(east - d_east)
        # endposNorth = int(north + d_north)
        # endposEast = int(east + d_east)
        # endposUp = int(alt + d_alt)
        # voxmap[initposSouth:endposNorth,initposWest:endposEast,0:alt_size] =True
        # for j in range(initposSouth,endposNorth):
        #     for k in range(initposWest,endposEast):
        #         for l in range(0,alt_size):
        #             voxmap[j,k,l] =True
        # TODO: fill in the voxels that are part of an obstacle with `True`
        #
        # i.e. grid[0:5, 20:26, 2:7] = True
        #voxmap = voxmap
        obstacle = [
            int(north - d_north - north_min) // voxel_size,
            int(north + d_north - north_min) // voxel_size,
            int(east - d_east - east_min) // voxel_size,
            int(east + d_east - east_min) // voxel_size,
        ]
        height = int(alt +d_alt)
        voxmap[obstacle[0]:obstacle[1], obstacle[2]:obstacle[3], 0:height] = True

    return voxmap
if __name__ == "__main__":
    voxmap = create_voxmap(data, 10)
    print(voxmap.shape)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.voxels(voxmap, edgecolor='k')
    ax.set_xlim(voxmap.shape[0], 0)
    ax.set_ylim(0, voxmap.shape[1])
    # add 100 to the height so the buildings aren't so tall
    ax.set_zlim(0, voxmap.shape[2]+70)

    plt.xlabel('North')
    plt.ylabel('East')

    plt.show()
