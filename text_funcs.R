get_lower_thresh <- function(chunk_name) {
    
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




get_num_words <-function(text){
    require(stringr)
    map_int(text, ~ str_count(.x, "\\b[\\w-]+\\b[^\\w]*")[[1]])
}

get_sentences <- function(text_to_split){
    require(stringi)
    stri_split_boundaries(text_to_split,type='sentence')%>%
        lapply(stri_trim_right)
}


combine_chunks_to_size <- function(chunk_lengths, target_size, split_before_target = FALSE) {
    new_chunk_idxs <- integer(0)  # output indices
    current_idx <- 0             # running group index
    current_join_len <- 0           # running length of current group
    current_join_num_chunks <- 0
    for (i in seq_along(chunk_lengths)) {
        current_chunk_len <- chunk_lengths[i]
        current_join_len <- current_join_len + current_chunk_len
        
        if (current_join_len<target_size){
            current_join_num_chunks <- current_join_num_chunks + 1
            #print(sprintf("On index %d with new join length of %d made up of %d chunks. Continuing", 
            #             current_idx, current_join_len, current_join_num_chunks))
            
            
        } else if ((current_join_len == target_size) | (!split_before_target)){
            #print(sprintf(" on index %d with %d chunks.", current_idx, current_join_num_chunks))
            current_join_num_chunks = current_join_num_chunks+1
            
            # print(sprintf("Matched or supassed target size with current length %d, extending list with index %d and %d chunks", 
            #              current_join_len, current_idx, current_join_num_chunks))
            new_chunk_idxs <- c(new_chunk_idxs, rep(current_idx, current_join_num_chunks))
            
            #reset
            current_idx <-current_idx + 1
            current_join_len <- 0
            current_join_num_chunks <-0
            
        } else {
            # means it surpasses the target
            # print(sprintf("passed target and splitting before: extending list with index %d and %d chunks",
            #              current_idx, current_join_num_chunks))
            new_chunk_idxs <- c(new_chunk_idxs, rep(current_idx, current_join_num_chunks))
            
            #starting the next index
            current_join_num_chunks <- 1
            current_idx <- current_idx + 1
            current_join_len <- current_chunk_len
            
            
            
        }
    }
    if (current_join_num_chunks>0){
        #  print(sprintf("leftover chunks: extending list with index %d and %d chunks", current_idx, current_join_num_chunks))
        new_chunk_idxs <- c(new_chunk_idxs, rep(current_idx, current_join_num_chunks)) #add any remaining chunks
        
    }
    if (length(new_chunk_idxs) != length(chunk_lengths)) {
        stop(sprintf("\nIndex list of length %d does not match sentence list length %d",
                     length(new_chunk_idxs), length(chunk_lengths)))
    }
    
    new_chunk_idxs
}

make_sentence_chunks <- function(doc_df, target_size) {
    require(dplyr)
    
    sentence_df <- doc_df %>%
        mutate(sentence = get_sentences(text)) %>%
        unnest(sentence) %>%
        filter(str_detect(sentence, "[a-zA-Z]+")) %>%
        mutate(num_words = get_num_words(sentence)) %>%
        group_by(text_id) %>%
        mutate(sent_idx = combine_chunks_to_size(
            num_words,
            target_size,
            split_before_target = FALSE
        )) %>%
        group_by(text_id, sent_idx) %>%
        summarize(
            year = first(year),
            text = paste(sentence, collapse = " "),
            .groups = "drop"
        ) %>%
        mutate(
            text_id = paste0(text_id, "-", sent_idx)
        ) %>%
        select(text_id, year, text)
    
    sentence_df
}

preprocess_make_dfm <- function(chunked_df) {
    require(quanteda)
    require(dplyr)
    require(stm)
    
    corpus <- corpus(
        chunked_df,
        docid_field = "text_id",
        text_field  = "text",
        unique_docnames = TRUE
    )
    
    tokens <- tokens(
        corpus,
        remove_punct = TRUE,
        remove_symbols = TRUE,
        remove_numbers = TRUE,
        remove_url = FALSE,
        remove_separators = TRUE,
        split_hyphens = FALSE,
        split_tags = FALSE,
        include_docvars = TRUE,
        padding = FALSE,
        concatenator = "_"
    )
    
    tokens_processed <- tokens %>%
        tokens_tolower() %>%
        
        ## --- multi-word normalization ---
        tokens_compound(
            pattern = phrase(c("per cent",'market place'))
        ) %>%
        tokens_replace(
            pattern = c("per_cent",'market_place',"to-day", "per-cent", "market-place"),
            replacement = c("percent",'marketplace',"today", "percent", "marketplace")
        ) %>%
        
        ## --- standard preprocessing ---
        tokens_remove(stopwords("en")) %>%
        tokens_wordstem()
    
    metadata <- chunked_df %>%
        select(text_id, year)
    
    dfm <- dfm(tokens_processed)
    dfm_stm<- dfm%>% convert(to = "stm", docvars = metadata)
    result<-list(dfm = dfm, dfm_stm=dfm_stm)
    return(result)
}

chunk_documents_by_word <- function(doc_df, chunk_size = 500, overlap = 0) {
    require(tibble)
    require(quanteda)
    toks<-str_extract_all(doc_df$text,"\\b[\\w-]+\\b(?=[^\\w]*)")%>%tokens()

    docnames(toks) <- doc_df$text_id
    
    # chunk tokens
    toks_chunked <- tokens_chunk(
        toks,
        size = chunk_size,
        overlap = overlap
    )
    
    # collapse tokens back to text
    chunk_text <- sapply(toks_chunked, paste, collapse = " ")
    
    # build chunk-level dataframe
    chunk_df <- tibble(
        chunk_id = str_replace_all(names(chunk_text), "\\.", "-"),
        text_id = str_remove(names(chunk_text), "\\.[0-9]+$"),
        text = unname(chunk_text)
    ) %>%
        left_join(
            doc_df %>% select(text_id, year),
            by = "text_id"
        ) %>%
        rename(doc_id=text_id,
               text_id=chunk_id
               )%>%
        select(doc_id,text_id,year,text)
    
    return(chunk_df)
}
