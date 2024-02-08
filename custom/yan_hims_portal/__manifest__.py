# -*- coding: utf-8 -*-

{
    'name' : 'Patient Portal - Hospital Information Management System',
    'summary' : 'This Module allow Patients to access to their appointments and prescriptions',
    'description' : """
    This Module allow Patients to access to their appointments and prescriptions
    """,
    'version': '1.2',
    'category': 'Medical',
    'author': 'Yanos Group.',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends' : ['portal','yan_hims_tasks','website'],
    'data' : [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/email_template.xml',
        'data/data.xml',
        'views/yan_hms_view.xml',
        'views/template.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'web/static/lib/Chart/Chart.js',
            'yan_hims_portal/static/src/js/portal_chart.js'
        ]
    },
    'installable': True,
    'application': True,
    'sequence': 1,

}
