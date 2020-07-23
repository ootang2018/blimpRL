#!/bin/bash

echo "Spawning PETS"
screen -dm -S PETS screen sh -c "/home/yliu_local/blimp_ws/blimpRL_ws/src/blimpRL/mbrl_pets/script/pets/main.py -logdir /home/yliu_local/blimp_ws/exp_log/PETS/BACKWARD/8act"

date
# exit 0
