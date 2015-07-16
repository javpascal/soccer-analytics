#A web scraper for Brazil Serie A team data from Globo Esporte.

import requests
import pandas as pd
from collections import OrderedDict
from bs4 import BeautifulSoup as bs

header= 'http://globoesporte.globo.com/futebol/times/'
response = requests.get(header)
soup = bs(response.text)

#The site has a menu with links to the pages of all 20 first division teams, so I use that as my starting point.
#There are other teams there are well, so I only take the first 20 elements.
teams = soup.findAll('li',{'class':'glb-ge-mosaico-list-item'})
team_list = [pl for pl in teams]
serieA_team_list = team_list[:20]

players_list = []

for team in serieA_team_list:
    team_link = team.find('a').get('href')
    team_name = team.find('a').get('title')
	
    response2 = requests.get(team_link)
    soup2 = bs(response2.text)
	
    players = soup2.findAll('li',{'class':'ge-card-elenco-jogador'})
    temp_player_list = [player for player in players]
    
    for player in temp_player_list:
        player_dict = OrderedDict()
        player_dict['Team'] = team_name
        player_dict['Name'] = player.find('span',{'class':'ge-card-elenco-jogador-nome'}).text.strip()    
        player_dict['Age'] = player.find('span',{'class':'ge-card-elenco-jogador-detalhes'}).text.strip()
		
		#This info is on players with injuries/suspensions and how long they are expected to be unavailable.
		#Since it's conditional, I put it in a try and except.
        try:
            player_dict['Status'] = player.find('span',{'class':'ge-card-elenco-status-status status-texto'}).text.strip()
            player_dict['Notes'] = player.find('span',{'class':'ge-card-elenco-status-tempo'}).text.strip()
        except:
            player_dict['Status'] = 'Available'
            player_dict['Notes'] = 'N/A'

        players_list.append(player_dict) 

#Now that that's done I manipulate the data into a way that I want, and output it to a csv.	
players_df = pd.DataFrame(players_list)
players_df2 = players_df[['Team','Name','Age','Status','Notes']]
players_df2.to_csv('globo_player_data.csv')