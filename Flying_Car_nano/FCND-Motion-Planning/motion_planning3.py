import argparse
import time
import msgpack #""" NEW library in motion planning """
from enum import Enum, auto

import numpy as np

import csv
from skimage.morphology import medial_axis
from skimage.util import invert
import matplotlib.pyplot as plt

from planning_utils import heuristic, create_grid, prune_path, find_start_goal, a_star, get3DPath
from sampling import Sampler
from udacidrone import Drone
from udacidrone.connection import MavlinkConnection
from udacidrone.messaging import MsgID
from udacidrone.frame_utils import global_to_local

UseLatLonAlt = True
#grid_goal_lat_lon_alt = (-122.39966, 37.793593, 0) # Californa avenue and front
#grid_goal_lat_lon_alt = (-122.39652, 37.79360, 15) # On the roof
#grid_goal_lat_lon_alt = (-122.39686, 37.79426, 0) # center of hollow small building
grid_goal_lat_lon_alt = (-122.39629, 37.79244, 0) # center of hollow Tall building
#grid_goal_lat_lon_alt = (-122.402273, 37.79741, 0) # cloce to C letter on hollow building far Away north west
#grid_goal_lat_lon_alt = (-122.392300, 37.791315, 0) # Spear St Plaza behind building far Away south east


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
            if np.linalg.norm(self.target_position[0:2] - self.local_position[0:2]) < 5.0:
                if len(self.waypoints) > 0:
                    self.waypoint_transition()
                else:
                    # Be strict with the landing position to be accurate
                    if np.linalg.norm(self.target_position[0:2] - self.local_position[0:2]) < 0.5:
                        if np.linalg.norm(self.local_velocity[0:2]) < 1.0:
                            self.landing_transition()

    def velocity_callback(self):
        if self.flight_state == States.LANDING:
            if (self.global_position[2]-grid_goal_lat_lon_alt[2]) - self.global_home[2] < 0.1:
                if abs(self.local_position[2]+grid_goal_lat_lon_alt[2]) < 0.1:
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
        Zmax = np.max(data[:, 2] + data[:, 5])
        # Define a grid for a particular altitude and safety margin around obstacles
        """ Create grid comes from the planning_utils.py so we can call it directly here"""
        grid, north_offset, east_offset = create_grid(data, TARGET_ALTITUDE, SAFETY_DISTANCE)
        """ Using Medial-Axis solution for motion planning 3"""
        skeleton = medial_axis(invert(grid))
        print("North offset = {0}, east offset = {1}".format(north_offset, east_offset))
        # Define starting point on the grid (this is just grid center)
        grid_center = (north_offset, east_offset)
        # TODO: convert start position to current position rather than map center
        """ Get local grid position and determine the new grid start from global home then
        add it to grid center """
        Localcurrent = global_to_local(self.global_position,self.global_home)
        grid_start = (int(-grid_center[0]+Localcurrent[0]),int(-grid_center[1]+Localcurrent[1]))
        #if local position is not at altitude 0, update the altitute for takeoff
        if -Localcurrent[2] > TARGET_ALTITUDE:
                    TARGET_ALTITUDE = int(TARGET_ALTITUDE -Localcurrent[2])
                    self.target_position[2] = TARGET_ALTITUDE
        # Set goal as some arbitrary position on the grid
        if UseLatLonAlt == False:
            grid_goal = (-north_offset + Localcurrent[0] + 10, -east_offset +Localcurrent[1] + 10)
            print ("using grid position for the goal")
        else:
            print ("using Lat, Lon, Alt position for the goal")
            # TODO: adapt to set goal as latitude / longitude position and convert
            """ See global variable grid_lat_lon at the top of the file"""
            """ code to get the grid goal based on LAT LONG position, assume altitude is 0 for goal"""
            grid_goal = global_to_local(grid_goal_lat_lon_alt,self.global_home)
            grid_goal = tuple((int(grid_goal[0]-north_offset),int(grid_goal[1]-east_offset)))
            print(grid_start, grid_goal)
            # if Altitude is not ground level adapt to new altitude
            if grid_goal_lat_lon_alt[2] > TARGET_ALTITUDE:
                TARGET_ALTITUDE = grid_goal_lat_lon_alt[2] + SAFETY_DISTANCE
                self.target_position[2] = TARGET_ALTITUDE
                #self.global_home[2] = grid_goal_lat_lon_alt[2]
                grid, north_offset, east_offset = create_grid(data, TARGET_ALTITUDE, SAFETY_DISTANCE)
                """ Using Medial-Axis solution for motion planning 3"""
                skeleton = medial_axis(invert(grid))
        # Run A* to find a path from start to goal
        # TODO: add diagonal motions with a cost of sqrt(2) to your A* implementation 
        """ Done on Planning_utils.py """ 
        # or move to a different search space such as a graph (not done here)
        print('Local Start and Goal: ', grid_start, grid_goal)
 
        """ Using Medial-Axis solution to find the skeleton start and goal"""
        skel_start, skel_goal = find_start_goal(skeleton, grid_start, grid_goal)

        print(grid_start, grid_goal)
        print(skel_start, skel_goal)
        """ a_star, heuristic come from the planning_utils.py so we can call it directly"""
        #path, _ = a_star(grid, heuristic, grid_start, grid_goal)
        path, _, FoundPath = a_star(invert(skeleton).astype(np.int), heuristic, tuple(skel_start), tuple(skel_goal))
        while FoundPath == False:
            # increase target altitude by 5 ft, get new skeeton and try again
            TARGET_ALTITUDE += 20
            print ("TRY AGAIN, NEW CRUISE ALTITUDE")
            print(TARGET_ALTITUDE)
            self.target_position[2] = TARGET_ALTITUDE
            grid, north_offset, east_offset = create_grid(data, TARGET_ALTITUDE, SAFETY_DISTANCE)
            skeleton = medial_axis(invert(grid))
            skel_start, skel_goal = find_start_goal(skeleton, grid_start, grid_goal)
            path, _, FoundPath = a_star(invert(skeleton).astype(np.int), heuristic, tuple(skel_start), tuple(skel_goal))
            if TARGET_ALTITUDE > Zmax:
                break
        # TODO: prune path to minimize number of waypoints
        pruned_path = prune_path(path)
        """ Add the grid goal so that it can fly to the exact location"""
        pruned_path.append([grid_goal[0],grid_goal[1]])
        sampler = Sampler(data, SAFETY_DISTANCE)
        polygons = sampler._polygons
        # Second Prunning to try to minimize waypoints by doing direct to
        # Also add Altitude
        Path3D, TARGET_ALTITUDE = get3DPath(pruned_path,TARGET_ALTITUDE,self.local_position[2],\
                            grid_goal_lat_lon_alt[2],SAFETY_DISTANCE, polygons)

        # TODO (if you're feeling ambitious): Try a different approach altogether!
        #add heading to all the waypoints
        Path_with_heading = []
        Path_with_heading.append([Path3D[0][0],Path3D[0][1],0])
        for i in range(0,len(Path3D)-1):
            heading = np.arctan2((Path3D[i+1][1]-Path3D[i][1]),(Path3D[i+1][0]-Path3D[i][0]))
            Path_with_heading.append([Path3D[i+1][0],Path3D[i+1][1],int(heading)])
        if FoundPath == False:
            # if path not found then takeoff and land on the spot
            localpos = global_to_local(self.global_position,self.global_home)
            waypoints = [[int(localpos[0]),int(localpos[1]),5,0],\
                        [int(localpos[0]),int(localpos[1]),0,0]]
        else:
            # Convert path to waypoints
            waypoints = [[int(p[0] + north_offset),int(p[1] + east_offset), TARGET_ALTITUDE,int(p[2])] for p in Path_with_heading]
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
