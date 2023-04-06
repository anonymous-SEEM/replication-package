library(lme4)
library(car)
library(plm)

regression <- function(repo){
	url = paste0('data/data_for_RQ3/',repo, '_data_for_RQ3.csv')
	df <- read.csv(url)
	fm1 <- lm(entropy_for_peripheral_developer_standard~communicative_standard+organizational_standard+typical_standard+supportive_standard,data=df1)
	print(summary(fm1))
	print(Anova(fm1,type="II"))
}

#['go','bootstrap','react','tensorflow','rails','vue','electron','rust']
regression('go')