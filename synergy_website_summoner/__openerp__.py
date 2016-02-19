{
    'name': 'Synergy Summoner Website',
    'category': 'Website',
    'website': 'http://synergy.gg',
    'summary': 'Consult Summoner Stats',
    'version': '1.0',
    'description': """
    Synergy Website Module

        """,
    'author': 'Synergy.gg',
    'depends': ['website_partner'],
    'data': [
        'data/data.xml',
        'views/website_summoner.xml',
        'views/summoner_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
