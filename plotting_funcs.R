plotRemoved_custom<-function (documents, lower.thresh,chosen_thresh) {
    require(stm)
    
    lower.thresh <- sort(lower.thresh)
    triplet <- doc.to.ijv(documents)
    wordcounts <- tabulate(triplet$j)
    tokencount <- tabulate(rep(triplet$j, times = triplet$v))
    drop <- sapply(lower.thresh, function(x) which(wordcounts <= 
                                                       x), simplify = FALSE)
    nwords <- unlist(lapply(drop, length))
    ntokens <- unlist(lapply(drop, function(x) sum(tokencount[x])))
    docthresh <- unlist(lapply(documents, function(x) max(wordcounts[x[1, 
    ]])))
    ndocs <- sapply(lower.thresh, function(x) sum(docthresh <= 
                                                      x), simplify = TRUE)
    oldpar <- par(no.readonly = TRUE)
    par(mfrow = c(1, 3), oma = c(2, 2, 2, 2))
    plot(lower.thresh, ndocs, type = "n", xlab = "", ylab = "Number of Documents Removed", 
         main = "Documents Removed by Threshold")
    lines(lower.thresh, ndocs, lty = 1, col = 1)
    abline(a = length(documents), lty = 2, b = 0, col = "red")
    plot(lower.thresh, nwords, type = "n", xlab = "Threshold (Minimum No. Documents Appearing)", 
         ylab = "Number of Words Removed", main = "Words Removed by Threshold")
    lines(lower.thresh, nwords, lty = 1, col = 1)
    abline(a = length(tokencount), lty = 2, b = 0, col = "red")
    plot(lower.thresh, ntokens, type = "n", xlab = "", ylab = "Number of Tokens Removed", 
         main = "Tokens Removed by Threshold")
    lines(lower.thresh, ntokens, lty = 1, col = 1)
    abline(a = sum(tokencount), lty = 2, b = 0, col = "red")
    par(oldpar)
    
    return(invisible(list(lower.thresh = lower.thresh, ndocs = ndocs, 
                          nwords = nwords, ntokens = ntokens)))
}