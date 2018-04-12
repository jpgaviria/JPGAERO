import numpy as np
import matplotlib.pyplot as plt
from grid import create_grid
from skimage.morphology import medial_axis
from skimage.util import invert
from planning import a_star
import os
#%matplotlib inline
plt.rcParams['figure.figsize'] = 12, 12
# This is the same obstacle data from the previous lesson.
filename = 'colliders.csv'
os.chdir('C:\\Users\jpgaviri\iCloudDrive\Personal\Python\Flying_Car_nano')


def find_start_goal(skel, start, goal):
    # TODO: find start and goal on skeleton
    # Some useful functions might be:
        # np.nonzero()
        # np.transpose()
        # np.linalg.norm()
        # np.argmin()
    # a = np.nonzero(skel)
    # Start_Posfound = False
    # Goal_Posfound = False
    # i=0
    # actualx = start[0]
    # actualy = start[1]
    # while Start_Posfound == False:
    #     #actualx +=i
    #     #actualy +=i
    #     i+=1
    #     if skel[actualx+i][actualy+i] == True:
    #         near_start = [actualx+i,actualy+i]
    #         Start_Posfound = True
    #     elif skel[actualx][actualy+i] == True:
    #         near_start = [actualx,actualy+i]
    #         Start_Posfound = True
    #     elif skel[actualx-i][actualy+i] == True:
    #         near_start = [actualx-i,actualy+i]
    #         Start_Posfound = True
    #     elif skel[actualx-i][actualy] == True:
    #         near_start = [actualx-i,actualy]
    #         Start_Posfound = True
    #     elif skel[actualx-i][actualy-i] == True:
    #         near_start = [actualx-i,actualy-i]
    #         Start_Posfound = True
    #     elif skel[actualx][actualy-i] == True:
    #         near_start = [actualx,actualy-i]
    #         Start_Posfound = True
    #     elif skel[actualx-i][actualy-i] == True:
    #         near_start = [actualx-i,actualy-i]
    #         Start_Posfound = True
    #     elif skel[actualx+i][actualy] == True:
    #         near_start = [actualx+i,actualy]
    #         Start_Posfound = True
    # #find closest point to end
    # i=0
    # actualx = goal[0]
    # actualy = goal[1]
    # while Goal_Posfound == False:
    #     #actualx +=i
    #     #actualy +=i
    #     i+=1
    #     if skel[actualx+i][actualy+i] == True:
    #         near_goal = [actualx+i,actualy+i]
    #         Goal_Posfound = True
    #     elif skel[actualx][actualy+i] == True:
    #         near_goal = [actualx,actualy+i]
    #         Goal_Posfound = True
    #     elif skel[actualx-i][actualy+i] == True:
    #         near_goal = [actualx-i,actualy+i]
    #         Goal_Posfound = True
    #     elif skel[actualx-i][actualy] == True:
    #         near_goal = [actualx-i,actualy]
    #         Goal_Posfound = True
    #     elif skel[actualx-i][actualy-i] == True:
    #         near_goal = [actualx-i,actualy-i]
    #         Goal_Posfound = True
    #     elif skel[actualx][actualy-i] == True:
    #         near_goal = [actualx,actualy-i]
    #         Goal_Posfound = True
    #     elif skel[actualx-i][actualy-i] == True:
    #         near_goal = [actualx-i,actualy-i]
    #         Goal_Posfound = True
    #     elif skel[actualx+i][actualy] == True:
    #         near_goal = [actualx+i,actualy]
    #         Goal_Posfound = True   
    # #near_start = None
    # #near_goal = None
    skel_cells = np.transpose(skel.nonzero())
    start_min_dist = np.linalg.norm(np.array(start) - np.array(skel_cells),                                    axis=1).argmin()
    near_start = skel_cells[start_min_dist]
    goal_min_dist = np.linalg.norm(np.array(goal) - np.array(skel_cells),                                    axis=1).argmin()
    near_goal = skel_cells[goal_min_dist]
    return near_start, near_goal

def heuristic_func(position, goal_position):
    # TODO: define a heuristic
    h = 0
    h = (abs(position[0]-goal_position[0])+abs(position[1]-goal_position[1]))
    return h



if __name__ == "__main__":
    data = np.loadtxt(filename, delimiter=',', dtype='Float64', skiprows=2)
    print(data)
    start_ne = (25,  100)
    goal_ne = (650, 500)
    # Static drone altitude (meters)
    drone_altitude = 5
    safety_distance = 2

    grid = create_grid(data, drone_altitude, safety_distance)
    skeleton = medial_axis(invert(grid))
    # equivalent to
    # plt.imshow(np.flip(grid, 0))

    plt.imshow(grid, cmap='Greys', origin='lower')
    plt.imshow(skeleton, cmap='Greys', origin='lower', alpha=0.7)
        
    plt.plot(start_ne[1], start_ne[0], 'rx')
    plt.plot(goal_ne[1], goal_ne[0], 'rx')

    plt.xlabel('EAST')
    plt.ylabel('NORTH')
    #plt.show()
    # TODO: Your start and goal location defined above
    # will not necessarily be on the skeleton so you
    # must first identify the nearest cell on the 
    # skeleton to start and goal
    skel_start, skel_goal = find_start_goal(skeleton, start_ne, goal_ne)

    print(start_ne, goal_ne)
    print(skel_start, skel_goal)

    # Run A* on the skeleton
    path, cost = a_star(invert(skeleton).astype(np.int), heuristic_func, tuple(skel_start), tuple(skel_goal))
    print("Path length = {0}, path cost = {1}".format(len(path), cost))
    # Compare to regular A* on the grid
    path2, cost2 = a_star(grid, heuristic_func, start_ne, goal_ne)

    plt.imshow(grid, cmap='Greys', origin='lower')
    plt.imshow(skeleton, cmap='Greys', origin='lower', alpha=0.7)
    # For the purposes of the visual the east coordinate lay along
    # the x-axis and the north coordinates long the y-axis.
    #plt.plot(start_ne[1], start_ne[0], 'x')
    # Uncomment the following as needed
    plt.plot(skel_start[1], skel_start[0], 'x')
    plt.plot(skel_goal[1], skel_goal[0], 'x')

    #pp = np.array(path)
    coord = []
    actualpath = np.array((skel_start[0], skel_start[1]))
    coord.append(actualpath)
    for i in range(1,len(path)):
        delta = np.array(path[i].delta)
        actualpath = actualpath + delta
        coord.append(actualpath)
    pp = np.array(coord)
    plt.plot(pp[:, 1], pp[:, 0], 'g')
    coord2 = []
    actualpath = np.array((start_ne[0], start_ne[1]))
    for i in range(0,len(path2)):
        delta = np.array(path2[i].delta)
        actualpath = actualpath + delta
        coord2.append(actualpath)
    pp2 = np.array(coord2)
    #pp2 = np.array(path2)
    plt.plot(pp2[:, 1], pp2[:, 0], 'r')

    plt.xlabel('EAST')
    plt.ylabel('NORTH')
    plt.show()