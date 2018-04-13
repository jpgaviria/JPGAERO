import argparse
import time
import msgpack #""" NEW library in motion planning """
from enum import Enum, auto
import networkx as nx
from shapely.geometry import Polygon, Point, LineString
from sklearn.neighbors import KDTree
from sampling import Sampler
import matplotlib.pyplot as plt

import numpy as np
#import pandas as pd
import csv

""" USE PLANNING UTILS 2 for MOTION PLANNING 2"""
from planning_utils2 import a_star_NX, heuristic, create_grid, can_connect, create_graph#, collides, extract_polygons
from sampling import Sampler
from udacidrone import Drone
from udacidrone.connection import MavlinkConnection
from udacidrone.messaging import MsgID
from udacidrone.frame_utils import global_to_local


class States(Enum):
    MANUAL = auto()
    ARMING = auto()
    TAKEOFF = auto()
    WAYPOINT = auto()
    LANDING = auto()
    DISARMING = auto()
    PLANNING = auto()


class MotionPlanning(Drone):

    def __init__(self, connection):
        super().__init__(connection)

        self.target_position = np.array([0.0, 0.0, 0.0])
        self.waypoints = []
        self.in_mission = True
        self.check_state = {}

        # initial state
        self.flight_state = States.MANUAL

        # register all your callbacks here
        self.register_callback(MsgID.LOCAL_POSITION, self.local_position_callback)
        self.register_callback(MsgID.LOCAL_VELOCITY, self.velocity_callback)
        self.register_callback(MsgID.STATE, self.state_callback)

    def local_position_callback(self):
        if self.flight_state == States.TAKEOFF:
            if -1.0 * self.local_position[2] > 0.95 * self.target_position[2]:
                self.waypoint_transition()
        elif self.flight_state == States.WAYPOINT:
            if np.linalg.norm(self.target_position[0:2] - self.local_position[0:2]) < 1.0:
                if len(self.waypoints) > 0:
                    self.waypoint_transition()
                else:
                    if np.linalg.norm(self.local_velocity[0:2]) < 1.0:
                        self.landing_transition()

    def velocity_callback(self):
        if self.flight_state == States.LANDING:
            if self.global_position[2] - self.global_home[2] < 0.1:
                if abs(self.local_position[2]) < 0.01:
                    self.disarming_transition()

    def state_callback(self):
        if self.in_mission:
            if self.flight_state == States.MANUAL:
                self.arming_transition()
                """ New in motion planning, call plan_path() function after arming drone, before was automatically
                calling takeoff, now the plan needs to be created first"""
            elif self.flight_state == States.ARMING:
                if self.armed:
                    self.plan_path()
            elif self.flight_state == States.PLANNING:
                self.takeoff_transition()
            elif self.flight_state == States.DISARMING:
                if ~self.armed & ~self.guided:
                    self.manual_transition()

    def arming_transition(self):
        self.flight_state = States.ARMING
        print("arming transition")
        self.arm()
        self.take_control()

    def takeoff_transition(self):
        self.flight_state = States.TAKEOFF
        print("takeoff transition")
        self.takeoff(self.target_position[2])

    def waypoint_transition(self):
        self.flight_state = States.WAYPOINT
        print("waypoint transition")
        self.target_position = self.waypoints.pop(0)
        print('target position', self.target_position)
        self.cmd_position(self.target_position[0], self.target_position[1], self.target_position[2], self.target_position[3])

    def landing_transition(self):
        self.flight_state = States.LANDING
        print("landing transition")
        self.land()

    def disarming_transition(self):
        self.flight_state = States.DISARMING
        print("disarm transition")
        self.disarm()
        self.release_control()

    def manual_transition(self):
        self.flight_state = States.MANUAL
        print("manual transition")
        self.stop()
        self.in_mission = False
    """ New function in motion planning to send the waypoints to the sim
    this is just for visualization of waypoints """
    def send_waypoints(self):
        print("Sending waypoints to simulator ...")
        data = msgpack.dumps(self.waypoints)
        self.connection._master.write(data)
    """ New function in motion planning to make a plan, get's called after arming state"""
    def plan_path(self):
        self.flight_state = States.PLANNING
        print("Searching for a path ...")
        TARGET_ALTITUDE = 5
        SAFETY_DISTANCE = 5

        self.target_position[2] = TARGET_ALTITUDE

        # TODO: read lat0, lon0 from colliders into floating point values
        """ probably the np.genfromtxt fuction could have done this, but I was not able
        to find the way, used csv.reader to get it"""
        latlondata = csv.reader(open('colliders.csv', newline=''), delimiter=',')
        for row in latlondata:
            lat0, lon0 = row[:2]
            break
        lat0 = lat0.replace("lat0 ","")
        lon0 = lon0.replace(" lon0 ","")
        lat0 = float(lat0)
        lon0 = float(lon0)
        # # TODO: set home position to (lon0, lat0, 0)
        self.set_home_position(lon0,lat0,0)
        # TODO: retrieve current global position
        Globalcurrent = np.array((self.global_position[0], self.global_position[1],self.global_position[2]))
        # TODO: convert to current local position using global_to_local()
        Localcurrent = global_to_local(Globalcurrent,self.global_home)
        #self.local_position = [Localcurrent[0],Localcurrent[1],Localcurrent[2]]
        print('global home {0}, position {1}, local position {2}'.format(self.global_home, self.global_position,
                                                                         self.local_position))
        # Read in obstacle map
        data = np.loadtxt('colliders.csv', delimiter=',', dtype='Float64', skiprows=2)


        # Define a grid for a particular altitude and safety margin around obstacles
        #""" Create grid comes from the planning_utils.py so we can call it directly here"""
        #grid, north_offset, east_offset = create_grid(data, TARGET_ALTITUDE, SAFETY_DISTANCE)

        # TODO (if you're feeling ambitious): Try a different approach altogether!
        """ USING Probabilistic roadmap"""
        sampler = Sampler(data)
        polygons = sampler._polygons
        nodes = sampler.sample(200)
        print(len(nodes))

        grid , north_offset, east_offset = create_grid(data, sampler._zmax, SAFETY_DISTANCE)
        print("North offset = {0}, east offset = {1}".format(north_offset, east_offset))
        # to support starting on any point on the map add the local current to the offset
        print("North offset = {0}, east offset = {1}".format(north_offset, east_offset))
        # Define starting point on the grid (this is just grid center)
        grid_center = (north_offset, east_offset)
        # TODO: convert start position to current position rather than map center
        """ Get local grid position and determine the new grid start from global home then
        add it to grid center """
        Localcurrent = global_to_local(self.global_position,self.global_home)
        grid_start = (int(-grid_center[0]+Localcurrent[0]),int(-grid_center[1]+Localcurrent[1]))

        # Set goal as some arbitrary position on the grid
        # TODO: adapt to set goal as latitude / longitude position and convert
        """ code to get the grid goal based on LAT LONG position, assume altitude is 0 for goal"""
        grid_goal_lat_lon = (-122.397185, 37.792857, 0)
        grid_goal = global_to_local(grid_goal_lat_lon,self.global_home)
        grid_goal = tuple((int(grid_goal[0]-north_offset),int(grid_goal[1]-east_offset)))

        start_point = np.array((grid_start[0],grid_start[1],10))
        goal_point  = np.array((grid_goal[0],grid_goal[1],10))

        nodes.append(start_point)
        nodes.append(goal_point)

        g = create_graph(nodes, 3, polygons)
        print("Number of edges", len(g.edges))
        # fig = plt.figure()

        # plt.imshow(grid, cmap='Greys', origin='lower')

        # nmin = np.min(data[:, 0])
        # emin = np.min(data[:, 1])

        # # draw edges
        # for (n1, n2) in g.edges:
        #     plt.plot([n1[1] - emin, n2[1] - emin], [n1[0] - nmin, n2[0] - nmin], 'black' , alpha=0.5)

        # # draw all nodes
        # for n1 in nodes:
        #     plt.scatter(n1[1] - emin, n1[0] - nmin, c='blue')
            
        # # draw connected nodes
        # for n1 in g.nodes:
        #     plt.scatter(n1[1] - emin, n1[0] - nmin, c='red')
            


        # plt.xlabel('NORTH')
        # plt.ylabel('EAST')

        # plt.show()

        start = list(g.nodes)[-2]
        goal = list(g.nodes)[-1]
        print (start, goal)
        path, cost = a_star_NX(g, heuristic, start, goal)
        print(len(path), path)

        # Convert path to waypoints
        if path == []:
            waypoints = [[0,0,TARGET_ALTITUDE, 0],[int(10.0),int( 0.0), TARGET_ALTITUDE, 0], [int(10.0), int(10.0), TARGET_ALTITUDE, 0]\
                        , [int(0.0), int(10.0), TARGET_ALTITUDE,0], [int(0.0), int(0.0), TARGET_ALTITUDE,0]]
        else:
            waypoints = [[0,0,TARGET_ALTITUDE, 0]]
            for p in path:
                waypoints.append([int(p[0]) + north_offset, int(p[1]) + east_offset, TARGET_ALTITUDE, 0])
            waypoints.append([goal_point[0]+north_offset,goal_point[1]+east_offset,TARGET_ALTITUDE,0])
        print (waypoints)
        # Set self.waypoints
        self.waypoints = waypoints
        # TODO: send waypoints to sim (this is just for visualization of waypoints)
        """ This function sends the waypoints to the sim for visualization"""
        self.send_waypoints()

    def start(self):
        self.start_log("Logs", "NavLog.txt")

        print("starting connection")
        self.connection.start()

        # Only required if they do threaded
        # while self.in_mission:
        #    pass

        self.stop_log()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5760, help='Port number')
    parser.add_argument('--host', type=str, default='127.0.0.1', help="host address, i.e. '127.0.0.1'")
    args = parser.parse_args()

    conn = MavlinkConnection('tcp:{0}:{1}'.format(args.host, args.port), timeout=60)
    drone = MotionPlanning(conn)
    time.sleep(1)

    drone.start()
