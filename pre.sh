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

# Purge and load necessary modules
module purge
module load envi




# Source bashrc and activate the environment
source /home/${USER}/.bashrc
conda activate dart-export

# Job variables
PREPROCESSING_SCRIPT="pre.sh"
JOB_LOG_NAME='log-pre'
if [ ! -d "data" ]; then
    mkdir data
    mkdir -p data/logs data/scripts data/storage
else
    echo "Directory 'data' already exists."
    rm -r data
    mkdir data
    mkdir -p data/logs data/scripts data/storage
fi
CURRENT_STORAGE="data/storage"
SCRIPTS_STORAGE="data/scripts"
LOGS_STORAGE="data/logs"
JOB_LOG="${LOGS_STORAGE}/${JOB_LOG_NAME}"



/bin/echo -e "CURRENT_STORAGE: $CURRENT_STORAGE" > $JOB_LOG 2>&1
 
# Configuration and main script files
CONFIG_FILE="current_config.py"
MAIN_SCRIPT="tilted_plume.py"

# Print the current working directory to the log file
/bin/echo -e "\nCurrent Directory:" >> $JOB_LOG
pwd >> $JOB_LOG

# Copying necessary files to specified locations
cp "$PREPROCESSING_SCRIPT" "$SCRIPTS_STORAGE"
cp "$MAIN_SCRIPT" "$CURRENT_STORAGE/"
cp "$CONFIG_FILE" "$CURRENT_STORAGE/"

# # Output file name
# OUTPUT_FILE='model_input_file.rtin'

# # Delete the .rtin file from the previous run, if it exists
# rm -f "$OUTPUT_FILE"

/bin/echo -e "Beginning Preprocessing..." >> $JOB_LOG 2>&1

# Run the Python script and log output
/home/sselvam/scratch/miniconda3/envs/dart-export/bin/python tilted_plume.py >> $JOB_LOG 2>&1

# Copy the results to storage
# cp "$OUTPUT_FILE" "$CURRENT_STORAGE/"

/bin/echo -e "Preprocessing finished!" >> $JOB_LOG 2>&1