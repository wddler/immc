# immc_demo

Demo pipeline of navigation and manipulation capabilities of the mobile manipulator.

## How to run demo

Specify TurtleBot model (in each temrinal where you have error _RLException: Invalid arg tag: environment variable 'TURTLEBOT3_MODEL' is not set._)

`$ export TURTLEBOT3_MODEL=waffle_pi`

Launch pilotfactory world with turtlebot3_manipulator, MoveIt and Navigation if you haven't done it yet.

`$ roslaunch immc_bringup immc_bringup_factory.launch`

Run demo via rosrun or directly from the directory

`$ rosrun immc_demo immc_demo.py`

[![IMMC Demo Video](https://img.youtube.com/vi/YSt4utC4-y8/0.jpg)](https://youtu.be/YSt4utC4-y8)
