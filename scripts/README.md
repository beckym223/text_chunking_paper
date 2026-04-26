# Text Chunking and Sankey Creation Pipeline

## Pipeline Steps:
1. [submit_all.sh](scripts/bash_scripts/submit_all.sh): Run from unity terminal to submit batch jobs for various stages in the text cleaning and model selection process, from chunking texts to executing `searchK`
2. [plot_exclus_semcoh.R](scripts/rscripts/plot_exclus_semcoh.R): Loads search K results, produces graphs of semantic coherence and exclusivity, and prompts user to input candidate values of K, which are then saved.
3. [select_save_sankey_paths.R](scripts/rscripts/select_save_sankey_paths.R): Preps for Sankey diagram by setting up source-target data frames and jsons from "paths" of candidate models, such as over values of K. Automatically groups models with equal values of K, as well as model combinations hard coded into the script. 
4. [make_sankeys.py](scripts/pyscripts/make_sankeys.py): Python script executed to load jsons of model paths then create and save sankey diagrams of word overlap.
