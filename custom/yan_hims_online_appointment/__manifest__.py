# -*- coding: utf-8 -*-

{
    'name' : 'Online Appointment - Hospital Information Management System',
    'summary' : 'Allow patients to Book an Appointment on-line',
    'description' : """Book an Appointment online to HIMS system. """,
    'version': '1.0.6',
    'category': 'Medical',
    'author': 'Momona Healthcare',
    'website': 'https://www.momonahealthcare.com',
    'license': 'OPL-1',
    'depends' : ['yan_hims_portal','website_payment','account_payment'],
    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/website_page.xml',
        'views/hms_base_view.xml',
        'views/schedule_views.xml',
        'views/template.xml',
        'views/res_config_settings_views.xml',
        'wizard/appointment_scheduler_wizard.xml',
        'wizard/payment_link_views.xml',
        'views/menu_item.xml',
    ],
    'assets': {
        'web.assets_frontend': [        
            'yan_hims_online_appointment/static/src/js/payment_form.js',
            'yan_hims_online_appointment/static/src/js/hms_portal.js',
            'yan_hims_online_appointment/static/src/scss/custom.scss',
        ]
    },

    'installable': True,
    'application': True,
    'sequence': 1,
}
