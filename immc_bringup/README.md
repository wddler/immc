# immc_bringup

This package contains the _launch/immc_bringup_factory.launch_ which is the starting point of the task within the Virtual Micro Challenge.

This launch file will:

- Run the Gazebo simulator with the factory world.
- Spawn the mobile manipulator at the origin of the factory world.
- Run the move_group interface to control the arm and the gripper.
- Run the navigation stack to control the mobile base.
- Provide the map of the factory world to the map server for autonomous navigation.
- Spawn objects for manipulation at the input are (stock).
- Run order manager node.

To start:

1. Source you workspace directory
2. Specify Turtlebot3 robot model `$ export TURTLEBOT3_MODEL=waffle_pi`
3. Launch the file `$ roslaunch immc_bringup immc_bringup_factory.launch`
