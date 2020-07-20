#!/bin/bash

echo "Spawning PETS"
screen -dm -S PETS screen sh -c "/home/rtallamraju/blimp_ws/blimp_rl_ws/src/blimpRL/mbrl_pets/script/pets/main.py -logdir /home/rtallamraju/blimp_ws/exp_log/pets/HOVER/4act"

date
# exit 0
