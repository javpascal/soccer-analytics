#Intro Stuff

library(openxlsx)
library(tidyr)
library(ggplot2)
library(dplyr)

bund_xg <- read.xlsx("data/bundesliga_xg_2015_2016.xlsx")

bund_xg.long <- gather(bund_xg, Status, Team, Home:Away)
bund_xg.long$xG <- ifelse(bund_xg.long$Status == 'Home', 
                          bund_xg.long$xG_H, 
                          bund_xg.long$xG_A)
bund_xg.long.team <- group_by(bund_xg.long, Team)

xg.plot <-  ggplot(data = bund_xg.long, 
       aes(x = GW, y = xG, group = Status, color = Status)) + 
  geom_point() + 
  geom_line() + 
  labs(title = 'Bundesliga 15/16', x = 'Game Week', y ='Expected Goals For') +
  facet_wrap(~Team)

xg.plot
ggsave(plot = xg.plot, filename = 'bund_xg_plot.png')

library(ggvis)

bund_xg.long[bund_xg.long$Team == 'Bayern',] %>% 
  ggvis(~GW, ~xG) %>% 
  layer_points() %>% layer_lines()
  #add_tooltip(function(df) df$GW)

library(rCharts)

p = rPlot(xG ~ GW, 
      data = bund_xg.long[bund_xg.long$Team == 'Bayern',], 
      color = 'Status', 
      type = 'line')

p$set(title = 'Bayern Munich (Bundesliga 15/16)')
p$guides(x = list(title = "Game Week"))
p$guides(y = list(title = "Expected Goals"))

#Webscraping

library(rvest)
library(RSelenium)

startServer()
mybrowser <- remoteDriver()
mybrowser$open()
mybrowser$navigate("http://us.soccerway.com/national/germany/bundesliga/20152016/regular-season/r31545/")
mybrowser$maxWindowSize()

#Clicks the game week button to order matches by game week at the top.
game.week <- mybrowser$findElement(using = 'css selector', 
                                    '#page_competition_1_block_competition_matches_summary_6_1_2')
game.week$clickElement()

game.week.results <- list()

#Appends the current page's results to the list, cutting off useless columns.
game.week.results[[length(game.week.results) + 1]] <- readHTMLTable(htmlParse(mybrowser$getPageSource()[[1]]))[[1]][, -c(1,2,6,7)]

#Does the above again for the previous page of results.
prev <- mybrowser$findElement(using = 'css selector', 
                              '#page_competition_1_block_competition_matches_summary_6_previous')
prev$clickElement()
game.week.results[[length(game.week.results) + 1]] <- readHTMLTable(htmlParse(mybrowser$getPageSource()[[1]]))[[1]][, -c(1,2,6,7)]

#Cycles through the rest of the results and adds them.
len <- length(game.week.results)

while(length(game.week.results) < 32) {
  prev$clickElement()
  Sys.sleep(3)
  game.week.results[[length(game.week.results) + 1]] <- readHTMLTable(htmlParse(mybrowser$getPageSource()[[1]]))[[1]][, -c(1,2,6,7)]
}

mybrowser$close()

#I only have xG data for 30 rounds. I have 32 rounds of scores in descending order.
#I need to get rid of the first two entries.

game.week.results.30 <- game.week.results[-c(1,2)]
df.scores  <- bind_rows(game.week.results.30)
colnames(df.scores) <- c('Home.Team', 'Score', 'Away.Team')
df.scores  <- separate(df.scores, Score, 
                       c('Home.Score', 'Away.Score'), 
                       sep = " - ", remove = T)
write.csv(x = df.scores, file = 'bundesliga_15_16_scores.csv', row.names = F)

##ther Stuff that Might come back to

library(zoo)
bayern.rolling.xg <- rollmean(
  bund_xg.long.team[bund_xg.long.team$Team == 'Bayern',][,4],
  5)

#ggplot(data = as.data.frame(bayern.rolling.xg)) + geom_line()
