# -*- coding: utf-8 -*-

{ 
    'name': 'Laboratory I - Hospital Information Management System',
    'summary': 'Manage Lab requests, Lab tests, Invoicing and related history for hospital.',
    'description': """
        This module add functionality to manage Laboratory flow. laboratory management system
        Hospital Information Management lab tests laboratory invoices laboratory test results 
    """,
    'version': '1.1',
    'category': 'Medical',
    'author': 'Yanos Group',
    'support': 'support@yanosgroup.com',
    'website': 'www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_start'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/report_yan_lab_prescription.xml',
        'report/lab_report.xml',
        'report/lab_request_results.xml',
        'report/lab_samples_report.xml',
        'report/paper_format.xml',

        'data/mail_template.xml',
        'data/laboratory_data.xml',
        'data/lab_uom_data.xml',
        'data/lab_category_list_data.xml',
        'data/lab_sample_type_data.xml',
        'data/lab_category_list_data.xml',
        'data/digest_data.xml',
        'data/laboratory_data_service.xml',
        
        'views/lab_uom_view.xml',
        'views/laboratory_request_view.xml',
        'views/laboratory_view.xml',
        'views/laboratory_test_view.xml',
        'views/laboratory_patient_test_view.xml',
        'views/laboratory_sample_view.xml',
        'views/hms_base_view.xml',
        'views/res_config.xml',
        'views/portal_template.xml',
        'views/templates_view.xml',
        'views/digest_view.xml',
        'views/menu_item.xml',
    ],
    'demo': [
        'data/laboratory_demo.xml',
    ],
    
    'installable': True,
    'application': True,
    'sequence': 1,

}
