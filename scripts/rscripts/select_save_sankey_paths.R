library(dplyr)
library(jsonlite)
source("scripts/utils/standard_names.R")
label_df<-read_csv(proj_env$agg_topic_df_path,show_col_types = F)

get_topic_overlap<-function(label_df,topic_id1,topic_id2){
    topic1_tokens<-label_df[label_df$topic_id==topic_id1,'token']%>%unlist()
    topic2_tokens<-label_df[label_df$topic_id==topic_id2,'token']%>%unlist()
}

token_vects<-label_df%>%
    group_by(topic_id)%>%
    mutate(token_list = list(token))%>%
    distinct(token_list,.keep_all=T)%>%
    select(-c(rank,token))

token_unions<-token_vects%>%
    select(model_id,topic_id,token_list)%>%
    cross_join(.,.)%>%
    filter(topic_id.x!=topic_id.y)%>%
    mutate(
        overlap_toks=map2(token_list.x,token_list.y,intersect),
        overlap_size = map(overlap_toks,length)%>%as.integer()
    )%>%filter(overlap_size!=0)%>%arrange(overlap_size)%>%
    rename(source=topic_id.x,
           target=topic_id.y,
           src_model = model_id.x,
           target_model = model_id.y)
make_source_target_from_path<-function(model_path){
    pairs <- lapply(1:(length(model_path) - 1), function(i) list(src=model_path[i],target=model_path[i + 1]))
    all_nodes<-data.frame()
    all_links<-data.frame()
    for (i in seq_along(pairs)){
        p<-pairs[[i]]
        unions<-token_unions%>%
            filter((src_model==p$src)&(target_model==p$target))
        
        all_links<-unions%>%
            select(source,target,overlap_size)%>%
            bind_rows(all_links)
        new_nodes<-unions%>%
            pivot_longer(cols=c(source,target),values_to = 'topic_id')%>%
            mutate(is.source = (name=='source'),
                   is.target = (name=='target'),
                   model_id = str_extract(topic_id,"\\w+\\d+k"),
                   topic_num = as.numeric(str_extract(topic_id,"\\d+$"))
            )%>%
            select(topic_id,model_id,topic_num,overlap_toks,is.source,is.target)
        
        all_nodes<-new_nodes%>%
            bind_rows(all_nodes)%>%
            group_by(topic_id,model_id,topic_num)%>%
            summarise(
                overlap_toks = list(reduce(overlap_toks, union)),
                is.source = any(is.source),
                is.target= any(is.target),
                .groups = "drop"
            )
        
    }
    
    all_nodes<-all_nodes%>%
        arrange(model_id,topic_num)%>%
        mutate(node_id=row_number()-1,
               label = paste0(topic_num,": ",map(overlap_toks,str_flatten_comma)%>%unlist()))
    all_links_id<-all_links%>%
        merge(
            all_nodes%>%
                select(topic_id,node_id)%>%
                rename(source=topic_id,source_id=node_id)
        )%>%
        merge(
            all_nodes%>%
                select(topic_id,node_id)%>%
                rename(target=topic_id,target_id=node_id)
        )%>%
        select(source,source_id,target,target_id,overlap_size)
    
    list(nodes=all_nodes,links=all_links_id)
}

make_save_sankey_prep<-function(model_path){
    result<-make_source_target_from_path(model_path)
    links_out<-proj_env$get_sankey_links_path(model_path)%>%
        create_dir_from_path()
    nodes_out<-proj_env$get_sankey_nodes_path(model_path)%>%
        create_dir_from_path()
    
    json_out_path<-proj_env$get_sankey_data_json(model_path)%>%
        create_dir_from_path()
    result$links%>%write_csv(links_out)
    result$nodes%>%write_csv(nodes_out)
    json_output = list(
        model_ids = model_path,
        data=result
        
    )
    write_json(json_output,
               json_out_path,
               pretty = TRUE,
               dataframe='columns',
               auto_unbox = TRUE)
}
model_df<-label_df%>%distinct(model_id,chunk_name,K)
splits<-model_df%>%arrange(K)%>%split(.$chunk_name)%>%
    lapply(function(x) x$model_id)
paths<-splits[splits%>%map(length)>1]%>%unname()

cust_paths<-list(
    c("word_500_8k", "word_500_ol_15k","word_500_18k"),
    c("sent_200_8k", "word_200_8k","word_500_8k"),
    c("word_200_8k","sent_200_8k","word_500_8k"),
    c("word_200_8k","word_500_8k","sent_200_8k"),
    c("document_10k","page_10k","sent_500_11k","paragraph_11k"),
    c("paragraph_14k","word_200_15k","word_500_ol_15k"),
    c("sent_200_17k", "sent_500_17k","word_500_18k"),
    c("word_500_18k","page_20k","document_23k")
)
all_paths<-c(paths,cust_paths)

walk(cust_paths,make_save_sankey_prep)
