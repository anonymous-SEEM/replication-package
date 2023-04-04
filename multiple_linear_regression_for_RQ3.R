['go','bootstrap','react','tensorflow','rails','vue','electron','rust']
library(lme4)
library(car)
library(plm)
df1 <- read.csv('D:/op/Desktop/data2analyse/goEventCountStandardy5.csv')
df2 <- read.csv('D:/op/Desktop/data2analyse/bootstrapEventCountStandardy5.csv')
df3 <- read.csv('D:/op/Desktop/data2analyse/reactEventCountStandardy5.csv')
df4 <- read.csv('D:/op/Desktop/data2analyse/tensorflowEventCountStandardy5.csv')
df5 <- read.csv('D:/op/Desktop/data2analyse/railsEventCountStandardy5.csv')
df6 <- read.csv('D:/op/Desktop/data2analyse/vueEventCountStandardy5.csv')
df7 <- read.csv('D:/op/Desktop/data2analyse/electronEventCountStandardy5.csv')
df8 <- read.csv('D:/op/Desktop/data2analyse/rustEventCountStandardy5.csv')

#cor(df1 [,c(4,5,6,7)],method="pearson")

data1 <- rbind(df1,df2,df3,df4)
data2 <- rbind(df5,df6,df7,df8)


fm1 <- lm(y5final~communicativeRepo+organizationalRepo+typicalRepo+supportiveRepo ,data=df8)
summary(fm1)
Anova(fm1,type="II")