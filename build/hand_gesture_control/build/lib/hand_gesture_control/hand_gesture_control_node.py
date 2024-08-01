#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from roboflowoak import RoboflowOak
import cv2
import numpy as np

class HandGestureControlNode(Node):
    def __init__(self):
        super().__init__('hand_gesture_control')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10Hz
        
        self.rf = RoboflowOak(model="hand-gestures-2rou9", confidence=0.05, overlap=0.5,
                              version="1", api_key="qWsDQI59Ym1TiwZTt1sQ", rgb=True,
                              depth=True, device=None, blocking=True)
        
        self.twist_msg = Twist()
        self.is_moving = False

    def timer_callback(self):
        result, frame, raw_frame, depth = self.rf.detect()
        predictions = result["predictions"]

        for prediction in predictions:
            if prediction.class_name == 'fist' and not self.is_moving:
                self.start_moving()
            elif prediction.class_name == 'hand' and self.is_moving:
                self.stop_moving()

        # Display the frame (optional, can be commented out if running headless)
        cv2.imshow("frame", frame)
        cv2.waitKey(1)

    def start_moving(self):
        self.twist_msg.linear.x = 0.5  # Adjust speed as needed
        self.publisher.publish(self.twist_msg)
        self.is_moving = True
        self.get_logger().info('Starting to move')

    def stop_moving(self):
        self.twist_msg.linear.x = 0.0
        self.publisher.publish(self.twist_msg)
        self.is_moving = False
        self.get_logger().info('Stopping')

def main(args=None):
    rclpy.init(args=args)
    node = HandGestureControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
