# -*- coding: utf-8 -*-

{
    'name': 'Tasks - Hospital Information Management System ',
    'summary': 'Hospital Information Management System for managing Hospital and medical centers',
    'description': """ Hospital Information Management System,  tasks and procedures to manage facilities workflows flows
            """,
    'version': '1.2',
    'category': 'Medical',
    'author': 'Yanos Group',
    'website': 'https://www.yanosgroup.com',
    'license': 'OPL-1',
    'depends': ['yan_hims_start', 'yan_web_timer', 'website', 'digest'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/patient_cardreport.xml',
        'report/report_medical_advice.xml',
        'report/report_prescription.xml',
        'report/appointment_report.xml',
        'report/evaluation_report.xml',
        'report/treatment_report.xml',
        'report/procedure_report.xml',

        'data/sequence.xml',
        'data/mail_template.xml',
        'data/hms_data.xml',
        'data/digest_data.xml',
        
        'wizard/cancel_reason_view.xml',
        'wizard/pain_level_view.xml',
        'wizard/reschedule_appointments_view.xml',

        'views/hms_base_views.xml',
        'views/patient_view.xml',
        'views/physician_view.xml',
        'views/evaluation_view.xml',
        'views/appointment_view.xml',
        'views/diseases_view.xml',
        'views/medicament_view.xml',
        'views/prescription_view.xml',
        'views/medication_view.xml',
        'views/treatment_view.xml',
        'views/procedure_view.xml',
        'views/resource_cal.xml',
        'views/medical_alert.xml',
        'views/account_view.xml',
        'views/product_kit_view.xml',
        'views/template.xml',
        'views/res_config_settings_views.xml',
        'views/digest_view.xml',
        'views/menu_item.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'yan_hims_tasks/static/src/js/hms_graph_field.js',
            'yan_hims_tasks/static/src/js/hms_graph_field.xml',
            'yan_hims_tasks/static/src/js/hms_graph_field.scss',
            'yan_hims_tasks/static/src/scss/custom.scss',
        ]
    },
    'demo': [

    ],
    'installable': True,
    'application': True,
    'sequence': 1,

}
