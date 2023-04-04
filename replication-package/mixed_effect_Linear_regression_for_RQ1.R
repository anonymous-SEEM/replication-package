library(lmerTest)
library(car)
library(rsq)
df1 <- read.csv('data/data_for_RQ1/go_data_for_RQ1.csv')
df2 <- read.csv('data/data_for_RQ1/bootstrap_data_for_RQ1.csv')
df3 <- read.csv('data/data_for_RQ1/react_data_for_RQ1.csv')
df4 <- read.csv('data/data_for_RQ1/tensorflow_data_for_RQ1.csv')
df5 <- read.csv('data/data_for_RQ1/rails_data_for_RQ1.csv')
df6 <- read.csv('data/data_for_RQ1/vue_data_for_RQ1.csv')
df7 <- read.csv('data/data_for_RQ1/electron_data_for_RQ1.csv')
df8 <- read.csv('data/data_for_RQ1/rust_data_for_RQ1.csv')

df1$project <- rep(c('go'),times=length(df1[,1]))
df2$project <- rep(c('bootstrap'),times=length(df2[,1]))
df3$project <- rep(c('react'),times=length(df3[,1]))
df4$project <- rep(c('tensorflow'),times=length(df4[,1]))
df5$project <- rep(c('rails'),times=length(df5[,1]))
df6$project <- rep(c('vue'),times=length(df6[,1]))
df7$project <- rep(c('electron'),times=length(df7[,1]))
df8$project <- rep(c('rust'),times=length(df8[,1]))

data <- rbind(df1,df2,df3,df4,df5,df6,df7,df8)

data$IssueAvgUser <- data$IssueAvgEvent/data$UserAvgEvent
data[is.na(data)]<-0
data[data==Inf]<-0
data$IssueAvgUser_standard <- scale(data$IssueAvgUser)

fm1 <- lmer(entropy_for_whole_project_standard~NumEliteUser_standard+ NumPeripheralUser_standard+ RatioEliteUser_standard+ UserAvgEvent_standard+ projectAge_standard+ NumOpenIssue_standard+NumOpenPull_standard+ IssueAvgEvent_standard + IssueAvgUser_standard+  (0+NumEliteUser_standard| project),data=data)
summary(fm1)
rsq(fm1)
Anova(fm1,type="II")

fm2 <- lmer(entropy_for_peripheral_developer_standard~NumEliteUser_standard+ NumPeripheralUser_standard+ RatioEliteUser_standard+ UserAvgEvent_standard+ projectAge_standard+ NumOpenIssue_standard+NumOpenPull_standard+ IssueAvgEvent_standard + IssueAvgUser_standard+  (0+NumEliteUser_standard| project),data=data)
summary(fm2)
rsq(fm2)
Anova(fm2,type="II")
