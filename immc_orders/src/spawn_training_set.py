#!/usr/bin/env python

from gazebo_msgs.srv import SpawnModel
import rospy, rospkg, tf
from geometry_msgs.msg import Quaternion, Pose, Point

rospy.init_node('spawn_objects',log_level=rospy.INFO)
rospy.wait_for_service('/gazebo/spawn_sdf_model')
spawn_model_client = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)

rospack = rospkg.RosPack()

#spawns a single object
def spawn_object(object_name, position):
    object_path = rospack.get_path('immc_orders')+"/urdf/"+object_name[:-1]+".urdf"
    quat = tf.transformations.quaternion_from_euler(0,0,0)
    pose = Pose(position, Quaternion(quat[0],quat[1],quat[2],quat[3]))
    spawn_model_client(model_name=object_name, model_xml=open(object_path, 'r').read(), initial_pose=pose, reference_frame='world')

#spawns 5 cubes on the floor in a row (for each of three colors)
def spawn_row_cubes(cube_color):    
    if cube_color == "red":
        position_default = Point(x=7.5,y=-7.85,z=0.9)
    elif cube_color == "green":
        position_default = Point(x=7.5,y=-8.35,z=0.9) 
    elif cube_color == "blue":
        position_default = Point(x=7.5, y=-8.85, z=0.9)

    offset_x = 0.0
    for i in range(5): 
        position = Point(x=position_default.x-offset_x, y = position_default.y, z = position_default.z)
        spawn_object(cube_color+"_cube"+str(i), position)
        i = i+1
        offset_x = offset_x+0.1

cubes = ["red", "green", "blue"]
for cube in cubes:
    spawn_row_cubes(cube)