# -*- coding: utf-8 -*-

{ 
    'name': 'Ambulance -- Hospital Information Management System',
    'summary': 'Hospital Ambulance Management System',
    'description': """
        This Module will install Ambulance Module, which will help to register Ambulance bookings, Fleet management, Invoicing and related tracking.
    """,
    'version': '1.0.2',
    'category': 'Medical',
    'author': 'Yanos IT Solutions and Momona Healthcare',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_tasks','fleet'],
    'data': [
        'security/hms_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/ambulance_views.xml',
        'views/hms_base_view.xml',
        'views/res_config_view.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 2,
}
