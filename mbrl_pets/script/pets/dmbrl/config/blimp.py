from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import numpy as np
import tensorflow.compat.v1 as tf ###
tf.disable_eager_execution() ###

from dotmap import DotMap
# import gym
# import ipdb;ipdb.set_trace()

import sys

from dmbrl.misc.DotmapUtils import get_required_argument
from dmbrl.modeling.layers import FC

class BlimpConfigModule:
    ENV_NAME = "blimp"
    SLEEP_RATE = 2 # 1 2 5 10
    TASK_TIME = 30 #(sec)
    PLAN_HOR = 10 # 5 7 10 15 20
    USE_MPC = False # use mpc assigned way point
    Action_Choice = [1,1,1,1,1,1,1,1] # action number
    NTRAIN_ITERS = 1000 # 500, 1000, 2000

    TASK_HORIZON = TASK_TIME * SLEEP_RATE 
    NROLLOUTS_PER_ITER = 1
    MODEL_IN, MODEL_OUT = 23, 15 

    def __init__(self):
        from dmbrl.env.blimp import BlimpEnv

        self.ENV = BlimpEnv(self.SLEEP_RATE, self.TASK_TIME ,self.USE_MPC, self.Action_Choice)
        cfg = tf.ConfigProto()
        cfg.gpu_options.allow_growth = True
        self.SESS = tf.Session(config=cfg)
        self.NN_TRAIN_CFG = {"epochs": 5}
        self.OPT_CFG = {
            "Random": {
                "popsize": 2500
            },
            "CEM": {
                "popsize": 500,
                "num_elites": 50,
                "max_iters": 5,
                "alpha": 0.1
            }
        }

    """
    .obs_preproc (func): (optional) A function which modifies observations (in a 2D matrix)
        before they are passed into the model. Defaults to lambda obs: obs.
        Note: Must be able to process both NumPy and Tensorflow arrays.
    .obs_postproc (func): (optional) A function which returns vectors calculated from
        the previous observations and model predictions, which will then be passed into
        the provided cost function on observations. Defaults to lambda obs, model_out: model_out.
        Note: Must be able to process both NumPy and Tensorflow arrays.
    .obs_postproc2 (func): (optional) A function which takes the vectors returned by
        obs_postproc and (possibly) modifies it into the predicted observations for the
        next time step. Defaults to lambda obs: obs.
        Note: Must be able to process both NumPy and Tensorflow arrays.
    .targ_proc (func): (optional) A function which takes current observations and next
        observations and returns the array of targets (so that the model learns the mapping
        obs -> targ_proc(obs, next_obs)). Defaults to lambda obs, next_obs: next_obs.
        Note: Only needs to process NumPy arrays.3
    """
    @staticmethod
    def obs_postproc(obs, pred):
        return obs + pred

    @staticmethod
    def targ_proc(obs, next_obs):
        return next_obs - obs

    """
    .obs_cost_fn (func): A function which computes the cost of every observation
        in a 2D matrix.
        Note: Must be able to process both NumPy and Tensorflow arrays.
    .ac_cost_fn (func): A function which computes the cost of every action
        in a 2D matrix.
    """
    @staticmethod
    def obs_cost_fn(obs):
        '''
        state
        0:2 relative_angle
        3:5 angular velocity
        6:8 relative_position
        9:11 velocity
        12:14 acceleration
        '''
        w_alt, w_dist, w_ang = 0.0, 0.8, 0.1

        # define altitude cost
        alt_cost = tf.abs(obs[:, 8])
        alt_cost = tf.math.tanh(0.05*alt_cost, name=None) #value~-0.3

        # define distance cost, temporarily disabled 
        dist_cost = obs[:, 6:9]
        dist_cost = tf.norm(dist_cost, ord='euclidean', axis=1, name=None)
        dist_cost = tf.math.tanh(0.05*dist_cost, name=None) #value~-0.3

        # define angle cost 
        ang_cost = obs[:, 0:3]
        ang_cost = tf.math.reduce_mean(tf.abs(ang_cost), axis=1)
        ang_cost = tf.math.tanh(ang_cost, name=None) #value~-0.8

        #plotter
        # dist_cost = tf.Print(dist_cost,[dist_cost],message="This is dist_cost: ")

        return w_alt*alt_cost + w_dist*dist_cost + w_ang*ang_cost

    @staticmethod
    def ac_cost_fn(acs):
        '''
        0: left motor 
        1: right motor
        2: back motor
        3: servo
        4: top fin
        5: bottom fin 
        6: left fin
        7: right fin
        '''
        w_act = 0.1
      
        # define action cost
        act_cost = tf.norm(acs, ord='euclidean', axis=1, name=None) 
        act_cost = tf.math.tanh(0.2*act_cost, name=None)

        return w_act*act_cost

    def nn_constructor(self, model_init_cfg):
        model = get_required_argument(model_init_cfg, "model_class", "Must provide model class")(DotMap(
            name="model", num_networks=get_required_argument(model_init_cfg, "num_nets", "Must provide ensemble size"),
            sess=self.SESS, load_model=model_init_cfg.get("load_model", False),
            model_dir=model_init_cfg.get("model_dir", None)
        ))
        if not model_init_cfg.get("load_model", False):
            model.add(FC(250, input_dim=self.MODEL_IN, activation="swish", weight_decay=0.000025))
            model.add(FC(250, activation="swish", weight_decay=0.00005))
            model.add(FC(250, activation="swish", weight_decay=0.000075))
            model.add(FC(self.MODEL_OUT, weight_decay=0.0001))
        model.finalize(tf.train.AdamOptimizer, {"learning_rate": 0.001})
        return model

CONFIG_MODULE = BlimpConfigModule
