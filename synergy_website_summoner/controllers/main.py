# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today SYNERGY.GG <nakaplatform@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import base64

import werkzeug
import werkzeug.urls

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from datetime import datetime as DT, timedelta
import calendar
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF, DEFAULT_SERVER_DATE_FORMAT as DATF
from pytz import timezone
import pytz
import urllib
import urllib2
import json
import time
import operator
import re, urlparse

key = u"74537082-db44-4916-9ca3-09f8f8b7638e"

summoner_fields = [
    'summoner',
    'matches',
    'win',
    'loose',
    'win_rate',
    'bro_participants',
    'champions',
    'roles',
    ]

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

def TsToDt(ts_date):
    ts_date = ts_date / 1000
    return DT.fromtimestamp(ts_date, tz=pytz.utc)

def DtToTs(date):
    dt_date = DT.strptime(date, DTF)
    timestamp = calendar.timegm(dt_date.timetuple()) * 1000
    return str(timestamp)

def GetJson(url):
    url = iriToUri(url)
    result = urllib2.urlopen(url).read()
    return json.loads(result)

class summoner(http.Controller):
    
    def get_profile(self, name, region):
        summoner_obj = request.registry['summoner.summoner']
        kwargs = {}
        name = name.replace(' ','')
        url = u"https://" + region + u".api.pvp.net/api/lol/" + region + u"/v1.4/summoner/by-name/" + name + u"?api_key=" + key
        result = GetJson(url)
        profile = result[name.lower()]
        domain = [('summoner_id','=', profile['id'])]
        summoner_ids = summoner_obj.search(request.cr, request.uid, domain, context=request.context)
        if summoner_ids:
            summoner_id = summoner_ids[0]
            summoner = summoner_obj.browse(request.cr, request.uid, summoner_id, context=request.context)
            old_revision_date = summoner.revision_date
            revision_date = TsToDt(profile['revisionDate'])
            vals = {
                'name': name.lower(),
                'summoner_name': profile['name'],
                'summoner_id': profile['id'],
                'revision_date': revision_date,
                'profile_icon_id': profile['profileIconId'],
                'summoner_level': profile['summonerLevel'],
                'region': region,
                    }
            summoner_obj.write(request.cr, request.uid,[summoner_id], vals, context=request.context)
        else:
            old_revision_date = False
            revision_date = TsToDt(profile['revisionDate'])
            vals = {
                'name': name.lower(),
                'summoner_name': profile['name'],
                'summoner_id': profile['id'],
                'revision_date': revision_date,
                'profile_icon_id': profile['profileIconId'],
                'summoner_level': profile['summonerLevel'],
                'region': region,
                    }
            summoner_id = summoner_obj.create(request.cr, request.uid, vals, context=request.context)
            summoner = summoner_obj.browse(request.cr, request.uid, summoner_id, context=request.context)
        kwargs['summoner'] = summoner
        kwargs['old_revision_date'] = old_revision_date
        return kwargs
    
    def get_matches(self, kwargs, region):
        match_obj = request.registry['summoner.matches']
        summoner = kwargs['summoner']
        matches_url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v2.2/matchlist/by-summoner/" +  summoner.summoner_id + "?api_key=" + key + "&rankedQueues=TEAM_BUILDER_DRAFT_RANKED_5x5"
        if kwargs.get('old_revision_date'):
            begin_time = DtToTs(kwargs['old_revision_date'])
            matches_url = matches_url + "&beginTime=" + begin_time
        result_matches = GetJson(matches_url)
        matches = []
        if result_matches.get('matches'):
            for match in result_matches['matches']:
                date = TsToDt(match['timestamp'])
                champion_id = match['champion']
                champion_url = "https://global.api.pvp.net/api/lol/static-data/" + region + "/v1.2/champion/" + str(champion_id) + "?api_key=" + key
                champion = GetJson(champion_url)
                champion_key = champion['key']
                champion_name = champion['name']
                vals = {
                    'summoner_id': summoner.id,
                    'date': date,
                    'champion_id': champion_id,
                    'champion_name': champion_name,
                    'champion_key': champion_key,
                    'region': match['region'],
                    'queue': match['queue'],
                    'season': match['season'],
                    'match_id': match['matchId'],
                    'role': match['role'],
                    'platform_id': match['platformId'],
                    'lane': match['lane'],
                        }
                match_id = match_obj.create(request.cr, request.uid, vals, context=request.context)
                match = match_obj.browse(request.cr, request.uid, match_id, context=request.context)
                matches.append(match)
        kwargs['matches'] = matches
        return kwargs
    
    def get_champion_details(self, kwargs, region):
        champion_list_by_id_url = "https://global.api.pvp.net/api/lol/static-data/" + region + "/v1.2/champion?dataById=True&api_key=" + key
        result_champion = GetJson(champion_list_by_id_url)
        champion_dict = result_champion['data']
        champions = {}
        roles = {}
        for match in kwargs['matches']:
            if match.lane == 'MID':
                official_role = 'MID'
            elif match.lane == 'TOP':
                official_role = 'TOP'
            elif match.lane == 'JUNGLE':
                official_role = 'JNG'
            elif match.lane == 'BOTTOM':
                official_role = 'BOT'
                if match.lane == 'DUO_SUPPORT':
                    official_role = 'SUP'
                elif match.lane == 'DUO_CARRY':
                    official_role = 'ADC'
            match.write({'official_role': official_role})
        return kwargs

    def get_match_details(self, kwargs, region):
        summoner = kwargs['summoner']
        summoner_obj = request.registry['summoner.summoner']
        match_obj = request.registry['summoner.matches']
        details_obj = request.registry['summoner.matches.details']
        details_participants_obj = request.registry['summoner.matches.details.participants']
        details_participants_stats_obj = request.registry['summoner.matches.details.participants.stats']
        details_participantidentities_obj = request.registry['summoner.matches.details.participantidentities']
        details_participantidentities_player_obj = request.registry['summoner.matches.details.participantidentities.player']
        details_teams_obj = request.registry['summoner.matches.details.teams']
        for match in kwargs['matches']:
            match_id = match.match_id
            match_url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v2.2/match/" + str(match_id) + "?api_key=" + key
            time.sleep(1)
            result_match = GetJson(match_url)
            match_creation = TsToDt(result_match.get('matchCreation'))
            match_duration = str(timedelta(seconds=result_match.get('matchDuration')))
            vals = {
                'matchid': result_match.get('matchId'),
                'matchtype': result_match.get('matchType'),
                'matchcreation': match_creation,
                'platformid':  result_match.get('platformId'),
                'matchmode':  result_match.get('matchMode'),
                'matchversion':  result_match.get('matchVersion'),
                'mapid':  result_match.get('mapId'),
                'season':  result_match.get('season'),
                'queuetype':  result_match.get('queueType'),
                'matchduration': match_duration,
            }
            match_details_id = details_obj.create(request.cr, request.uid, vals, request.context)
            match_id = match_obj.write(request.cr, request.uid, [match.id], {'match_details_id': match_details_id}, context=request.context)
            ## STILL NEED TO IMPLEMENT RUNES AND MASTERIES
            for participant in result_match.get('participants'):
                vals = {
                    'spell1id': participant.get('spell1Id'),
                    'spell2id': participant.get('spell2Id'),
                    'participantid': participant.get('participantId'),
                    'championid': participant.get('championId'),
                    'teamid': participant.get('teamId'),
                    'highestachievedseasontier': participant.get('highestAchievedSeasonTier'),
                    'match_details_id': match_details_id,
                }
                match_details_participant_id = details_participants_obj.create(request.cr, request.uid, vals, request.context)
                stats = participant.get('stats')
                vals = {}
                for item in stats.items():
                    vals[item[0].lower()] = item[1]
                vals['match_details_participant_id'] = match_details_participant_id
                details_participants_stats_id = details_participants_stats_obj.create(request.cr, request.uid, vals, request.context)
                details_participants_obj.write(request.cr, request.uid,[match_details_participant_id], {'stats_id': details_participants_stats_id}, request.context)
            for participantidentity in result_match.get('participantIdentities'):
                vals = {
                    'participantid': participantidentity.get('participantId'),
                    'match_details_id': match_details_id,
                }
                match_details_participantidentities_id = details_participantidentities_obj.create(request.cr, request.uid, vals, request.context)
                player = participantidentity.get('player')
                vals = {}
                for item in player.items():
                    vals[item[0].lower()] = item[1]
                vals['match_details_participantidentities_id'] = match_details_participantidentities_id
                details_participantidentities_player_id = details_participantidentities_player_obj.create(request.cr, request.uid, vals, request.context)
                details_participantidentities_player = details_participantidentities_player_obj.browse(request.cr, request.uid, details_participantidentities_player_id, request.context)
                if details_participantidentities_player.summonerid == summoner.summoner_id:
                    match_obj.write(request.cr, request.uid, [match.id], {'participant_id': participantidentity.get('participantId')}, request.context)
                details_participantidentities_id = details_participantidentities_obj.write(request.cr, request.uid,[match_details_participantidentities_id], {'player': details_participantidentities_player_id}, request.context)
            for team in result_match.get('teams'):
                vals = {}
                for item in team.items():
                    vals[item[0].lower()] = item[1]
                vals['match_details_id'] = match_details_id
                details_teams_obj.create(request.cr, request.uid, vals, request.context)
        return kwargs 
    
    def complete_matches(self, kwargs):
        match_obj = request.registry['summoner.matches']
        details_participants_obj = request.registry['summoner.matches.details.participants']
        for match in kwargs['matches']:
            details_participant_ids = details_participants_obj.search(request.cr, request.uid, [('match_details_id','=', match.match_details_id.id), ('participantid','=', match.participant_id)], context=request.context)
            if details_participant_ids:
                details_participant_id = details_participant_ids[0]
                details_participant = details_participants_obj.browse(request.cr, request.uid, details_participant_id, context=request.context)
                kills = float(details_participant.stats_id.kills)
                deaths = float(details_participant.stats_id.deaths)
                assists = float(details_participant.stats_id.assists)
                if deaths == 0:
                    kda = "Perfect"
                else:
                    kda = (kills + assists) / deaths
                    kda = float("{0:.2f}".format(kda))
                if details_participant.stats_id.winner:
                    win = True
                    loose = False
                else:
                    win = False
                    loose = True
                if details_participant.spell1id:
                    spell1 = details_participant.spell1id
                    spell1_url = "https://global.api.pvp.net/api/lol/static-data/euw/v1.2/summoner-spell/" + spell1 +"?api_key=" + key
                    spell1 = GetJson(spell1_url)
                    print spell1
                if details_participant.spell2id:
                    spell2 = details_participant.spell2id
                    spell2_url = "https://global.api.pvp.net/api/lol/static-data/euw/v1.2/summoner-spell/" + spell2 +"?api_key=" + key
                    spell2 = GetJson(spell2_url)
                    print spell2
                vals = {
                    'kills': kills,
                    'deaths': deaths,
                    'assists': assists,
                    'kda': kda,
                    'win': win,
                    'loose': loose,
                    'item0': details_participant.stats_id.item0,
                    'item1': details_participant.stats_id.item1,
                    'item2': details_participant.stats_id.item2,
                    'item3': details_participant.stats_id.item3,
                    'item4': details_participant.stats_id.item4,
                    'item5': details_participant.stats_id.item5,
                    'item6': details_participant.stats_id.item6,
                    'minionskilled': int(details_participant.stats_id.minionskilled) + int(details_participant.stats_id.neutralminionskilled),
                    'champlevel': details_participant.stats_id.champlevel,
                    'spell1id': spell1.get('key'),
                    'spell2id': spell2.get('key'),
                }
                match_obj.write(request.cr, request.uid, [match.id], vals, context=request.context)
        return kwargs    
    
    def get_stored_data(self, kwargs):
        match_obj = request.registry['summoner.matches']
        summoner = kwargs['summoner']
        matches = []
        for match_id in match_obj.search(request.cr, request.uid, [('summoner_id','=', summoner.id)], context=request.context):
            match = match_obj.browse(request.cr, request.uid, match_id, context=request.context)
            matches.append(match)
        kwargs['matches'] = matches
        return kwargs    
    
    @http.route([
         '/summoner',
     ], type='http', auth="public", website=True)
    def summoner(self, name=None, **kwargs):
        values = {}
        if kwargs:
            name = kwargs.get('summoner_name')
            region = kwargs.get('summoner_region')
            kwargs = self.get_profile(name, region)
            kwargs = self.get_matches(kwargs, region)
            kwargs = self.get_champion_details(kwargs, region)
            kwargs = self.get_match_details(kwargs, region)
            kawrgs = self.complete_matches(kwargs)
            kwargs = self.get_stored_data(kwargs)
        for field in summoner_fields:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return request.website.render("synergy_website_summoner.summoner", values)

