# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 credativ ltd. <info@credativ.co.uk>
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
#    Tesk Key 74537082-db44-4916-9ca3-09f8f8b7638e
#
#################################################################################

{
    "name" : "RIOT API",
    "version" : "1.0",
    "author" : "Julius Network Solutions",
    "website" : "http://julius.fr",
    "category" : "riot",
    "depends" : [
        'base',
    ],
    "description": """
    Specific Notification Module for Please
    """,
    "demo" : [],
    "data" : [
        'wizard/request_api_wizard.xml',
    ],
    'installable' : True,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
