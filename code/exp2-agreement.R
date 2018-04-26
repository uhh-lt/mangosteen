#!/usr/bin/env Rscript

library(irr)

args = commandArgs(trailingOnly=TRUE)

for (n in seq(1, length(args))) {
  print(args[n])
  df <- read.csv(args[n])

  df$worker <- factor(df$worker)
  df$unit   <- factor(df$unit)
  df$bad    <- factor(df$bad, ordered=T)

  degree  <- aggregate(worker ~ unit, data=df, FUN=length)
  workers <- levels(df$worker)
  tasks   <- levels(df$unit)

  ratings <- matrix(nrow=length(workers), ncol=length(tasks))

  for (i in 1:nrow(df)) {
    row <- df[i,]
    ratings[row$worker, row$unit] <- row$bad
  }

  rm(i, row)

  alpha <- kripp.alpha(ratings, 'nominal')
  print(alpha)
}
