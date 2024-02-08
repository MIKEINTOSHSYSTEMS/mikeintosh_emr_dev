# -*- coding: utf-8 -*-

{
    'name' : 'Documents Preview II - Hospital Information Management System',
    'summary': 'Patient Documents Preview.',
    'description': """Hospital / Patient Documents Preview. Document management system 
    """,
    'version': '1.0.1',
    'category': 'Medical',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends' : ['yan_hims_tasks','yan_documents_preview'],
    'data': [
        'views/yan_hms_views.xml',
    ],
    'application': False,
    'sequence': 2,
}
