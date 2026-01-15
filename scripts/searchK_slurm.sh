#!/bin/bash
#SBATCH --job-name=searchK
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=24G
#SBATCH --output=results/logs/searchK_%A_%a.out
#SBATCH --error=results/logs/searchK_%A_%a.err

CHUNK=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" scripts/chunks.txt)

Rscript scripts/searchK.R "$CHUNK"