#!/bin/bash

echo "kill pid control"
screen -ls  | egrep "^\s*[0-9]+.PID" | awk -F "." '{print $1}' | xargs kill

date
# exit 0
