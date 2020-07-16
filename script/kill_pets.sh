#!/bin/bash

echo "kill pets"
screen -ls  | egrep "^\s*[0-9]+.PETS" | awk -F "." '{print $1}' | xargs kill

date
# exit 0
