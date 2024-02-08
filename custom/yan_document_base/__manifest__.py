# -*- coding: utf-8 -*-

{
    'name': 'Documents Preview Base - Hospital Information Management System',
    'summary': 'Manage Documents at single place or see all related documents directly.',
    'description': """Manage Documents at single place or see all related documents directly on patient.
    """,
    'version': '1.0.1',
    'category': 'Medical',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['mail', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'view/document_view.xml',
        'view/attachment_view.xml',
        'view/menu_item.xml',
    ],
    'application': False,
    'sequence': 2,
}