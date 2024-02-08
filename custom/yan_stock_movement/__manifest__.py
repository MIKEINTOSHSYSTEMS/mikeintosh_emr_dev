# -*- coding: utf-8 -*-

{
    'name': 'Create Stock Moves With Invoice And Refunds',
    'category': 'Accounting',
    'version': '1.0.1',
    'author' : 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'summary': """Update Stock Automatically when validate Invoice And Refunds.""",
    'description': """Update Stock Automatically when validate Invoice And Refunds.
    change stock on refund stock move on refund picking with invoice with picking
    update stock on refund stock updatation on invoice update stock on invoice stock moves on invoice
    create piking on invoice 
    """,
    'depends': ['account', 'stock', 'product_expiry'],
    'data': [
        'views/invoice_view.xml',
        'views/res_users_view.xml',
    ],
    'installable': True,
    'auto_install': False,

}