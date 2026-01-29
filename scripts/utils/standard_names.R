
proj_env<-new.env()

create_dir_from_path<-function(path){
    out.dir<-dirname(path)
    if(!dir.exists(out.dir)){
        dir.create(out.dir, recursive = T,showWarnings = F)
    }
    path
}
proj_env$get_lower_thresh <- function(chunk_name) {
    
    ## ---------- USER-EDITABLE THRESHOLDS ----------
    lower_thresholds <- c(
        document   = 10,
        paragraph  = 20,
        page       = 20,
        sent_200   = 20,
        sent_500   = 20
    )
    ## ---------------------------------------------
    
    if (chunk_name %in% names(lower_thresholds)) {
        lower_thresholds[[chunk_name]]
    } else {
        10
    }
}

proj_env$chunk_names_path<-"scripts/chunks.txt"

proj_env$load_chunk_names<-function(){
    chunk_names=readLines(proj_env$chunk_names_path)
    chunk_names[chunk_names!=""]
}

proj_env$chunk_display_names<-list(
        document  = "full document",
        page      = "page",
        paragraph = "paragraph",
        sent_200  = "200 word - nearest sentence",
        sent_500  = "500 word - nearest sentence",
        word_200 = "200 word",
        word_500 = "500 word",
        word_500_ol = "500 word overlapping"
    )


proj_env$chunk_df_path<-"data/chunked_dfs.rds"

proj_env$get_chunk_csv_path<-function(chunk_name){
    file.path(data, paste0(chunk_name, ".csv"))
}

proj_env$get_dfm_path<-function(chunk_name){
    file.path("results/dfms", chunk_name, "dfm.rds")
}

proj_env$get_dfm_stm_path<-function(chunk_name){
    file.path("results/dfms", chunk_name, "dfm_stm.rds")
}

proj_env$get_plot_removed_path<-function(chunk_name){
    file.path("results/plotRemoved", chunk_name,"plotRemoved.png")
}



proj_env$get_prepped_out_path<-function(chunk_name){
    file.path("results/prepped", chunk_name, "prepped_documents.rds")
}

proj_env$get_searchK_out_path<-function(chunk_name){
    file.path("results/searchK", chunk_name, "searchK_results.rds")
}

proj_env$get_searchK_plot_path<-function(chunk_name){
    file.path("results/searchK", chunk_name, "searchK_plot.png")
}

proj_env$get_chooseK_df_path<-function(chunk_name){
    file.path("results/chooseK",chunk_name,"chosen_k_df.csv")
}

proj_env$get_chooseK_plot_path<-function(chunk_name){
    file.path("results/chooseK",chunk_name,"chosen_k_metric.png")
}

proj_env$get_stm_dir<-function(chunk_name){
    file.path("results/chosen_stms",chunk_name)
}

proj_env$get_stm_path<-function(chunk_name,k){
    file.path(proj_env$get_stm_dir(chunk_name),sprintf("stm_%d.rds",k))
}

proj_env$get_model_id<-function(chunk_name,k){
    sprintf("%s_%dk",chunk_name,k)
}

proj_env$get_topic_id<-function(chunk_name,k,topic_num){
    paste0(proj_env$get_model_id(chunk_name,k),"_t",topic_num)
}

proj_env$agg_topic_df_path<-"results/combined_results/agg_topic_labels.csv"