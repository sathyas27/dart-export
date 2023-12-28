#!/bin/bash

. ~/.profile

# Purge and load necessary modules
module purge
module load python
module load envi

# Source bashrc and activate the environment
source /home/${USER}/.bashrc
conda activate dart-export

# Job variables
PREPROCESSING_SCRIPT="pre.sh"
JOB_LOG='log-pre'
# Parsing command-line arguments
# while getopts d:s:l: flag
# do
#     case "${flag}" in
#         d) CURRENT_STORAGE=${OPTARG};;
#         s) SCRIPTS_STORAGE=${OPTARG};;
#         l) LOGS_STORAGE=${OPTARG};;
#     esac
# done
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
JOB_LOG="${LOGS_STORAGE}/${JOB_LOG}"



/bin/echo -e "CURRENT_STORAGE: $CURRENT_STORAGE" > $JOB_LOG 2>&1
 
# Configuration and main script files
CONFIG_FILE="current_config.py"
MAIN_SCRIPT="TiltedPlume.py"

# Copying necessary files to specified locations
cp "$PREPROCESSING_SCRIPT" "$SCRIPTS_STORAGE"
cp "$MAIN_SCRIPT" "$CURRENT_STORAGE/"
cp "$CONFIG_FILE" "$CURRENT_STORAGE/"

# Output file name
OUTPUT_FILE='model_input_file.rtin'

# Delete the .rtin file from the previous run, if it exists
rm -f "$OUTPUT_FILE"

/bin/echo -e "Beginning Preprocessing..." >> $JOB_LOG 2>&1

# Run the Python script and log output
which python >> $JOB_LOG 2>&1
python TiltedPlume.py >> $JOB_LOG 2>&1

# Copy the results to storage
cp "$OUTPUT_FILE" "$CURRENT_STORAGE/"

/bin/echo -e "Preprocessing finished!" >> $JOB_LOG 2>&1

