# Libraries

library(tidyverse)
library(stringr)
library(stringi)
library(quanteda)

source("text_funcs.R")



# Load paragraph data frame, make output dir

para_df_path<-"data_const/para_df.csv"
para_df<-read_csv(para_df_path,show_col_types = F)%>%
    mutate(text_id=paste(doc_id,sprintf("%03.0f",para_num),sep="-"),
           year=meeting_num+1886
    )%>%
    select(doc_id,text_id,year,text)

output.dir<-"data"

if(!dir.exists(output.dir)){
    dir.create(output.dir, recursive = T)
}


# Chunking full documents


doc_df <- para_df %>%
    group_by(doc_id) %>%
    summarize(
        year = first(year),
        text = paste(text, collapse = "\n"),
        .groups = "drop"
    ) %>%
    mutate(text_id = as.character(doc_id)) %>%
    select(text_id, year, text)


# Loading original document pages


page_df <- read_csv("data_const/page_df.csv", show_col_types = FALSE) %>%
    rename(text_id=page_id)%>%
    mutate(year=meeting_num+1886)%>%
    transmute(
        doc_id,
        text_id,
        year,
        text
    )




# Chunking to fixed size, nearest sentence

sent_200_df <- make_sentence_chunks(doc_df, 200)
sent_500_df <- make_sentence_chunks(doc_df, 500)


word_200_df<-chunk_documents_by_word(doc_df,
                                     chunk_size=200,
                                     overlap=0
)
word_500_df<-chunk_documents_by_word(doc_df,
                                     chunk_size=500,
                                     overlap=0
)
word_500_ol_df<-chunk_documents_by_word(doc_df,
                                        chunk_size=500,
                                        overlap=250
)




# Put into named list

chunked_dfs <- list(
    document  = doc_df,
    page      = page_df,
    paragraph = para_df,
    sent_200  = sent_200_df,
    sent_500  = sent_500_df,
    word_200 = word_200_df,
    word_500 = word_500_df,
    word_500_ol = word_500_ol_df
)

saveRDS(
    chunked_dfs,
    file = file.path(output.dir, "chunked_dfs.rds")
)

#write to text file
chunk_names <- names(chunked_dfs)

writeLines(
    chunk_names,
    con = file.path("scripts", "chunks.txt")
)


#save to csv also

iwalk(
    chunked_dfs,
    ~ write_csv(.x, file.path(output.dir, paste0(.y, ".csv"))))



