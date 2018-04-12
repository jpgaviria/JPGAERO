import matplotlib.pyplot as plt
import math 
from mpl_toolkits.mplot3d import Axes3D
#from IPython import get_ipython

import numpy as np
from enum import Enum

#%matplotlib inline
#get_ipython().run_line_magic('matplotlib', 'inline')
np.set_printoptions(precision=3, suppress=True)
plt.rcParams["figure.figsize"] = [12, 12]
class Rotation(Enum):
    ROLL = 0
    PITCH = 1
    YAW = 2  


class EulerRotation:
    
    def __init__(self, rotations):
        """
        `rotations` is a list of 2-element tuples where the
        first element is the rotation kind and the second element
        is angle in degrees.
        
        Ex:
        
            [(Rotation.ROLL, 45), (Rotation.YAW, 32), (Rotation.PITCH, 55)]
            
        """
        self._rotations = rotations
        self._rotation_map = {Rotation.ROLL : self.roll, Rotation.PITCH : self.pitch, Rotation.YAW : self.yaw}

    def roll(self, phi):
        """Returns a rotation matrix along the roll axis"""
        Rx = [[1,0,0],[0,math.cos(phi),-(math.sin(phi))],[0,math.sin(phi),math.cos(phi)]]
        return Rx
    
    def pitch(self, theta):
        """Returns the rotation matrix along the pitch axis"""
        Ry = [[math.cos(theta),0,math.sin(theta)],[0,1,0],[-(math.sin(theta)),0,math.cos(theta)]]
        return Ry

    def yaw(self, psi):
        """Returns the rotation matrix along the yaw axis"""
        Rz = [[math.cos(psi),-(math.sin(psi)),0],[math.sin(psi),math.cos(psi),0],[0,0,1]]
        return Rz

    def rotate(self):
        """Applies the rotations in sequential order"""
        Rx = self.roll(self._rotations[0][1])
        Ry = self.pitch(self._rotations[1][1])
        Rz = self.yaw(self._rotations[2][1])
        Rotation = np.matrix(Rz)*np.matrix(Ry)*np.matrix(Rx)
        t = np.eye(3)
        for r in self._rotations:
            kind = r[0]
            # convert from degrees to radians
            angle = np.deg2rad(r[1])
            t = np.dot(self._rotation_map[kind](angle), t)
        return t
if __name__ == "__main__":
    # Test your code by passing in some rotation values
    rotations = [
        (Rotation.ROLL, 25),
        (Rotation.PITCH, 75),
        (Rotation.YAW, 90),
    ]

    R = EulerRotation(rotations).rotate()
    print('Rotation matrix ...')
    print(R)
    # Should print
    # Rotation matrix ...
    # [[ 0.    -0.906  0.423]
    #  [ 0.259  0.408  0.875]
    #  [-0.966  0.109  0.235]]

    # TODO: calculate 3 rotation matrices.
    rot1 = [rotations[0], rotations[2], rotations[1]]
    rot2 = [rotations[1], rotations[2], rotations[0]]
    rot3 = [rotations[2], rotations[1], rotations[0]]
    R1 = EulerRotation(rot1).rotate()
    R2 = EulerRotation(rot2).rotate()
    R3 = EulerRotation(rot3).rotate()
    # unit vector along x-axis
    v = np.array([1, 0, 0])

    # TODO: calculate the new rotated versions of `v`.
    rv1 = np.dot(R1,v)
    rv2 = np.dot(R2,v)
    rv3 = np.dot(R3,v)
    # rv = np.dot(R, v)

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # axes (shown in black)
    ax.quiver(0, 0, 0, 1.5, 0, 0, color='black', arrow_length_ratio=0.15)
    ax.quiver(0, 0, 0, 0, 1.5, 0, color='black', arrow_length_ratio=0.15)
    ax.quiver(0, 0, 0, 0, 0, 1.5, color='black', arrow_length_ratio=0.15)


    # Original Vector (shown in blue)
    ax.quiver(0, 0, 0, v[0], v[1], v[2], color='blue', arrow_length_ratio=0.15)

    # Rotated Vectors (shown in red)
    ax.quiver(0, 0, 0, rv1[0], rv1[1], rv1[2], color='red', arrow_length_ratio=0.15)
    ax.quiver(0, 0, 0, rv2[0], rv2[1], rv2[2], color='purple', arrow_length_ratio=0.15)
    ax.quiver(0, 0, 0, rv3[0], rv3[1], rv3[2], color='green', arrow_length_ratio=0.15)

    ax.set_xlim3d(-1, 1)
    ax.set_ylim3d(1, -1)
    ax.set_zlim3d(1, -1)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()