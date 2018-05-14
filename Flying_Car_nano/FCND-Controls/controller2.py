"""
PID Controller

components:
    follow attitude commands
    gps commands and yaw
    waypoint following
"""
import numpy as np
from frame_utils import euler2RM
import math
from math import sin, cos, tan, sqrt

DRONE_MASS_KG = 0.5
MOI = np.array([0.005, 0.005, 0.01])
MAX_THRUST = 10.0
MIN_THRUST = 2.0
MAX_TORQUE = 1.0
maxSpeedXY = 10.0
maxAccelXY = 10.0
maxAscentRate = 1000.0
maxDescentRate = 1000.0
maxTiltAngle = 0.3

class NonlinearController(object):

    def __init__(self,
                x_k_p=0.0,
                x_k_d=1.0,
                y_k_p=0.0,
                y_k_d=1.0,
                z_k_p=1.5, 
                z_k_d=6.0, 
                z_k_i=0.0, 
                k_p_roll=5.0,
                k_p_pitch=5.0,#0.5,
                k_p_yaw=1.0,
                #k_p_p=0.05,
                #k_p_q=0.075,
                #k_p_r=0.05):
                k_p_p=25.0,
                k_p_q=25.0,
                k_p_r=10.0):
        """Initialize the controller object and control gains"""
        self.z_k_p = z_k_p
        self.z_k_d = z_k_d
        self.z_k_i = z_k_i
        self.x_k_p = x_k_p
        self.x_k_d = x_k_d
        self.y_k_p = y_k_p
        self.y_k_d = y_k_d
        self.k_p_roll = k_p_roll
        self.k_p_pitch = k_p_pitch
        self.k_p_yaw = k_p_yaw
        self.k_p_p = k_p_p
        self.k_p_q = k_p_q
        self.k_p_r = k_p_r
        self.g= -9.81

        return
    def CONSTRAIN(self,variable, minimum, maximum):
        if variable < minimum:
            variable = minimum
        elif variable > maximum:
            variable = maximum
        return variable

 
    def trajectory_control(self, position_trajectory, yaw_trajectory, time_trajectory, velocity_trajectory_FF, accel_trajectory_FF, current_time):
        """Generate a commanded position, velocity and yaw based on the trajectory
        
        Args:
            position_trajectory: list of 3-element numpy arrays, NED positions
            yaw_trajectory: list yaw commands in radians
            time_trajectory: list of times (in seconds) that correspond to the position and yaw commands
            current_time: float corresponding to the current time in seconds
            
        Returns: tuple (commanded position, commanded velocity, commanded yaw)
                
        """

        ind_min = np.argmin(np.abs(np.array(time_trajectory) - current_time))
        time_ref = time_trajectory[ind_min]
        
        
        if current_time < time_ref:
            position0 = position_trajectory[ind_min - 1]
            position1 = position_trajectory[ind_min]
            velocity0 = velocity_trajectory_FF[ind_min - 1]
            velocity1 = velocity_trajectory_FF[ind_min]

            
            
            time0 = time_trajectory[ind_min - 1]
            time1 = time_trajectory[ind_min]
            yaw_cmd = yaw_trajectory[ind_min - 1]
            
        else:
            yaw_cmd = yaw_trajectory[ind_min]
            if ind_min >= len(position_trajectory) - 1:
                position0 = position_trajectory[ind_min]
                position1 = position_trajectory[ind_min]
                velocity0 = velocity_trajectory_FF[ind_min]
                velocity1 = velocity_trajectory_FF[ind_min]
                
                time0 = 0.0
                time1 = 1.0
            else:

                position0 = position_trajectory[ind_min]
                position1 = position_trajectory[ind_min + 1]
                velocity0 = velocity_trajectory_FF[ind_min]
                velocity1 = velocity_trajectory_FF[ind_min + 1]

                time0 = time_trajectory[ind_min]
                time1 = time_trajectory[ind_min + 1]
            
        position_cmd = (position1 - position0) * \
                        (current_time - time0) / (time1 - time0) + position0
        velocity_cmd = (position1 - position0) / (time1 - time0)
        accel_cmd = (velocity1 - velocity0) / (time1 - time0)
        
        
        return (position_cmd, velocity_cmd, yaw_cmd, accel_cmd)
    
    def lateral_position_control(self, local_position_cmd, local_velocity_cmd, local_position, local_velocity,
                               acceleration_ff = np.array([0.0, 0.0])):
        """Generate horizontal acceleration commands for the vehicle in the local frame

        Args:
            local_position_cmd: desired 2D position in local frame [north, east]
            local_velocity_cmd: desired 2D velocity in local frame [north_velocity, east_velocity]
            local_position: vehicle position in the local frame [north, east]
            local_velocity: vehicle velocity in the local frame [north_velocity, east_velocity]
            acceleration_cmd: feedforward acceleration command
            
        Returns: desired vehicle 2D acceleration in the local frame [north, east]
        """
        x_pos_error = (local_position_cmd[0] - local_position[0])
        x_dot_cmd = (self.x_k_p * x_pos_error) + local_velocity_cmd[0]
        x_dot_cmd = self.CONSTRAIN(x_dot_cmd, -maxSpeedXY,maxSpeedXY)

        x_dot_error = x_dot_cmd - local_velocity[0]
        x_dot_dot_cmd = (self.x_k_d *x_dot_error) + acceleration_ff[0]
        x_dot_dot_cmd = self.CONSTRAIN(x_dot_dot_cmd, -maxAccelXY,maxAccelXY)

        b_x_c = x_dot_dot_cmd

        y_pos_error = (local_position_cmd[1] - local_position[1])
        y_dot_cmd = (self.y_k_p * y_pos_error) + local_velocity_cmd[1]
        y_dot_cmd = self.CONSTRAIN(y_dot_cmd, -maxSpeedXY,maxSpeedXY)

        y_dot_error = y_dot_cmd - local_velocity[1]
        y_dot_dot_cmd = (self.y_k_d *y_dot_error) + acceleration_ff[1]
        y_dot_dot_cmd = self.CONSTRAIN(y_dot_dot_cmd, -maxAccelXY,maxAccelXY)

        b_y_c = y_dot_dot_cmd
      
        return np.array([b_x_c,b_y_c])
    
    def altitude_control(self, altitude_cmd, vertical_velocity_cmd, altitude, vertical_velocity, attitude, acceleration_ff=0.0):
        """Generate vertical acceleration (thrust) command

        Args:
            altitude_cmd: desired vertical position (+up)
            vertical_velocity_cmd: desired vertical velocity (+up)
            altitude: vehicle vertical position (+up)
            vertical_velocity: vehicle vertical velocity (+up)
            attitude: the vehicle's current attitude, 3 element numpy array (roll, pitch, yaw) in radians
            acceleration_ff: feedforward acceleration command (+up)
            
        Returns: thrust command for the vehicle (+up)
        """
        rot_mat = euler2RM(attitude[0],attitude[1],attitude[2])
        b_z = rot_mat[2][2]
        z_pos_error = altitude_cmd - altitude
        integratedAltitudeError = 0.0
        z_vel_cmd = (self.z_k_p * z_pos_error) + vertical_velocity_cmd
        #z_vel_cmd = self.CONSTRAIN(z_vel_cmd, -maxAscentRate, maxDescentRate)

        z_vel_error = z_vel_cmd - vertical_velocity
        z_Accel_cmd = self.z_k_d * (z_vel_error) + (self.z_k_i * integratedAltitudeError) + acceleration_ff
        Acceleration = (z_Accel_cmd - self.g) / b_z

        thrust = Acceleration * DRONE_MASS_KG
        thrust = self.CONSTRAIN(thrust, MIN_THRUST, MAX_THRUST)
       
        #print(thrust)

        return thrust
        
    
    def roll_pitch_controller(self, acceleration_cmd, attitude, thrust_cmd):
        """ Generate the rollrate and pitchrate commands in the body frame
        
        Args:
            target_acceleration: 2-element numpy array (north_acceleration_cmd,east_acceleration_cmd) in m/s^2
            attitude: 3-element numpy array (roll, pitch, yaw) in radians
            thrust_cmd: vehicle thruts command in Newton
            
        Returns: 2-element numpy array, desired rollrate (p) and pitchrate (q) commands in radians/s
        """
        rot_mat = euler2RM(attitude[0],attitude[1],attitude[2])
        c = -thrust_cmd / DRONE_MASS_KG
        b_x = rot_mat[0][2]
        b_x_err = (acceleration_cmd[0] / c) - b_x

        b_x_err = self.CONSTRAIN(b_x_err, -maxTiltAngle, maxTiltAngle)
        b_x_p_term = self.k_p_pitch * b_x_err

        b_y = rot_mat[1][2]
        b_y_err = (acceleration_cmd[1] / c) - b_y

        b_y_err = self.CONSTRAIN(b_y_err, -maxTiltAngle, maxTiltAngle)
        b_y_p_term = self.k_p_roll * b_y_err

        # rot_mat1 = np.array([
        #                 [(rot_mat[1][0] / rot_mat[2][2]), (-rot_mat[0][0] / rot_mat[2][2])] , 
        #                 [([rot_mat[1][1] / rot_mat[2][2]), (-rot_mat[0][1] / rot_mat[2][2]) 
        #                 ] )
        rot_mat1=np.array([[rot_mat[1,0],-rot_mat[0,0]],[rot_mat[1,1],-rot_mat[0,1]]])/rot_mat[2,2]
        
        rot_rate = np.matmul(rot_mat1,np.array([b_x_p_term,b_y_p_term]).T)    
        p_c = rot_rate[0]
        q_c = rot_rate[1]

        return np.array([p_c, q_c])
    
    def body_rate_control(self, body_rate_cmd, body_rate):
        """ Generate the roll, pitch, yaw moment commands in the body frame
        
        Args:
            body_rate_cmd: 3-element numpy array (p_cmd,q_cmd,r_cmd) in radians/second^2
            body_rate: 3-element numpy array (p,q,r) in radians/second^2
            
        Returns: 3-element numpy array, desired roll moment, pitch moment, and yaw moment commands in Newtons*meters
        """
        p_error = (body_rate_cmd[0] - body_rate[0])
        q_error = (body_rate_cmd[1] - body_rate[1])
        r_error = (body_rate_cmd[2] - body_rate[2])
        p_dot = self.k_p_p * p_error
        q_dot = self.k_p_q * q_error
        r_dot = self.k_p_r * r_error

        u_bar_p = MOI[0] * p_dot
        u_bar_q = MOI[1] * q_dot
        u_bar_r = MOI[2] * r_dot
        
        return np.array([u_bar_p, u_bar_q, u_bar_r])
    
    def yaw_control(self, yaw_cmd, yaw):
        """ Generate the target yawrate
        
        Args:
            yaw_cmd: desired vehicle yaw in radians
            yaw: vehicle yaw in radians
        
        Returns: target yawrate in radians/sec
        """
        yaw_cmd = self.CONSTRAIN(yaw_cmd, -1, 1)
        
        psi_err = yaw_cmd - yaw
        #if (psi_err> 5.0):
        #    print(yaw_cmd)
        #if (psi_err< 5.0):
        #    print(yaw_cmd)
        #psi_err = self.CONSTRAIN(psi_err, -math.pi, math.pi)
        psi_err = self.CONSTRAIN(psi_err, -math.pi, math.pi)
        r_c = self.k_p_yaw * psi_err

        return r_c
  
