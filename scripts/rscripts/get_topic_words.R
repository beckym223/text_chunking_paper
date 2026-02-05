library(tidyverse)
library(stm)
library(purrr)
### iterate over chunk names in chunks.txt
source("scripts/utils/standard_names.R")
chunk_names<-proj_env$load_chunk_names()
chunk_display_names<-proj_env$chunk_display_names

### For each chunking thing:

get_chosen_ks<-function(chunk_name){
    ks<-read_csv(proj_env$get_chooseK_df_path(chunk_name),show_col_types = F)%>%
        filter(chosen)%>%
        distinct(K)%>%
        .$K
    if (length(ks)==0){
        warning(sprintf("No ks selected for chunk '%s'",chunk_name))
    }
    ks
}

load_doc_fit_stms<-function(chunk_name){
    
    chosen<-get_chosen_ks(chunk_name)
    prepped_doc_path<-proj_env$get_prepped_out_path(chunk_name)
    prepped<-read_rds(prepped_doc_path)
    
    for (i in seq_along(chosen)){
        k<- chosen[i]
        cat(sprintf(("Fitting topic for '%s' with %d topics\n"),chunk_name,k))
        stm_obj<-stm(
            prepped$documents,
            prepped$vocab,
            k,
            prevalence=~s(year),
            data=prepped$meta,
            init.type = "Spectral",
            seed = 121,
            verbose = F
    )
        out_path<-proj_env$get_stm_path(chunk_name,k)%>%
            create_dir_from_path()
        write_rds(stm_obj,out_path)
        
        cat(sprintf("Successfully saved %d topic STM to %s\n",k,out_path))
        
}
    
}


load_fitted_stms<-function(chunk_name){
    dir<-proj_env$get_stm_dir(chunk_name)
    
    map(list.files(dir,full.names=T),read_rds)
    
}


make_topic_label_df<-function(model,name,n=10){
    K<-model$settings$dim$K
    label_df<-labelTopics(model,n=n)$frex%>%t()%>%as.data.frame()
    colnames(label_df)<-seq(K)
    label_df%>%
        mutate(chunk_name=name,K=K,
               rank=row_number(),
               model_id = proj_env$get_model_id(name,K))%>%
        pivot_longer(cols=seq(K),names_to = "topic",values_to = "token")%>%
        mutate(topic_id = proj_env$get_topic_id(name,K,topic))
    
}

chosen_ks<-map(chunk_names,get_chosen_ks)

out<-readline("Input 'Y' to confirm refitting models or anything else to load current ones: ")

if (str_to_lower(out)=="y"){
    walk(chunk_names,load_doc_fit_stms)
}

stms<-map(chunk_names,load_fitted_stms)
names(stms) = chunk_names

stm_unlisted<-stms%>%unlist(recursive=F)
model<-stms$page[[2]]
t<-labelTopics(stms$document[[1]])$frex

full_topic_df<-imap(stms,
    function(models,name){
        lapply(models,function(m) make_topic_label_df(m,name=name))%>%bind_rows()
        }
)%>%bind_rows()

df_save_path<-proj_env$agg_topic_df_path%>%create_dir_from_path()

full_topic_df%>%write_csv(df_save_path)
