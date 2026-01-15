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
source("text_funcs.R")
# ----------------------------
# Paths
# ----------------------------
dfm_path <- file.path("results/dfms", chunk, "dfm_stm.rds")
out_dir  <- file.path("results/prepped", chunk)

dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)



lower_thresh <- get_lower_thresh(chunk)


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
    file.path(out_dir, "prepped_documents.rds")
)
