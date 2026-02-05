suppressPackageStartupMessages({
    library(quanteda)
    library(stm)
})
source("scripts/rscripts/utils/text_funcs.R")
source("scripts/rscripts/utils/standard_names.R")
args <- commandArgs(trailingOnly = TRUE)
chunk_name <- args[1]

chunk_dfs <- readRDS(proj_env$chunk_df_path)
chunk_df  <- chunk_dfs[[chunk_name]]

result <- preprocess_make_dfm(chunk_df)
dfm_stm<-result$dfm_stm
dfm<-result$dfm

out_dfm_path<-proj_env$get_dfm_path(chunk_name)%>%
    create_dir_from_path()

out_dfm_stm_path<-proj_env$get_dfm_stm_path(chunk_name)%>%
    create_dir_from_path()

out_plot_path<-proj_env$get_plot_removed_path(chunk_name)%>%
    create_dir_from_path()

saveRDS(dfm_stm, out_dfm_stm_path)
saveRDS(dfm, out_dfm_path)

png(
    out_plot_path,
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
