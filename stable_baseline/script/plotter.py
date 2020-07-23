from stable_baselines import results_plotter
import matplotlib.pyplot as plt


log_dir = '/home/yliu2/blimp_ws/exp_log/SAC/HOVER/4act/exp1'
SLEEP_RATE = 2
N_EPISODE = 5000
EPISODE_LENGTH = SLEEP_RATE*30 #30 sec
TOTAL_TIMESTEPS = EPISODE_LENGTH * N_EPISODE

results_plotter.plot_results([log_dir], TOTAL_TIMESTEPS, results_plotter.X_TIMESTEPS, "SAC BLIMP")
plt.show()
