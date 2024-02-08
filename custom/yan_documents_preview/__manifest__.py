# -*- coding: utf-8 -*-

{
    'name' : 'Documents Preview I - Hospital Information Management System',
    'summary': 'Patient Documents Preview.',
    'description': """Hospital / Patient Documents Preview. Document management system document preview 
    """,
    'version': '1.0.1',
    'category': 'Medical',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends' : ['portal','yan_document_base'],
    'data' : [
        'views/template.xml',
    ],
    "cloc_exclude": [
        "static/**/*", # exclude all files in a folder hierarchy recursively
    ],
    'application': False,
    'sequence': 0,
}