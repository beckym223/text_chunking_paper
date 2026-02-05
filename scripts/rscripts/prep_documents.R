#!/usr/bin/env Rscript

suppressPackageStartupMessages({
    library(stm)
    library(dplyr)
})
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
    stop("Usage: Rscript prep_documents.R <chunk_name>")
}
chunk <- args[[1]]
source("scripts/rscripts/utils/text_funcs.R")
source("scripts/rscripts/utils/standard_names.R")

# ----------------------------
# Paths
# ----------------------------
dfm_path<-proj_env$get_dfm_stm_path(chunk)
prepped_out_path<-proj_env$get_prepped_out_path(chunk)%>%
    create_dir_from_path()

lower_thresh <- proj_env$get_lower_thresh(chunk)


# ----------------------------
# Load DFM
# ----------------------------
dfm <- readRDS(dfm_path)

# ----------------------------
# Prep documents
# ----------------------------
prepped <- prepDocuments(
    dfm$documents,
    dfm$vocab,
    meta = dfm$meta,
    lower.thresh = lower_thresh
)

saveRDS(
    prepped,
    prepped_out_path
)
