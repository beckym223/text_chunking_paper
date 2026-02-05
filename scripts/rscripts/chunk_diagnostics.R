library(dplyr)
library(ggplot2)
# ----------------------------
# Diagnostics by year
# ----------------------------
doc_lengths <- rowSums(prepped$documents)

diag_df <- prepped$meta %>%
    mutate(tokens = doc_lengths) %>%
    group_by(year) %>%
    summarize(
        n_docs = n(),
        avg_tokens = mean(tokens),
        .groups = "drop"
    )

saveRDS(
    diag_df,
    file.path(out_dir, "diagnostics_by_year.rds")
)

# ----------------------------
# Plots
# ----------------------------
png(file.path(out_dir, "num_documents_by_year.png"), 900, 700)
ggplot(diag_df, aes(year, n_docs)) +
    geom_col() +
    labs(
        title = paste("Documents by Year:", chunk),
        y = "Number of Documents"
    )
dev.off()

png(file.path(out_dir, "avg_tokens_by_year.png"), 900, 700)
ggplot(diag_df, aes(year, avg_tokens)) +
    geom_col() +
    labs(
        title = paste("Average Tokens per Document:", chunk),
        y = "Average Tokens"
    )
dev.off()
