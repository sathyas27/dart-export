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
module load hdf5/intel/2021.4.0/intel-mpi/2021.6.0/zen2/1.10.7

# Initial parameters
CUR_JOB_FILE='current_job'
PERFORM_WORK_FILENAME='main-process.sh'
STORAGE_DIRECTORY='storage'
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

# Run the MPI code
mpirun /home/sselvam/scratch/miniconda3/envs/dart-export/bin/hyperion_sph_mpi model_input_file.rtin model_result_file.rtout >> "$CUR_JOB_FILE" 2>&1

# Extract image
cp "$PYTHON_CONFIG_FILE" "$CURRENT_STORAGE/"
cp "$RADIATIVE_OUTPUT_FILE" "$CURRENT_STORAGE/"
cp tilted_plume.py "$CURRENT_STORAGE/"

/bin/echo -e "Job ID $STORAGE_ID finished!" >> "$CUR_JOB_FILE" 2>&1
/bin/echo -e "Job ID $STORAGE_ID finished!"