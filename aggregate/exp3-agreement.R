#!/usr/bin/env Rscript

library(irr)

df <- read.csv('cf-results.csv')

df$worker  <- factor(df$worker)
df$unit    <- factor(df$unit)
df$relevant <- as.integer(ifelse(df$relevant == 'True', 1, 0))

degree  <- aggregate(worker ~ unit, data=df, FUN=length)
workers <- levels(df$worker)
tasks   <- levels(df$unit)

ratings <- matrix(nrow=length(workers), ncol=length(tasks))

for (i in 1:nrow(df)) {
  row <- df[i,]
  ratings[row$worker, row$unit] <- row$relevant
}

rm(i, row)

alpha <- kripp.alpha(ratings)
print(alpha)
