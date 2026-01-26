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
result_path_format<-"~/cleaner_package/results/searchK/%s/searchK_results.rds"
chooseK_out_dir<-"~/cleaner_package/results/chooseK"
plot_exclus_semcoh_basic<-function(metric_df){
    metric_df%>%
        ggplot(aes(x=K,y=value))+
    geom_point(size=0.5)+
        geom_line()+
        facet_wrap(~metric,nrow=2,scales='free_y')+
        theme_minimal()
    
}

plot_choose_searchK<-function(metric_df){
    p<-plot_exclus_semcoh_basic(metric_df)
    
    show(p)
    
    tryCatch({
        val = readline("Good k: ")%>%
            str_split(regex(" ?, ?"))%>%lapply(as.integer)%>%unlist()
        print(val)
    }, warning=function(e){stop("Invalid input. Quitting")}
    )
    
  return(metric_df%>%
        mutate(chosen=K %in%val))
    
 
}

save_search_k_plot<-function(chunk_name,metric_df){
  out_dir<-file.path(chooseK_out_dir,chunk_name)
    chosen<-metric_df%>%filter(chosen)
    max_k<-max(metric_df$K)
    new_p<-plot_exclus_semcoh_basic(metric_df)+
        geom_point(data=chosen,aes(x=K,y=value,color="Potential K"),
                        shape='circle plus',
                        size=1.5)+
        labs(
            title = paste0("Diagnostics and chosen K for STM chunked at\n",chunk_display_names[chunk_name]," level"),
            x = "Number of Topics (K)",
            y = "Mean Value over Topics",
            color = "",
            shape="")+
      scale_x_continuous(breaks = seq(5, max_k, by = 5),
      minor_breaks = seq(min(metric_df$K),max_k))+
        theme_minimal()
    
    plot_save_path<-file.path(out_dir,"chosen_k_metric.png")
    ggsave(plot_save_path,width = 1100,height=780,dpi=200,units='px')
    
    
    show(new_p)
    #print(df_save_path)
    write_csv(metric_df,df_save_path)
}

load_results<-function(chunk_name){
    searchK_res <- readRDS(sprintf(result_path_format,chunk_name))
    res<-searchK_res$results
    res[c("K","exclus","semcoh")]%>%
      lapply(unlist)%>%
      bind_cols()%>%
      mutate(across(everything(),as.numeric))%>%
      right_join(
        data.frame(K=seq(
          min(.$K,na.rm=T),
          max(.$K,na.rm=T)
          )
      ),
      by=join_by(K)
      )%>%arrange(K)%>%
        pivot_longer(cols = c(exclus,semcoh))%>%
        mutate(
            metric = factor(name,labels=c("Exclusivity","Semantic Coherence")),
               chunk_name=chunk_name)%>%
        as.data.frame()
}
results<-map(chunk_names,load_results)

out<-readline("Input 'Y' to confirm selecting and overwriting chosen K values, or anything else to load current ones: ")

if (str_to_lower(out)=="y"){
  metrics<-map(results,plot_choose_searchK)
}


o<-map2(chunk_names,metrics,~save_search_k_plot(.x,.y))
