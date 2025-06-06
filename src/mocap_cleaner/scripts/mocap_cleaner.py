#!/usr/bin/env python2

import rospy
from geometry_msgs.msg import PoseStamped, Pose
from visualization_msgs.msg import Marker
from  tf.transformations import quaternion_multiply, quaternion_about_axis
import math

from matplotlib import colors

FREQUENCY = 10

class MocapCleanerNode:
    """ Node to clean up the mocap data by removing the first and last frames. """
    def __init__(self):
        # Initialize the node
        rospy.init_node("mocap_cleaner", anonymous=False)
        self.name = rospy.get_name().split("/")[-1]

        # Subscriber to the mocap data
        subscribe_topic = rospy.get_param("~subscribe_topic", "/UNSPECIFIED_subscribe_topic")
        self.mocap_subscriber = rospy.Subscriber(subscribe_topic, PoseStamped, self.mocap_callback)
        
        publish_topic = rospy.get_param("~publish_topic", "/UNSPECIFIED_publish_topic")
        # Publisher for the cleaned mocap data
        self.cleaned_mocap_publisher = rospy.Publisher(publish_topic, Marker, queue_size=10)
        self.color = rospy.get_param("~color", default="red")

        # self.marker = Marker()

    def mocap_callback(self, msg):
        
        # remove z coordinate
        msg.pose.position.x = msg.pose.position.x * 1000.
        msg.pose.position.y = msg.pose.position.z * -1000.
        msg.pose.position.z = 0.0

        # remove all rotation except yaw
        quaternion = [msg.pose.orientation.x, msg.pose.orientation.z, msg.pose.orientation.y, msg.pose.orientation.w]
        # rotation = quaternion_about_axis(math.pi, (0, 0, 1))
        # quaternion = quaternion_multiply(quaternion, rotation)
        msg.pose.orientation.x = quaternion[0]
        msg.pose.orientation.y = quaternion[1]
        msg.pose.orientation.z = quaternion[2]
        msg.pose.orientation.w = quaternion[3]

        marker = Marker()
        marker.header.frame_id = "base_link"
        marker.header.stamp = rospy.Time.now()
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        marker.pose = msg.pose
        marker.scale.x = 200
        marker.scale.y = 50
        marker.scale.z = 50
        color = colors.to_rgba(self.color)
        marker.color.r = color[0]
        marker.color.g = color[1]
        marker.color.b = color[2]
        marker.color.a = color[3]

        self.marker = marker

        # Publish the cleaned mocap data
        # self.cleaned_mocap_publisher.publish(marker)
        # rospy.loginfo("Published cleaned mocap data: %s", msg)

if __name__ == "__main__":
    try:
        node = MocapCleanerNode()
        # rospy.spin()
        while not rospy.is_shutdown():
            node.cleaned_mocap_publisher.publish(node.marker)
            rospy.sleep(1.0 / FREQUENCY)
    except rospy.ROSInterruptException:
        pass

