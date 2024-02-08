# -*- coding: utf-8 -*-

{
    'name': 'Start - Hospital Information Management System ',
    'summary': 'Hospital Management System Base for further flows',
    'description': """
        Hospital Information Management System for managing Hospital and medical functions from start to end
          """,
    'version': '1.2',
    'category': 'Medical',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['account', 'stock', 'hr', 'product_expiry'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/paper_format.xml',
        'report/report_layout.xml',
        'report/report_invoice.xml',

        'data/sequence.xml',
        'data/mail_template.xml',

        'views/hms_base_views.xml',
        'views/patient_view.xml',
        'views/physician_view.xml',
        'views/product_view.xml',
        'views/drug_view.xml',
        'views/account_view.xml',
        'views/res_config_settings.xml',
        'views/menu_item.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
}

