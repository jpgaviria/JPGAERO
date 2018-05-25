import numpy as np 
import matplotlib.pyplot as plt

from helpers import IMU, plot_compare

class ComplementaryFilter:
    def __init__(self,dt,tau): 
        self.dt = dt
        self.tau = tau
        self.estimated_theta = 0.0
        self.estimated_phi   = 0.0
        
    def update(self,z):
        
        # TODO: 
        #  implement the estimated pitch and roll 
        
        self.estimated_theta = None
        self.estimated_phi = None 
            
    def make_estimates(self,measurements):
        self.estimated_theta = 0.0
        self.estimated_phi = 0.0
        estimates = np.zeros((2, measurements.shape[1]))
        for i in range(measurements.shape[1]):
            z = measurements[:,i]
            self.update(z)
            est = np.array([self.estimated_theta, self.estimated_phi])
            estimates[:,i] = est
        return estimates



if __name__ == "__main__":

    # drone hovers for all N measurements 
    N = 2000 
    true_values = np.zeros((4, N))

    # simulate sensor measurements
    imu = IMU()
    measurements = imu.make_measurements(true_values)

    # Parameters for complementary filter
    # 
    # TODO - try modifying TAU. 
    #   What value gives you the best estimate?
    #   What do your plots look like when TAU = DT * 100?
    #   What about when TAU = DT * 1? 

    DT  = 0.01
    TAU = DT * 1
    cf  = ComplementaryFilter(DT, TAU)

    # make estimates based on measurements
    estimates = cf.make_estimates(measurements)

    # integrating gyro directly
    integrated_ests = np.zeros((2,N))
    integrated_ests[0,:] = np.cumsum(measurements[2,:]) * DT
    integrated_ests[1,:] = np.cumsum(measurements[3,:]) * DT

    # plot pitch
    plot_compare(true_values,estimates,measurements,integrated_ests, DT, 0)
    # plot roll
    plot_compare(true_values,estimates,measurements,integrated_ests, DT, 1)