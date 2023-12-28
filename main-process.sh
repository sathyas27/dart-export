#!/bin/bash

. ~/.profile

# Load necessary modules
module purge
module load python

# Initial parameters
CUR_JOB_FILE='current_job'
PERFORM_WORK_FILENAME='main-process'
STORAGE_DIRECTORY='../storage'
IMAGE_FILE='images.fits.gz'

# Often-tunable initial parameters
PYTHON_CONFIG_FILE='current_config.py'
RADIATIVE_OUTPUT_FILE='model_result_file.rtout'

# Create the main storage directory if it does not exist
if [ ! -d "$STORAGE_DIRECTORY" ]; then
    mkdir "$STORAGE_DIRECTORY"
fi

# Create new storage folder to store the results
STORAGE_CREATED=0
STORAGE_ID=0
while [ $STORAGE_CREATED -eq 0 ]; do
    let STORAGE_ID++
    if [ ! -d "${STORAGE_DIRECTORY}/${STORAGE_ID}" ]; then
        CURRENT_STORAGE="${STORAGE_DIRECTORY}/${STORAGE_ID}"
        mkdir "$CURRENT_STORAGE"
        STORAGE_CREATED=1
    fi
done

# Save this file to storage
cp "$PERFORM_WORK_FILENAME" "$CURRENT_STORAGE/"

# Delete the .rtout file if it exists
rm -f "$RADIATIVE_OUTPUT_FILE"

/bin/echo -e "Job ID is $STORAGE_ID. Beginning run.." > "$CUR_JOB_FILE" 2>&1
/bin/echo -e "Job ID is $STORAGE_ID. Beginning run.."

# Run the MPI code
mpirun ../../anaconda3/envs/hyperion/bin/hyperion_sph_mpi model_input_file.rtin model_result_file.rtout >> "$CUR_JOB_FILE" 2>&1

# Extract image
cp "$PYTHON_CONFIG_FILE" "$CURRENT_STORAGE/"
cp "$RADIATIVE_OUTPUT_FILE" "$CURRENT_STORAGE/"
cp TiltedPlume.py "$CURRENT_STORAGE/"

/bin/echo -e "Job ID $STORAGE_ID finished!" >> "$CUR_JOB_FILE" 2>&1
/bin/echo -e "Job ID $STORAGE_ID finished!"
