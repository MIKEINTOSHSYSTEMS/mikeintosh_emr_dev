# -*- coding: utf-8 -*-

{ 
    'name': 'Pharmacy II- Hospital Information Management System',
    'summary': 'Hospital Pharmacy Management system. Manage pharmacy operations of sale, purchase, batch pricing and barcoding',
    'description': """
    Hospital Pharmacy Management system. Manage pharmacy operations of sale, purchase, batch pricing and barcoding Pharmacy Menus. Barcode generation
        Batch Wise Pricing Product Expiry Product Manufacture Lock Lot yan hms medical healthcare health care
    """,
    'version': '1.2',
    'category': 'Medical',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_tasks', 'yan_pharmacy'],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/hms_base_view.xml",
        "views/menu_item.xml",
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
}
