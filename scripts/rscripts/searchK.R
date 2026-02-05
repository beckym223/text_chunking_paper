#!/usr/bin/env Rscript

suppressPackageStartupMessages({
    library(stm)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
    stop("Usage: Rscript search_k.R <chunk_name>")
}
chunk <- args[[1]]
source("scripts/rscripts/utils/standard_names.R")
# ----------------------------
# Paths
# ----------------------------
prep_path <- proj_env$get_prepped_out_path(chunk)

# ----------------------------
# Load data
# ----------------------------
prepped <- readRDS(prep_path)

# ----------------------------
# searchK
# ----------------------------
set.seed(123)
result_out_path<-proj_env$get_searchK_out_path(chunk)%>%
    create_dir_from_path()

plot_out_path<-proj_env$get_searchK_plot_path(chunk)%>%
    create_dir_from_path()

search <- searchK(
    documents  = prepped$documents,
    vocab      = prepped$vocab,
    K          = seq(3,50),
    prevalence = ~ s(year),
    data       = prepped$meta,
    cores      = 15,
    verbose = F
)

saveRDS(
    search,
    result_out_path
)

png(plot_out_path, 900, 700)
plot(search)
dev.off()