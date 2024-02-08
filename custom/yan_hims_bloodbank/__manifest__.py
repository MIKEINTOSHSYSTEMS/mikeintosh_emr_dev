# -*- coding: utf-8 -*-
{ 
    'name': 'Blood Bank - Hospital Information Management System',
    'summary': 'Hospital Blood Bank Management System by AlmightyCS',
    'description': """
        This Module will install Blood Bank Module, which will help to register user, and managed blood 
        in the Blood Bank. 
    """,
    'version': '1.0.2',
    'category': 'Medical',
    'author': 'Yanos IT Solutions with Momona healthcare.',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_tasks','product_expiry'],
    'data': [
        'security/hms_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/blood_bank_views.xml',
        'views/partner_view.xml',
        'views/patient_view.xml',
        'views/stock_view.xml',
        'views/res_config_view.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 2,
}
