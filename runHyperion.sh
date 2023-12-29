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

SETUP_FILENAME="runHyperion.sh"
STORAGE_DIRECTORY="storage"

PREPROCESSING_SCRIPT="pre.sh"
MPI_SCRIPT="main-process.sh"

JOB_LOG='log-main'

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
        SCRIPTS_STORAGE="${CURRENT_STORAGE}/scripts"
        LOGS_STORAGE="${CURRENT_STORAGE}/logs"
        mkdir "$CURRENT_STORAGE"
        mkdir "$SCRIPTS_STORAGE"
        mkdir "$LOGS_STORAGE"
        STORAGE_CREATED=1
    fi
done

cp "$SETUP_FILENAME" "$SCRIPTS_STORAGE/"
/bin/echo -e "Job ID is $STORAGE_ID. Beginning run..." > "$JOB_LOG" 2>&1

# Call the preprocessing script
/bin/echo -e "Preprocessing..." >> "$JOB_LOG" 2>&1
bash "$PREPROCESSING_SCRIPT" -d "$CURRENT_STORAGE" -s "$SCRIPTS_STORAGE" -l "$LOGS_STORAGE" >> "$JOB_LOG" 2>&1

# Assuming the preprocessing script's success is vital for the next step
if [ $? -eq 0 ]; then
    /bin/echo -e "Running MPI script..." >> "$JOB_LOG" 2>&1
    bash "$MPI_SCRIPT" -d "$CURRENT_STORAGE" -s "$SCRIPTS_STORAGE" -l "$LOGS_STORAGE" >> "$JOB_LOG" 2>&1
else
    /bin/echo -e "Preprocessing failed. MPI script not run." >> "$JOB_LOG" 2>&1
fi

/bin/echo -e "Completed Job $STORAGE_ID!" >> "$JOB_LOG" 2>&1
cp "$JOB_LOG" "$LOGS_STORAGE/"
