import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab

import trajectories
import simulate
import plotting

pylab.rcParams['figure.figsize'] = 10, 10
class Drone2D:
    """
    Simulates the dynamics of a drone confined to 
    motion in the y-z plane. 
    """
    def __init__(self,
                 I_x = 0.1, # moment of inertia around the x-axis
                 m = 0.2,   # mass of the vehicle 
                ):
        
        self.I_x = I_x
        self.m = m
        
        self.u1 = 0.0 # collective thrust
        self.u2 = 0.0 # moment about the x axis
        self.g = 9.81
        
        # z, y, phi, z_dot, y_dot, phi_dot
        self.X = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
    
    @property
    def y_dot_dot(self):
        phi = self.X[2]
        return self.u1 / self.m * np.sin(phi)
    
    @property
    def z_dot_dot(self):
        phi = self.X[2]
        return self.g - self.u1*np.cos(phi)/self.m
    
    @property
    def phi_dot_dot(self):
        return self.u2 / self.I_x
    
    def advance_state(self, dt):
        
        X_dot = np.array([self.X[3], 
                        self.X[4],
                        self.X[5], 
                        self.z_dot_dot,
                        self.y_dot_dot, 
                        self.phi_dot_dot])
        
        
        # Change in state will be 
        self.X = self.X + X_dot * dt
        return self.X 
    
    def set_controls(self, u1, u2):
        self.u1 = u1
        self.u2 = u2

class LinearCascadingController:
    
    def __init__(self,
                 m,   # needed to convert u1_bar to u1
                 I_x, # needed to convert u2_bar to u2
                 z_k_p=1.0,   
                 z_k_d=1.0,   
                 y_k_p=1.0,
                 y_k_d=1.0,
                 phi_k_p=1.0,
                 phi_k_d=1.0):
        
        self.z_k_p = z_k_p
        self.z_k_d = z_k_d   
        self.y_k_p = y_k_p
        self.y_k_d = y_k_d
        self.phi_k_p = phi_k_p
        self.phi_k_d = phi_k_d
        
        self.g = 9.81
        self.I_x = I_x
        self.m = m

    def altitude_controller(self, 
                    z_target, 
                    z_actual, 
                    z_dot_target, 
                    z_dot_actual,
                    z_dot_dot_target,
                    phi_actual, # unused parameter. Ignore for now.
                    ):
        """
        A PD controller which commands a thrust (u_1) 
        for the vehicle. 
        """
        
        # TODO (recommended to do AFTER attitude)
        #   Implement feedforward PD control to calculate
        #   u_1_bar and then use the linear math from above
        #   to transform u_1_bar into u_1 and then return u_1
        
        u_1 = 0.0
        return u_1

    
    def lateral_controller(self, 
                        y_target, 
                        y_actual, 
                        y_dot_target, 
                        y_dot_actual,
                        u_1=None, # unused parameter. Ignore for now.
                        y_dot_dot_ff=0.0,
                        ):
        """
        A PD controller which commands a target roll 
        angle (phi_commanded).
        """
        
        # TODO (recommended to do AFTER attitude)
        #   Implement feedforward PD control to calculate
        #   y_dot_dot_target and then use the linear math from above
        #   to transform y_dot_dot_target into phi_commanded
        #   and then return phi_commanded
        phi_commanded = 0.0
        return phi_commanded 



    def attitude_controller(self, 
                            phi_target, 
                            phi_actual, 
                            phi_dot_actual,
                            phi_dot_target=0.0
                           ):
        """
        A PD controller which commands a moment (u_2)
        about the x axis for the vehicle.
        """
        
        # TODO (recommended to do FIRST)
        #   Implement PD control to calculate u_2_bar
        #   and then use the linear math from above to
        #   transform u_2_bar into u_2 and then return u_2
        u_2 = 0.0
        return u_2


if __name__ == "__main__":
    # TESTING CELL 
    # 
    # Note - this cell will only give nice output when your code
    #  is working AND you've tuned your parameters correctly.
    #  you might find it helpful to come up with a strategy
    #  for first testing the inner loop controller and THEN 
    #  testing the outer loop.
    #
    # Run this cell when you think your controller is ready!
    #
    # You'll have to tune the controller gains to get good results.

    #### CONTROLLER GAINS (TUNE THESE) ######

    z_k_p   = 0.0  
    z_k_d   = 0.0  
    y_k_p   = 0.0
    y_k_d   = 0.0
    phi_k_p = 0.0
    phi_k_d = 0.0

    #########################################

    drone = Drone2D()

    # INSTANTIATE CONTROLLER
    linear_controller = LinearCascadingController(
        drone.m,
        drone.I_x,
        z_k_p=z_k_p,   
        z_k_d=z_k_d,   
        y_k_p=y_k_p,
        y_k_d=y_k_d,
        phi_k_p=phi_k_p,
        phi_k_d=phi_k_d
    )

    # TRAJECTORY PARAMETERS (you don't need to change these)
    total_time = 100.0  
    omega_z = 1.0       # angular frequency of figure 8

    # GENERATE FIGURE 8
    z_traj, y_traj, t = trajectories.figure_8(omega_z, total_time, dt=0.02)
    z_path, z_dot_path, z_dot_dot_path = z_traj
    y_path, y_dot_path, y_dot_dot_path = y_traj

    # SIMULATE MOTION
    linear_history     = simulate.zy_flight(z_traj, 
                                            y_traj,
                                            t, 
                                            linear_controller,
                                            inner_loop_speed_up=10)
    # PLOT RESULTS
    plotting.plot_zy_flight_path(z_path, y_path, linear_history)
