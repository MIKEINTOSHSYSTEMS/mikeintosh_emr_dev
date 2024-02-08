# -*- coding: utf-8 -*-

{ 
    'name': 'Radiology I - Hospital Information Management System',
    'summary': 'Manage Radiology requests, Radiology tests, Invoicing and related history for hospital.',
    'description': """
        This module add functionality to manage Radiology flow. radiology management system
        Hospital Management lab tests radiology invoices radiology test results 
    """,
    'version': '1.0.5',
    'category': 'Medical',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_start', 'yan_hmis_documents_preview'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/radiology_prescription.xml',
        'report/radiology_report.xml',
        'report/radiology_request_results.xml',

        'data/mail_template.xml',
        'data/data.xml',
        'data/digest_data.xml',
        'data/radiology_data.xml',

        'views/radiology_request_view.xml',
        'views/radiology_test_view.xml',
        'views/radiology_patient_test_view.xml',
        'views/hms_base_view.xml',
        'views/res_config.xml',
        'views/portal_template.xml',
        'views/templates_view.xml',
        'views/radiology_view.xml',
        'views/digest_view.xml',

        'views/menu_item.xml',
    ],
    'demo': [
        'data/radiology_demo.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
}