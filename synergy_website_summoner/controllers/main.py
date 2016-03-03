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
from operator import itemgetter
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
    'ranked_stats',
    'current_game'
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
        summoner_ids = summoner_obj.search(request.cr, 1, domain, context=request.context)
        if summoner_ids:
            summoner_id = summoner_ids[0]
            summoner = summoner_obj.browse(request.cr, 1, summoner_id, context=request.context)
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
            summoner_obj.write(request.cr, 1,[summoner_id], vals, context=request.context)
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
            summoner_id = summoner_obj.create(request.cr, 1, vals, context=request.context)
            summoner = summoner_obj.browse(request.cr, 1, summoner_id, context=request.context)
        kwargs['summoner'] = summoner
        kwargs['old_revision_date'] = old_revision_date
        return kwargs
    
    def get_matches(self, kwargs, region):
        match_obj = request.registry['summoner.matches']
        summoner = kwargs['summoner']
        matches_url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v2.2/matchlist/by-summoner/" +  summoner.summoner_id + "?api_key=" + key + "&rankedQueues=TEAM_BUILDER_DRAFT_RANKED_5x5"
#         if kwargs.get('old_revision_date'):
#             begin_time = DtToTs(kwargs['old_revision_date'])
#             matches_url = matches_url + "&beginTime=" + begin_time
        result_matches = GetJson(matches_url)
        matches = []
        if result_matches.get('matches'):
            for match in result_matches['matches']:
                date = TsToDt(match['timestamp'])
                match = {
                    'summoner_id': summoner.id,
                    'date': date,
                    'region': match['region'],
                    'champion_id': match['champion'],
                    'queue': match['queue'],
                    'season': match['season'],
                    'match_id': match['matchId'],
                    'role': match['role'],
                    'platform_id': match['platformId'],
                    'lane': match['lane'],
                        }
                matches.append(match)
        kwargs['matches'] = matches[:5]
        return kwargs
    
    def get_champion_details(self, kwargs, region):
        champ_obj = request.registry['summoner.champions']
        for match in kwargs['matches']:
            champ_ids = champ_obj.search(request.cr, 1, [('champion_id','=', int(match.get('champion_id')))], context=request.context)
            if champ_ids:
                champ = champ_obj.browse(request.cr, 1, champ_ids[0], context=request.context)
                champion_key = champ.key
                champion_name = champ.name
                vals = {
                    'champion_name': champion_name,
                    'champion_key': champion_key,
                        }
                match.update(vals)
            if match.get('lane') == 'MID':
                official_role = 'MID'
            elif match.get('lane') == 'TOP':
                official_role = 'TOP'
            elif match.get('lane') == 'JUNGLE':
                official_role = 'JNG'
            elif match.get('lane') == 'BOTTOM':
                official_role = 'BOT'
                if match.get('role') == 'DUO_SUPPORT':
                    official_role = 'SUP'
                elif match.get('role') == 'DUO_CARRY':
                    official_role = 'ADC'
            match['official_role'] = official_role
        return kwargs

    def get_match_details(self, kwargs, region):
        summoner = kwargs['summoner']
        summoner_obj = request.registry['summoner.summoner']
        match_obj = request.registry['summoner.matches']
        i = 0
        for match in kwargs['matches']:
            match_id = match.get('match_id')
            i += 1
            match_url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v2.2/match/" + str(match_id) + "?api_key=" + key
            result_match = GetJson(match_url)
            match_creation = TsToDt(result_match.get('matchCreation'))
            match_duration = str(timedelta(seconds=result_match.get('matchDuration')))
            match_details = {
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
            match['details'] = match_details
            participants = []
            for participant in result_match.get('participants'):
                vals = {
                    'spell1id': participant.get('spell1Id'),
                    'spell2id': participant.get('spell2Id'),
                    'participantid': participant.get('participantId'),
                    'championid': participant.get('championId'),
                    'teamid': participant.get('teamId'),
                    'highestachievedseasontier': participant.get('highestAchievedSeasonTier'),
                }
                participants.append(vals)
                stats = participant.get('stats')
                values = {}
                for item in stats.items():
                    values[item[0].lower()] = item[1]
                vals['stats'] = values
            match['participants'] = participants
            participantidentities = []
            for participantidentity in result_match.get('participantIdentities'):
                vals = {
                    'participantid': participantidentity.get('participantId'),
                }
                participantidentities.append(vals)
                player = participantidentity.get('player')
                values = {}
                for item in player.items():
                    values[item[0].lower()] = item[1]
                vals['player'] = values
                summoner_id = int(values.get('summonerid'))
                if summoner_id == int(summoner.summoner_id):
                    match['participant_id'] = participantidentity.get('participantId')
            match['participantidentities'] = participantidentities
        return kwargs 
    
    def complete_matches(self, kwargs):
        spell_obj = request.registry['summoner.spells']
        for match in kwargs['matches']:
            for participant in match.get('participants'):
                if participant.get('participantid') == match.get('participant_id'):
                    stats = participant.get('stats')
                    kills = 0
                    deaths = 0
                    assists = 0
                    if stats.get('kills'):
                        kills = int(stats.get('kills')) or 0
                    if stats.get('deaths'):
                        deaths = int(stats.get('deaths')) or 0
                    if stats.get('assists'):
                        assists = int(stats.get('assists')) or 0
                    if deaths == 0:
                        kda = "Perfect"
                    else:
                        kda = (float(kills) + float(assists)) / float(deaths)
                        kda = float("{0:.2f}".format(kda))
                    if stats.get('winner'):
                        win = True
                        loose = False
                    else:
                        win = False
                        loose = True
                    if participant.get('spell1id'):
                        sepll1_ids = spell_obj.search(request.cr, 1, [('spell_id','=', int(participant.get('spell1id')))], context=request.context)
                        if sepll1_ids:
                            spell1 = spell_obj.browse(request.cr, 1, sepll1_ids[0], context=request.context)
                    if participant.get('spell2id'):
                        sepll2_ids = spell_obj.search(request.cr, 1, [('spell_id','=', int(participant.get('spell2id')))], context=request.context)
                        if sepll2_ids:
                            spell2 = spell_obj.browse(request.cr, 1, sepll2_ids[0], context=request.context)
                    vals = {
                        'kills': kills,
                        'deaths': deaths,
                        'assists': assists,
                        'kda': kda,
                        'win': win,
                        'loose': loose,
                        'item0': stats.get('item0'),
                        'item1': stats.get('item1'),
                        'item2': stats.get('item2'),
                        'item3': stats.get('item3'),
                        'item4': stats.get('item4'),
                        'item5': stats.get('item5'),
                        'item6': stats.get('item6'),
                        'minionskilled': int(stats.get('minionskilled')) + int(stats.get('neutralminionskilled')),
                        'champlevel': stats.get('champlevel'),
                        'spell1id': spell1.key,
                        'spell2id': spell2.key,
                    }
                    match.update(vals)
        return kwargs
    
    def get_ranked_stats(self, kwargs, region):
        summoner = kwargs['summoner']
        ranked_url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v2.5/league/by-summoner/" +  summoner.summoner_id + "/entry?api_key=" + key
        ranked_stats = GetJson(ranked_url)
        kwargs['ranked_stats'] = {}
        ranked_stats =  ranked_stats[str(summoner.summoner_id)][0]
        entry = ranked_stats.get('entries')[0]
        total_won = int(entry.get('wins'))
        total_lost = int(entry.get('losses'))
        total_played = total_won + total_lost
        total_winrate = (float(total_won) / float(total_played)) * 100
        total_winrate = float("{0:.2f}".format(total_winrate))
        vals = {
            'total_played': total_played,
            'total_won':  total_won,
            'total_lost': total_lost,
            'total_winrate': total_winrate,
            'league_name': ranked_stats.get('name'),
            'league_tier': ranked_stats.get('tier'),
            'league_division': entry.get('division'),
            'league_points': entry.get('leaguePoints'),
        }
        kwargs['ranked_stats'] = vals
        return kwargs
    
    def get_champions_stats(self, kwargs, region):
        champ_obj = request.registry['summoner.champions']
        summoner = kwargs['summoner']
        ranked_stats = kwargs['ranked_stats']
        ranked_played = ranked_stats.get('total_played')
        stats_url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v1.3/stats/by-summoner/" +  summoner.summoner_id + "/ranked?season=SEASON2016&api_key=" + key
        stats = GetJson(stats_url)
        kwargs['champions'] = []
        champions = stats.get('champions')
        for champion in champions:
            if champion.get('id') == 0:
                continue
            stats = champion.get('stats')
            total_won = int(stats.get('totalSessionsWon'))
            total_lost = int(stats.get('totalSessionsLost'))
            total_played = int(stats.get('totalSessionsPlayed'))
            total_winrate = (float(total_won) / float(total_played)) * 100
            total_winrate = float("{0:.2f}".format(total_winrate))
            total_kills = int(stats.get('totalChampionKills')) or 0
            total_deaths = int(stats.get('totalDeathsPerSession')) or 0
            total_assists = int(stats.get('totalAssists')) or 0
            fb_pct = float(stats.get('totalFirstBlood')) / float(total_played) *100
            fb_pct = float("{0:.2f}".format(fb_pct))
            total_gold_earned = stats.get('totalGoldEarned')
            kills = float(total_kills) / float(total_played)
            kills = float("{0:.2f}".format(kills))
            deaths = float(total_deaths) / float(total_played)
            deaths = float("{0:.2f}".format(deaths))
            assists = float(total_assists) / float(total_played)
            assists = float("{0:.2f}".format(assists))
            gold_earned = float(total_gold_earned) / float(total_played)
            gold_earned = float("{0:.2f}".format(gold_earned))
            gp_pct = float(total_played) / float(ranked_played) *100
            gp_pct = float("{0:.2f}".format(gp_pct))
            if deaths == 0:
                kda = "Perfect"
            else:
                kda = (float(kills) + float(assists)) / float(deaths)
                kda = float("{0:.2f}".format(kda))
            vals = {
                'total_played': total_played,
                'total_won':  total_won,
                'total_lost': total_lost,
                'total_winrate': total_winrate,
                'total_kills': total_kills,
                'total_deaths': total_deaths,
                'total_assists': total_assists,
                'total_gold_earned': total_gold_earned,
                'kills': kills,
                'deaths': deaths,
                'assists': assists,
                'gold_earned': gold_earned,
                'kda': kda,
                'fb_pct': fb_pct,
                'gp_pct': gp_pct,
            }
            champ_ids = champ_obj.search(request.cr, 1, [('champion_id','=', int(champion.get('id')))], context=request.context)
            if champ_ids:
                champ = champ_obj.browse(request.cr, 1, champ_ids[0], context=request.context)
                champion_key = champ.key
                champion_name = champ.name
                champion_title = champ.title
                values = {
                    'champion_name': champion_name,
                    'champion_key': champion_key,
                    'champion_title': champion_title,
                }
                vals.update(values)
            kwargs['champions'].append(vals)
        kwargs['champions'] = sorted(kwargs['champions'], key=itemgetter('total_played'), reverse=True) 
        return kwargs
    
    def get_current_game(self, kwargs, region):
        champ_obj = request.registry['summoner.champions']
        spell_obj = request.registry['summoner.spells']
        summoner = kwargs['summoner']
        try:
            current_game_url = "https://" + region + ".api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/" + region.upper() + "1/" +  summoner.summoner_id + "?api_key=" + key
            url = iriToUri(current_game_url)
            result = urllib2.urlopen(url).read()
            game = json.loads(result)
            blue_side = []
            blue_side_id = 0
            red_side = []
            red_side_id = 0
            participants = game.get('participants')
            for participant in participants:
                if participant.get('spell1Id'):
                    sepll1_ids = spell_obj.search(request.cr, 1, [('spell_id','=', int(participant.get('spell1Id')))], context=request.context)
                    if sepll1_ids:
                        spell1 = spell_obj.browse(request.cr, 1, sepll1_ids[0], context=request.context)
                if participant.get('spell2Id'):
                    sepll2_ids = spell_obj.search(request.cr, 1, [('spell_id','=', int(participant.get('spell2Id')))], context=request.context)
                    if sepll2_ids:
                        spell2 = spell_obj.browse(request.cr, 1, sepll2_ids[0], context=request.context)
                champ_ids = champ_obj.search(request.cr, 1, [('champion_id','=', participant.get('championId'))], context=request.context)
                if champ_ids:
                    champ = champ_obj.browse(request.cr, 1, champ_ids[0], context=request.context)
                    champion_key = champ.key
                    champion_name = champ.name
                    champion_title = champ.title
                vals = {
                    'name': participant.get('summonerName'),
                    'icon_id': participant.get('profileIconId'),
                    'spell1id': spell1.key,
                    'spell2id': spell2.key,
                    'champion_name': champion_name,
                    'champion_key': champion_key,
                    'champion_title': champion_title,
                }
                if participant.get('teamId') == 100:
                    blue_side_id += 1
                    vals.update({'participant_id': blue_side_id})
                    blue_side.append(vals)
                if participant.get('teamId') == 200:
                    red_side_id += 1
                    vals.update({'participant_id': red_side_id})
                    red_side.append(vals)
            vals = {
                'blue_side': blue_side,
                'red_side': red_side,
            }
            kwargs['current_game'] = vals
        except:
            kwargs['current_game'] = False
        return kwargs
    
    @http.route([
         '/summoner',
         '/summoner/<region>/<name>',
     ], type='http', auth="public", website=True)
    def summoner(self, name=None, region=None, **kwargs):
        values = {}
        if kwargs or (name and region):
            if not name:
                name = kwargs.get('summoner_name')
            if not region:
                region = kwargs.get('summoner_region')
            print "0", DT.now()
            kwargs = self.get_profile(name, region)
            print "1", DT.now()
            kwargs = self.get_matches(kwargs, region)
            print "2", DT.now()
            kwargs = self.get_champion_details(kwargs, region)
            print "3", DT.now()
            kwargs = self.get_match_details(kwargs, region)
            print "4", DT.now()
            kwargs = self.complete_matches(kwargs)
            print "5", DT.now()
            kwargs = self.get_ranked_stats(kwargs, region)
            print "6", DT.now()
            kwargs = self.get_champions_stats(kwargs, region)
            print "7"
            kwargs = self.get_current_game(kwargs, region)
            print "8"
        for field in summoner_fields:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return request.website.render("synergy_website_summoner.summoner", values)

