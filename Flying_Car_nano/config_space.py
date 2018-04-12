import numpy as np 
import matplotlib.pyplot as plt
import os

#%matplotlib inline
plt.rcParams["figure.figsize"] = [12, 12]
filename = 'colliders.csv'
# Read in the data skipping the first two lines.  
# Note: the first line contains the latitude and longitude of map center
# Where is this??

os.chdir('C:\\Users\jpgaviri\iCloudDrive\Personal\Python\Flying_Car_nano')
print (os.getcwd())
data = np.loadtxt(filename,delimiter=',',dtype='Float64',skiprows=2)
print(data)
# Static drone altitude (metres)
drone_altitude = 5

# Minimum distance required to stay away from an obstacle (metres)
# Think of this as padding around the obstacles.
safe_distance = 3
def create_grid(data, drone_altitude, safety_distance):
    """
    Returns a grid representation of a 2D configuration space
    based on given obstacle data, drone altitude and safety distance
    arguments.
    """

    # minimum and maximum north coordinates
    north_min = np.floor(np.amin(data[:, 0] - data[:, 3]))
    north_max = np.ceil(np.amax(data[:, 0] + data[:, 3]))

    # minimum and maximum east coordinates
    east_min = np.floor(np.amin(data[:, 1] - data[:, 4]))
    east_max = np.ceil(np.amax(data[:, 1] + data[:, 4]))

    # given the minimum and maximum coordinates we can
    # calculate the size of the grid.
    north_size = int(np.ceil(north_max - north_min))
    east_size = int(np.ceil(east_max - east_min))
    # Initialize an empty grid
    grid = np.zeros((north_size, east_size))
    # Center offset for grid
    north_min_center = np.min(data[:, 0])
    east_min_center = np.min(data[:, 1])
    # Populate the grid with obstacles
    for i in range(data.shape[0]):
        north, east, alt, d_north, d_east, d_alt = data[i, :]
        #rebaseline coordinates to be on the grid position that starts at 0
        north = north + abs(north_min_center)
        east = east + abs(east_min_center)
        print(north, east, alt, d_north, d_east, d_alt)
        initposSouth = int(north - d_north - safety_distance)
        initposWest = int(east - d_east - safety_distance)
        endposNorth = int(north + d_north + safety_distance)
        endposEast = int(east + d_east + safety_distance)
        # check for limits
        # if initposNorth >= north_max:
            # initposNorth = int(north_max)
        # if initposWest <= east_min:
            # initposWest =  int(east_min)
        # if endposSouth <= north_min:
            # endposSouth =  int(north_min)
        # if endposEast >= east_max:
            # endposEast =  int(east_max)
        for j in range(initposSouth,endposNorth):
            for k in range(initposWest,endposEast):
                if drone_altitude < ((int(d_alt)*2)+safe_distance):
                    grid[j,k] =1
        #for j in range(len(d_north))
        # TODO: Determine which cells contain obstacles
        # and set them to 1.
        #
        # Example:
        #
        #    grid[north_coordinate, east_coordinate] = 1

    return grid
if __name__ == "__main__":
    grid = create_grid(data, drone_altitude, safe_distance)
    # equivalent to
    # plt.imshow(np.flip(grid, 0))
    # NOTE: we're placing the origin in the lower lefthand corner here
    # so that north is up, if you didn't do this north would be positive down
    plt.imshow(grid, origin='lower') 

    plt.xlabel('EAST')
    plt.ylabel('NORTH')
    plt.show()