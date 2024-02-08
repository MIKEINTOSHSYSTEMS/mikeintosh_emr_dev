# -*- coding: utf-8 -*-

{
    'name': 'Medical Surgery - Hospital Information Management System',
    'category': 'Medical',
    'summary': 'Manage Medical Surgery related operations',
    'description': """
    Manage Medical Surgery related operations hospital Information management system 
    """,
    'version': '1.5',
    'author': 'Yanos Group',
    'support': 'support@yanosgroup.com',
    'website': 'www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_tasks'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/digest_data.xml',
        'report/package_report.xml',
        'report/surgery_report.xml',
        'views/surgery_base.xml',
        'views/surgery_template_view.xml',
        'views/surgery_view.xml',
        'views/hms_base_view.xml',
        'views/package_view.xml',
        'views/res_config_settings_views.xml',
        'views/digest_view.xml',
        'views/menu_item.xml',
    ],
    'demo': [
        'demo/hms_demo.xml',
    ],
    'sequence': 1,
    'application': True,

}
