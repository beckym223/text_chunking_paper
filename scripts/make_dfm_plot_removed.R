suppressPackageStartupMessages({
    library(quanteda)
    library(stm)
})
source("text_funcs.R")
args <- commandArgs(trailingOnly = TRUE)
chunk_name <- args[1]


lower_thresh <- get_lower_thresh(chunk_name)

chunk_dfs <- readRDS("data/chunked_dfs.rds")
chunk_df  <- chunk_dfs[[chunk_name]]

result <- preprocess_make_dfm(chunk_df)

out_dfm_dir <- file.path("results/dfms", chunk_name)
out_plot_dir <- file.path("results/plotRemoved", chunk_name)

dir.create(out_dfm_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(out_plot_dir, recursive = TRUE, showWarnings = FALSE)

saveRDS(result$dfm_stm, file.path(out_dfm_dir, "dfm_stm.rds"))
saveRDS(result$dfm, file.path(out_dfm_dir, "dfm.rds"))

png(
    file.path(out_plot_dir, "plotRemoved.png"),
    width = 800,
    height = 600
)

plotRemoved(
    dfm_stm$documents,
    c(1, seq(5, 50, 5))
)


title(
    main = paste(
        "plotRemoved diagnostics:",
        chunk_name
    )
)

dev.off()
