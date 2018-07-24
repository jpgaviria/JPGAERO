import numpy as np 
#import math
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
#import jdc
from ipywidgets import interactive
from scipy.stats import multivariate_normal

from StateSpaceDisplay import state_space_display, state_space_display_updated

from CoaxialDrone import CoaxialCopter
from PIDcontroller import PIDController_with_ff
from PathGeneration import flight_path

from DronewithPIDControllerKF import DronewithPIDKF

from DronewithPIDControllerKF import DronewithPIDKFKnobs

pylab.rcParams['figure.figsize'] = 10, 10

class KF:
    def __init__(self,
                 sensor_sigma,             # Sensor noise
                 velocity_sigma,           # Velocity uncertainty
                 position_sigma,           # Position uncertainty
                 dt                        # dt time between samples 
                ):
        
        # Sensor measurement covariance
        self.r_t = np.array([[sensor_sigma**2]])
        
        # Motion model noise for velocity and position
        self.q_t = np.array([[velocity_sigma**2,0.0],
                             [0.0,position_sigma**2]]) 
        self.dt = dt
        
        self.mu = np.array([0.0])
        self.sigma = np.array([0.0])
        
        self.mu_bar = self.mu
        self.sigma_bar = self.sigma

    @property
    def a(self):
        return np.array([[1.0, 0.0],
                         [self.dt, 1.0]])

    @property
    def b(self):
        return np.array([[self.dt],
                         [0.0]])

    def g(self, 
          previous_mu, # Previous mu
          u            # Control input \ddot{z}
          ):
        '''Generates the transition function for the height. '''
        # TODO: return the g matrix using A and B matrixes 
        return np.matmul(self.a,previous_mu) + self.b*u

    def g_prime(self):
        '''The derivative of the transition function.'''
        # TODO: return the derivative of the g matrix
        return np.array([[1.0, 0.0],
                         [self.dt, 1.0]])


    def initial_values(self, 
                       mu_0, 
                       sigma_0):

        '''Setting initial values for the mu and sigma of the KF'''

        self.mu = mu_0
        self.sigma = sigma_0



    def predict(self, 
                u             # Control input 
               ):

        '''Prediction step of the KF filter '''

        # TODO: Follow the prediction steps outlined in theoretical part of the lesson and implement the next variables. 
        mu_bar = self.g(self.mu,u)
        g_now  = self.g_prime()
        sigma_bar = np.matmul(g_now, np.matmul(self.sigma, np.transpose(g_now)))

        
        self.mu_bar = mu_bar
        self.sigma_bar = sigma_bar

        return mu_bar, sigma_bar


    def h_prime(self):
        return np.array([[0.0, 1.0]])
        
    def h(self,mu):
        return np.matmul(np.array([[0.0, 1.0]]), mu) 

    def update(self, z):
        
        # TODO: Follow the update step outlined in theoretical part of the lesson and implement the next variables. 
        H = self.h_prime*self.mu_bar 
        S = np.matmul(np.matmul(H, self.sigma_bar), np.transpose(H)) + self.r_t  
        K = np.matmul(np.matmul(self.sigma_bar, np.transpose(H)), np.linalg.inv(S))
        
        mu = self.mu_bar + np.matmul(K,(z - self.h(self.mu_bar)))
        sigma = np.matmul((np.identity(2) - np.matmul(K, H)), self.sigma_bar)
        
        self.mu = mu
        self.sigma = sigma
        
        return mu, sigma


class IMU:
    def __init__(self):
        pass
        
    def measure(self, z, sigma=0.001): 
        return z + np.random.normal(0.0, sigma)

if __name__ == "__main__":

    z = 0.0                         # Initial position
    v = 1.0                         # Initial velocity
    dt = 1.0                        # The time difference between measures
    sensor_error = 0.1              # Sensor sigma
    velocity_sigma = 0.1            # Velocity uncertainty
    position_sigma = 0.1            # Position uncertainty


    mu_0 = np.array([[v],
                    [z]]) 

    sigma_0 = np.array([[velocity_sigma**2, 0.0],
                        [0.0, position_sigma**2]])

    u = np.array([[0.0],
                [0.0]])     # no control input is given \ddot{z} = 0 

    # Initialize the object
    MYKF = KF(sensor_error, velocity_sigma, position_sigma, dt)

    # Input the initial values 
    MYKF.initial_values(mu_0, sigma_0)

    # Call the predict function
    mu_bar, sigma_bar = MYKF.predict(u)

    print('mu_bar = \n', mu_bar)
    print('sigma_bar = \n', sigma_bar)

    state_space_display(z, v, mu_0, sigma_0, mu_bar, sigma_bar)

    measure = 1.01 # only measuring the Z coordinate

    mu_updated, sigma_updated = MYKF.update(measure)

    print('updated mean = \n', mu_updated)
    print('updated sigma = \n', sigma_updated)

    state_space_display_updated(z, v, mu_0, sigma_0, mu_bar, sigma_bar, mu_updated, sigma_updated)

    total_time = 10.0  # Total flight time
    dt = 0.01          # Time intervale between measurements 

    t, z_path, z_dot_path, z_dot_dot_path =  flight_path(total_time, dt,'constant' )

    sensor_error  = 0.1
    velocity_sigma = 0.1
    position_sigma = 0.1 
    MYKF = KF(sensor_error, velocity_sigma, position_sigma, dt)

    # Initializing the drone with PID controller and providing information of the desired flight path. 
    FlyingDrone = DronewithPIDKF(z_path, z_dot_path, z_dot_dot_path, t, dt, IMU, KF)

    interactive_plot = interactive(FlyingDrone.PID_controler_with_KF, 
                                position_sigma = (0.0, 0.1, 0.001),
                                motion_sigma = (0.0, 0.1, 0.001))
    output = interactive_plot.children[-1]
    output.layout.height = '800px'
    interactive_plot

    FlyingDroneKnobs = DronewithPIDKFKnobs(z_path, z_dot_path, z_dot_dot_path, t, dt, IMU, KF)

    interactive_plot = interactive(FlyingDroneKnobs.PID_controler_with_KF_knobs,
                                k_p=(5.0, 35.0, 1),
                                k_d=(0.0, 10, 0.5), 
                                k_i=(0.0, 10, 0.5), 
                                mass_err =(0.7, 1.31, 0.01),
                                sigma = (0.0, 0.1, 0.001),
                                position_sigma = (0.0, 0.1, 0.001),
                                motion_sigma = (0.0, 0.1, 0.001))

    output = interactive_plot.children[-1]
    output.layout.height = '800px'
    interactive_plot











