#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import time

import numpy as np
import pandas as pd

from bs4 import BeautifulSoup

from pydantic import BaseModel
from typing import List, Optional

from selenium import webdriver

from supabase import create_client, Client

from bs4 import BeautifulSoup as BS
import bs4
import soupsieve


# In[ ]:


class MatchEvent(BaseModel):
    id: int
    event_id: int
    minute: int
    second: Optional[float] = None
    team_id: int
    player_id: int
    x: float
    y: float
    end_x: Optional[float] = None
    end_y: Optional[float] = None
    qualifiers: List[dict]
    is_touch: bool
    blocked_x: Optional[float] = None
    blocked_y: Optional[float] = None
    goal_mouth_z: Optional[float] = None
    goal_mouth_y: Optional[float] = None
    is_shot: bool
    card_type: bool
    is_goal: bool
    type_display_name: str
    outcome_type_display_name: str
    period_display_name: str


# In[ ]:


def insert_match_events(df, supabase):
    events = [
        MatchEvent(**x).dict()
        for x in df.to_dict(orient='records')
    ]
    
    execution = supabase.table('matchevent').upsert(events).execute()


# In[ ]:


class Player(BaseModel):
    player_id: int
    shirt_no: int
    name: str
    age: int
    position: str
    team_id: int


# In[ ]:


def insert_players(team_info, supabase):
    players = []
    for team in team_info:
        for player in team['players']:
            players.append({
                'player_id': player['playerId'],
                'team_id': team['team_id'],
                'shirt_no': player['shirtNo'],
                'name': player['name'],
                'position': player['position'],
                'age': player['age']
            })
            
    execution = supabase.table('player').upsert(players).execute()


# In[ ]:


supabase_password = 'postgres12345@A'
project_url = 'https://ppwrgbgkjhsvumgxofuu.supabase.co'
api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBwd3JnYmdramhzdnVtZ3hvZnV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY1NjA5NTEsImV4cCI6MjA1MjEzNjk1MX0.xEpiyf7xiY4pu6iCTJ2UesAIAwupVwE7W-fzoG-Ser0'

supabase = create_client(project_url, api_key)


# In[ ]:


driver = webdriver.Chrome()


# In[ ]:


def scrape_match_events(whoscored_url, driver):
    
    driver.get(whoscored_url)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    element = soup.select_one('script:-soup-contains("matchCentreData")')
    
    matchdict = json.loads(element.text.split("matchCentreData: ")[1].split(',\n')[0])
    
    match_events = matchdict['events']
    
    df = pd.DataFrame(match_events)
    
    df.dropna(subset='playerId', inplace=True)
    
    df = df.where(pd.notnull(df), None)
    
    df = df.rename(
    {
        'eventId': 'event_id',
        'expandedMinute': 'expanded_minute',
        'outcomeType': 'outcome_type',
        'isTouch': 'is_touch',
        'playerId': 'player_id',
        'teamId': 'team_id',
        'endX': 'end_x',
        'endY': 'end_y',
        'blockedX': 'blocked_x',
        'blockedY': 'blocked_y',
        'goalMouthZ': 'goal_mouth_z',
        'goalMouthY': 'goal_mouth_y',
        'isShot': 'is_shot',
        'cardType': 'card_type',
        'isGoal': 'is_goal'
    },
        axis=1
    )
    
    df['period_display_name'] = df['period'].apply(lambda x: x['displayName'])
    df['type_display_name'] = df['type'].apply(lambda x: x['displayName'])
    df['outcome_type_display_name'] = df['outcome_type'].apply(lambda x: x['displayName'])
    
    df.drop(columns=["period", "type", "outcome_type"], inplace=True)
    
    if 'is_goal' not in df.columns:
        df['is_goal'] = False
        
    if 'is_card' not in df.columns:
        df['is_card'] = False
        df['card_type'] = False
        
    df = df[~(df['type_display_name'] == "OffsideGiven")]
    
    df = df[[
        'id', 'event_id', 'minute', 'second', 'team_id', 'player_id', 'x', 'y', 'end_x', 'end_y',
        'qualifiers', 'is_touch', 'blocked_x', 'blocked_y', 'goal_mouth_z', 'goal_mouth_y', 'is_shot',
        'card_type', 'is_goal', 'type_display_name', 'outcome_type_display_name',
        'period_display_name'
    ]]
    
    df[['id', 'event_id', 'minute', 'team_id', 'player_id']] = df[['id', 'event_id', 'minute', 'team_id', 'player_id']].astype(np.int64)
    df[['second', 'x', 'y', 'end_x', 'end_y']] = df[['second', 'x', 'y', 'end_x', 'end_y']].astype(float)
    df[['is_shot', 'is_goal', 'card_type']] = df[['is_shot', 'is_goal', 'card_type']].astype(bool)
    
    df['is_goal'] = df['is_goal'].fillna(False)
    df['is_shot'] = df['is_shot'].fillna(False)
    
    for column in df.columns:
        if df[column].dtype == np.float64 or df[column].dtype == np.float32:
            df[column] = np.where(
                np.isnan(df[column]),
                None,
                df[column]
            )
            
            
    insert_match_events(df, supabase)
    
    
    team_info = []
    team_info.append({
        'team_id': matchdict['home']['teamId'],
        'name': matchdict['home']['name'],
        'country_name': matchdict['home']['countryName'],
        'manager_name': matchdict['home']['managerName'],
        'players': matchdict['home']['players'],
    })

    team_info.append({
        'team_id': matchdict['away']['teamId'],
        'name': matchdict['away']['name'],
        'country_name': matchdict['away']['countryName'],
        'manager_name': matchdict['away']['managerName'],
        'players': matchdict['away']['players'],
    })
    
    insert_players(team_info, supabase)
    
    return print('Success')


# In[ ]:


ws_url = "https://www.whoscored.com/Matches/1821302/Live/England-Premier-League-2024-2025-Liverpool-Manchester-United"


# In[ ]:


driver.get(ws_url)


# In[ ]:


scrape_match_events(whoscored_url=url,driver=driver)


# # For a season/competition data

# In[ ]:


driver.get('https://www.whoscored.com/Teams/340/Fixtures/Portugal-Portugal')
time.sleep(3)


# In[ ]:


soup = BeautifulSoup(driver.page_source, 'html.parser')


# In[ ]:


all_urls = soup.select('a[href*="\/Live\/"]')
all_urls = list(set([
    'https://www.whoscored.com' + x.attrs['href']
    for x in all_urls
]))


# In[ ]:


for url in all_urls:
    print(url)
    scrape_match_events(
        whoscored_url=url,
        driver=driver
    )
    
    time.sleep(2)

