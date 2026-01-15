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

# ----------------------------
# Paths
# ----------------------------
dfm_path <- file.path("results/dfms", chunk, "dfm_stm.rds")
out_dir  <- file.path("results/prepped", chunk)

dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

# ----------------------------
# Thresholds (DEFAULT = 10)
# ----------------------------
lower_thresholds <- c(
    document = 10,
    paragraph = 20,
    page = 20,
    sent_200 = 20,
    sent_500 = 20
    
)

lower_thresh <- lower_thresholds[[chunk]]
if (is.null(lower_thresh)) lower_thresh <- 10

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
