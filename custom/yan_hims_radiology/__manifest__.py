# -*- coding: utf-8 -*-

{ 
    'name': 'Radiology II - Hospital Information Management System',
    'summary': 'Manage Radiology requests, Radiology tests, Invoicing and related history for hospital.',
    'description': """
        This module add functionality to manage Radiology flow. radiology management system
        Hospital Management lab tests radiology invoices radiology test results
    """,
    'version': '1.0.2',
    'category': 'Medical',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_tasks','yan_radiology'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/report_yan_radiology_prescription.xml',
        'report/radiology_report.xml',
        'report/report_medical_advice.xml',

        'views/hms_base_view.xml',
        'views/radiology_view.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,

}
