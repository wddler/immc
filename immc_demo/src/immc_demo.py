#!/usr/bin/env python

from time import sleep
import rospy
import actionlib
import tf
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from immc_msgs.srv import SubmitOrder, PendingOrders
import sys
import moveit_commander
import moveit_msgs.msg
from gazebo_msgs.msg import ContactsState
from gazebo_ros_link_attacher.srv import Attach


pick_up_location = (7.725, -8.355)
drop_location = (-1, -4.65)

def movebase_client(x_coord, y_coord):

    client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
    client.wait_for_server()

    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = x_coord
    goal.target_pose.pose.position.y = y_coord
    quat = tf.transformations.quaternion_from_euler(0,0,3.14159)
    goal.target_pose.pose.orientation.x = quat[0]
    goal.target_pose.pose.orientation.y = quat[1]
    goal.target_pose.pose.orientation.z = quat[2]
    goal.target_pose.pose.orientation.w = quat[3]

    client.send_goal(goal)
    wait = client.wait_for_result()
    if not wait:
        rospy.logerr("Action server not available!")
        rospy.signal_shutdown("Action server not available!")
    else:
        return client.get_result()

def attach_cube_to_gripper(contact):
    rospy.wait_for_service('/link_attacher_node/attach')
    attach = rospy.ServiceProxy('/link_attacher_node/attach', Attach)

    result = attach.call(contact.collision1_name.split("::")[0], contact.collision1_name.split("::")[1], contact.collision2_name.split("::")[0], contact.collision2_name.split("::")[1])
    
    return result
        
def get_contacts(contacts_message):
    if (len(contacts_message.states) != 0):
        if ('gripper_link' or 'gripper_link_sub' in contacts_message.states[0].collision1_name) :
            rospy.loginfo("Collision detected with %s." % contacts_message.states[0].collision2_name.split("::")[0])
            attach_cube_to_gripper(contacts_message.states[0])
        elif ('gripper_link' or 'gripper_link_sub' in contacts_message.states[0].collision2_name) :
            rospy.loginfo("Collision detected with %s." % contacts_message.states[0].collision1_name.split("::")[0])
            attach_cube_to_gripper(contacts_message.states[0])
        else:
            rospy.loginfo("Unknown collision")

def move_arm(target_position):
    robot1_group = moveit_commander.MoveGroupCommander("arm")
    robot1_client = actionlib.SimpleActionClient(
        'execute_trajectory',
        moveit_msgs.msg.ExecuteTrajectoryAction)
    robot1_client.wait_for_server()
    rospy.loginfo('Execute Trajectory server is available for arm')
    robot1_group.set_named_target(target_position)
    _, plan, _, _ = robot1_group.plan()
    robot1_goal = moveit_msgs.msg.ExecuteTrajectoryGoal()
    robot1_goal.trajectory = plan
    robot1_client.send_goal(robot1_goal)
    robot1_client.wait_for_result()

def move_gripper(target_position):
    gripper_group = moveit_commander.MoveGroupCommander("gripper")
    gripper_client= actionlib.SimpleActionClient(
        'execute_trajectory',
        moveit_msgs.msg.ExecuteTrajectoryAction)
    gripper_client.wait_for_server()
    rospy.loginfo('Execute Trajectory server is available for gripper')
    gripper_group.set_named_target(target_position)
    _, plan, _, _ = gripper_group.plan()
    gripper_goal = moveit_msgs.msg.ExecuteTrajectoryGoal()
    gripper_goal.trajectory = plan
    gripper_client.send_goal(gripper_goal)
    gripper_client.wait_for_result()

def pick_object():
    moveit_commander.roscpp_initialize(sys.argv)
    #open gripper
    move_gripper("full_open")

    #move the arm to the pre_grasp position
    move_arm("pre_grasp")
    
    #close the gripper (grasp the object)
    move_gripper("close")
    
    #fix grasping (attach cube to the gripper)
    try: 
        contact_msg = rospy.wait_for_message('/gripper_contacts', ContactsState)
        get_contacts(contact_msg)
    except:
        rospy.logwarn("grasp fix failed")

    #move the arm to the transportation position
    move_arm("transportation")

def drop_object():
    move_arm("pre_release")

    detach = rospy.ServiceProxy('/link_attacher_node/detach', Attach)
    res = detach.call('green_cube0', 'base_link', 'robot', 'gripper_link')
    res = detach.call('green_cube0', 'base_link', 'robot', 'gripper_link_sub')
    
    move_gripper("full_open")

    move_arm("home")
    
    # When finished shut down moveit_commander.
    moveit_commander.roscpp_shutdown()

if __name__ == '__main__':
    try:
        rospy.loginfo("Demo started")
        rospy.init_node('movebase_client_py')
        
        rospy.sleep(1)

        rospy.wait_for_service('/pending_orders')
        pending_orders = rospy.ServiceProxy('/pending_orders', PendingOrders)
        fulfill_order = pending_orders()
        rospy.loginfo(fulfill_order.pending_orders)
        
        movebase_client(pick_up_location[0], pick_up_location[1])
        
        pick_object()
        
        movebase_client(drop_location[0], drop_location[1])
        
        drop_object()

        rospy.wait_for_service("/submit_order")
        submit_order = rospy.ServiceProxy("/submit_order", SubmitOrder)
        submit_order(2)
        rospy.loginfo("Mobile pick and place demo pipeline finished")
        
    except rospy.ROSInterruptException:
        rospy.loginfo("Mobile pick and place demo pipeline went wrong")