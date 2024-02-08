# -*- coding: utf-8 -*-

{
    'name': 'Add Products by Barcode reader in to Invoice',
    'version': '1.0.1',
    'category': 'Accounting',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'summary': """Add Products by scanning barcode to avoid mistakes and make work faster in Invoice.""",
    'description': """Add Products by scanning barcode to avoid mistakes and make work faster in Invoice.
    """,
    'license': 'OPL-1', 
    "depends": ["account",'barcodes'],
    "data": [
        "views/account_invoice_view.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
