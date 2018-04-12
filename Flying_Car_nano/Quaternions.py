import numpy as np

def euler_to_quaternion(angles):
    roll = angles[0]
    pitch = angles[1]
    yaw = angles[2]
    
    # TODO: complete the conversion
    # and return a numpy array of
    # 4 elements representing a quaternion [a, b, c, d]
    a = [[np.cos(yaw/2)],[0],[0],[np.sin(yaw/2)]]
    b = [[np.cos(pitch/2)],[0],[np.sin(pitch/2)],[0]]
    c = [[np.cos(roll/2)],[np.sin(roll/2)],[0],[0]]
    d = np.matrix(a)*np.matrix(b)*np.matrix(c)
    return d

def quaternion_to_euler(quaternion):
    a = 1#quaternion[0]
    b = 1#quaternion[1]
    c = 1#quaternion[2]
    d = 1#quaternion[3]
    
    # TODO: complete the conversion
    # and return a numpy array of
    # 3 element representing the euler angles [roll, pitch, yaw]
if __name__ == "__main__":
    euler = np.array([np.deg2rad(90), np.deg2rad(30), np.deg2rad(0)])

    q = euler_to_quaternion(euler) # should be [ 0.683  0.683  0.183 -0.183]
    print(q)

    assert np.allclose(euler, quaternion_to_euler(q))