# -*- coding: utf-8 -*-
import base64

import werkzeug
import werkzeug.urls

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
import urllib
import urllib2
import json
import time

key = "74537082-db44-4916-9ca3-09f8f8b7638e"

summoner_fields = [
    'summoner_name',
    'summoner_region',
    'id',
    'name', 
    'region', 
    'profileIconId', 
    'summonerLevel', 
    'revisionDate', 
    'matches',
    'win',
    'loose',
    'win_rate',
    ]

class summoner(http.Controller):
    
    def get_profile(self, name, region):
        url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v1.4/summoner/by-name/" + name + "?api_key=" + key
        result = urllib2.urlopen(url).read()
        result = json.loads(result)
        kwargs = result[name]
        kwargs['summoner_name'] = name
        kwargs['summoner_region'] = region
        return kwargs
    
    def get_matches(self, kwargs, region):
        matches_url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v2.2/matchlist/by-summoner/" +  str(kwargs['id']) + "?api_key=" + key + "&rankedQueues=TEAM_BUILDER_DRAFT_RANKED_5x5"
        result_matches = urllib2.urlopen(matches_url).read()
        result_matches = json.loads(result_matches)
        kwargs['matches'] = result_matches['matches']
        return kwargs
    
    def get_champion_details(self, kwargs, region):
        champion_list_by_id_url = "https://global.api.pvp.net/api/lol/static-data/" + region + "/v1.2/champion?dataById=True&api_key=" + key
        result_champion = urllib2.urlopen(champion_list_by_id_url).read()
        result_champion = json.loads(result_champion)
        champion_dict = result_champion['data']
        for match in kwargs['matches']:
            champion_id = match['champion']
            match['champion_name'] = champion_dict[str(champion_id)]['name']
            match['champion_icon_name'] = match['champion_name'].replace(' ','')
            if match['lane'] == 'MID':
                official_role = 'MID'
            elif match['lane'] == 'TOP':
                official_role = 'TOP'
            elif match['lane'] == 'JUNGLE':
                official_role = 'JUNGLE'
            elif match['lane'] == 'BOTTOM':
                official_role = 'BOT'
                if match['role'] == 'DUO_SUPPORT':
                    official_role = 'SUPPORT'
                elif match['role'] == 'DUO_CARRY':
                    official_role = 'ADC'
            match['official_role'] = official_role
        return kwargs

    def get_match_details(self, kwargs, region):
        kwargs['win'] = 0
        kwargs['loose'] = 0
        kwargs['win_rate']= 0
        for match in kwargs['matches']:
            match_id = match['matchId']
            match_url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v2.2/match/" + str(match_id) + "?api_key=" + key
            result_match = urllib2.urlopen(match_url).read()
            time.sleep(1)
            result_match = json.loads(result_match)
            participant_identities = result_match['participantIdentities']
            for participant_identity in participant_identities:
                player = participant_identity['player']
                if player['summonerId'] == kwargs['id']:
                    participant_id = participant_identity['participantId']
            participants = result_match['participants']        
            for participant in participants:
                if participant['participantId'] == participant_id:
                    stats = participant['stats']
                    match['kills'] = stats['kills']
                    match['deaths'] = stats['deaths']
                    match['assists'] = stats['assists']
                    if int(match['deaths']) == 0:
                        match['kda'] = "Perfect"
                    else:  
                        match['kda'] = str((float(match['kills']) + float(match['assists'])) / float(match['deaths']))
                    if stats['winner'] == True:
                        match['win'] = True
                        kwargs['win'] += 1
                    else:
                        match['loose'] = True
                        kwargs['loose'] += 1
        win_rate = float(kwargs['win']) / (float(kwargs['loose']) + float(kwargs['win']))
        kwargs['win_rate'] = win_rate * 100
        return kwargs 
    
    @http.route(['/page/synergy_website_summoner.summoner', '/summoner/update'], type='http', auth="public", website=True)
    def summoner(self, **kwargs):
        values = {}
        if kwargs:
            name = kwargs.get('summoner_name')
            region = kwargs.get('summoner_region')
            kwargs = self.get_profile(name, region)
            kwargs = self.get_matches(kwargs, region)
            kwargs = self.get_champion_details(kwargs, region)
            kwargs = self.get_match_details(kwargs, region)
        for field in summoner_fields:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return request.website.render("synergy_website_summoner.summoner", values)

