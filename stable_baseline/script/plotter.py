from stable_baselines import results_plotter
import matplotlib.pyplot as plt


log_dir = '/home/yliu2/rl_log/sac/ALT/3act/exp3'
SLEEP_RATE = 100
N_EPISODE = 30000
EPISODE_LENGTH = SLEEP_RATE*30 #30 sec
TOTAL_TIMESTEPS = EPISODE_LENGTH * N_EPISODE

results_plotter.plot_results([log_dir], TOTAL_TIMESTEPS, results_plotter.X_TIMESTEPS, "SAC BLIMP")
plt.show()
