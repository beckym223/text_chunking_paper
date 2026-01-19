#!/bin/bash
#SBATCH --job-name=prep_docs
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --output=results/logs/prep_%A_%a.out
#SBATCH --error=results/logs/prep_%A_%a.err

module load r-rocker-ml-verse/4.4.0+apptainer
# Set working directory
cd ~/cleaner_package || { echo "Failed to change directory to ~/cleaner_package"; exit 1; }

CHUNK=$(grep -ve '^[[:space:]]*$' scripts/chunks.txt | sed -n "$((SLURM_ARRAY_TASK_ID+1))p")
Rscript scripts/prep_documents.R "$CHUNK"