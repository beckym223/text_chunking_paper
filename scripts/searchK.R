#!/usr/bin/env Rscript

suppressPackageStartupMessages({
    library(stm)
    library(parallel)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
    stop("Usage: Rscript search_k.R <chunk_name>")
}
chunk <- args[[1]]

# ----------------------------
# Paths
# ----------------------------
prep_path <- file.path("results/prepped", chunk, "prepped_documents.rds")
out_dir   <- file.path("results/searchK", chunk)

dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

# ----------------------------
# Load data
# ----------------------------
prepped <- readRDS(prep_path)

# ----------------------------
# searchK
# ----------------------------
set.seed(123)
cores <- parallel::detectCores()

search <- searchK(
    documents  = prepped$documents,
    vocab      = prepped$vocab,
    K          = seq(3,50),
    prevalence = ~ s(year),
    data       = prepped$meta,
    cores      = cores
)

saveRDS(
    search,
    file.path(out_dir, "searchK_results.rds")
)

png(file.path(out_dir, "searchK_plot.png"), 900, 700)
plot(search)
dev.off()