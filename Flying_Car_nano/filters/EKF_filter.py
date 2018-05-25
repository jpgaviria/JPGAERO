import numpy as np 
from math import sin, cos
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
#import jdc
from ipywidgets import interactive
from scipy.stats import multivariate_normal
from StateSpaceDisplayFor2D import state_space_display_predict, state_space_display_updated

from PIDcontroller import PIDController_with_ff
from PathGeneration import flight_path
#from StateSpaceDisplayFor2D import state_space_display_updated
from DronewithPIDControllerEKF2D import DronewithPIDEKF, DronewithPIDKFKnobs
#from DronewithPIDControllerEKF2D import DronewithPIDKFKnobs


import time 

pylab.rcParams['figure.figsize'] = 10, 10

class EKF:
    def __init__(self,
                 motion_error,             # Motion noise
                 angle_sigma,              # Angle sigma
                 velocity_sigma,           # Velocity uncertainty
                 position_sigma,           # Position uncertainty
                 dt                        # dt time between samples 
                ):
        
        # Sensor measurement covariance
        self.r_t = np.array([[motion_error**2]])
        
        # Motion model noise for angle, velocity and position
        self.q_t = np.array([[angle_sigma**2,0.0,0.0],
                             [0.0,velocity_sigma**2,0.0],
                             [0.0,0.0,position_sigma**2]]) 
        
        self.dt = dt
        
        self.mu = np.array([0])
        self.sigma = np.array([0])
        
        self.mu_bar = self.mu
        self.sigma_bar = self.sigma
        
    def initial_values(self,mu_0, sigma_0):
        self.mu= mu_0
        self.sigma = sigma_0
        

    def g(self, 
          u       # The new input
         ):
        '''
        Calculates g matrix for transition model 
        '''

        current_phi, current_y_dot, current_y = self.mu

        # TODO: return the g matrix 
        new_phi = u
        new_y_dot = current_y_dot - sin(current_phi) * self.dt
        new_y = current_y + current_y_dot * self.dt

        g = np.array([new_phi, new_y_dot, new_y])

        return g

    def g_prime(self):
        '''
        Calculates the g prime matrix
        '''
        current_phi = self.mu[0]

        # TODO: return the derivative of the g matrix 
        g_prime = np.array([[0.0, 0.0, 0.0],
                            [-cos(current_phi) * self.dt, 1.0, 0.0],
                            [0.0, self.dt, 1.0]])

        return g_prime


    def predict(self, u):

        previous_covariance = self.sigma
        mu_bar = self.g(u)
        G_now  = self.g_prime()
        sigma_bar = np.matmul(G_now,np.matmul(previous_covariance,np.transpose(G_now))) + self.r_t

        self.mu_bar  = mu_bar 
        self.sigma_bar = sigma_bar

        return mu_bar, sigma_bar

    def h_prime(self,mu_bar):
        
        predicted_phi, predicted_y_dot, predicted_y = mu_bar
        # TODO: Calculate the derivative of the h matrix
        return np.array([[float(-predicted_y*sin(predicted_phi)/cos(predicted_phi)**2), 0.0, -1/cos(predicted_phi)]]) 

    def h(self,mu_bar):
        
        predicted_phi, predicted_y_dot, predicted_y = mu_bar
        # TODO: Calculate the h matrix 
        return np.array([-predicted_y / cos(predicted_phi)])

    def update(self, z):
        
        H = self.h_prime(self.mu_bar)
        S = np.matmul(np.matmul(H,self.sigma_bar),np.transpose(H)) + self.q_t     
        K = np.matmul(np.matmul(self.sigma_bar,np.transpose(H)),np.linalg.inv(S))

        mu = self.mu_bar + np.matmul(K,(-z-self.h(self.mu_bar)))
        sigma = np.matmul((np.identity(3) - np.matmul(K,H)),self.sigma_bar)
        
        self.mu=mu
        self.sigma=sigma
        
        return mu, sigma
        
class IMU:
    def __init__(self):
        pass
        
    def measure(self,z,sigma=0.001):
        return z + np.random.normal(0.0, sigma)
class Drone:
    def __init__(self,
                phi,
                y_dot,
                y):
        
        self.X = np.array([phi,y_dot,y])
        
        
    def advance_state(self, phi_new, dt): 
        self.X = np.array([phi_new, self.X[1]-np.sin(phi_new)*dt, self.X[2]+self.X[1]*dt])
        
        return self.X         
if __name__ == "__main__":
    y = 1.0                         # Initial position
    y_dot = 1.0                     # Initial velocity
    phi = 0.1                       # Initial roll angle

    dt = 1.0                        # The time difference between measures
    motion_error = 0.1              # Motion error 
    angle_error = 0.1               # Angle uncertainty 
    velocity_sigma = 0.1            # Velocity uncertainty
    position_sigma = 0.1            # Position uncertainty

    mu_0 = np.array([[phi],[y_dot],[y]]) 
    sigma_0 = np.matmul(np.identity(3), np.array([angle_error,velocity_sigma,position_sigma]))

    u = np.array([phi])    


    # Initialize the object
    MYEKF=EKF(motion_error,angle_error,velocity_sigma,position_sigma,dt)

    # Input the initial values 
    MYEKF.initial_values(mu_0, sigma_0)

    # Call the predict function
    mu_bar, sigma_bar = MYEKF.predict(u)

    print('mu_bar = \n',mu_bar)
    print('sigma_bar = \n', sigma_bar)

    #state_space_display_predict(y,y_dot,mu_0,sigma_0,mu_bar,sigma_bar)

    measure =2.05 

    mu_updated, sigma_updated = MYEKF.update(measure)
    print('updated mean = \n', mu_updated)
    print('updated sigma = \n', sigma_updated)

    #state_space_display_updated(y,y_dot,mu_0,sigma_0,mu_bar,sigma_bar,mu_updated,sigma_updated)

    total_time = 10.0
    dt = 0.01

    t, z_path, z_dot_path, z_dot_dot_path =  flight_path(total_time, dt,'constant' )

    FlyingDrone = DronewithPIDEKF(z_path, z_dot_path, z_dot_dot_path, t, dt,IMU,Drone,EKF)

    interactive_plot = interactive(FlyingDrone.PID_controler_with_EKF, 
                                angle_error = (0.0, 0.01, 0.001),
                                position_sigma = (0.0, 0.05, 0.001),
                                motion_sigma = (0.0, 0.05, 0.001))
    output = interactive_plot.children[-1]
    output.layout.height = '800px'
    interactive_plot

    FlyingDroneKnobs = DronewithPIDKFKnobs(z_path, z_dot_path, z_dot_dot_path, t, dt,IMU,Drone,EKF)

    interactive_plot = interactive(FlyingDroneKnobs.PID_controler_with_KF_knobs,
                                k_p=(5.0, 35.0, 1),
                                k_d=(0.0,10,0.5), 
                                k_i=(0.0,10,0.5), 
                                angle_error = (0.0, 0.1, 0.001),
                                position_sigma = (0.0, 0.1, 0.001),
                                motion_sigma = (0.0, 0.1, 0.001))

    output = interactive_plot.children[-1]
    output.layout.height = '800px'
    interactive_plot    
