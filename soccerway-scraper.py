# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 09:49:50 2015

@author: Gordon
"""

from bs4 import BeautifulSoup as bs
import requests
from itertools import chain
import collections
import pandas as pd
 
#The data is being scraped from Soccer Way. I need to reuse the header later on, so that's the reason for...
#...separating the original link into two.
 
header = 'http://int.soccerway.com'
league_ext = '/national/brazil/serie-a/2015/regular-season/r30889/?ICID=TN_02_01_10'
league_header = header + league_ext
 
response = requests.get(league_header)
soup = bs(response.text)
teams = soup.findAll('td',{'class':"text"})
 
#The page has a tiny window with information from five teams in other leagues, so I cut off the last 5 elements to exclude them.
teams = teams[:-5]
 
players_list = []
 
for team in teams:
    note_team = team.text
    for item in team.children:
        team_url = item.get('href')
    
    #Here's the reason for the header variable before.
    squad_list = header+team_url+'squad/'
    
    response2 = requests.get(squad_list)
    soup2 = bs(response2.text)
    
    #The player's data in scored in odd and even classes, so I got them separately and then combined them.
    
    team_info_odd = soup2.findAll('tr',{'class':'odd'})
    team_info_even = soup2.findAll('tr',{'class':'even'})
    team_info = [item for item in chain(team_info_even,team_info_odd)]
    
    for player in team_info:
        data_point_list = []
        for data_point in player.children:
            data_point_list.append(data_point)        
             
        player_dict = collections.OrderedDict()
        
        player_dict['name'] = data_point_list[3].text
        player_dict['team'] = note_team
        
        #Errors made this try and except statement a necessity. Turns out there was more than player info stored in those tags.
        #I sidestepped those by setting the corresponding values to -1.
        
        try:
            player_dict['age'] = data_point_list[7].text
            player_dict['position'] = data_point_list[9].text
            player_dict['minutes_played'] = data_point_list[11].text
        except:
            player_dict['age'] = -1
            player_dict['position'] = -1
            player_dict['minutes_played'] = -1
        
        players_list.append(player_dict)
 
#Now my dictionary is a dataframe.
players_df = pd.DataFrame(players_list)
 
#And the unruly elements have been removed, some of which are players without much data. They're not really relevant.
players_df2 = players_df[players_df.position!=-1]
 
#I retool my dataframe to collect the categories I'm interested in--at least for now--and output the data to a csv. 
players_df2 = players_df2[['name','team','age','position','minutes_played']]
players_df2.to_csv('brazil_serieA_players_round9Info.csv')
