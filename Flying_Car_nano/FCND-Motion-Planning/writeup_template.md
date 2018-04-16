## Project: 3D Motion Planning
![Quad Image](./misc/enroute.png)

---


# Required Steps for a Passing Submission:
1. Load the 2.5D map in the colliders.csv file describing the environment.
2. Discretize the environment into a grid or graph representation.
3. Define the start and goal locations.
4. Perform a search using A* or other search algorithm.
5. Use a collinearity test or ray tracing method (like Bresenham) to remove unnecessary waypoints.
6. Return waypoints in local ECEF coordinates (format for `self.all_waypoints` is [N, E, altitude, heading], where the drone’s start location corresponds to [0, 0, 0, 0].
7. Write it up.
8. Congratulations!  Your Done!

## [Rubric](https://review.udacity.com/#!/rubrics/1534/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it! Below I describe how I addressed each rubric point and where in my code each point is handled.

And here's a lovely image of my results (ok this image has nothing to do with it, but it's a nice example of how to include images in your writeup!)
![Top Down View](./misc/high_up.png)

Here's | A | Snappy | Table
--- | --- | --- | ---
1 | `highlight` | **bold** | 7.41
2 | a | b | c
3 | *italic* | text | 403
4 | 2 | 3 | abcd



### Explain the Starter Code

#### 1. Explain the functionality of what's provided in `motion_planning.py` and `planning_utils.py`
**MOTION_PLANNING.PY**
Motion Planning is a similar to backyard flyie, except that now there is a new state called PLANNING, this state is called
after ARMING and before TAKEOFF state and it serves as a state to calculate the complete route before taking off 

There is also a new fuction that sends the waypoints for visualization to the simulator called send_waypoints()

Function plan_path() is the one responsible to to plan the entire trip for the drone

**PLANNING_UTILS.PY**
This module contains basic functions to help us plan the mission, this saves us from having to implement all common functions for planning a flight, now we can just import functions from planning_utils.py
I added some other functions to this module, I added prune_path, find_start_goal, a_star and get3DPath

### Implementing Your Path Planning Algorithm
I tried 3 different of methods: 
**motion_planner.py:** This is the original from the excercise that is used in motion_planning.py, it was memory intensive so I discarded it quickly, it was also not safe as it will find a path very close to buildings.
**motion_planner2.py:** This method was using probabilistic method, I created the sampler class and I found this method to be complicated, in order to be able to get a path I needed to have aroound 300 sample points and it will not always find a path, it was also very memory intensive and slow
**motion_planner3.py:** This method I used medial-axis. This provided me a very safe path and very quick planning method. Knowing I was on the safest path it allowed me to relax the tolerances on the prune_path function and also between waypoints, the drone is able to travel very fast between 2 places on the grid.
To be able to go from anywhere to anywhere on the grid I created a replanning function that in case a path is not possible then just add 20 meters to the cruise altitude, find a new skeleton and try a_star again, this enabled me to make a 3D planning function that will always work, the drone is able to land on the roof of buildings, even in Hollow buildings.
Something I really Appreciated of medial axis is that it creates safe airways at different altitudes, similar to how aircraft fly between cities int he world.
I tried to implement a function in planning utils to see if I could prune the path even more by checking if I can go direct-to from waypoint i to waypoint i+2 then pop waypoint i+1, it seemed to work sometimes, but I had issues with the function to check if a line crosses a polygon, sometimes it would just let me crash into buildings.

At the end, my motion_planner3.py is the best method, quick, efficient and safe.

here are some snaopshots of plans going from all places in the map

![Top Down View](./misc/Capture1.png)
![Top Down View](./misc/Capture2.png)
![Top Down View](./misc/Capture3.png)
![Top Down View](./misc/Capture4.png)
![Top Down View](./misc/Capture5.png)
![Top Down View](./misc/Capture6.png)



#### 1. Set your global home position
Here students should read the first line of the csv file, extract lat0 and lon0 as floating point values and use the self.set_home_position() method to set global home. Explain briefly how you accomplished this in your code.


And here is a lovely picture of our downtown San Francisco environment from above!
![Map of SF](./misc/map.png)

#### 2. Set your current local position
Here as long as you successfully determine your local position relative to global home you'll be all set. Explain briefly how you accomplished this in your code.


Meanwhile, here's a picture of me flying through the trees!
![Forest Flying](./misc/in_the_trees.png)

#### 3. Set grid start position from local position
This is another step in adding flexibility to the start location. As long as it works you're good to go!

#### 4. Set grid goal position from geodetic coords
This step is to add flexibility to the desired goal location. Should be able to choose any (lat, lon) within the map and have it rendered to a goal location on the grid.

#### 5. Modify A* to include diagonal motion (or replace A* altogether)
Minimal requirement here is to modify the code in planning_utils() to update the A* implementation to include diagonal motions on the grid that have a cost of sqrt(2), but more creative solutions are welcome. Explain the code you used to accomplish this step.

#### 6. Cull waypoints 
For this step you can use a collinearity test or ray tracing method like Bresenham. The idea is simply to prune your path of unnecessary waypoints. Explain the code you used to accomplish this step.



### Execute the flight
#### 1. Does it work?
It works!

### Double check that you've met specifications for each of the [rubric](https://review.udacity.com/#!/rubrics/1534/view) points.
  
# Extra Challenges: Real World Planning

For an extra challenge, consider implementing some of the techniques described in the "Real World Planning" lesson. You could try implementing a vehicle model to take dynamic constraints into account, or implement a replanning method to invoke if you get off course or encounter unexpected obstacles.


