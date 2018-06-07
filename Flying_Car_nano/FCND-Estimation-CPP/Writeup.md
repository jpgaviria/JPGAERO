# Estimation Project #



## The Tasks ##

Here is the explanation on what I did to pass all the scenarios

Project outline:

 - [Step 1: Sensor Noise](#step-1-sensor-noise)
 - [Step 2: Attitude Estimation](#step-2-attitude-estimation)
 - [Step 3: Prediction Step](#step-3-prediction-step)
 - [Step 4: Magnetometer Update](#step-4-magnetometer-update)
 - [Step 5: Closed Loop + GPS Update](#step-5-closed-loop--gps-update)
 - [Step 6: Adding Your Controller](#step-6-adding-your-controller)



### Step 1: Sensor Noise ###

1. Ran Scenario `06_NoisySensors` and produced the graph 1 and graph 2 text files for (GPS X data) and (Accelerometer X data)

2. Changed extension of each of the files to .csv and imported them in excel and used excel to calculate standard deviation

3. found the std deviations to be 0.70062 for GPS X data and 0.476429 for Accelerometer X data

4. Pluged in my calculated std deviations into the file `config/6_Sensornoise.txt` and re-ran the test and this time it passed

![Step 1](images/Capture1.PNG)

### Step 2: Attitude Estimation ###

1. Implemented `UpdateFromIMU()` function of `QuadEstimatorEKF.cpp` 
- I used the option 2 in the hints to simplify my implementation, that way I don't have to create a rotation matrix.
- Create a quaternion class object from the roll, pitch and yaw
- Use the bult in function of the quaternon class to integrate using giro and DT of the IMU
- Get the integrated pitch, roll and yaw to be used on the integraton and update function
- normalize yaw to -pi .. pi
![Implementation](images/Capture3.PNG)

2. After the implementing the complementary filter the test passed

![Result](images/Capture2.PNG)

### Step 3: Prediction Step ###

In this next step you will be implementing the prediction step of your filter.

1. Implemented `PredictState()` function in `QuadEstimatorEKF.cpp`
- Rotate the acceleration vector into the Inertial frame to be able to use it on the predict function
- Update all state matrix components taking the current one and adding the integral with time.
- For Z acceleration we need to substract gravity
- For yaw we were told that the IMU already includes the integration, so we just pass the current state from IMU.
![PredictState](images/Capture4.PNG)

2. Implemented `GetRbgPrime()` in `QuadEstimatorEKF.cpp` following the math from the document
![Get Rbg Prime](images/Capture5.PNG)

3. Implemented `Predict()` function in `QuadEstimatorEKF.cpp` to predict the covariance forward
- Fill out g prime matrix using the document
- Update covariance matrix g Prime and the model covariance Q
![Predict Covariance](images/Capture6.PNG)

4. Tuned QPosXYStd and the QVelXYStd in `QuadEstimatorEKF.txt` to try to find a reasonable plot. there are no pass or fail criteria for this step so I made it look similar to the good solution in the readme.


### Step 4: Magnetometer Update ###

1. Tuned QYawStd in `QuadEstimatorEKF.txt` to capture the magnitude of the drift

2. Implemented `UpdateFromMag()` function in `QuadEstimatorEKF.cpp`
- Update zFromX from the predicted state
- Normalize zfromX from - Pi to Pi to avoid jumps
- Fill out h prime as per the document for a magnetometer
![Magnetometer](images/Capture6.PNG)

1. Run scenario `10_MagUpdate`.  This scenario uses a realistic IMU, but the magnetometer update hasn’t been implemented yet. As a result, you will notice that the estimate yaw is drifting away from the real value (and the estimated standard deviation is also increasing).  Note that in this case the plot is showing you the estimated yaw error (`quad.est.e.yaw`), which is drifting away from zero as the simulation runs.  You should also see the estimated standard deviation of that state (white boundary) is also increasing.

2. Tune the parameter `QYawStd` (`QuadEstimatorEKF.txt`) for the QuadEstimatorEKF so that it approximately captures the magnitude of the drift, as demonstrated here:

![mag drift](images/mag-drift.png)

3. Implement magnetometer update in the function `UpdateFromMag()`.  Once completed, you should see a resulting plot similar to this one:

![mag good](images/mag-good-solution.png)

***Success criteria:*** *Your goal is to both have an estimated standard deviation that accurately captures the error and maintain an error of less than 0.1rad in heading for at least 10 seconds of the simulation.*

**Hint: after implementing the magnetometer update, you may have to once again tune the parameter `QYawStd` to better balance between the long term drift and short-time noise from the magnetometer.**

**Hint: see section 7.3.2 of [Estimation for Quadrotors](https://www.overleaf.com/read/vymfngphcccj) for a refresher on the magnetometer update.**


### Step 5: Closed Loop + GPS Update ###

1. Run scenario `11_GPSUpdate`.  At the moment this scenario is using both an ideal estimator and and ideal IMU.  Even with these ideal elements, watch the position and velocity errors (bottom right). As you see they are drifting away, since GPS update is not yet implemented.

2. Let's change to using your estimator by setting `Quad.UseIdealEstimator` to 0 in `config/11_GPSUpdate.txt`.  Rerun the scenario to get an idea of how well your estimator work with an ideal IMU.

3. Now repeat with realistic IMU by commenting out these lines in `config/11_GPSUpdate.txt`:
```
#SimIMU.AccelStd = 0,0,0
#SimIMU.GyroStd = 0,0,0
```

4. Tune the process noise model in `QuadEstimatorEKF.txt` to try to approximately capture the error you see with the estimated uncertainty (standard deviation) of the filter.

5. Implement the EKF GPS Update in the function `UpdateFromGPS()`.

6. Now once again re-run the simulation.  Your objective is to complete the entire simulation cycle with estimated position error of < 1m (you’ll see a green box over the bottom graph if you succeed).  You may want to try experimenting with the GPS update parameters to try and get better performance.

***Success criteria:*** *Your objective is to complete the entire simulation cycle with estimated position error of < 1m.*

**Hint: see section 7.3.1 of [Estimation for Quadrotors](https://www.overleaf.com/read/vymfngphcccj) for a refresher on the GPS update.**

At this point, congratulations on having a working estimator!

### Step 6: Adding Your Controller ###

Up to this point, we have been working with a controller that has been relaxed to work with an estimated state instead of a real state.  So now, you will see how well your controller performs and de-tune your controller accordingly.

1. Replace `QuadController.cpp` with the controller you wrote in the last project.

2. Replace `QuadControlParams.txt` with the control parameters you came up with in the last project.

3. Run scenario `11_GPSUpdate`. If your controller crashes immediately do not panic. Flying from an estimated state (even with ideal sensors) is very different from flying with ideal pose. You may need to de-tune your controller. Decrease the position and velocity gains (we’ve seen about 30% detuning being effective) to stabilize it.  Your goal is to once again complete the entire simulation cycle with an estimated position error of < 1m.

**Hint: you may find it easiest to do your de-tuning as a 2 step process by reverting to ideal sensors and de-tuning under those conditions first.**

***Success criteria:*** *Your objective is to complete the entire simulation cycle with estimated position error of < 1m.*


## Tips and Tricks ##

 - When it comes to transposing matrices, `.transposeInPlace()` is the function you want to use to transpose a matrix

 - The [Estimation for Quadrotors](https://www.overleaf.com/read/vymfngphcccj) document contains a helpful mathematical breakdown of the core elements on your estimator

## Submission ##

For this project, you will need to submit:

 - a completed estimator that meets the performance criteria for each of the steps by submitting:
   - `QuadEstimatorEKF.cpp`
   - `config/QuadEstimatorEKF.txt`

 - a re-tuned controller that, in conjunction with your tuned estimator, is capable of meeting the criteria laid out in Step 6 by submitting:
   - `QuadController.cpp`
   - `config/QuadControlParams.txt`

 - a write up addressing all the points of the rubric

## Authors ##

Thanks to Fotokite for the initial development of the project code and simulator.