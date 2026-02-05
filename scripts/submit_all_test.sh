#!/bin/bash
set -euo pipefail

module load r-rocker-ml-verse/4.4.0+apptainer
# Set working directory
cd ~/cleaner_package || { echo "Failed to change directory to ~/cleaner_package"; exit 1; }
Rscript scripts/make_chunked_dfs.R
CHUNK_FILE="scripts/chunks.txt"

# Count non-empty lines safely
NUM_CHUNKS=$(grep -cve '^[[:space:]]*$' "$CHUNK_FILE")

if [ "$NUM_CHUNKS" -eq 0 ]; then
echo "No chunks found in $CHUNK_FILE"
exit 1
fi

ARRAY_SPEC="0-$((NUM_CHUNKS-1))"

# ----------------------------
# 3. searchK (after prep)
# ----------------------------
SEARCH_JOB_ID=$(sbatch \
                --array="$ARRAY_SPEC" \
                scripts/searchK_test_slurm.sh\
                | awk '{print $4}')

echo "Submitted searchK job: $SEARCH_JOB_ID"
