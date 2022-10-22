#!/usr/bin/env python

from immc_msgs.srv import PendingOrders, PendingOrdersResponse, SubmitOrder, SubmitOrderResponse
import rospy
from immc_msgs.msg import Order
from geometry_msgs.msg import Point
from gazebo_msgs.srv import DeleteModel, GetModelState, GetWorldProperties

TOLERANCE = 1 #tolerance for the drop location

BL = [-1.5, -5]
TR = [-0.3, -4.3]

order_location = Point(x=-1,y=-4.67,z=0.0)

order_1 = Order()
order_1.id = 1
order_1.desired_location = order_location
order_1.objects = ['red_cube', 'blue_cube']

order_2 = Order()
order_2.id = 2
order_2.desired_location = order_location
order_2.objects = ['green_cube']

order_3 = Order()
order_3.id = 3
order_3.desired_location = order_location
order_3.objects = ['green_cube', 'red_cube', 'blue_cube']

orders = [order_1, order_2, order_3]

def handle_pending_orders(request):
    response = PendingOrdersResponse()
    response.pending_orders = [order_1, order_2, order_3]
    return response

def handle_order_submission(order):
    for item in orders:
        if item.id == order.order_id:
            rospy.wait_for_service('/gazebo/get_world_properties')
            try:
                get_world_properties_proxy = rospy.ServiceProxy('/gazebo/get_world_properties', GetWorldProperties)
                world_properties = get_world_properties_proxy()
            except rospy.ServiceException as e:
                print("Service call failed: %s"%e)
            pool_of_objects = list(filter(lambda k: 'cube' in k, world_properties.model_names))
            validated_objects = 0
            models_to_delete = []
            for object_to_validate in item.objects:
                validated = False
                for obj in pool_of_objects:
                    if object_to_validate in obj and validated==False:
                        rospy.wait_for_service('/gazebo/get_model_state')
                        try:
                            get_status_prox = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
                            current_pose = get_status_prox(obj, 'world')
                        except rospy.ServiceException as e:
                            print("Service call failed: %s"%e)
                        result = check_object_from_order(BL, TR, [current_pose.pose.position.x, current_pose.pose.position.y] )
                        if result==True:
                            validated_objects = validated_objects+1
                            models_to_delete.append(obj)
                            validated = True
                            
            if validated_objects >= len(item.objects):
                del_model_prox = rospy.ServiceProxy('gazebo/delete_model', DeleteModel)
                for model in models_to_delete:
                    del_model_prox(model)
                del orders[orders.index(item)]
                rospy.loginfo("order {} accepted".format(order.order_id))
                if len(orders) == 0:
                    rospy.loginfo("All orders fulfilled. Congratulations! You have reached the end of the Virtual Micro Challenge.")
                return SubmitOrderResponse(True)
            else:
                rospy.logerr("Order incomplete. Not enough objects or not right location")
                return SubmitOrderResponse(False)

    rospy.logerr("no pending order with id {}".format(order.order_id))    
    
    return SubmitOrderResponse(False)

def check_object_from_order(bottom_left: list, top_right: list, object_position: list):
    if abs(order_location.x-object_position[0]) < TOLERANCE and abs(order_location.y-object_position[1]) < TOLERANCE:
        return True
    
    else:
        return False

def pending_orders_server():
    rospy.init_node('order_manager_node')
    s = rospy.Service('pending_orders', PendingOrders, handle_pending_orders)
    rospy.loginfo("pending_orders_server is ready")
    print("enter handle_order_submission")
    s1 = rospy.Service('submit_order', SubmitOrder, handle_order_submission)

    rospy.loginfo("submit_order is ready")

    rospy.spin()

if __name__ == "__main__":
    pending_orders_server()