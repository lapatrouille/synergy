# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from openerp import models, fields, api, _
from openerp.osv import fields as old_fields
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import hashlib
import random
import urllib
import urllib2
import json

class request_api(models.TransientModel):
    _name = 'request.api'
    
    summoner_name = fields.Char('Name')
    region = fields.Selection([('euw','EUW'), ('na','NA')], 'Region')
    api_return = fields.Text('API Return')
    
    @api.one
    def call_api_request(self):
        #         url = 'http://please-middleware.netapsys.fr/notification/pushnotification'
        name = self.summoner_name
        region = self.region
        key = "74537082-db44-4916-9ca3-09f8f8b7638e"
#         url = https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/RiotSchmick?api_key=<key>
        url = "https://" + region + ".api.pvp.net/api/lol/" + region + "/v1.4/summoner/by-name/" + name + "?api_key=" + key
        print url
        response = urllib2.urlopen(url)
        print response
        result = response.read()
        print result
        self.write({'api_return': result})
        return self.write({'api_return': result})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
