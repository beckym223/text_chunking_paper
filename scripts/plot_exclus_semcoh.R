library(tidyverse)
library(purrr)
### iterate over chunk names in chunks.txt
chunk_names=readLines(con="scripts/chunks.txt")
chunk_names=chunk_names[chunk_names!=""]
### For each chunking thing:
result_path_format<-"~/cleaner_package/results/searchK_test/%s/searchK_test_results.rds"

plot_exclus_semcoh_basic<-function(metric_df){
    metric_df%>%
        ggplot(aes(x=K,y=value))+
        geom_line()+
        facet_wrap(~metric,nrow=2,scales='free_y')+
        theme_minimal()
    
}

plot_choose_searchK<-function(chunk_name){
    searchK_res <- readRDS(sprintf(result_path_format,chunk_name))
    res<-searchK_res$results
    out_dir<-file.path("~/cleaner_package/results/chooseK",chunk_name)
    dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
    metric_df<-res[c("K","exclus","semcoh")]%>%
        lapply(unlist)%>%
        bind_cols()%>%
        as.data.frame()%>%
        pivot_longer(cols = c(exclus,semcoh))%>%
        mutate(metric = factor(name,labels=c("Exclusivity","Semantic Coherence")))
    p<-plot_exclus_semcoh_basic(metric_df)
    
    show(p)
    
    tryCatch({
        val = readline("Good k: ")%>%
            str_split(regex(" ?, ?"))%>%lapply(as.integer)
    }, warning=function(e){stop("Invalid input. Quitting")}
    )
    
  return(metric_df%>%
        mutate(chosen=K %in%val))
    
 
}

save_search_k_plot<-function(chunk_name,metric_df){
    chosen<-metric_df%>%filter(chosen)
    new_p<-plot_exclus_semcoh_basic(metric_df)+
        geom_point(data=chosen,aes(x=K,y=value,color="Potential K"),
                        shape='circle plus',
                        size=1.5)+
        labs(
            x = "Number of Topics (K)",
            y = "Mean Value over Topics",
            color = "",
            shape="")+
        theme_minimal()
    
    plot_save_path<-file.path(out_dir,"chosen_k_metric.png")
    ggsave(plot_save_path,width = 1100,height=780,dpi=200,units='px')
    
    df_save_path<-file.path(out_dir,"chosen_k_df.csv")
    write_csv(metric_df,df_save_path)
}

metrics<-map(chunk_names,plot_choose_searchK)

walk2(
    chunk_names,metrics,save_search_k_plot
)
