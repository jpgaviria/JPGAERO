# OK this might look a little ugly but...
# need to import the latest version of networkx
# This occassionally fails, so if the next cell 
# doesn't show that you're using networkx 2.1
# please "restart and clear output" from "Kernel" menu
# above and try again.
import sys
#!{sys.executable} -m pip install -I networkx==2.1
import pkg_resources
pkg_resources.require("networkx==2.1")
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from grid import create_grid_and_edges
import numpy.linalg as LA

import os
#%matplotlib inline 
plt.rcParams['figure.figsize'] = 12, 12

# This is the same obstacle data from the previous lesson.
filename = 'colliders_med.csv'
os.chdir('C:\\Users\jpgaviri\iCloudDrive\Personal\Python\Flying_Car_nano')
data = np.loadtxt(filename, delimiter=',', dtype='Float64', skiprows=2)
print(data)
from queue import PriorityQueue
from enum import Enum
def heuristic(n1, n2):
    # h = 0
    # h = (abs(n1[0]-n2[0])+abs(n1[1]-n2[1]))
    # return h
    #return np.sqrt((position[0] - goal_position[0])**2 + (position[1] - goal_position[1])**2)
    return LA.norm(np.array(n2) - np.array(n1))
def closest_point(graph, current_point):
    """
    Compute the closest point in the `graph`
    to the `current_point`.
    """
    closest_point = None
    dist = 100000
    for p in graph.nodes:
        d = LA.norm(np.array(p) - np.array(current_point))
        if d < dist:
            closest_point = p
            dist = d
    return closest_point

###### THIS IS YOUR OLD GRID-BASED A* IMPLEMENTATION #######
###### With a few minor modifications it can work with graphs! ####
#TODO: modify A* to work with a graph
def a_star(graph, heuristic, start, goal):
    
    path = []
    queue = PriorityQueue()
    queue.put((0, start))
    visited = set(start)

    branch = {}
    found = False
    
    while not queue.empty():
        item = queue.get()
        current_cost = item[0]
        current_node = item[1]

        if current_node == goal:        
            print('Found a path.')
            found = True
            break
            
        else:
            for next_node in graph[current_node]:
                # get the tuple representation
                cost = graph.edges[current_node, next_node]['weight']
                new_cost = current_cost + cost + heuristic(next_node, goal)
                
                if next_node not in visited:                
                    visited.add(next_node)               
                    queue.put((new_cost, next_node))
                    
                    branch[next_node] = (new_cost, current_node)
             
    path = []
    actual_path = []
    path_cost = 0
    if found:
        
        # retrace steps
        path = []
        n = goal
        path_cost = branch[n][0]
        path.append(goal)
        while branch[n][1] != start:
            path.append(branch[n][1])
            n = branch[n][1]
        path.append(branch[n][1])
            
    return path[::-1], path_cost
if __name__ == "__main__":
    print(nx.__version__)
    start_ne = (25,  100)
    goal_ne = (750., 370.)
    # Static drone altitude (metres)
    drone_altitude = 90
    safety_distance = 3
    # This is now the routine using Voronoi
    grid, edges = create_grid_and_edges(data, drone_altitude, safety_distance)
    print(len(edges))
    # equivalent to
    # plt.imshow(np.flip(grid, 0))
    plt.imshow(grid, origin='lower', cmap='Greys') 

    for e in edges:
        p1 = e[0]
        p2 = e[1]
        plt.plot([p1[1], p2[1]], [p1[0], p2[0]], 'b-')

        
    plt.plot(start_ne[1], start_ne[0], 'rx')
    plt.plot(goal_ne[1], goal_ne[0], 'rx')

    plt.xlabel('EAST')
    plt.ylabel('NORTH')
    #plt.show()

    # TODO: create the graph with the weight of the edges
    # set to the Euclidean distance between the points
    G = nx.Graph()
    for e in edges:
        p1 = e[0]
        p2 = e[1]
        dist = LA.norm(np.array(p2) - np.array(p1))
        G.add_edge(p1, p2, weight=dist)

    start_ne_g = closest_point(G, start_ne)
    goal_ne_g = closest_point(G, goal_ne)
    print(start_ne_g)
    print(goal_ne_g)

    path, cost = a_star(G, heuristic, tuple(start_ne_g), tuple(goal_ne_g))
    print("Path length = {0}, path cost = {1}".format(len(path), cost))

    pp = np.array(path)
    plt.plot(pp[:, 1], pp[:, 0], 'g')
    plt.xlabel('EAST')
    plt.ylabel('NORTH')
    plt.show()