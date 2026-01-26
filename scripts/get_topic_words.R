library(tidyverse)
library(purrr)
### iterate over chunk names in chunks.txt
chunk_names=readLines(con="scripts/chunks.txt")
chunk_names=chunk_names[chunk_names!=""]


chunk_display_names<-list(
    document  = "full document",
    page      = "page",
    paragraph = "paragraph",
    sent_200  = "200 word - nearest sentence",
    sent_500  = "500 word - nearest sentence",
    word_200 = "200 word",
    word_500 = "500 word",
    word_500_ol = "500 word overlapping"
)

### For each chunking thing:

chosenK_df_format<-"~/cleaner_package/results/chooseK/%s/chosen_k_df.csv"

chunk_name<-"paragraph"
get_chosen_ks<-function(chunk_name){
    ks<-read_csv(sprintf(chosenK_df_format,chunk_name),show_col_types = F)%>%
        filter(chosen)%>%
        distinct(K)%>%
        .$K
    if (length(ks)==0){
        warning(sprintf("No ks selected for chunk '%s'",chunk_name))
    }
    ks
}

chosen_ks<-map(chunk_names,get_chosen_ks)
prep_path <- file.path("results/prepped", chunk, "prepped_documents.rds")


