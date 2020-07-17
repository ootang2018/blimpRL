#!/usr/bin/env python
import time
import numpy as np
import rospy

from std_msgs.msg import Header
from geometry_msgs.msg import PoseArray, Pose
from nav_msgs.msg import Odometry
from blimp import BlimpEnv
from rotor_controller import RotorController
from plane_controller import LongitudinalAutoPilot
from plane_controller import LateralAutoPilot
from mixer import BlimpMixer
from myTF import MyTF

EPISODE_LENGTH = 30000#30*100

class ControlsFlyer():

    def __init__(self, SLEEP_RATE = 2, TASK_TIME= 30, USE_MPC=False, Action_Choice= np.array([1,1,1,1,1,1,1,1])):
        self.env = BlimpEnv(SLEEP_RATE, TASK_TIME, USE_MPC, Action_Choice)

        self.rotor_controller = RotorController()
        self.longitudinal_controller = LongitudinalAutoPilot()
        self.lateral_controller = LateralAutoPilot()
        self.mixer = BlimpMixer()

        self.cnt=0

        self.position_trajectory = []
        self.yaw_trajectory = []
        self.time_trajectory = []

        self.local_position = np.array([0.0,0.0,0.0])
        self.local_velocity = np.array([0.0,0.0,0.0])
        self.attitude = np.array([0.0,0.0,0.0])
        self.body_rate = np.array([0.0,0.0,0.0])

        self.rotor_position_target = np.array([0.0,0.0,0.0])
        self.rotor_velocity_target = np.array([0.0,0.0,0.0])
        self.rotor_acceleration_target = np.array([0.0,0.0,0.0])
        self.rotor_attitude_target = np.array([0.0,0.0,0.0])
        self.rotor_body_rate_target = np.array([0.0,0.0,0.0])

        self.rotor_thrust_cmd = 0.0
        self.cmd_rotor = np.array([0.0,0.0,0.0,0.0])
        self.cmd_plane = np.array([0.0,0.0,0.0,0.0])

        self.dt = 0.01

    ########################
    #   rotor controller   #
    ########################
    def rotor_position_controller(self):

        acceleration_cmd = self.rotor_controller.lateral_position_control(
                self.rotor_position_target[0:2],
                self.rotor_velocity_target[0:2],
                self.local_position[0:2],
                self.local_velocity[0:2])
        self.rotor_acceleration_target = np.array([acceleration_cmd[0],
                                                   acceleration_cmd[1],
                                                   0.0])

    def rotor_attitude_controller(self):
        self.rotor_thrust_cmd = self.rotor_controller.altitude_control(
                -self.rotor_position_target[2],
                -self.rotor_velocity_target[2],
                -self.local_position[2],
                -self.local_velocity[2],
                self.attitude,
                9.81)
        roll_pitch_rate_cmd = self.rotor_controller.roll_pitch_controller(
                self.rotor_acceleration_target[0:2],
                self.attitude,
                self.rotor_thrust_cmd)
        yawrate_cmd = self.rotor_controller.yaw_control(
                self.rotor_attitude_target[2],
                self.attitude[2],
                self.body_rate[2])
        self.rotor_body_rate_target = np.array(
                [roll_pitch_rate_cmd[0], roll_pitch_rate_cmd[1], yawrate_cmd])

    def rotor_bodyrate_controller(self):
        moment_cmd = self.rotor_controller.body_rate_control(
                self.rotor_body_rate_target,
                self.body_rate)
        self.cmd_rotor = [moment_cmd[0],
                        moment_cmd[1],
                        moment_cmd[2],
                        self.rotor_thrust_cmd]

    def rotor_control_update(self):
        self.rotor_position_controller()
        self.rotor_attitude_controller()
        self.rotor_bodyrate_controller()

    ########################
    #   plane controller   #
    ########################
    def plane_altitude_controller(self):
        pitch_cmd = self.longitudinal_controller.altitude_loop(self.local_position[2], -2.5, self.dt) 
        q_cmd = self.longitudinal_controller.pitch_loop(self.attitude[1], self.body_rate[1], pitch_cmd)
        self.cmd_plane = [0, q_cmd, 0, 35]

    # def plane_speed_controller(self):
        # throttle_cmd = self.longitudinal_controller.airspeed_loop(airspeed, airspeed_cmd, self.dt)

    def plane_control_update(self):
        # self.plane_speed_controller() 
        self.plane_altitude_controller()


    ########################
    #   control interface  #
    ########################
    def control_update(self):
        self.rotor_control_update()
        self.plane_control_update()

    def actuation_update(self):
        self.action = self.mixer.mix(self.cmd_rotor, self.cmd_plane)

    def unwrap_obs(self, obs):
        angle = obs[0:3]
        angular_velocity = obs[3:6]
        position = obs[6:9]
        velocity = obs[9:12]
        linear_acceleration = obs[12:15]
        target_angle = obs[15:18]
        target_position = obs[18:21]

        self.local_position = np.array(position)
        self.rotor_position_target = np.array(target_position)
        self.local_velocity = np.array(velocity)
        self.attitude = np.array(angle)
        self.rotor_attitude_target = np.array(target_angle)
        self.body_rate = np.array(angular_velocity)

    def start(self):
        time_step=0
        total_reward=0
        obs = self.env.reset()
        self.unwrap_obs(obs)

        while time_step < EPISODE_LENGTH:
            time_step+=1
            self.control_update()
            self.actuation_update()
            obs, reward, done, _ = self.env.step(self.action)
            self.unwrap_obs(obs)

            if time_step%10 == 0:
                total_reward+=reward
                print("----------------------------")
                print("action = ", self.action)
                print("p_cmd = %2.3f, q_cmd=%2.3f, r_cmd=%2.3f, throttle_cmd=%2.3f" % (self.cmd_plane[0],self.cmd_plane[1],self.cmd_plane[2],self.cmd_plane[3]))
                # print("target poisition = ", self.rotor_position_target)
                print("(x,y,z) = ", self.local_position)
                print("(phi,the,psi) = ", self.attitude)

        obs = self.env.reset()
        print("total reward = ", total_reward)

if __name__ == "__main__":
    SLEEP_RATE = 100
    TASK_TIME= 30
    USE_MPC= True
    Action_Choice= np.array([1,1,1,1,0,0,0,0])
    drone = ControlsFlyer(SLEEP_RATE, TASK_TIME, USE_MPC, Action_Choice)

    time.sleep(2)
    drone.start()
