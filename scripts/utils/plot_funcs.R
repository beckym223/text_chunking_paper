get_plot_df<-function(model,metadata){
    require(stm)
    require(dplyr)
    est<-estimateEffect(~s(year),model,metadata)
    
    p<-plot(est,'year',method='continuous',omit.plot=T)
    k=model$settings$dim$K
    plot<-tibble()
    for (i in 1:k){
        df<-tibble(x=p$x,
                   y=p$means[[i]],
                   topic = as.integer(i)
        )%>%mutate(
            lower_ci=p$ci[[i]][1,],
            upper_ci=p$ci[[i]][2,]
        )
        plot<-bind_rows(plot,df)%>%
            distinct()
    }
    plot%>%
        mutate(Topic = as.factor(topic))
}

get_prop_prevalence<-function(model,prepped_docs){
    require(stm)
    require(dplyr)

    data<-prepped_docs$meta
    data$lengths<-prepped_docs$documents%>%sapply(sum)
    K = model$settings$dim$K
    topics = seq(K)
    proportions<-as.data.frame(model$theta)
    colnames(proportions) = topics
    t<-proportions%>%bind_cols(data)%>%
        group_by(year)%>%
        mutate(prop_of_doc=lengths/sum(lengths))%>%
        summarise(across(all_of(topics),function(x){sum(x*prop_of_doc)}))%>%
        pivot_longer(cols=seq(2,K+1))%>%
        mutate(topic = as.factor(name))
}

get_labels<-function(model,n=4,wrap=2,with_num=T){
    require(dplyr)
    require(stm)
    require(stringr)
    tibble(t=seq(model$settings$dim$K))%>%
        bind_cols(labelTopics(model,n=n)$frex%>%
                      as_tibble()
        )%>%
        apply(1,
              function(x){str_flatten_comma(x)%>%
                      str_replace("\\s*(\\d*),",ifelse(with_num,"Topic \\1:",""))%>%
                      str_replace_all(sprintf("(([\\w]+, ?){%d})( )",wrap),
                                      "\\1\n"
                      )})
}