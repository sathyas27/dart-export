#!/bin/bash

# Node and core requirements
## Number of MPI task
#SBATCH --ntasks=13

## Number of CPU cores to use for each task
#SBATCH --cpus-per-task=1

# Memory requirements
# The default is 6GB per CPU core
# sbatch command specifies memory in mb.
#SBATCH --mem-per-cpu=2048

#SBATCH --time=01:00:00  # Set a limit of one hour for the job


# Whether or not other jobs can be on the same node
## Hurts performance while decreasing SU usage
## Increased performance and SU usage
#SBATCH --exclusive

. ~/.profile

# Load necessary modules
module purge
module load envi

# Source user's bashrc and activate the environment
source /home/${USER}/.bashrc
conda activate dart-export
sleep 10

# Initial parameters
MAIN_SCRIPT='ExtractImage.py'
JOB_LOG='log-post'

# Run the code
which python >> "$JOB_LOG" 2>&1
python "${MAIN_SCRIPT}" >> "$JOB_LOG" 2>&1
