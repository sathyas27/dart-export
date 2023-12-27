#!/bin/bash

. ~/.profile

# Load necessary modules
module purge
module load python

# Source user's bashrc and activate the environment
source /home/${USER}/.bashrc
source activate hyperion
sleep 10

# Initial parameters
MAIN_SCRIPT='ExtractImage.py'
JOB_LOG='log-post'

# Run the code
which python >> "$JOB_LOG" 2>&1
python "${MAIN_SCRIPT}" >> "$JOB_LOG" 2>&1
