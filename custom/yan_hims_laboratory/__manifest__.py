# -*- coding: utf-8 -*-

{ 
    'name': 'Laboratory II - Hospital Information Management System',
    'summary': 'Manage Lab requests, Lab tests, Invoicing and related history for hospital.',
    'description': """
        This module add functionality to manage Laboratory flow. laboratory management system
        Hospital Management lab tests laboratory invoices laboratory test results
    """,
    'version': '1.1',
    'category': 'Medical',
    'author': 'Yanos Group.',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_tasks','yan_laboratory'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/report_yan_lab_prescription.xml',
        'report/lab_report.xml',
        'report/report_medical_advice.xml',

        'views/hms_base_view.xml',
        'views/laboratory_view.xml',
    ],
    
    'installable': True,
    'application': True,
    'sequence': 1,

}
