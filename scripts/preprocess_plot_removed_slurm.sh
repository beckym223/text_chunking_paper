#!/bin/bash
#SBATCH --job-name=stm_plotRemoved
#SBATCH --output=cleaner_package/results/logs/plotRemoved_%A_%a.out
#SBATCH --error=cleaner_package/results/logs/plotRemoved_%A_%a.err
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00

module load r-rocker-ml-verse/4.4.0+apptainer
# Set working directory
cd ~/cleaner_package || { echo "Failed to change directory to ~/stm_work"; exit 1; }

CHUNK=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" scripts/chunks.txt)

Rscript scripts/make_dfm_plot_removed.R $CHUNK

# sbatch ~/cleaner_package/slurm_scripts/preprocess_plot_removed_slurm.sh