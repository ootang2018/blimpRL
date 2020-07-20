#!/bin/bash

echo "Spawning PETS"
screen -dm -S PETS screen sh -c "/home/rtallamraju/blimp_ws/blimp_rl_ws/src/blimpRL/mbrl_pets/script/pets/render.py -logdir /home/rtallamraju/blimp_ws/exp_log/test/pets_and_mpc/hover/4act"

date
# exit 0
