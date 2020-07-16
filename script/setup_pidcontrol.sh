#!/bin/bash

echo "Spawning pidcontrol"
screen -dm -S PID screen sh -c "python /home/rtallamraju/blimp_ws/blimp_rl_ws/src/blimpRL/pid_controller/controls_flyer.py"

date
# exit 0
