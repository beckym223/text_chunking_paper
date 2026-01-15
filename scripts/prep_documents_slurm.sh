#!/bin/bash
#SBATCH --job-name=prep_docs
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --output=results/logs/prep_%A_%a.out
#SBATCH --error=results/logs/prep_%A_%a.err

# Set working directory

CHUNK=$(grep -ve '^[[:space:]]*$' scripts/chunks.txt | sed -n "$((SLURM_ARRAY_TASK_ID+1))p")
Rscript scripts/prep_documents.R "$CHUNK"