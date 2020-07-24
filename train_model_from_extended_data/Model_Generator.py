import os
import scipy
from scipy.io import loadmat, savemat
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class ModelGenerator:

    def __init__(self, params):
        self.model = get_required_argument(
            params.prop_cfg.model_init_cfg, "model_constructor", "Must provide a model constructor."
        )(params.prop_cfg.model_init_cfg)

        self.model_train_cfg = params.prop_cfg.get("model_train_cfg", {})
        pass


    def read(self, dir):
        ''' read data from directories, concat them, and output each inventory
        Arguments:
            dir: target directory

        Returns:
            observations: A np.ndarray of observations
            actions: A np.ndarray of actions
            rewards: A np.ndarray of rewards
        '''
        observations = np.array([])
        actions = np.array([])
        returns = np.array([])
        rewards = np.array([])
        data = []
        for subdir in os.listdir(dir):
            data = loadmat(os.path.join(dir, subdir, "logs.mat"))
            observations = np.vstack([data['observations'], observations]) if observations.size else data['observations']
            actions = np.vstack([data['actions'], actions]) if actions.size else data['actions']
            returns = np.vstack([data['returns'], returns]) if returns.size else data['returns']
            rewards = np.vstack([data['rewards'], rewards]) if rewards.size else data['rewards']

        return observations, actions, rewards

    def concat(self, obs_data, acs_data, rew_data):
        ''' concatenate data
        Arguments:
            obs: A list of observation matrices, array([episode, timestep, values])
            acs: A list of action matrices, actions in rows.
            rew: A list of reward arrays.

        Returns: array of train_in, train_targs.
        '''
        new_train_in, new_train_targs = [], []
        train_in, train_targs = [], []
        for i in range(len(obs_data)): # unwarp epsisode
            for obs, acs in zip(obs_data[i], acs_data[i]): # unwarp timestep
                new_train_in.append(np.concatenate([obs[:-1], acs], axis=-1))
                new_train_targs.append(self.targ_proc(obs[:-1], obs[1:]))
            train_in = np.concatenate([train_in] + new_train_in, axis=0)
            train_targs = np.concatenate([train_targs] + new_train_targs, axis=0)

        return train_in, train_targs


    def train(self,train_in, train_targs, model_train_cfg):
        '''
        Arguments:
            train_in: training input, a matrix
            train_targs: training target, a matrix

        Returns: None
        '''
        self.model.train(train_in, train_targs, model_train_cfg)

    def targ_proc(self, obs, next_obs):
        return next_obs - obs


    def save_model(self, model, save_dir):
        ''' save the trained model to the dir
        Arguments:
            model: trained model
            save_dir: save directory

        Returns: None
        '''
        raise NotImplementedError("Must be implemented in subclass.")

if __name__ == "__main__":
    import ipdb; ipdb.set_trace()
    dir = "/home/yliu2/rl_log/merge_data"

    MG = ModelGenerator()
    obs, acs, rew = MG.read(dir)
    train_in, train_targs = MG.concat(obs, acs, rew)
    model = MG.train(train_in, train_targs) # train model from the given data
    MG.save_model(model, dir) # save the trained model
