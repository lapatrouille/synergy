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
from openerp import models, fields, api, _

class summoner_summoner(models.Model):
    _name = 'summoner.summoner'
    _inherit = ['mail.thread']

    name = fields.Char('Name')
    summoner_name = fields.Char('Summoner Name')
    summoner_id = fields.Char('sumomnerID')
    revision_date = fields.Datetime('revisionDate')
    profile_icon_id = fields.Char('profileIconId')
    summoner_level = fields.Char('summonerLevel')
    region = fields.Char('Region')
    match_ids = fields.One2many('summoner.matches','summoner_id', 'Matches')
    
class summoner_matches(models.Model):
    _name = 'summoner.matches'
    
    summoner_id = fields.Many2one('summoner.summoner', 'Summoner', ondelete='cascade')
    date = fields.Datetime('revisionDate')
    champion_id = fields.Char('Champion ID')
    champion_key = fields.Char('Champion Key')
    champion_name = fields.Char('Chapion Name')
    region = fields.Char('Region')
    queue = fields.Char('Queue')
    season = fields.Char('Season')
    match_id = fields.Char('MatchId')
    role = fields.Char('Role')
    official_role = fields.Char('Official Role')
    platform_id = fields.Char('PlatformId')
    lane = fields.Char('Lane')
    participant_id = fields.Char('ParticipantId')
    match_details_id = fields.Many2one('summoner.matches.details', 'Match Details')
    kills = fields.Char('Kills')
    deaths = fields.Char('Deaths')
    assists = fields.Char('Assists')
    kda = fields.Char('KDA')
    win = fields.Boolean('Win')
    loose = fields.Boolean('Loose')
    minionskilled = fields.Char('minionsKilled')
    champlevel = fields.Char('champlevel')
    item0 = fields.Char('item0')
    item1 = fields.Char('item1')
    item2 = fields.Char('item2')
    item3 = fields.Char('item3')
    item4 = fields.Char('item4')
    item5 = fields.Char('item5')
    item6 = fields.Char('item6')
    spell1id =  fields.Char('spell1Id')
    spell2id =  fields.Char('spell2Id')
    
class summoner_matches_details(models.Model):
    _name = 'summoner.matches.details'
    
    matchid = fields.Char('MatchId')
    matchtype = fields.Char('matchType')
    matchcreation = fields.Datetime('matchCreation')
    platformid =  fields.Char('platformId')
    matchmode =  fields.Char('matchMode')
    matchversion =  fields.Char('matchVersion')
    mapid =  fields.Char('mapId')
    season =  fields.Char('season')
    queuetype =  fields.Char('queueType')
    matchduration =  fields.Char('matchDuration')

    teams_ids = fields.One2many('summoner.matches.details.teams', 'match_details_id', 'Teams')
    participantIdentities_ids = fields.One2many('summoner.matches.details.participantidentities', 'match_details_id', 'ParticipantsIdentities')
    participants_ids = fields.One2many('summoner.matches.details.participants', 'match_details_id', 'Participants')

class summoner_matches_details_teams(models.Model):
    _name = 'summoner.matches.details.teams'
    
    match_details_id = fields.Many2one('summoner.matches.details', ondelete='cascade')
    
    firstblood =  fields.Boolean('firstBlood')
    firsttower =  fields.Boolean('firstTower')
    firstinhibitor =  fields.Boolean('firstInhibitor')
    winner =  fields.Boolean('winner')
    firstdragon =  fields.Boolean('firstDragon')
    vilemawkills =  fields.Char('vilemawKills')
    baronkills =  fields.Char('baronKills')
    teamid =  fields.Char('teamId')
    inhibitorkills =  fields.Char('inhibitorKills')
    dominionvictoryscore =  fields.Char('dominionVictoryScore')
    riftheraldkills =  fields.Char('riftHeraldKills')
    firstriftherald =  fields.Boolean('firstRiftHerald')
    towerkills =  fields.Char('towerKills')
    firstbaron =  fields.Boolean('firstBaron')
    dragonkills =  fields.Char('dragonKills')


class summoner_matches_details_participantidentities(models.Model):
    _name = 'summoner.matches.details.participantidentities'
    
    match_details_id = fields.Many2one('summoner.matches.details', ondelete='cascade')
    
    participantid =  fields.Char('participantId')
    player = fields.Many2one('summoner.matches.details.participantidentities.player','Player')


class summoner_matches_details_participantidentities_player(models.Model):
    _name = 'summoner.matches.details.participantidentities.player'
    
    match_details_participantidentities_id = fields.Many2one('summoner.matches.details.participantidentities', 'participantIdentities')
    profileicon =  fields.Char('profileIcon')
    matchhistoryuri =  fields.Char('matchHistoryUri')
    summonername =  fields.Char('summonerName')
    summonerid =  fields.Char('summonerId')



#STILL NEED TO ADD TimeLine
class summoner_matches_details_participants(models.Model):
    _name = 'summoner.matches.details.participants'
    
    match_details_id = fields.Many2one('summoner.matches.details', ondelete='cascade')
    
    spell1id =  fields.Char('spell1Id')
    spell2id =  fields.Char('spell2Id')
    participantid =  fields.Char('participantId')
    championid =  fields.Char('championId')
    teamid =  fields.Char('teamId')
    highestachievedseasontier =  fields.Char('highestAchievedSeasonTier')
    
    masteries_ids = fields.One2many('summoner.matches.details.participants.masteries', 'match_details_participant_id','Masteries')
    stats_id = fields.Many2one('summoner.matches.details.participants.stats', 'stats')
    runes_ids = fields.One2many('summoner.matches.details.participants.runes', 'match_details_participant_id', 'runes')

class summoner_matches_details_participants_masteries(models.Model):
    _name = 'summoner.matches.details.participants.masteries'
    
    match_details_participant_id = fields.Many2one('summoner.matches.details.participants', 'Participant')
    
    rank = fields.Char('Rank')
    masteryid = fields.Char('masteryId')

class summoner_matches_details_participants_runes(models.Model):
    _name = 'summoner.matches.details.participants.runes'
    
    match_details_participant_id = fields.Many2one('summoner.matches.details.participants', 'Participant')
    rank = fields.Char('Rank')
    runeid = fields.Char('runeId')
    
class summoner_matches_details_participants_stats(models.Model):
    _name = 'summoner.matches.details.participants.stats'
    
    match_details_participant_id = fields.Many2one('summoner.matches.details.participants', 'Participant', ondelete='cascade')
    
    unrealkills = fields.Char('unrealKills')
    assists = fields.Char('assists')
    champlevel = fields.Char('champLevel')
    combatplayerscore = fields.Char('combatPlayerScore')
    deaths = fields.Char('deaths')
    doublekills = fields.Char('doubleKills')
    firstbloodassist = fields.Boolean('firstBloodAssist')
    firstbloodkill = fields.Boolean('firstBloodKill')
    firstinhibitorassist = fields.Boolean('firstInhibitorAssist')
    firstinhibitorkill = fields.Boolean('firstInhibitorKill')
    firsttowerassist = fields.Boolean('firstTowerAssist')
    firsttowerkill = fields.Boolean('firstTowerKill')
    goldearned = fields.Char('goldEarned')
    goldspent = fields.Char('goldSpent')
    inhibitorkills = fields.Char('inhibitorKills')
    item0 = fields.Char('item0')
    item1 = fields.Char('item1')
    item2 = fields.Char('item2')
    item3 = fields.Char('item3')
    item4 = fields.Char('item4')
    item5 = fields.Char('item5')
    item6 = fields.Char('item6')
    killingsprees = fields.Char('killingSprees')
    kills = fields.Char('kills')
    largestcriticalstrike = fields.Char('largestCriticalStrike')
    largestkillingspree = fields.Char('largestKillingSpree')
    largestmultikill = fields.Char('largestMultiKill')
    magicdamagedealt = fields.Char('magicDamageDealt')
    magicdamagedealttochampions = fields.Char('magicDamageDealtToChampions')
    magicdamagetaken = fields.Char('magicDamageTaken')
    minionskilled = fields.Char('minionsKilled')
    neutralminionskilled = fields.Char('neutralMinionsKilled')
    neutralminionskilledenemyjungle = fields.Char('neutralMinionsKilledEnemyJungle')
    neutralminionskilledteamjungle = fields.Char('neutralMinionsKilledTeamJungle')
    objectiveplayerscore = fields.Char('objectivePlayerScore')
    pentakills = fields.Char('pentaKills')
    physicaldamagedealt = fields.Char('physicalDamageDealt')
    physicaldamagedealttochampions = fields.Char('physicalDamageDealtToChampions')
    physicaldamagetaken = fields.Char('physicalDamageTaken')
    quadrakills = fields.Char('quadraKills')
    sightwardsboughtingame = fields.Char('sightWardsBoughtInGame')
    totaldamagedealt = fields.Char('totalDamageDealt')
    totaldamagedealttochampions = fields.Char('totalDamageDealtToChampions')
    totaldamagetaken = fields.Char('totalDamageTaken')
    totalheal = fields.Char('totalHeal')
    totalplayerscore = fields.Char('totalPlayerScore')
    totalscorerank = fields.Char('totalScoreRank')
    totaltimecrowdcontroldealt = fields.Char('totalTimeCrowdControlDealt')
    totalunitshealed = fields.Char('totalUnitsHealed')
    towerkills = fields.Char('towerKills')
    triplekills = fields.Char('tripleKills')
    truedamagedealt = fields.Char('trueDamageDealt')
    truedamagedealttochampions = fields.Char('trueDamageDealtToChampions')
    truedamagetaken = fields.Char('trueDamageTaken')
    visionwardsboughtingame = fields.Char('visionWardsBoughtInGame')
    wardskilled = fields.Char('wardsKilled')
    wardsplaced = fields.Char('wardsPlaced')
    winner = fields.Boolean('winner')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    