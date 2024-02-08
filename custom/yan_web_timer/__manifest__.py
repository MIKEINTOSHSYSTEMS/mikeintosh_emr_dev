# -*- coding: utf-8 -*-

{
    'name': "Timer Controller",
    'category': "web",
    'version': "1.0.1",
    'summary': """Add timer controller on web view.""",
    'description': """This module allows you to set timer on any field by passing your start and end date. start stop timer working time""",
    "website": 'www.yanosgroup.com',
    'author': 'Yanos Group',
    'license': 'OPL-1',
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'yan_web_timer/static/src/js/TimeCounter.js',
            'yan_web_timer/static/src/js/TimeCounter.xml',
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': False,

}
