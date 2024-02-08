# -*- coding: utf-8 -*-

{
    'name': 'Pharmacy I - Hospital Information Management System ',
    'summary': 'Pharmacy Management system. Manage pharmacy operations of sale, purchase, batch pricing and barcoding',
    'description': """Pharmacy Management system. Manage pharmacy operations of sale, purchase, batch pricing and barcoding Pharmacy Menus. 
        Batch Wise Pricing Product Expiry Product Manufacture Lock Lot yan hms medical healthcare health care
    """,
    'version': '1.0.1',
    'category': 'Medical',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_start', 'yan_stock_movement', 'yan_barcode_reader'],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/stock_view.xml",
        "views/product_view.xml",
        "views/invoice_view.xml",
        "report/lot_barcode_report.xml",
        "report/picking_barcode_report.xml",
        "report/paper_format.xml",
        "report/report_invoice.xml",
        "report/medicine_expiry_report.xml",
        "wizard/stock_wizard.xml",
        "wizard/wiz_lock_lot_view.xml",
        "wizard/wiz_medicine_expiry_view.xml",
        "views/menu_item.xml",
    ],
    'installable': True,
    'application': True,
    'sequence': 1,

}
