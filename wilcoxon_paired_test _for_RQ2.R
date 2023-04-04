['blog', 'award', 'released', 'add-issue-template', 'add-pr-template', 'add-contributing', 'conf', 'plan', 'test-released', 'activity']

library(rcompanion)

df <- read.csv('D:/op/Desktop/data2wilcoxony5.csv')
data <- df
data['beforey1'] <- as.data.frame(lapply(df[c('beforey1')],as.numeric))
data['aftery1'] <- as.data.frame(lapply(df[c('aftery1')],as.numeric))
data['beforey5'] <- as.data.frame(lapply(df[c('beforey5')],as.numeric))
data['aftery5'] <- as.data.frame(lapply(df[c('aftery5')],as.numeric))

i <- 'blog'
i <- 'award'
i <- 'released'
i <- 'test-released'
i <- 'add-issue-template'
i <- 'add-pr-template'
i <- 'add-contributing'
i <- 'conf'
i <- 'activity'
i <- 'plan'
beforey1 <- df$beforey1[data$item == i]
aftery1 <- df$aftery1[data$item == i]
beforey5 <- df$beforey5[data$item == i]
aftery5 <- df$aftery5[data$item == i]


res1 <- wilcox.test(aftery1, beforey1, paired = TRUE,alternative = "greater")
res2 <- wilcox.test(aftery5, beforey5, paired = TRUE,alternative = "greater")
res3 <- wilcox.test(beforey1, aftery1, paired = TRUE,alternative = "greater")
res4 <- wilcox.test(beforey5, aftery5, paired = TRUE,alternative = "greater")


daftery1 <- as.data.frame(aftery1)
daftery1$label <- rep(c('after'),times=length(daftery1[,1]))
names(daftery1)[1] <- 'y1'

dbeforey1 <- as.data.frame(beforey1)
dbeforey1$label <- rep(c('before'),times=length(dbeforey1[,1]))
names(dbeforey1)[1] <- 'y1'
dfy1 <- rbind(dbeforey1,daftery1)

daftery5 <- as.data.frame(aftery5)
daftery5$label <- rep(c('after'),times=length(daftery5[,1]))
names(daftery5)[1] <- 'y5'

dbeforey5 <- as.data.frame(beforey1)
dbeforey5$label <- rep(c('before'),times=length(dbeforey5[,1]))
names(dbeforey5)[1] <- 'y5'
dfy5 <- rbind(dbeforey5,daftery5)

res1
res3
cliffDelta(y1~label,data = dfy1)
freemanTheta(x=dfy1$y1,g=dfy1$label)

res2
res4
cliffDelta(y5~label,data = dfy5)
freemanTheta(x=dfy5$y5,g=dfy5$label)
