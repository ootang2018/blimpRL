from stable_baselines.sac.policies import MlpPolicy
from stable_baselines import SAC
from env.blimp import BlimpEnv
import numpy as np
import os
from scipy.io import savemat


class Agent():
    def __init__(self, model_path):
        SLEEP_RATE = 100 #1 100
        self.EPISODE_LENGTH = SLEEP_RATE*30 #60 120

        self.env = BlimpEnv(SLEEP_RATE)
        self.model = SAC.load(model_path)

    def sample(self, EPISODE_LENGTH):
        obs = self.env.reset()
        reward_total=0
        O=[]; A=[]; rewards=[]; reward_sum=[];

        for i in range(EPISODE_LENGTH):
            action, _states = self.model.predict(obs)
            obs, reward, dones, info = self.env.step(action)
            reward_total += reward

            O.append(obs)
            A.append(action)
            rewards.append(reward)

        obs = self.env.reset()
        reward_sum.append(reward_total)
        print("reward_total = ", reward_total)

        return {
            "obs": np.array(O),
            "ac": np.array(A),
            "reward_sum": reward_sum,
            "rewards": np.array(rewards),
        }

    def start(self, logdir):
            samples=[];traj_obs=[]; traj_acs=[]; traj_rets=[]; traj_rews=[];
            samples.append(self.sample(self.EPISODE_LENGTH))

            traj_obs.extend([sample["obs"] for sample in samples[:self.EPISODE_LENGTH]])
            traj_acs.extend([sample["ac"] for sample in samples[:self.EPISODE_LENGTH]])
            traj_rets.extend([sample["reward_sum"] for sample in samples[:1]])
            traj_rews.extend([sample["rewards"] for sample in samples[:self.EPISODE_LENGTH]])

            savemat(
                    os.path.join(logdir, "logs.mat"),
                    {
                        "observations": traj_obs,
                        "actions": traj_acs,
                        "returns":traj_rets,
                        "rewards": traj_rews
                    }
                )

if __name__ == "__main__":

    logdir = '/home/yliu2/rl_log/test/SAC/alt'
    model_path = '/home/yliu2/rl_log/SAC/ALT/3act/exp1/best_model.zip'

    agent = Agent(model_path)
    agent.start(logdir)
