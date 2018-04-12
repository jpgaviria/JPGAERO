import numpy as np
import matplotlib.pyplot as plt
#from config_space import create_grid
#from A_star import a_star
from grid import create_grid
from planning import a_star
import os

#%matplotlib inline

#from bresenham import bresenham
plt.rcParams['figure.figsize'] = 12, 12
#?create_grid
# This is the same obstacle data from the previous lesson.
filename = 'colliders.csv'
os.chdir('C:\\Users\jpgaviri\iCloudDrive\Personal\Python\Flying_Car_nano')
data = np.loadtxt(filename, delimiter=',', dtype='Float64', skiprows=2)
print(data)
# Static drone altitude (meters)
drone_altitude = 5

# Minimum distance stay away from obstacle (meters)
safe_distance = 3

def heuristic_func(position, goal_position):
    # TODO: write a heuristic!
    h = 0
    h = (abs(position[0]-goal_position[0])+abs(position[1]-goal_position[1]))
    return h
    #return 0
def point(p):
    return np.array([p[0], p[1], 1.]).reshape(1, -1)

def collinearity_check(p1, p2, p3, epsilon=1e-6):   
    m = np.concatenate((p1, p2, p3), 0)
    det = np.linalg.det(m)
    return abs(det) < epsilon
def prune_path(path):
    pruned_path = [p for p in path]
    # TODO: prune the path!
    for i in range(1,len(path)):
        #Matrx = np.vstack((point(path[i-1]),point(i),point(i+1)))

        collinear = collinearity_check(point(pruned_path[i-1]),point(pruned_path[i]),point(pruned_path[i+1]))
        if collinear:
            np.delete(pruned_path,pruned_path[i])

        a = np.array((pruned_path[i+1]))
        b = np.array((pruned_path[-1]))    
        if a[0] == b[0] and a[1] == b[1]:
            break
    return pruned_path

if __name__ == "__main__":
    # TODO: Use `create_grid` to create a grid configuration space of
    # the obstacle data.
    grid = create_grid(data, drone_altitude, safe_distance)
    # equivalent to
    # plt.imshow(np.flip(grid, 0))
    plt.imshow(grid, origin='lower') 

    plt.xlabel('EAST')
    plt.ylabel('NORTH')
    plt.show()
    start_ne = (25,  100)
    goal_ne = (750., 370.)
    # TODO: use `a_star` to compute the lowest cost path
    path, cost = a_star(grid, heuristic_func, start_ne, goal_ne)
    print(len(path), cost)

    plt.imshow(grid, cmap='Greys', origin='lower')

    # For the purposes of the visual the east coordinate lay along
    # the x-axis and the north coordinates long the y-axis.
    plt.plot(start_ne[1], start_ne[0], 'x')
    plt.plot(goal_ne[1], goal_ne[0], 'x')

    coord = []
    actualpath = np.array((start_ne[0], start_ne[1]))
    for i in range(0,len(path)):
        delta = np.array(path[i].delta)
        actualpath = actualpath + delta
        coord.append(actualpath)
    pp = np.array(coord)
    plt.plot(pp[:, 1], pp[:, 0], 'g')
    #for i in range(0,len(pp)):
        #plt.plot(pp[i].value[1], pp[i].value[0], 'g')
    #plt.plot((start_ne[1]+1), (start_ne[0]+1), 'g')

    plt.xlabel('EAST')
    plt.ylabel('NORTH')
    plt.show()

    pruned_path = prune_path(pp)
    print(len(pruned_path))

    plt.imshow(grid, cmap='Greys', origin='lower')

    plt.plot(start_ne[1], start_ne[0], 'x')
    plt.plot(goal_ne[1], goal_ne[0], 'x')

    pp = np.array(pruned_path)
    plt.plot(pp[:, 1], pp[:, 0], 'g')
    plt.scatter(pp[:, 1], pp[:, 0])

    plt.xlabel('EAST')
    plt.ylabel('NORTH')

    plt.show()

