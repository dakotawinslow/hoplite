#!/usr/bin/env python2

import rospy
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist, Quaternion, Pose, PoseStamped
from visualization_msgs.msg import Marker
from tf.transformations import quaternion_from_euler
from matplotlib import colors
import math

FREQUENCY = 10

class control_point(object):
  def __init__(self):
    rospy.init_node('joystick_controller', anonymous=False)
    self.x = 0
    self.y = 0
    self.theta = 0
    self.x_vel = 0
    self.y_vel = 0
    self.theta_vel = 0
    
    self.joy_subscriber = rospy.Subscriber('/joy', Joy, self.joy_callback)
    self.marker_publisher = rospy.Publisher('/joystick_controller/marker', Marker, queue_size=10)
    self.twist_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    self.last_update_time = rospy.Time.now()
    
  def joy_callback(self, msg):
    """ Callback function for the joystick input. It receives the joystick input and updates the control point. """
    self.x_vel = msg.axes[0] * -500
    self.y_vel = msg.axes[1] * 500
    self.theta_vel = msg.axes[2] * math.pi
    # self.update_control_point()
    
  def update_control_point(self):
    """ Update the control point based on the joystick input. """
    delta_time = rospy.Time.now() - self.last_update_time
    self.last_update_time = rospy.Time.now()
    if delta_time.to_sec() == 0:
      return
    self.x += self.x_vel * delta_time.to_sec()
    self.y += self.y_vel * delta_time.to_sec()
    self.theta += self.theta_vel * delta_time.to_sec()
    self.theta = self.theta % (2 * math.pi)

  def publish_marker(self):
    marker = Marker()
    marker.header.frame_id = "base_link"
    marker.header.stamp = rospy.Time.now()
    marker.type = Marker.ARROW
    marker.action = Marker.ADD
    marker.pose.position.x = self.x
    marker.pose.position.y = self.y
    marker.pose.position.z = 0
    quaternion = quaternion_from_euler(0, 0, self.theta)
    marker.pose.orientation.x = quaternion[0]
    marker.pose.orientation.y = quaternion[1]
    marker.pose.orientation.z = quaternion[2]
    marker.pose.orientation.w = quaternion[3]
    marker.scale.x = 150
    marker.scale.y = 15
    marker.scale.z = 15
    color = colors.to_rgb("limegreen")
    marker.color.r = color[0]
    marker.color.g = color[1]
    marker.color.b = color[2]
    marker.color.a = 1.0
    self.marker_publisher.publish(marker)

  def publish_twist(self):
    twist = Twist()
    twist.linear.x = self.x_vel
    twist.linear.y = self.y_vel
    twist.angular.z = self.theta_vel
    self.twist_publisher.publish(twist)

if __name__ == '__main__':
  try:
    controller = control_point()
    # rospy.spin()
    while not rospy.is_shutdown():
      controller.update_control_point()
      controller.publish_marker()
      controller.publish_twist()
      rospy.sleep(1.0 / FREQUENCY)
    # direct_control = rospy.get_param("~direct_control")
  except rospy.ROSInterruptException:
    pass
