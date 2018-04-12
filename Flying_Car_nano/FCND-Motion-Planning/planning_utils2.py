from enum import Enum
from queue import PriorityQueue
import numpy as np
from sklearn.neighbors import KDTree
from shapely.geometry import Polygon, Point, LineString
import networkx as nx

def create_grid(data, drone_altitude, safety_distance):
    """
    Returns a grid representation of a 2D configuration space
    based on given obstacle data, drone altitude and safety distance
    arguments.
    """

    # minimum and maximum north coordinates
    north_min = np.floor(np.min(data[:, 0] - data[:, 3]))
    north_max = np.ceil(np.max(data[:, 0] + data[:, 3]))

    # minimum and maximum east coordinates
    east_min = np.floor(np.min(data[:, 1] - data[:, 4]))
    east_max = np.ceil(np.max(data[:, 1] + data[:, 4]))

    # given the minimum and maximum coordinates we can
    # calculate the size of the grid.
    north_size = int(np.ceil(north_max - north_min))
    east_size = int(np.ceil(east_max - east_min))

    # Initialize an empty grid
    grid = np.zeros((north_size, east_size))

    # Populate the grid with obstacles
    for i in range(data.shape[0]):
        north, east, alt, d_north, d_east, d_alt = data[i, :]
        if alt + d_alt + safety_distance > drone_altitude:
            obstacle = [
                int(np.clip(north - d_north - safety_distance - north_min, 0, north_size-1)),
                int(np.clip(north + d_north + safety_distance - north_min, 0, north_size-1)),
                int(np.clip(east - d_east - safety_distance - east_min, 0, east_size-1)),
                int(np.clip(east + d_east + safety_distance - east_min, 0, east_size-1)),
            ]
            grid[obstacle[0]:obstacle[1]+1, obstacle[2]:obstacle[3]+1] = 1

    return grid, int(north_min), int(east_min)


# Assume all actions cost the same.
class Action(Enum):
    """
    An action is represented by a 3 element tuple.

    The first 2 values are the delta of the action relative
    to the current grid position. The third and final value
    is the cost of performing the action.
    """

    WEST = (0, -1, 1)
    EAST = (0, 1, 1)
    NORTH = (-1, 0, 1)
    SOUTH = (1, 0, 1)
    NORTH_EAST = (1,1,np.sqrt(2))
    SOUTH_EAST = (-1,1,np.sqrt(2))
    NORTH_WEST = (1,-1,np.sqrt(2))
    SOUTH_WEST = (-1,-1,np.sqrt(2))

    @property
    def cost(self):
        return self.value[2]

    @property
    def delta(self):
        return (self.value[0], self.value[1])


def valid_actions(grid, current_node):
    """
    Returns a list of valid actions given a grid and current node.
    """
    valid_actions = list(Action)
    n, m = grid.shape[0] - 1, grid.shape[1] - 1
    x, y = current_node

    # check if the node is off the grid or
    # it's an obstacle

    if x - 1 < 0 or grid[x - 1, y] == 1:
        valid_actions.remove(Action.NORTH)
    if x + 1 > n or grid[x + 1, y] == 1:
        valid_actions.remove(Action.SOUTH)
    if y - 1 < 0 or grid[x, y - 1] == 1:
        valid_actions.remove(Action.WEST)
    if y + 1 > m or grid[x, y + 1] == 1:
        valid_actions.remove(Action.EAST)
    #Adding diagonal actions
    if (x - 1 < 0 or grid[x - 1, y] == 1) or (y + 1 > m or grid[x, y + 1] == 1):
        valid_actions.remove(Action.NORTH_EAST)
    if (x + 1 > n or grid[x + 1, y] == 1) or (y + 1 > m or grid[x, y + 1] == 1):
        valid_actions.remove(Action.SOUTH_EAST)
    if (x - 1 < 0 or grid[x - 1, y] == 1) or (y - 1 < 0 or grid[x, y - 1] == 1):
        valid_actions.remove(Action.NORTH_WEST)
    if (x + 1 > n or grid[x + 1, y] == 1) or (y - 1 < 0 or grid[x, y - 1] == 1):
        valid_actions.remove(Action.SOUTH_WEST)

    return valid_actions


def a_star_NX(graph, heuristic, start, goal):


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
                cost = graph.edges[current_node, next_node]['weight']
                new_cost = current_cost + cost + heuristic(next_node, goal)
                
                if next_node not in visited:                
                    visited.add(next_node)               
                    queue.put((new_cost, next_node))
                    
                    branch[next_node] = (new_cost, current_node)
             
    path = []
    path_cost = 0
    if found:
        
        # retrace steps
        path = []
        n = goal
        path_cost = branch[n][0]
        while branch[n][1] != start:
            path.append(branch[n][1])
            n = branch[n][1]
        path.append(branch[n][1])
            
    return path[::-1], path_cost



def heuristic(position, goal_position):
    return np.linalg.norm(np.array(position) - np.array(goal_position))
def point(p):
    return np.array([p[0], p[1], 1.]).reshape(1, -1)

def collinearity_check(p1, p2, p3, epsilon=1e-6):   
    m = np.concatenate((p1, p2, p3), 0)
    det = np.linalg.det(m)
    return abs(det) < epsilon
def prune_path(path):
    pruned_path = [p for p in path]
    # TODO: prune the path!
 
    i = 0
    while i < len(pruned_path) - 2:
        p1 = point(pruned_path[i])
        p2 = point(pruned_path[i+1])
        p3 = point(pruned_path[i+2])
        
        # If the 3 points are in a line remove
        # the 2nd point.
        # The 3rd point now becomes and 2nd point
        # and the check is redone with a new third point
        # on the next iteration.
        if collinearity_check(p1, p2, p3):
            # Something subtle here but we can mutate
            # `pruned_path` freely because the length
            # of the list is check on every iteration.
            pruned_path.remove(pruned_path[i+1])
        else:
            i += 1
    return pruned_path
def can_connect(n1, n2, polygons):
    l = LineString([n1, n2])
    for p in polygons:
        if p[0].crosses(l) and p[1] >= min(n1[2], n2[2]):
            return False
    return True
    # possible = False
    # n1 = np.array(n1)
    # n2 = np.array(n2)
    # line = LineString([n1[:2],n2[:2]])
    # for poly in polygons:
    #     possible = False
    #     if not line.crosses(poly[0]):# and poly[1] >= min(n1[2], n2[2]):
    #         possible = True
    #     elif possible == False:
    #         break
    # return possible

def create_graph(nodes, k, polygons):
    g = nx.Graph()
    tree = KDTree(nodes)
    for n1 in nodes:
        # for each node connect try to connect to k nearest nodes
        idxs = tree.query([n1], k, return_distance=False)[0]
        
        for idx in idxs:
            if idx != 0:
                n2 = nodes[idx]
                if can_connect(n1, n2, polygons):
                    g.add_edge(tuple(n1),tuple(n2), weight=1)
    return g
# def extract_polygons(data):

    # polygons = []
    # for i in range(data.shape[0]):
        # north, east, alt, d_north, d_east, d_alt = data[i, :]

        # # polygons.append(Polygon(coords))
        # # TODO: Extract the 4 corners of the obstacle
        # p1 = (north - d_north,east + d_east)
        # p2 = (north + d_north,east + d_east)
        # p3 = (north + d_north,east - d_east)
        # p4 = (north - d_north,east - d_east)
        # # NOTE: The order of the points matters since
        # # `shapely` draws the sequentially from point to point.
        # #
        # # If the area of the polygon is 0 you've likely got a weird
        # # order.
        # corners = [p1,p2,p3,p4]
        
        # # TODO: Compute the height of the polygon
        # height = alt + d_alt

        # # TODO: Once you've defined corners, define polygons
        # p = Polygon(corners)
        # polygons.append((p, height))

    # return polygons
# def collides(polygon, point):   
    # # TODO: Determine whether the point collides
    # # with any obstacles.
    # collide = False
    # #for poly in polygons:
    # if polygon[0].contains(Point(point))and polygon[1] >= point[2]:
        # collide = True    
    # return collide