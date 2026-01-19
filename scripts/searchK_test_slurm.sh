#!/bin/bash
#SBATCH --job-name=searchK_test
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=24G
#SBATCH --output=results/logs/searchKtest_%A_%a.out
#SBATCH --error=results/logs/searchKtest_%A_%a.err


cd ~/cleaner_package || { echo "Failed to change directory to ~/cleaner_package"; exit 1; }

module load r-rocker-ml-verse/4.4.0+apptainer

CHUNK=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" scripts/chunks.txt)

Rscript scripts/searchK_test.R "$CHUNK"